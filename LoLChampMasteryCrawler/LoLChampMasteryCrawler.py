from typing import Dict, Tuple, Any
from pantheon import pantheon
import asyncio
import asyncpg
from config import dbConfig, riotConfig
import json
import os


def requestsLog(url: str, status:str, headers:str) -> None:
    pass
    # print(url)
    # print(status)
    # print(headers)


async def getWorkingSummonerNames(summonerNameQueue: asyncio.Queue, visitedSummoners: set,
                                pool: asyncpg.pool.Pool) -> None:
    if not riotConfig['revisitSummoners']:
        async with pool.acquire() as connection:
            workingSummoners = await connection.fetch('SELECT DISTINCT l."summonerName" \
                                                    FROM "Participant_Stats" l \
                                                    WHERE NOT EXISTS (SELECT r."summonerName" \
                                                                      FROM "Champion_Mastery" r \
                                                                      WHERE l."summonerName" = r."summonerName") \
                                                    ORDER BY l."summonerName" ASC')
    else:
        async with pool.acquire() as connection:
            workingSummoners = await connection.fetch('SELECT DISTINCT "summonerName" \
                                                       FROM "Participant_Stats"\
                                                       ORDER BY "summonerName" ASC'
                                                     )

    for record in workingSummoners:
        if record[0] not in visitedSummoners:
            summonerNameQueue.put_nowait(record[0])


async def getSummonerId(summonerNameQueue: asyncio.Queue, summonerIdQueue: asyncio.Queue,
                        summonerId2summonerName: Dict[str,str], visitedSummoners: set,
                        pool: asyncpg.pool.Pool) -> None:
    while True:
        try:
            summonerName = await summonerNameQueue.get()
            print(f'[INFO] Looking up summonerId for: {summonerName}')
            data = await panth.getSummonerByName(summonerName)
            summonerIdQueue.put_nowait(data['id'])
            summonerId2summonerName[data['id']] = summonerName
            print(f"[INFO] summonerNameQueue: {summonerNameQueue.qsize()}")
        except Exception as e:
            print(f'[WARNING] getSummonerId ({summonerName}): {e}')
            if not any(x in str(e).lower() for x in ['rate limit', 'retry', 'limit ']):
                visitedSummoners.add(summonerName)
        finally:
            if summonerNameQueue.empty():
                print(f'[INFO] summonerNameQueue is empty. Looking in database for new summoners.')
                await getWorkingSummonerNames(summonerNameQueue, visitedSummoners, pool)
            summonerNameQueue.task_done()


async def getChampMastery(champMasteryQueue: asyncio.Queue, summonerIdQueue: asyncio.Queue,
                          summonerId2summonerName: Dict[str, str], visitedSummoners: set) -> None:
    while True:
        try:
            summonerId = await summonerIdQueue.get()
            champMasteryData = await panth.getChampionMasteries(summonerId)
            if champMasteryData:
                for champMastery in champMasteryData:
                    champMasteryQueue.put_nowait(champMastery)
            else:
                visitedSummoners.add(summonerId2summonerName[summonerId])
            # print(f"[INFO] summonerIdQueue: {summonerIdQueue.qsize()}")
        except Exception as e:
            # print(f'[ERROR] getChampMastery coroutine error.')
            print(f'[WARNING] getChampMastery ({summonerId}): {e}')
        finally:
            summonerIdQueue.task_done()


async def insertChampMastery(champMasteryQueue: asyncio.Queue, summonerId2summonerName:Dict[str,str], 
                            visitedSummoners: set, pool: asyncpg.pool.Pool) -> None:
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
                               f'ON CONFLICT ("summonerName", "championId")' 
                               f'DO UPDATE SET {upsertStatement};')
        
            async with pool.acquire() as connection:
                await connection.execute(insertStatement, *champMastery.values())
            visitedSummoners.add(champMastery['summonerName'])
            # print(f'[INFO] champMasteryQueue: {champMasteryQueue.qsize()}')
            # print(f'[INFO] Stored champion mastery for: {champMastery["summonerName"]}')
        except Exception as e:
            print(f'[ERROR] insertChampMastery: {e}')
            print(f'[ERROR] {champMastery}')
            print(f'[ERROR] {insertStatement}')
        finally:
            champMasteryQueue.task_done()

            # print(e)
        # print(f'champMasteryQueue: {champMasteryQueue.qsize()}')


async def getAllChampMastery(loop: asyncio.AbstractEventLoop, summonerNameQueue: asyncio.Queue,
                        visitedSummoners: set) -> None:
    try:
        pool = await asyncpg.create_pool(user=dbConfig['user'],
                                        password=dbConfig['password'],
                                        host=dbConfig['host'],
                                        port=dbConfig['port'],
                                        database=dbConfig['database'])
        # visitedSummoners.update(await getVisitedSummoners(pool))
        await getWorkingSummonerNames(summonerNameQueue, visitedSummoners, pool)
        if not riotConfig['revisitSummoners']:
            print(f"[INFO] Skipping {len(visitedSummoners)} visited summoners.")
        print(f"[INFO] Summoners to look up: {summonerNameQueue.qsize()}")
        champMasteryQueue = asyncio.Queue()
        summonerIdQueue = asyncio.Queue()
        summonerId2summonerName = dict()
        preProducers = [loop.create_task(getSummonerId(summonerNameQueue, summonerIdQueue, summonerId2summonerName, visitedSummoners, pool)) for _ in range(riotConfig['apiRate'])]
        producers = [loop.create_task(getChampMastery(champMasteryQueue, summonerIdQueue, summonerId2summonerName, visitedSummoners)) for _ in range(riotConfig['apiRate'])]
        consumers = [loop.create_task(insertChampMastery(champMasteryQueue, summonerId2summonerName, visitedSummoners, pool)) for _ in range(riotConfig['apiRate'])]
        await asyncio.gather(*preProducers)
        # await asyncio.gather(*producers)
        for p in producers:
            p.cancel()
        for c in consumers:
            c.cancel()
    except Exception as e:
        await pool.close()
        print(e)


def main() -> None:
    try:
        loop = asyncio.get_event_loop()
        summonerNameQueue = asyncio.Queue()
        visitedSummoners = set()
        if not riotConfig['revisitSummoners'] and os.path.isfile('.\ChampMasteryWIP\progress.json') and os.access('.\ChampMasteryWIP\progress.json', os.R_OK):
            with open('.\ChampMasteryWIP\progress.json') as f:
                data = json.load(f)
            visitedSummoners.update(data['visitedSummoners'])
            if os.path.isfile('.\ChampMasteryWIP\progress2.json') and os.access('.\ChampMasteryWIP\progress2.json', os.R_OK):
                with open('.\ChampMasteryWIP\progress2.json') as f:
                    data = json.load(f)
            visitedSummoners.update(data['visitedSummoners'])
        loop.run_until_complete(getAllChampMastery(loop, summonerNameQueue, visitedSummoners))
    except KeyboardInterrupt:
        print('Exiting.....')
    except Exception as e:
        print(f'[ERROR] Main: {e}')
    finally:
        # print(f'summonerIdQueue:\n{summonerIdQueue}')
        for task in asyncio.Task.all_tasks():
            task.cancel()
        # summonerNameList = {summonerNameQueue.get_nowait() for _ in range(summonerNameQueue.qsize())}
        print('-'*80)
        print(f'Visited {len(visitedSummoners)} summoners')
        # print(f'{visitedSummoners}')
        # print('-'*80)
        # print(f'summonerIdQueue({len(summonerNameList)})')
        # print(f'{summonerIdList}')
        print('-'*80)
        data = {
                'numVisitedSummoners': len(visitedSummoners),
                'visitedSummoners': sorted(list(visitedSummoners))
                }
        if not os.path.exists('ChampMasteryWIP'):
            os.mkdir('ChampMasteryWIP')
        with open('.\ChampMasteryWIP\progress.json', 'w') as outputFile:
            json.dump(data, outputFile, indent=4)

panth = pantheon.Pantheon(riotConfig['server'], riotConfig['api_key'], errorHandling=True, requestsLoggingFunction=requestsLog, debug=True)

if __name__ == '__main__':
    main()

