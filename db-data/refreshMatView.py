import asyncpg
import asyncio
from config import dbConfig


async def run():
    connection = await asyncpg.connect(user=dbConfig['user'],
                                password=dbConfig['password'],
                                host=dbConfig['host'],
                                port=dbConfig['port'],
                                database=dbConfig['database'])
    async with connection.transaction():
        refreshQuery = f'REFRESH MATERIALIZED VIEW "games_mat_view";'
        status = await connection.execute(refreshQuery)
    return status

loop = asyncio.get_event_loop()
status = loop.run_until_complete(run())
print(status)

