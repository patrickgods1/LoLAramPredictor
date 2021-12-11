from typing import Dict, Tuple, Any
from pantheon import pantheon
import asyncio
import aioconsole
from config import dbConfig, riotConfig
import json
import os
import ssl
from catboost import CatBoostClassifier
import pandas as pd


def requestsLog(url: str, status:str, headers:str) -> None:
    pass
    # print(url)
    # print(status)
    # print(headers)


# async def getWorkingSummonerNames(summonerNameQueue: asyncio.Queue, visitedSummoners: set,
#                                 pool: asyncpg.pool.Pool) -> None:
#     if not riotConfig['revisitSummoners']:
#         async with pool.acquire() as connection:
#             workingSummoners = await connection.fetch('SELECT DISTINCT l."summonerName" \
#                                                     FROM "Participant_Stats" l \
#                                                     WHERE NOT EXISTS (SELECT r."summonerName" \
#                                                                       FROM "Champion_Mastery" r \
#                                                                       WHERE l."summonerName" = r."summonerName") \
#                                                     ORDER BY l."summonerName" ASC')
#     else:
#         async with pool.acquire() as connection:
#             workingSummoners = await connection.fetch('SELECT DISTINCT "summonerName" \
#                                                        FROM "Participant_Stats"\
#                                                        ORDER BY "summonerName" ASC'
#                                                      )

#     for record in workingSummoners:
#         if record[0] not in visitedSummoners:
#             summonerNameQueue.put_nowait(record[0])


async def getUserInput(summonerNameQueue: asyncio.Queue) -> None:
    while True:
        try:
            # user_input = await asyncio.get_event_loop().run_in_executor(None, lambda: input('Enter a summoner name (Type "quit" to exit): '))
            user_input = await aioconsole.ainput('Enter a summoner name (Press Crtl + C to exit): ')
            await summonerNameQueue.put(user_input)
            await asyncio.sleep(10)
            # return input('Enter a summoner name (Type "quit" to exit): ')
            # return user_input
        except Exception as e:
            print(f'[Error] getUserInput ({user_input}): {e}')


async def getSummonerId(summonerNameQueue: asyncio.Queue, summonerIdQueue: asyncio.Queue,
                        summonerId2summonerName: Dict[str,str], loop: asyncio.AbstractEventLoop) -> None:
    while True:
        try:
            summonerName = await summonerNameQueue.get()
            print(f'[INFO] Looking up summonerId for: {summonerName}')
            data = await panth.getSummonerByName(summonerName)
            # print(f'data: {data}')
            summonerIdQueue.put_nowait(data['id'])
            # summonerId2summonerName[data['id']] = summonerName
            # print(f"[INFO] summonerNameQueue: {summonerNameQueue.qsize()}")
        except Exception as e:
            print(f'[WARNING] getSummonerId ({summonerName}): {e}')
        finally:
            # pass
            # if summonerNameQueue.empty():
            #     print(f'[INFO] summonerNameQueue is empty. Looking in database for new summoners.')
            #     await getUserInput(summonerNameQueue)
            summonerNameQueue.task_done()


async def getSpectatorInfo(summonerIdQueue: asyncio.Queue, model: CatBoostClassifier) -> None:
    while True:
        try:
            summonerId = await summonerIdQueue.get()
            spectatorData = await panth.getCurrentGame(summonerId)
            if spectatorData and spectatorData['gameMode'] == 'ARAM':
                targetTeam = ''
                targetName = ''
                paritipantsList = []
                coroList1 = []
                # coroList2 = []
                for i in range(len(spectatorData['participants'])):
                    if spectatorData['participants'][i]['summonerId'] == summonerId:
                        targetTeam = 'Blue' if spectatorData['participants'][i]['teamId'] == 100 else 'Red'
                        targetName = spectatorData['participants'][i]['summonerName']
                    participant = {'teamId': spectatorData['participants'][i]['teamId'],
                                    'summonerName': spectatorData['participants'][i]['summonerName'],
                                    'summonerId': spectatorData['participants'][i]['summonerId'],
                                    'spell1Id': spectatorData['participants'][i]['spell1Id'],
                                    'spell2Id': spectatorData['participants'][i]['spell2Id'],
                                    'championId': spectatorData['participants'][i]['championId'],
                                    'perk_0': spectatorData['participants'][i]['perks']['perkIds'][0],
                                    'perk_1': spectatorData['participants'][i]['perks']['perkIds'][1],
                                    'perk_2': spectatorData['participants'][i]['perks']['perkIds'][2],
                                    'perk_3': spectatorData['participants'][i]['perks']['perkIds'][3],
                                    'perk_4': spectatorData['participants'][i]['perks']['perkIds'][4],
                                    'perk_5': spectatorData['participants'][i]['perks']['perkIds'][5],
                                    'perk_6': spectatorData['participants'][i]['perks']['perkIds'][6],
                                    'perk_7': spectatorData['participants'][i]['perks']['perkIds'][7],
                                    'perk_8': spectatorData['participants'][i]['perks']['perkIds'][8]}
                    # summonerId2summonerName[spectatorData['participants'][i]['summonerId']] = spectatorData['participants'][i]['summonerName']
                    coroList1.append(getChampMastery(participant['summonerId'], participant['championId']))
                    # coroList2.append(getRankInfo(participant['summonerId']))
                    paritipantsList.append(participant)

                champMasteryResults = await asyncio.gather(*coroList1)
                # rankResults = await asyncio.gather(*coroList2)
                for i in range(len(paritipantsList)):
                    paritipantsList[i]['champPts'] = champMasteryResults[i]
                    # (paritipantsList[i]['rank'], paritipantsList[i]['rankWins'], paritipantsList[i]['rankLosses']) = rankResults[i]
                paritipantsList = sorted(paritipantsList, key = lambda i: (i['teamId'], i['championId']))
                gameDict = {}
                avgChampMastery1 = 0
                avgChampMastery2 = 0
                for i in range(len(paritipantsList)):
                    gameDict[f'champ_{i+1}'] = paritipantsList[i]['championId']
                    gameDict[f'champPts_{i+1}'] = paritipantsList[i]['champPts']
                    if i <= 4:
                        avgChampMastery1 += paritipantsList[i]['champPts']
                    else:
                        avgChampMastery2 += paritipantsList[i]['champPts']
                url = 'https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json'
                response = await panth.fetch(url, method='GET')
                currentVersion = json.loads(await response.text())['patches'][-1]['name']
                # print(f'currentVersion: {currentVersion}')
                gameVersionMap = {'Other': 0, '10.1':  1, '10.10':  2, '10.11':  3, '10.12':  4, '10.13':  5, '10.14':  6, '10.15':  7, '10.16':  8, '10.18':  9, '10.19':  10, '10.2':  11, '10.20':  12, '10.21':  13, '10.3':  14, '10.4':  15, '10.5':  16, '10.6':  17, '10.7':  18, '10.8':  19, '10.9':  20, '8.16':  21, '8.17':  22, '8.18':  23, '8.19':  24, '8.20':  25, '8.21':  26, '8.22':  27, '8.23':  28, '8.24':  29, '9.1':  30, '9.10':  31, '9.11':  32, '9.12':  33, '9.13':  34, '9.14':  35, '9.15':  36, '9.16':  37, '9.17':  38, '9.18':  39, '9.19':  40, '9.2':  41, '9.20':  42, '9.21':  43, '9.22':  44, '9.23':  45, '9.24':  46, '9.3':  47, '9.4':  48, '9.5':  49, '9.6':  50, '9.7':  51, '9.8':  52, '9.9':  53}
                if currentVersion in gameVersionMap.keys():
                    gameDict['gameVersion'] = gameVersionMap[currentVersion]
                else:
                    gameDict['gameVersion'] = gameVersionMap['Other']
                gameDict['avgChampMastery1'] = avgChampMastery1 / (len(paritipantsList)/2)
                gameDict['avgChampMastery2'] = avgChampMastery2 / (len(paritipantsList)/2)
                # print(f'{targetName} on {targetTeam} team:')
                # print(gameDict)

                # for p in paritipantsList:
                #     print(f"summonerName: {p['summonerName']}")
                #     print(f"teamId: {p['teamId']}")
                #     print(f"championId: {p['championId']}")
                #     print(f"champPts: {p['champPts']}")
                #     # print(f"rank: {p['rank']}")
                #     # print(f"rankWins: {p['rankWins']}")
                #     # print(f"rankLosses: {p['rankLosses']}")
                #     print('~'*25)
                # gameId = spectatorData['gameId']
                # summonerName = summonerId2summonerName[summonerId]

            else:
                print(f'[Warning] getSpectatorInfo ({summonerId}): No ARAM game found.')
        except Exception as e:
            print(f'[WARNING] getSpectatorInfo ({summonerId}): {e}')
        finally:
            # if summonerNameQueue.empty():
            #     print(f'[INFO] summonerNameQueue is empty. Looking in database for new summoners.')
            #     await getUserInput(summonerNameQueue)
            # res = await asyncio.gather(predictGame(model, targetName, targetTeam, gameDict))
            await predictGame(model, targetName, targetTeam, gameDict)
            summonerIdQueue.task_done()


async def getChampMastery(summonerId, championId) -> None:
    try:
        champMasteryData = await panth.getChampionMasteriesByChampionId(summonerId, championId)
        if champMasteryData:
            champPts = champMasteryData['championPoints']
        else:
            champPts = 0
            print(f"[Warning] getChampMastery ({summonerId}, {championId}): None found.")
        # print(f"[INFO] summonerIdQueue: {summonerIdQueue.qsize()}")
    except Exception as e:
        print(f"[Warning] getChampMastery ({summonerId}, {championId}): {e}")
        champPts = 0
    finally:
        return champPts


async def getRankInfo(summonerId) -> None:
    try:
        rankData = await panth.getLeaguePosition(summonerId)
        rank = ''
        rankWins = -9999999
        rankLosses = -9999999
        rankMap = {0: 'UNRANKED',
                    1: 'IRON IV',
                    2: 'IRON III',
                    3: 'IRON II',
                    4: 'IRON I',
                    5: 'BRONZE IV',
                    6: 'BRONZE III',
                    7: 'BRONZE II',
                    8: 'BRONZE I',
                    9: 'SILVER IV',
                    10: 'SILVER III',
                    11: 'SILVER II',
                    12: 'SILVER I',
                    13: 'GOLD IV',
                    14: 'GOLD III',
                    15: 'GOLD II',
                    16: 'GOLD I',
                    17: 'PLATINUM IV',
                    18: 'PLATINUM III',
                    19: 'PLATINUM II',
                    20: 'PLATINUM I',
                    21: 'DIAMOND IV',
                    22: 'DIAMOND III',
                    23: 'DIAMOND II',
                    24: 'DIAMOND I',
                    25: 'MASTER I',
                    26: 'GRANDMASTER I',
                    27: 'CHALLENGER I'}
        if rankData:
            for r in rankData:
                if r['queueType'] == 'RANKED_SOLO_5x5':
                    rank = f"{r['tier']} {r['rank']}"
                    rankWins = r['wins']
                    rankLosses = r['losses']
            if not rank:
                rank = 'UNRANKED'
                rankWins = -9999999
                rankLosses = -9999999
        else:
            # print(f'[INFO] No rank info: {summonerId}')
            rank = 'UNRANKED'
            rankWins = -9999999
            rankLosses = -9999999
    except Exception as e:
        print(f'[WARNING] getRankInfo ({summonerId}): {e}')
        rank = 'UNRANKED'
        rankWins = -9999999
        rankLosses = -9999999
    finally:
        return rank, rankWins, rankLosses


async def loadModel(model_name: str) -> CatBoostClassifier:
    model = CatBoostClassifier()
    model.load_model(model_name)
    return model


async def predictGame(model, targetName, targetTeam, gameData) -> None:
    X = pd.DataFrame([gameData], columns=['champ_1', 'champ_2', 'champ_3', 'champ_4', 'champ_5', 'champ_6',
       'champ_7', 'champ_8', 'champ_9', 'champ_10', 'champPts_1', 'champPts_2',
       'champPts_3', 'champPts_4', 'champPts_5', 'champPts_6', 'champPts_7',
       'champPts_8', 'champPts_9', 'champPts_10', 'gameVersion',
       'avgChampMastery1', 'avgChampMastery2'])
    prob = model.predict_proba(X)
    # print(prob)
    if targetTeam == 'Blue':
        print(f"[Blue] {targetName}'s team has {prob[0,1]*100:0.2f}% chance of winning.")
        print(f"[Red] Enemy team has {prob[0,0]*100:0.2f}% chance of winning.")
    else:
        print(f"[Red] {targetName}'s team has {prob[0,0]*100:0.2f}% chance of winning.")
        print(f"[Blue] Enemy team has {prob[0,1]*100:0.2f}% chance of winning.")
    print('~'*50)

async def getLiveGames(loop: asyncio.AbstractEventLoop, summonerNameQueue: asyncio.Queue) -> None:
    try:
        # champMasteryQueue = asyncio.Queue()
        summonerIdQueue = asyncio.Queue()
        # rankQueue = asyncio.Queue()
        summonerId2summonerName = dict()
        model = await loadModel('OptimizeBrierMin01913212391')
        # print(model.get_all_params())
        # producers = loop.create_task(getUserInput(summonerNameQueue))
        producers = getUserInput(summonerNameQueue)
        consumers1 = asyncio.ensure_future(getSummonerId(summonerNameQueue, summonerIdQueue, summonerId2summonerName, loop))
        consumers2 = asyncio.ensure_future(getSpectatorInfo(summonerIdQueue, model))
        # consumers3 = asyncio.ensure_future(predictGame(model, rankQueue))
        # consumers4 = asyncio.ensure_future(getRank(rankQueue))
        await asyncio.gather(producers, return_exceptions=True)
        await summonerNameQueue.join()
        consumers1.cancel()
        consumers2.cancel()
        # consumers3.cancel()
        # for p in producers:
        #     p.cancel()
        # for c in consumers1:
        #     c.cancel()
        # for c in consumers2:
        #     c.cancel()
    except Exception as e:
        # await pool.close()
        print(e)


def main() -> None:
    try:
        loop = asyncio.get_event_loop()
        summonerNameQueue = asyncio.Queue()
        # visitedSummoners = set()
        # if not riotConfig['revisitSummoners'] and os.path.isfile('.\ChampMasteryWIP\progress.json') and os.access('.\ChampMasteryWIP\progress.json', os.R_OK):
        #     with open('.\ChampMasteryWIP\progress.json') as f:
        #         data = json.load(f)
        #     visitedSummoners.update(data['visitedSummoners'])
        loop.run_until_complete(getLiveGames(loop, summonerNameQueue))
    except KeyboardInterrupt:
        print('Exiting.....')
    except Exception as e:
        print(f'[ERROR] Main: {e}')
    finally:
        # print(f'summonerIdQueue:\n{summonerIdQueue}')
        for task in asyncio.Task.all_tasks():
            task.cancel()
        # summonerNameList = {summonerNameQueue.get_nowait() for _ in range(summonerNameQueue.qsize())}
        # print('-'*80)
        # print(f'Visited {len(visitedSummoners)} summoners')
        # # print(f'{visitedSummoners}')
        # # print('-'*80)
        # # print(f'summonerIdQueue({len(summonerNameList)})')
        # # print(f'{summonerIdList}')
        # print('-'*80)
        # data = {
        #         'numVisitedSummoners': len(visitedSummoners),
        #         'visitedSummoners': sorted(list(visitedSummoners))
        #         }
        # if not os.path.exists('ChampMasteryWIP'):
        #     os.mkdir('ChampMasteryWIP')
        # with open('.\ChampMasteryWIP\progress.json', 'w') as outputFile:
        #     json.dump(data, outputFile, indent=4)

ssl.match_hostname = lambda cert, hostname: True
panth = pantheon.Pantheon(riotConfig['server'], riotConfig['api_key'], errorHandling=True, requestsLoggingFunction=requestsLog, debug=True)

if __name__ == '__main__':
    main()