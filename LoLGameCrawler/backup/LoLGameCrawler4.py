from typing import Dict, Tuple, Any
from pantheon import pantheon
import asyncio
import asyncpg
from config4 import dbConfig, matchlistParams, riotConfig
import json
import os
import ssl
from bs4 import BeautifulSoup
import random

def requestsLog(url: str, status:str, headers:str) -> None:
    pass
    # print(url)
    # print(status)
    # print(headers)


async def getTop500() -> list:
    res = await panth.fetch('https://aram.moe/', method='GET')
    html = await res.text()
    soup = BeautifulSoup(html, 'html.parser')
    return [name.text for name in soup.find_all('span', {'class': 'name'})]


async def getAccount(name: str) -> Tuple[str, str]:
    try:
        data = await panth.getSummonerByName(name)
    except Exception as e:
        print(e)
    else:
        return (data['accountId'], data['name'])


async def getSeedAccounts(loop: asyncio.AbstractEventLoop, nameList: list) -> list:
    try:
        top500 = await getTop500()
        nameList.extend(random.sample(top500, 50))
        tasks = [loop.create_task(getAccount(name)) for name in nameList]
        accounts = await asyncio.gather(*tasks)
    except Exception as e:
        print(e)
    else:
        return [acc for acc in accounts if acc]


async def getAllMatches(loop: asyncio.AbstractEventLoop, accountIdQueue: asyncio.Queue, 
                        matchQueue: asyncio.Queue, accountId2summonerId: Dict[str, str],
                        summonerId2summonerName: Dict[str, str], visitedSummoners: set, 
                        visitedMatches: set, matchlistParams: Dict[str, int]) -> None:
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
        champMasteryQueue = asyncio.Queue()
        summonerIdQueue1 = asyncio.Queue()
        summonerIdQueue2 = asyncio.Queue()
        rankDataQueue = asyncio.Queue()
        producers = [loop.create_task(getMatches(accountIdQueue, matchQueue, accountId2summonerId,
                        visitedSummoners, visitedMatches, matchlistParams)) for _ in range(N_TASKS)]
        consumeMatch = [loop.create_task(processMatches(accountIdQueue, matchQueue, summonerIdQueue1, 
                        summonerIdQueue2, accountId2summonerId, summonerId2summonerName, 
                        visitedSummoners, visitedMatches, pool)) for _ in range(N_TASKS)]
        consumeChampMastery = [loop.create_task(getChampMastery(champMasteryQueue, summonerIdQueue1))
                                for _ in range(N_TASKS*10)]
        storeChampMastery = [loop.create_task(insertChampMastery(champMasteryQueue, summonerId2summonerName, pool))
                                for _ in range(N_TASKS*10*152)]
        consumeRank = [loop.create_task(getRankInfo(rankDataQueue, summonerIdQueue2, summonerId2summonerName, 
                        visitedSummoners)) for _ in range(N_TASKS*10)]
        storeRank = [loop.create_task(insertRankInfo(rankDataQueue, summonerId2summonerName, 
                        visitedSummoners, pool)) for _ in range(N_TASKS*10*2)]
        await asyncio.gather(*producers, *consumeMatch, *consumeChampMastery, *storeChampMastery, 
                                *consumeRank, *storeRank, return_exceptions=True)
        await accountIdQueue.join()
        consumeMatch.cancel()
        consumeChampMastery.cancel()
        storeChampMastery.cancel()
        consumeRank.cancel()
        storeRank.cancel()
    except Exception as e:
        await pool.close()
        print(f'[ERROR] getAllMatches: {e}')


async def getMatches(accountIdQueue: asyncio.Queue, matchQueue: asyncio.Queue, 
                     accountId2summonerId: Dict[str, str], visitedSummoners: set,
                     visitedMatches: set, matchlistParams: Dict[str, int] = {"endIndex": 5}) -> None:
    # while True:
    while matchQueue.empty():
        try:
            accountId = await accountIdQueue.get()
            matchList = await asyncio.gather(panth.getMatchlist(accountId, matchlistParams))
            for match in matchList[0]['matches']:
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
                        summonerIdQueue1: asyncio.Queue, summonerIdQueue2: asyncio.Queue, 
                        accountId2summonerId: Dict[str, str], summonerId2summonerName: Dict[str, str], 
                        visitedSummoners: set, visitedMatches: set, pool: asyncpg.pool.Pool) -> None:
    while True:
        try:
            gameId = await matchQueue.get()
            match = await panth.getMatch(gameId)
            await asyncio.ensure_future(insertMatch(match, pool))
            await asyncio.ensure_future(insertTeams(gameId, match['teams'], pool))
            columnNamesList = []
            participantStatsList = []
            for i in range(len(match['participantIdentities'])):
                accountId = match['participantIdentities'][i]['player']['currentAccountId']
                summonerId = match['participantIdentities'][i]['player']['summonerId']
                summonerName = match['participantIdentities'][i]['player']['summonerName']
                summonerId2summonerName[summonerId] = summonerName
                if summonerName not in visitedSummoners:
                    accountId2summonerId[accountId] = summonerName
                    accountIdQueue.put_nowait(accountId)
                    summonerIdQueue1.put_nowait(summonerId)
                    summonerIdQueue2.put_nowait(summonerId)
                columnNames, participantStats = await processParticipant(gameId, summonerName, match['participants'][i])
                columnNamesList.append(tuple(columnNames))
                participantStatsList.append(tuple(participantStats))
            await asyncio.ensure_future(insertParticipant(columnNamesList, participantStatsList, pool))
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
                await asyncio.ensure_future(getMatches(accountIdQueue, matchQueue, accountId2summonerId,
                        visitedSummoners, visitedMatches, params))
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


async def getChampMastery(champMasteryQueue: asyncio.Queue, summonerIdQueue1: asyncio.Queue) -> None:
    while True:
        try:
            summonerId = await summonerIdQueue1.get()
            champMasteryData = await panth.getChampionMasteries(summonerId)
            if champMasteryData:
                for champMastery in champMasteryData:
                    champMasteryQueue.put_nowait(champMastery)
            # else:
            #     visitedSummoners.add(summonerId2summonerName[summonerId])
            # print(f"[INFO] summonerIdQueue: {summonerIdQueue.qsize()}")
        except Exception as e:
            # print(f'[ERROR] getChampMastery coroutine error.')
            print(f'[WARNING] getChampMastery ({summonerId}): {e}')
        finally:
            # print(f'[INFO] champMasteryQueue: {champMasteryQueue.qsize()}')
            summonerIdQueue1.task_done()


async def insertChampMastery(champMasteryQueue: asyncio.Queue, summonerId2summonerName:Dict[str,str], 
                            pool: asyncpg.pool.Pool) -> None:
    while True:
        try:
            champMastery = await champMasteryQueue.get()
            champMastery['summonerName'] = summonerId2summonerName[champMastery['summonerId']]
            champMastery.pop("summonerId", None)
            columnNames = ', '.join([f'"{k}"' for k in champMastery.keys()])
            upsertStatement = ', '.join([f'"{k}" = EXCLUDED."{k}"' for k in champMastery.keys()])
            placeholders = ', '.join([f'${j+1}' for j in range(len(champMastery))])
            insertStatement = (f'INSERT INTO "Champion_Mastery" ({columnNames})\n'
                               f'VALUES ({placeholders})\n'
                               f'ON CONFLICT ("summonerName", "championId")\n' 
                               f'DO UPDATE SET {upsertStatement};')
        
            async with pool.acquire() as connection:
                await connection.execute(insertStatement, *champMastery.values())
            # visitedSummoners.add(champMastery['summonerName'])
            # print(f'[INFO] champMasteryQueue: {champMasteryQueue.qsize()}')
            # print(f'[INFO] Stored champion mastery for: {champMastery["summonerName"]}')
        except Exception as e:
            print(f'[ERROR] insertChampMastery: {e}')
            print(f'[ERROR] {champMastery}')
            print(f'[ERROR] {insertStatement}')
        finally:
            champMasteryQueue.task_done()


async def getRankInfo(rankDataQueue: asyncio.Queue, summonerIdQueue2: asyncio.Queue,
                      summonerId2summonerName: Dict[str, str], visitedSummoners: set) -> None:
    while True:
        try:
            summonerId = await summonerIdQueue2.get()
            rankData = await panth.getLeaguePosition(summonerId)
            if rankData:
                for rank in rankData:
                    rank.pop("miniSeries", None)
                    rankDataQueue.put_nowait(rank)
                print(f'[INFO] Found rank info: {summonerId2summonerName[summonerId]}')
            else:
                visitedSummoners.add(summonerId2summonerName[summonerId])
                print(f'[INFO] No rank info: {summonerId2summonerName[summonerId]}')
        except Exception as e:
            print(f'[WARNING] getRankInfo ({summonerId}): {e}')
        finally:
            # print(f'[INFO] rankDataQueue: {rankDataQueue.qsize()}')
            summonerIdQueue2.task_done()


async def insertRankInfo(rankDataQueue: asyncio.Queue, summonerId2summonerName: Dict[str,str], 
                         visitedSummoners: set, pool: asyncpg.pool.Pool) -> None:
    while True:
        try:
            rankData = await rankDataQueue.get()
            rankData['summonerName'] = summonerId2summonerName[rankData['summonerId']]
            rankData.pop("summonerId", None)
            columnNames = ', '.join([f'"{k}"' for k in rankData.keys()])
            upsertStatement = ', '.join([f'"{k}" = EXCLUDED."{k}"' for k in rankData.keys()])
            placeholders = ', '.join([f'${j+1}' for j in range(len(rankData))])
            insertStatement = (f'INSERT INTO "Rank" ({columnNames})\n'
                               f'VALUES ({placeholders})\n'
                               f'ON CONFLICT ("summonerName", "queueType")' 
                               f'DO UPDATE SET {upsertStatement};')
        
            async with pool.acquire() as connection:
                await connection.execute(insertStatement, *rankData.values())
            visitedSummoners.add(rankData['summonerName'])
            # print(f'[INFO] Stored Rank Info: {rankData["summonerName"]}')
            # print(f'[INFO] rankDataQueue: {rankDataQueue.qsize()}')
        except Exception as e:
            print(f'[ERROR] insertRankInfo: {e}')
            print(f'[ERROR] {rankData}')
        finally:
            rankDataQueue.task_done()
    
def main() -> None:
    params = {k: v for k, v in matchlistParams.items() if v}
    try:
        loop = asyncio.get_event_loop()
        accountIdQueue = asyncio.Queue()
        matchQueue = asyncio.Queue()
        accountId2summonerId = dict()
        summonerId2summonerName = dict()
        visitedMatches = set()
        visitedSummoners = set()
        if os.path.isfile(r'.\MatchWIP\progress4.json') and os.access(r'.\MatchWIP\progress4.json', os.R_OK):
            with open(r'.\MatchWIP\progress4.json') as f:
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
        if matchQueue.empty():
            seedAccountIds = loop.run_until_complete(getSeedAccounts(loop, riotConfig['seedSummonerNames']))
            for accountId, summonerName in seedAccountIds:
                print(f'{summonerName}: {accountId}')
                accountIdQueue.put_nowait(accountId)
                accountId2summonerId[accountId] = summonerName
        loop.run_until_complete(getAllMatches(loop, accountIdQueue, matchQueue, 
                                            accountId2summonerId, summonerId2summonerName, 
                                            visitedSummoners, visitedMatches, params))
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
        with open(r'.\MatchWIP\progress4.json', 'w') as outputFile:
            json.dump(data, outputFile, indent=4)


panth = pantheon.Pantheon(riotConfig['server'], riotConfig['api_key'], errorHandling=True, requestsLoggingFunction=requestsLog, debug=True)
ssl.match_hostname = lambda cert, hostname: True

if __name__ == '__main__':
    main()

