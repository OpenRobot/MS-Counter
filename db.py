import asyncpg, asyncio, json

class Database:
    def __init__(self, loop, db_uri):
        self.uri = str(db_uri)
        self.db = None
        loop.run_until_complete(self.initialize())

        self.is_modifying = False

    def wait_until_not_modifying(self):
        while self.is_modifying:
            pass

        return

    async def initialize(self):
        while True:
            try:
                self.db = await asyncpg.create_pool(self.uri)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break
        
        while True:
            try:
                async with self.db.acquire() as conn:
                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS counter(
                        count BIGINT DEFAULT 0
                    );
                    """)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.fetchrow("SELECT * FROM counter")
                    if not x:
                        await conn.execute("INSERT INTO counter VALUES ($1)", 0)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.execute("""
                    CREATE TABLE IF NOT EXISTS counter_lb(
                        user_id BIGINT,
                        counts BIGINT DEFAULT 0,
                        recent_counts JSONB NOT NULL DEFAULT '[]'::jsonb 
                    );
                    """)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        return self.db

    async def get_current_number(self) -> int:
        while True:
            self.wait_until_not_modifying()

            try:
                async with self.db.acquire() as conn:
                    x = await conn.fetchrow("SELECT * FROM counter")
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        if x is None:
            await self.initialize()

            return await self.get_current_number()
        else:
            return x['count']

    async def set_number(self, author, msg, num: int):
        self.is_modifying = True

        while True:
            try:
                async with self.db.acquire() as conn:
                    await conn.execute("UPDATE counter SET count = $1", int(num))
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.fetchrow("SELECT * FROM counter_lb WHERE user_id = $1", int(author.id))
                    if x:
                        await conn.execute(
                            "UPDATE counter_lb SET counts = $2, recent_counts = $3 WHERE user_id = $1", 
                            int(author.id), 
                            len(json.loads(x['recent_counts'])) + 1, 
                            json.dumps(json.loads(x['recent_counts']) + [{
                                'num': int(num), 
                                'message_id': msg.id, 
                                'message_url': msg.jump_url, 
                                'channel_id': msg.channel.id, 
                                'timestamp': msg.created_at.timestamp()
                            }])
                        )
                    else:
                        await conn.execute(
                            "INSERT INTO counter_lb VALUES ($1, $2, $3)",
                            int(author.id),
                            1,
                            json.dumps(
                                [{
                                    'num': int(num),
                                    'message_id': msg.id,
                                    'message_url': msg.jump_url,
                                    'channel_id': msg.channel.id,
                                    'timestamp': msg.created_at.timestamp()
                                }]
                            )
                        )
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        self.is_modifying = False

        return int(num)