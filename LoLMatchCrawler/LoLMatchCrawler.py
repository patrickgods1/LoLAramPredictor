from typing import Dict, Tuple, Any
from pantheon import pantheon
import asyncio
import asyncpg
from config import dbConfig, matchlistParams, riotConfig
import json
import os

def requestsLog(url: str, status:str, headers:str) -> None:
    pass
    # print(url)
    # print(status)
    # print(headers)


async def getAccount(name: str) -> Tuple[str, str]:
    try:
        data = await panth.getSummonerByName(name)
    except Exception as e:
        print(e)
    else:
        return (data['accountId'], data['name'])


async def getSeedAccounts(nameList: list) -> list:
    try:
        accounts = [await getAccount(name) for name in nameList]
    except Exception as e:
        print(e)
    else:
        return accounts

async def getAllMatches(loop: asyncio.AbstractEventLoop, accountIdQueue: asyncio.Queue, 
                        matchQueue: asyncio.Queue, accountId2summonerId: Dict[str, str,],
                        visitedSummoners: set, visitedMatches: set, 
                        matchlistParams: Dict[str, int] = {"endIndex": 5}) -> None:
    # N_TASKS = matchlistParams['endIndex']
    N_TASKS = riotConfig['apiRate']
    try:
        pool = await asyncpg.create_pool(user=dbConfig['user'],
                                        password=dbConfig['password'],
                                        host=dbConfig['host'],
                                        port=dbConfig['port'],
                                        database=dbConfig['database'])
        async with pool.acquire() as connection:
            gameIds = await connection.fetch('SELECT "gameId" FROM "Matches" ORDER BY "gameId" ASC')
            # summonerNames = await connection.fetch('SELECT DISTINCT "summonerName" FROM "Participant_Stats"')
        visitedMatches.update({record[0] for record in gameIds})
        # if not riotConfig['revisitSummoners']:
        #     visitedSummoners.update({record[0] for record in summonerNames})
        producers = [loop.create_task(processMatches(accountIdQueue, matchQueue, accountId2summonerId,
                        visitedSummoners, visitedMatches, pool)) for _ in range(N_TASKS)]
        consumers = [loop.create_task(getMatches(accountIdQueue, matchQueue, accountId2summonerId,
                        visitedSummoners, visitedMatches, matchlistParams)) for _ in range(N_TASKS)]
        await asyncio.gather(*producers)
        for c in consumers:
            c.cancel()
    except Exception as e:
        await pool.close()
        print(e)


async def getMatches(accountIdQueue: asyncio.Queue, matchQueue: asyncio.Queue, 
                     accountId2summonerId: Dict[str, str], visitedSummoners: set,
                     visitedMatches: set, matchlistParams: Dict[str, int] = {"endIndex": 5}) -> None:
    # while True:
    while matchQueue.empty():
        try:
            accountId = await accountIdQueue.get()
            matchList = await panth.getMatchlist(accountId, matchlistParams)
            for match in matchList['matches']:
                if match['gameId'] not in visitedMatches:
                    matchQueue.put_nowait(match['gameId'])
        except Exception as e:
            print(f'[WARNING] getMatches Error: {e}')
        else:
            visitedSummoners.add(accountId2summonerId[accountId])
            # print(f'matchQueue: {matchQueue}')
            print(f'[INFO] Visited {len(visitedSummoners)} accounts')
            # print(f':\n{visitedAccounts}')
            accountIdQueue.task_done()


async def processMatches(accountIdQueue: asyncio.Queue, matchQueue: asyncio.Queue, 
                        accountId2summonerId: Dict[str, str], visitedSummoners: set,
                         visitedMatches: set, pool: asyncpg.pool.Pool) -> None:
    while True:
        try:
            gameId = await matchQueue.get()
            match = await panth.getMatch(gameId)
            await insertMatch(match, pool)
            await insertTeams(gameId, match['teams'], pool)
            columnNamesList = []
            participantStatsList = []
            for i in range(len(match['participantIdentities'])):
                accountId = match['participantIdentities'][i]['player']['currentAccountId']
                # summonerId = match['participantIdentities'][i]['player']['summonerId']
                summonerName = match['participantIdentities'][i]['player']['summonerName']
                if summonerName not in visitedSummoners:
                    accountId2summonerId[accountId] = summonerName
                    accountIdQueue.put_nowait(accountId)
                columnNames, participantStats = await processParticipant(gameId, summonerName, match['participants'][i])
                columnNamesList.append(tuple(columnNames))
                participantStatsList.append(tuple(participantStats))
            await insertParticipant(columnNamesList, participantStatsList, pool)
        except Exception as e:
            print(f'[WARNING] processMatches Error ({gameId}): {e}')
        else:
            visitedMatches.add(gameId)
            # print(f'accountIdQueue: {accountIdQueue}')
            print(f'[INFO] Stored match: {gameId}')
            print(f'[INFO] Visited {len(visitedMatches)} matches')
            # print(f':\n{visitedMatches}')
            if matchQueue.empty():
                print(f'[INFO] matchQueue is empty. Looking up more summoners for new matches.')
                params = {k: v for k, v in matchlistParams.items() if v}
                await getMatches(accountIdQueue, matchQueue, accountId2summonerId,
                        visitedSummoners, visitedMatches, params)
            matchQueue.task_done()


async def insertMatch(match: Dict[str,any], pool: asyncpg.pool.Pool) -> None:
    columnNames = ('"gameId", "platformId", "gameCreation", "gameDuration", "queueId", '
                    '"mapId", "seasonId", "gameVersion", "gameMode", "gameType"')
    # matchInfo = ()
    insertStatement = (f'INSERT INTO "Matches" ({columnNames})\n'
                    f'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)\n'
                    f'ON CONFLICT DO NOTHING')
    try:
        async with pool.acquire() as connection:
            await connection.execute(insertStatement, 
                    match['gameId'],
                    match['platformId'],
                    match['gameCreation'],
                    match['gameDuration'],
                    match['queueId'],
                    match['mapId'],
                    match['seasonId'],
                    match['gameVersion'],
                    match['gameMode'],
                    match['gameType'])
    except Exception as e:
        print(f'insertMatch Error')
        print(e)
    

async def insertTeams(gameId: str, teams: Dict[str,any], pool: asyncpg.pool.Pool) -> None:
    columnNames = ('"gameId", "win", "teamColor", "firstBlood", "firstTower", '
                    '"firstInhibitor",  "firstBaron", "firstDragon", "firstRiftHerald", '
                    '"towerKills", "inhibitorKills", "baronKills", "dragonKills", '
                    '"vilemawKills", "riftHeraldKills", "dominionVictoryScore"')
    teamsList = []
    for team in teams:
        if team['teamId'] == 100:
            teamColor = 'Blue'
        else:
            teamColor = 'Red'
        teamsList.append((gameId, team['win'], teamColor, team['firstBlood'],
                        team['firstTower'], team['firstInhibitor'], team['firstBaron'],
                        team['firstDragon'], team['firstRiftHerald'], team['towerKills'],
                        team['inhibitorKills'], team['baronKills'], team['dragonKills'],
                        team['vilemawKills'], team['riftHeraldKills'], team['dominionVictoryScore']))
    insertStatement = (f'INSERT INTO "Team_Stats" ({columnNames})\n'
                    f'VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, '
                    f'$10, $11, $12, $13, $14, $15, $16)\n'
                    f'ON CONFLICT DO NOTHING')
    try:
        async with pool.acquire() as connection:
            await connection.executemany(insertStatement, teamsList)
    except Exception as e:
        print(f'insertTeams Error')
        print(e)


async def insertParticipant(columnNamesList: list, participantStatsList: list, pool: asyncpg.pool.Pool) -> None:
    for i in range(len(participantStatsList)):
        columnNames = ', '.join([f'"{c}"' for c in columnNamesList[i]])
        placeholders = ', '.join([f'${j+1}' for j in range(len(participantStatsList[i]))])
        insertStatement = (f'INSERT INTO "Participant_Stats" ({columnNames})\n'
                        f'VALUES ({placeholders})\n'
                        f'ON CONFLICT DO NOTHING')
        try:
            async with pool.acquire() as connection:
                await connection.execute(insertStatement, *participantStatsList[i])
        except Exception as e:
            print(f'insertParticipant Error')
            print(e)
            

async def processParticipant(gameId: str, summonerName: str, participant: Dict[str, any]) -> tuple:
    flattenDict = {'gameId': gameId, 'summonerName': summonerName}
    for key, val in participant.items():
        if isinstance(val, dict):
            for key2, val2 in val.items():
                if isinstance(val2, dict):
                    for key3, val3 in val2.items():
                        newKey = f'{key2}{key3}'
                        flattenDict.update({newKey:val3})
                elif key2 == 'participantId':
                    continue
                else:
                    flattenDict.update({key2:val2})
        elif key == 'participantId':
            continue
        elif key == 'teamId':
            flattenDict.update({'teamColor': 'Blue'} if val == 100 else {'teamColor': 'Red'})
        else:
            flattenDict.update({key:val})
    return (flattenDict.keys(), flattenDict.values())

    
def main() -> None:
    params = {k: v for k, v in matchlistParams.items() if v}
    try:
        loop = asyncio.get_event_loop()
        accountIdQueue = asyncio.Queue()
        matchQueue = asyncio.Queue()
        accountId2summonerId = dict()
        visitedMatches = set()
        visitedSummoners = set()
        if os.path.isfile('.\MatchWIP\progress.json') and os.access('.\MatchWIP\progress.json', os.R_OK):
            with open('.\MatchWIP\progress.json') as f:
                data = json.load(f)
            visitedSummoners.update(data['visitedSummoners'])
            # visitedMatches.update(data['visitedMatches'])
            # for id in data['workingAccountIds']:
            #     accountIdQueue.put_nowait(id)
            for match in data['workingMatches']:
                matchQueue.put_nowait(match)
            print('-'*80)
            # print(f'Visited {len(visitedMatches)} matches')
            # print(f'{visitedMatches}')
            # print('-'*80)
            # print(f'Visited {len(visitedSummoners)} accounts')
            # print(f'{visitedAccounts}')
            # print('-'*80)
            print(f'matchQueue({matchQueue})')
            print('-'*80)
            # print(f'accountIdQueue({accountIdQueue})')
            # print('-'*80)
        else:
            seedAccountIds = loop.run_until_complete(getSeedAccounts(riotConfig['seedSummonerNames']))
            for accountId, summonerName in seedAccountIds:
                print(f'{summonerName}: {accountId}')
                accountIdQueue.put_nowait(accountId)
                accountId2summonerId[accountId] = summonerName
        loop.run_until_complete(getAllMatches(loop, accountIdQueue, matchQueue, 
                                            accountId2summonerId, visitedSummoners, 
                                            visitedMatches, params))
    except KeyboardInterrupt:
        print('Exiting.....')
    except Exception as e:
        print(e)
    finally:
        # print(f'accountIdQueue:\n{accountIdQueue}')
        # print(f'matchQueue:\n{matchQueue}')
        for task in asyncio.Task.all_tasks():
            task.cancel()
        # accountIdList = [accountIdQueue.get_nowait() for _ in range(accountIdQueue.qsize())]
        matchList = [matchQueue.get_nowait() for _ in range(matchQueue.qsize())]
        print('-'*80)
        print(f'Visited {len(visitedMatches)} matches')
        # print(f'{visitedMatches}')
        print('-'*80)
        print(f'Visited {len(visitedSummoners)} summoners')
        # print(f'{visitedAccounts}')
        print('-'*80)
        print(f'matchQueue({len(matchList)})')
        # print(f'{matchList}')
        # print('-'*80)
        # print(f'accountIdQueue({len(accountIdList)})')
        # print(f'{accountIdList}')
        print('-'*80)
        data = {
                # 'numVisitedMatches': len(visitedMatches),
                # 'visitedMatches': list(visitedMatches),
                'numWorkingMatches': len(matchList),
                'workingMatches': sorted(matchList),
                'numVisitedSummoners': len(visitedSummoners),
                'visitedSummoners': sorted(list(visitedSummoners)),
                # 'numWorkingAccountIds': len(accountIdList),
                # 'workingAccountIds': accountIdList
                }
        if not os.path.exists('MatchWIP'):
            os.mkdir('MatchWIP')
        with open('.\MatchWIP\progress.json', 'w') as outputFile:
            json.dump(data, outputFile, indent=4)

panth = pantheon.Pantheon(riotConfig['server'], riotConfig['api_key'], errorHandling=True, requestsLoggingFunction=requestsLog, debug=True)

if __name__ == '__main__':
    main()

