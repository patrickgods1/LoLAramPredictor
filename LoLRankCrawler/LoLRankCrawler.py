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
                                                                      FROM "Rank" r \
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
    # while not summonerNameQueue.empty():
        # while summonerNameQueue.empty():
        #     print(f'[INFO] summonerNameQueue is empty. Looking in database for new summoners.')
        #     await getWorkingSummonerNames(summonerNameQueue, visitedSummoners, pool)
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


async def getRankInfo(rankDataQueue: asyncio.Queue, summonerIdQueue: asyncio.Queue,
                      summonerId2summonerName: Dict[str, str], visitedSummoners: set) -> None:
    while True:
        try:
            summonerId = await summonerIdQueue.get()
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
            summonerIdQueue.task_done()


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
            print(f'[INFO] Stored Rank Info: {rankData["summonerName"]}')

        except Exception as e:
            print(f'[ERROR] insertRankInfo: {e}')
            print(f'[ERROR] {rankData}')
        finally:
            rankDataQueue.task_done()


async def getAllRanks(loop: asyncio.AbstractEventLoop, summonerNameQueue: asyncio.Queue,
                        visitedSummoners: set) -> None:
    try:
        pool = await asyncpg.create_pool(user=dbConfig['user'],
                                        password=dbConfig['password'],
                                        host=dbConfig['host'],
                                        port=dbConfig['port'],
                                        database=dbConfig['database'])
        await getWorkingSummonerNames(summonerNameQueue, visitedSummoners, pool)

        if not riotConfig['revisitSummoners']:
            print(f"[INFO] Skipping {len(visitedSummoners)} visited summoners.")
        print(f"[INFO] Summoners to look up: {summonerNameQueue.qsize()}")

        rankDataQueue = asyncio.Queue()
        summonerIdQueue = asyncio.Queue()
        summonerId2summonerName = dict()
        preProducers = [loop.create_task(getSummonerId(summonerNameQueue, summonerIdQueue, summonerId2summonerName, visitedSummoners, pool)) for _ in range(riotConfig['apiRate'])]
        producers = [loop.create_task(getRankInfo(rankDataQueue, summonerIdQueue, summonerId2summonerName, visitedSummoners)) for _ in range(riotConfig['apiRate'])]
        consumers = [loop.create_task(insertRankInfo(rankDataQueue, summonerId2summonerName, visitedSummoners, pool)) for _ in range(riotConfig['apiRate'])]
        await asyncio.gather(*preProducers)
        await summonerNameQueue.join()
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
        if not riotConfig['revisitSummoners'] and os.path.isfile(r'.\RankWIP\progress.json') and os.access(r'.\RankWIP\progress.json', os.R_OK):
            with open(r'.\RankWIP\progress.json') as f:
                data = json.load(f)
            visitedSummoners.update(data['visitedSummoners'])
            if os.path.isfile(r'.\RankWIP\progress2.json') and os.access(r'.\RankWIP\progress2.json', os.R_OK):
                with open(r'.\RankWIP\progress2.json') as f:
                    data = json.load(f)
            visitedSummoners.update(data['visitedSummoners'])
        loop.run_until_complete(getAllRanks(loop, summonerNameQueue, visitedSummoners))
    except KeyboardInterrupt:
        print('Exiting.....')
    except Exception as e:
        print(f'[ERROR] Main: {e}')
    finally:
        for task in asyncio.Task.all_tasks():
            task.cancel()
        print('-'*80)
        print(f'Visited {len(visitedSummoners)} summoners')
        # print(f'{visitedSummoners}')
        print('-'*80)
        data = {
                'numVisitedSummoners': len(visitedSummoners),
                'visitedSummoners': sorted(list(visitedSummoners))
                }
        if not os.path.exists('RankWIP'):
            os.mkdir('RankWIP')
        with open(r'.\RankWIP\progress.json', 'w') as outputFile:
            json.dump(data, outputFile, indent=4)

panth = pantheon.Pantheon(riotConfig['server'], riotConfig['api_key'], errorHandling=True, requestsLoggingFunction=requestsLog, debug=True)

if __name__ == '__main__':
    main()

