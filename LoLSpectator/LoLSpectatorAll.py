from typing import Dict, Tuple, Any
from pantheon import pantheon
import asyncio
import aioconsole
from config import riotConfig
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


async def getSpectatorInfo(champions: pd.DataFrame, model: CatBoostClassifier, summonerIdQueue: asyncio.Queue, ) -> None:
    while True:
        try:
            summonerId = await summonerIdQueue.get()
            spectatorData = await panth.getCurrentGame(summonerId)
            if spectatorData and spectatorData['gameMode'] == 'ARAM':
                targetTeam = ''
                targetName = ''
                paritipantsList = []
                coroList1 = []
                coroList2 = []
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
                                    'perk0': spectatorData['participants'][i]['perks']['perkIds'][0],
                                    'perk1': spectatorData['participants'][i]['perks']['perkIds'][1],
                                    'perk2': spectatorData['participants'][i]['perks']['perkIds'][2],
                                    'perk3': spectatorData['participants'][i]['perks']['perkIds'][3],
                                    'perk4': spectatorData['participants'][i]['perks']['perkIds'][4],
                                    'perk5': spectatorData['participants'][i]['perks']['perkIds'][5],
                                    'perk6': spectatorData['participants'][i]['perks']['perkIds'][6],
                                    'perk7': spectatorData['participants'][i]['perks']['perkIds'][7],
                                    'perk8': spectatorData['participants'][i]['perks']['perkIds'][8]}
                    # summonerId2summonerName[spectatorData['participants'][i]['summonerId']] = spectatorData['participants'][i]['summonerName']
                    coroList1.append(getChampMastery(participant['summonerId'], participant['championId']))
                    coroList2.append(getRankInfo(participant['summonerId']))
                    paritipantsList.append(participant)

                champMasteryResults = await asyncio.gather(*coroList1)
                rankResults = await asyncio.gather(*coroList2)

                # avgChampMastery1 = 0
                # avgChampMastery2 = 0
                # avgRank1 = 0
                # avgRank2 = 0
                gameDict = {}
                gameDict['avgChampMastery1'] = 0
                gameDict['avgChampMastery2'] = 0
                gameDict['avgRank1'] = 0
                gameDict['avgRank2'] = 0
                count1 = 0
                count2 = 0
                rankMap = {'UNRANKED': 0,
                    'IRON IV': 1,
                    'IRON III': 2,
                    'IRON II': 3,
                    'IRON I': 4,
                    'BRONZE IV': 5,
                    'BRONZE III': 6,
                    'BRONZE II': 7,
                    'BRONZE I': 8,
                    'SILVER IV': 9,
                    'SILVER III': 10,
                    'SILVER II': 11,
                    'SILVER I': 12,
                    'GOLD IV': 13,
                    'GOLD III': 14,
                    'GOLD II': 15,
                    'GOLD I': 16,
                    'PLATINUM IV': 17,
                    'PLATINUM III': 18,
                    'PLATINUM II': 19,
                    'PLATINUM I': 20,
                    'DIAMOND IV': 21,
                    'DIAMOND III': 22,
                    'DIAMOND II': 23,
                    'DIAMOND I': 24,
                    'MASTER I': 25,
                    'GRANDMASTER I': 26,
                    'CHALLENGER I': 27}
                for i in range(len(paritipantsList)):
                    paritipantsList[i]['champPts'] = champMasteryResults[i]
                    (paritipantsList[i]['rank'], paritipantsList[i]['rankWins'], paritipantsList[i]['rankLosses']) = rankResults[i]
                    if i < 5:
                        if rankResults[i][0] != 'UNRANKED':
                            gameDict['avgRank1'] += rankMap[rankResults[i][0]]
                            count1 += 1
                        gameDict['avgChampMastery1'] += champMasteryResults[i]/(len(paritipantsList)/2)
                    else:
                        if rankResults[i][0] != 'UNRANKED':
                            gameDict['avgRank2'] += rankMap[rankResults[i][0]]
                            count2 += 1
                        gameDict['avgChampMastery2'] += champMasteryResults[i]/(len(paritipantsList)/2)
                        

                paritipantsList = sorted(paritipantsList, key = lambda i: (i['teamId'], i['championId']))
                # champIdMap = {'Other': 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 
                #                 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 
                #                 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 
                #                 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31, 32: 32, 33: 33, 
                #                 34: 34, 35: 35, 36: 36, 37: 37, 38: 38, 39: 39, 40: 40, 41: 41, 
                #                 42: 42, 43: 43, 44: 44, 45: 45, 48: 46, 50: 47, 51: 48, 53: 49, 
                #                 54: 50, 55: 51, 56: 52, 57: 53, 58: 54, 59: 55, 60: 56, 61: 57, 
                #                 62: 58, 63: 59, 64: 60, 67: 61, 68: 62, 69: 63, 72: 64, 74: 65, 
                #                 75: 66, 76: 67, 77: 68, 78: 69, 79: 70, 80: 71, 81: 72, 82: 73, 
                #                 83: 74, 84: 75, 85: 76, 86: 77, 89: 78, 90: 79, 91: 80, 92: 81, 
                #                 96: 82, 98: 83, 99: 84, 101: 85, 102: 86, 103: 87, 104: 88, 
                #                 105: 89, 106: 90, 107: 91, 110: 92, 111: 93, 112: 94, 113: 95, 
                #                 114: 96, 115: 97, 117: 98, 119: 99, 120: 100, 121: 101, 122: 102, 
                #                 126: 103, 127: 104, 131: 105, 133: 106, 134: 107, 136: 108, 
                #                 141: 109, 142: 110, 143: 111, 145: 112, 147: 113, 150: 114, 
                #                 154: 115, 157: 116, 161: 117, 163: 118, 164: 119, 201: 120, 
                #                 202: 121, 203: 122, 222: 123, 223: 124, 235: 125, 236: 126, 
                #                 238: 127, 240: 128, 245: 129, 246: 130, 254: 131, 266: 132, 
                #                 267: 133, 268: 134, 350: 135, 360: 136, 412: 137, 420: 138, 
                #                 421: 139, 427: 140, 429: 141, 432: 142, 497: 143, 498: 144, 
                #                 516: 145, 517: 146, 518: 147, 523: 148, 555: 149, 777: 150, 
                #                 875: 151, 876: 152}
                champClassMap = {'None': 0, 'Assassin': 1, 'Fighter': 2, 'Mage': 3, 'Marksman': 4, 
                                    'Support': 5, 'Tank': 6}
                perksMap = {'Other': 0, 8005: 1, 8008: 2, 8009: 3, 8010: 4, 8014: 5, 8017: 6, 
                            8021: 7, 8105: 8, 8106: 9, 8112: 10, 8120: 11, 8124: 12, 8126: 13, 
                            8128: 14, 8134: 15, 8135: 16, 8136: 17, 8138: 18, 8139: 19, 8143: 20, 
                            8210: 21, 8214: 22, 8224: 23, 8226: 24, 8229: 25, 8230: 26, 8232: 27, 
                            8233: 28, 8234: 29, 8236: 30, 8237: 31, 8242: 32, 8275: 33, 8299: 34, 
                            8304: 35, 8306: 36, 8313: 37, 8316: 38, 8321: 39, 8345: 40, 8347: 41, 
                            8351: 42, 8352: 43, 8358: 44, 8360: 45, 8401: 46, 8410: 47, 8429: 48, 
                            8437: 49, 8439: 50, 8444: 51, 8446: 52, 8451: 53, 8453: 54, 8463: 55, 
                            8465: 56, 8473: 57, 9101: 58, 9103: 59, 9104: 60, 9105: 61, 9111: 62, 
                            9923: 63}
                spellIdMap = {'Other': 0, 1: 1, 3: 2, 4: 3, 6: 4, 7: 5, 11: 6, 12: 7, 
                                13: 8, 14: 9, 21: 10, 30: 11, 31: 12, 32: 13, 39: 14}
                for i in range(len(paritipantsList)):
                    # gameDict[f'champ_{i+1}'] = champIdMap[paritipantsList[i]['championId']]
                    gameDict[f'summonerName_{i+1}'] = paritipantsList[i]['summonerName']
                    gameDict[f'champName_{i+1}'] = champions.loc[paritipantsList[i]['championId'], 'name']
                    gameDict[f'champ_{i+1}'] = paritipantsList[i]['championId']
                    gameDict[f'champPts_{i+1}'] = paritipantsList[i]['champPts']
                    gameDict[f'rank_{i+1}'] = paritipantsList[i]['rank']
                    gameDict[f'rankWins_{i+1}'] = paritipantsList[i]['rankWins']
                    gameDict[f'rankLosses_{i+1}'] = paritipantsList[i]['rankLosses']
                    gameDict[f'rankWinRatio_{i+1}'] = paritipantsList[i]['rankWins'] / (paritipantsList[i]['rankWins'] + paritipantsList[i]['rankLosses'])
                    gameDict[f'spell1Id_{i+1}'] = paritipantsList[i]['spell1Id']
                    gameDict[f'spell2Id_{i+1}'] = paritipantsList[i]['spell2Id']
                    gameDict[f'perk0_{i+1}'] = paritipantsList[i]['perk0']
                    gameDict[f'perk1_{i+1}'] = paritipantsList[i]['perk1']
                    gameDict[f'perk2_{i+1}'] = paritipantsList[i]['perk2']
                    gameDict[f'perk3_{i+1}'] = paritipantsList[i]['perk3']
                    gameDict[f'perk4_{i+1}'] = paritipantsList[i]['perk4']
                    gameDict[f'perk5_{i+1}'] = paritipantsList[i]['perk5']
                    gameDict[f'champPts_rank_{i+1}'] = paritipantsList[i]['champPts'] * rankMap[paritipantsList[i]['rank']]
                    gameDict[f'primaryClass_{i+1}'] = champions.loc[paritipantsList[i]['championId'], 'primaryClass']
                    gameDict[f'secondaryClass_{i+1}'] = champions.loc[paritipantsList[i]['championId'], 'secondaryClass']
                    # gameDict[f'spell1Id_{i+1}'] = spellIdMap[paritipantsList[i]['spell1Id']]
                    # gameDict[f'spell2Id_{i+1}'] = spellIdMap[paritipantsList[i]['spell2Id']]
                    # gameDict[f'perk0_{i+1}'] = perksMap[paritipantsList[i]['perk0']]
                    # gameDict[f'perk1_{i+1}'] = perksMap[paritipantsList[i]['perk1']]
                    # gameDict[f'perk2_{i+1}'] = perksMap[paritipantsList[i]['perk2']]
                    # gameDict[f'perk3_{i+1}'] = perksMap[paritipantsList[i]['perk3']]
                    # gameDict[f'perk4_{i+1}'] = perksMap[paritipantsList[i]['perk4']]
                    # gameDict[f'perk5_{i+1}'] = perksMap[paritipantsList[i]['perk5']]
                    # gameDict[f'champPts_rank_{i+1}'] = paritipantsList[i]['champPts'] * paritipantsList[i]['rank']
                    # gameDict[f'primaryClass_{i+1}'] = champClassMap[champions.loc[paritipantsList[i]['championId'], 'primaryClass']]
                    # gameDict[f'secondaryClass_{i+1}'] = champClassMap[champions.loc[paritipantsList[i]['championId'], 'secondaryClass']]

                # url = 'https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json'
                # response = await panth.fetch(url, method='GET')
                # currentVersion = json.loads(await response.text())['patches'][-1]['name']
                
                url = 'https://ddragon.leagueoflegends.com/realms/na.json'
                response = await panth.fetch(url, method='GET')
                currentVersion = '.'.join(json.loads(await response.text())['v'].split('.')[:2])
                # print(f'currentVersion: {currentVersion}')
                gameVersionMap = {'Other': 0, '10.1':  1, '10.10':  2, '10.11':  3, '10.12':  4, 
                                    '10.13':  5, '10.14':  6, '10.15':  7, '10.16':  8, 
                                    '10.18':  9, '10.19':  10, '10.2':  11, '10.20':  12, 
                                    '10.21':  13, '10.3':  14, '10.4':  15, '10.5':  16, 
                                    '10.6':  17, '10.7':  18, '10.8':  19, '10.9':  20, 
                                    '8.16':  21, '8.17':  22, '8.18':  23, '8.19':  24, 
                                    '8.20':  25, '8.21':  26, '8.22':  27, '8.23':  28, 
                                    '8.24':  29, '9.1':  30, '9.10':  31, '9.11':  32, 
                                    '9.12':  33, '9.13':  34, '9.14':  35, '9.15':  36, 
                                    '9.16':  37, '9.17':  38, '9.18':  39, '9.19':  40, 
                                    '9.2':  41, '9.20':  42, '9.21':  43, '9.22':  44, 
                                    '9.23':  45, '9.24':  46, '9.3':  47, '9.4':  48, 
                                    '9.5':  49, '9.6':  50, '9.7':  51, '9.8':  52, '9.9':  53}
                # if currentVersion in gameVersionMap.keys():
                #     # gameDict['gameVersion'] = gameVersionMap[currentVersion]
                #     gameDict['gameVersion'] = currentVersion
                # else:
                #     # gameDict['gameVersion'] = gameVersionMap['Other']
                #     gameDict['gameVersion'] = 'Other'
                gameDict['gameVersion'] = currentVersion
                reverseRankMap = dict((v,k) for k, v in rankMap.items())
                if count1:
                    gameDict['avgRank1'] = reverseRankMap[gameDict['avgRank1'] // count1]
                else:
                    gameDict['avgRank1'] = 'UNRANKED'
                if count2:
                    gameDict['avgRank2'] = reverseRankMap[gameDict['avgRank2'] // count2]
                else:
                    gameDict['avgRank2'] = 'UNRANKED'
                # print(f'{targetName} on {targetTeam} team:')
                # print(gameDict)
                res = await asyncio.gather(predictGame(model, targetName, targetTeam, gameDict))
            else:
                print(f'[Warning] getSpectatorInfo ({summonerId}): No ARAM game found.')
            
        except Exception as e:
            print(f'[Warning] getSpectatorInfo ({summonerId}): No ARAM game found. {e}')
            # print(f'[WARNING] getSpectatorInfo ({summonerId}): {e}')
        finally:
            # if summonerNameQueue.empty():
            #     print(f'[INFO] summonerNameQueue is empty. Looking in database for new summoners.')
            #     await getUserInput(summonerNameQueue)
            summonerIdQueue.task_done()
            # await predictGame(model, targetName, targetTeam, gameDict)
            


async def getChampMastery(summonerId, championId) -> None:
    try:
        champMasteryData = await panth.getChampionMasteriesByChampionId(summonerId, championId)
        if champMasteryData:
            champPts = champMasteryData['championPoints']
        else:
            champPts = 0
            print(f"[Warning] getChampMastery ({summonerId}, {championId}): None found.")
        # print(f"[INFO] summonerIdQueue: {summonerIdQueue.qsize()}")
    except Exception:
    # except Exception as e:
        # print(f"[Warning] getChampMastery ({summonerId}, {championId}): {e}")
        champPts = 0
    finally:
        return champPts


async def getRankInfo(summonerId) -> None:
    try:
        rankData = await panth.getLeaguePosition(summonerId)
        rank = ''
        rankWins = -9999999
        rankLosses = -9999999
        rankMap = {'UNRANKED': 0,
                    'IRON IV': 1,
                    'IRON III': 2,
                    'IRON II': 3,
                    'IRON I': 4,
                    'BRONZE IV': 5,
                    'BRONZE III': 6,
                    'BRONZE II': 7,
                    'BRONZE I': 8,
                    'SILVER IV': 9,
                    'SILVER III': 10,
                    'SILVER II': 11,
                    'SILVER I': 12,
                    'GOLD IV': 13,
                    'GOLD III': 14,
                    'GOLD II': 15,
                    'GOLD I': 16,
                    'PLATINUM IV': 17,
                    'PLATINUM III': 18,
                    'PLATINUM II': 19,
                    'PLATINUM I': 20,
                    'DIAMOND IV': 21,
                    'DIAMOND III': 22,
                    'DIAMOND II': 23,
                    'DIAMOND I': 24,
                    'MASTER I': 25,
                    'GRANDMASTER I': 26,
                    'CHALLENGER I': 27}
        if rankData:
            for r in rankData:
                if r['queueType'] == 'RANKED_SOLO_5x5':
                    # rank = rankMap[f"{r['tier']} {r['rank']}"]
                    rank = f"{r['tier']} {r['rank']}"
                    rankWins = r['wins']
                    rankLosses = r['losses']
            if not rank:
                # rank = rankMap['UNRANKED']
                rank = 'UNRANKED'
                rankWins = -9999999
                rankLosses = -9999999
        else:
            # print(f'[INFO] No rank info: {summonerId}')
            # rank = rankMap['UNRANKED']
            rank = 'UNRANKED'
            rankWins = -9999999
            rankLosses = -9999999
    except Exception:
    # except Exception as e:
        # print(f'[WARNING] getRankInfo ({summonerId}): {e}')
        # rank = rankMap['UNRANKED']
        rank = 'UNRANKED'
        rankWins = -9999999
        rankLosses = -9999999
    finally:
        return rank, rankWins, rankLosses


async def loadModel(model_name: str) -> CatBoostClassifier:
    model = CatBoostClassifier()
    model.load_model(model_name)
    return model

async def loadChampions() -> pd.DataFrame:
    versionResponse = await panth.fetch('https://ddragon.leagueoflegends.com/api/versions.json', method='GET')
    latestVersion = json.loads(await versionResponse.text())[0]
    championsResponse = await panth.fetch(f'http://ddragon.leagueoflegends.com/cdn/{latestVersion}/data/en_US/champion.json', method='GET')
    championData = json.loads(await championsResponse.text())

    champions = pd.DataFrame(columns = ['championId', 'name', 'attack', 'defense', 'magic', 'difficulty', 'primaryClass', 'secondaryClass', 'partype', 'hp', 'hpperlevel', 'mp', 'mpperlevel', 'movespeed', 'armor', 'armorperlevel', 'spellblock', 'spellblockperlevel', 'attackrange', 'hpregen', 'hpregenperlevel', 'mpregen', 'mpregenperlevel', 'crit', 'critperlevel', 'attackdamage', 'attackdamageperlevel', 'attackspeedperlevel', 'attackspeed'])

    for k, v in championData['data'].items():
        champions = champions.append({'championId': int(v['key']),
                            'name': v['name'], 
                            'attack': v['info']['attack'], 
                            'defense': v['info']['defense'], 
                            'magic': v['info']['magic'], 
                            'difficulty': v['info']['difficulty'], 
                            'primaryClass': v['tags'][0], 
                            'secondaryClass': v['tags'][1] if len(v['tags']) > 1 else 'None', 
                            'partype': v['partype'], 
                            'hp': v['stats']['hp'], 
                            'hpperlevel': v['stats']['hpperlevel'], 
                            'mp': v['stats']['mp'], 
                            'mpperlevel': v['stats']['mpperlevel'], 
                            'movespeed': v['stats']['movespeed'], 
                            'armor': v['stats']['armor'], 
                            'armorperlevel': v['stats']['armorperlevel'], 
                            'spellblock': v['stats']['spellblock'], 
                            'spellblockperlevel': v['stats']['spellblockperlevel'], 
                            'attackrange': v['stats']['attackrange'], 
                            'hpregen': v['stats']['hpregen'], 
                            'hpregenperlevel': v['stats']['hpregenperlevel'], 
                            'mpregen': v['stats']['mpregen'], 
                            'mpregenperlevel': v['stats']['mpregenperlevel'], 
                            'crit': v['stats']['crit'], 
                            'critperlevel': v['stats']['critperlevel'], 
                            'attackdamage': v['stats']['attackdamage'], 
                            'attackdamageperlevel': v['stats']['attackdamageperlevel'], 
                            'attackspeedperlevel': v['stats']['attackspeedperlevel'], 
                            'attackspeed': v['stats']['attackspeed']}, ignore_index=True)

    champions.set_index('championId', inplace=True)
    # print(champions.head())
    return champions


async def predictGame(model, targetName, targetTeam, gameData) -> None:
    columns = ['summonerName_1', 'summonerName_2', 'summonerName_3', 'summonerName_4', 
        'summonerName_5', 'summonerName_6', 'summonerName_7', 'summonerName_8', 'summonerName_9', 
        'summonerName_10', 'champName_1', 'champName_2', 'champName_3', 'champName_4', 
        'champName_5', 'champName_6', 'champName_7', 'champName_8', 'champName_9', 
        'champName_10', 'champ_1', 'champ_2', 'champ_3', 'champ_4', 'champ_5', 'champ_6', 
        'champ_7', 'champ_8', 'champ_9', 'champ_10', 'rank_1', 'rank_2', 'rank_3', 'rank_4', 
        'rank_5', 'rank_6', 'rank_7', 'rank_8', 'rank_9', 'rank_10', 'rankWins_1', 'rankWins_2', 
        'rankWins_3', 'rankWins_4', 'rankWins_5', 'rankWins_6', 'rankWins_7', 'rankWins_8', 
        'rankWins_9', 'rankWins_10', 'rankLosses_1', 'rankLosses_2', 'rankLosses_3', 
        'rankLosses_4', 'rankLosses_5', 'rankLosses_6', 'rankLosses_7', 'rankLosses_8', 
        'rankLosses_9', 'rankLosses_10', 'champPts_1', 'champPts_2', 'champPts_3', 'champPts_4', 
        'champPts_5', 'champPts_6', 'champPts_7', 'champPts_8', 'champPts_9', 'champPts_10', 
        'spell1Id_1', 'spell1Id_2', 'spell1Id_3', 'spell1Id_4', 'spell1Id_5', 'spell1Id_6', 
        'spell1Id_7', 'spell1Id_8', 'spell1Id_9', 'spell1Id_10', 'spell2Id_1', 'spell2Id_2', 
        'spell2Id_3', 'spell2Id_4', 'spell2Id_5', 'spell2Id_6', 'spell2Id_7', 'spell2Id_8', 
        'spell2Id_9', 'spell2Id_10', 'perk0_1', 'perk0_2', 'perk0_3', 'perk0_4', 'perk0_5', 
        'perk0_6', 'perk0_7', 'perk0_8', 'perk0_9', 'perk0_10', 'perk1_1', 'perk1_2', 'perk1_3', 
        'perk1_4', 'perk1_5', 'perk1_6', 'perk1_7', 'perk1_8', 'perk1_9', 'perk1_10', 'perk2_1', 
        'perk2_2', 'perk2_3', 'perk2_4', 'perk2_5', 'perk2_6', 'perk2_7', 'perk2_8', 'perk2_9', 
        'perk2_10', 'perk3_1', 'perk3_2', 'perk3_3', 'perk3_4', 'perk3_5', 'perk3_6', 'perk3_7', 
        'perk3_8', 'perk3_9', 'perk3_10', 'perk4_1', 'perk4_2', 'perk4_3', 'perk4_4', 'perk4_5', 
        'perk4_6', 'perk4_7', 'perk4_8', 'perk4_9', 'perk4_10', 'perk5_1', 'perk5_2', 'perk5_3', 
        'perk5_4', 'perk5_5', 'perk5_6', 'perk5_7', 'perk5_8', 'perk5_9', 'perk5_10', 
        'gameVersion', 'primaryClass_1', 'secondaryClass_1', 'primaryClass_2', 'secondaryClass_2', 
        'primaryClass_3', 'secondaryClass_3', 'primaryClass_4', 'secondaryClass_4', 
        'primaryClass_5', 'secondaryClass_5', 'primaryClass_6', 'secondaryClass_6', 
        'primaryClass_7', 'secondaryClass_7', 'primaryClass_8', 'secondaryClass_8', 
        'primaryClass_9', 'secondaryClass_9', 'primaryClass_10', 'secondaryClass_10', 
        'rankWinRatio_1', 'rankWinRatio_2', 'rankWinRatio_3', 'rankWinRatio_4', 'rankWinRatio_5', 
        'rankWinRatio_6', 'rankWinRatio_7', 'rankWinRatio_8', 'rankWinRatio_9', 'rankWinRatio_10', 
        'avgRank1', 'avgRank2', 'avgRankWR1', 'avgRankWR2', 'avgChampMastery1', 'avgChampMastery2', 
        'champPts_rank_1', 'champPts_rank_2', 'champPts_rank_3', 'champPts_rank_4', 'champPts_rank_5', 
        'champPts_rank_6', 'champPts_rank_7', 'champPts_rank_8', 'champPts_rank_9', 'champPts_rank_10'] 
    X = pd.DataFrame([gameData], columns=columns)
    # dropList = ['summonerName_1', 'summonerName_2', 'summonerName_3', 'summonerName_4', 
    #     'summonerName_5', 'summonerName_6', 'summonerName_7', 'summonerName_8', 'summonerName_9', 
    #     'summonerName_10', 'champName_1', 'champName_2', 'champName_3', 'champName_4', 
    #     'champName_5', 'champName_6', 'champName_7', 'champName_8', 'champName_9', 
    #     'champName_10', 'rankWinRatio_1', 'rankWinRatio_2', 'rankWinRatio_3', 
    #     'rankWinRatio_4', 'rankWinRatio_5', 'rankWinRatio_6', 'rankWinRatio_7', 'rankWinRatio_8', 
    #     'rankWinRatio_9', 'rankWinRatio_10']
    dropList = ['summonerName_1', 'summonerName_2', 'summonerName_3', 'summonerName_4', 
        'summonerName_5', 'summonerName_6', 'summonerName_7', 'summonerName_8', 'summonerName_9', 
        'summonerName_10', 'champName_1', 'champName_2', 'champName_3', 'champName_4', 
        'champName_5', 'champName_6', 'champName_7', 'champName_8', 'champName_9', 
        'champName_10']

    prob = model.predict_proba(X.drop(dropList, axis=1))
    # # print(prob)

    titles = ['summonerName', 'champName', 'rank', 'rankWins', 'rankLosses', 'rankWinRatio', 'champPts', 'primaryClass', 'secondaryClass']
    format_title = "{:<16}|{:<14}|{:<13}|{:<8}|{:<10}|{:<12}|{:<8}|{:<12}|{:<10}"
    format_string = "{:<16}|{:<14}|{:<13}|{:>8d}|{:>10d}|{:>12.5f}|{:>8d}|{:<12}|{:<10}"
    print('=' * 115)
    print('[Blue Team - {:0.2f}%] Average Rank: {:<13} | Average Champion Mastery: {:<10.2f} |'.format(prob[0,1]*100, X['avgRank1'].values[0], X['avgChampMastery1'].values[0]))
    print('-' * 89)
    print(format_title.format(*titles))
    print('-' * 115)
    for i in range(1, 6):
        print(format_string.format(*[X[f'{c}_{i}'].values[0] for c in titles]))
    print('=' * 115)
    print('[Red Team - {:0.2f}%] Average Rank: {:<13} | Average Champion Mastery: {:<10.2f} |'.format(prob[0,0]*100, X['avgRank2'].values[0], X['avgChampMastery2'].values[0]))
    print('-' * 87)
    print(format_title.format(*titles))
    print('-' * 115)
    for i in range(6, 11):
        print(format_string.format(*[X[f'{c}_{i}'].values[0] for c in titles]))
    print('=' * 115)
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
        model = await loadModel('OptimizeBrierMaxCat01716961192')
        champions = await loadChampions()
        # print(model.get_all_params())
        # producers = loop.create_task(getUserInput(summonerNameQueue))
        producers = getUserInput(summonerNameQueue)
        consumers1 = asyncio.ensure_future(getSummonerId(summonerNameQueue, summonerIdQueue, summonerId2summonerName, loop))
        consumers2 = asyncio.ensure_future(getSpectatorInfo(champions, model, summonerIdQueue))
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