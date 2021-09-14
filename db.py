import asyncpg, asyncio, json

class RomanDatabase:
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
                self.db = await asyncpg.create_pool(self.uri, max_size=20, min_size=5)
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

class BinaryDatabase:
    def __init__(self, loop, db_uri, db_obj):
        self.uri = str(db_uri)
        self.db = None

        self.is_modifying = False

        self.db_obj = db_obj

        loop.run_until_complete(self.initialize())

    def wait_until_not_modifying(self):
        while self.is_modifying:
            pass

        return

    async def initialize(self):
        if not self.db_obj: # For making sure it doesnt have too many connections and traffic and to handle TooManyConnectionsError.
            while True:
                try:
                    self.db = await asyncpg.create_pool(self.uri)
                except asyncpg.exceptions._base.InterfaceError:
                    await asyncio.sleep(5)
                    pass
                else:
                    break
        else:
            self.db = self.db_obj
        
        while True:
            try:
                async with self.db.acquire() as conn:
                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS binary_counter(
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
                    x = await conn.fetchrow("SELECT * FROM binary_counter")
                    if not x:
                        await conn.execute("INSERT INTO binary_counter VALUES ($1)", 0)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.execute("""
                    CREATE TABLE IF NOT EXISTS binary_counter_lb(
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
                    x = await conn.fetchrow("SELECT * FROM binary_counter")
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
                    await conn.execute("UPDATE binary_counter SET count = $1", int(num))
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.fetchrow("SELECT * FROM binary_counter_lb WHERE user_id = $1", int(author.id))
                    if x:
                        await conn.execute(
                            "UPDATE binary_counter_lb SET counts = $2, recent_counts = $3 WHERE user_id = $1", 
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
                            "INSERT INTO binary_counter_lb VALUES ($1, $2, $3)",
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

class HexadecimalDatabase:
    def __init__(self, loop, db_uri, db_obj):
        self.uri = str(db_uri)
        self.db = None

        self.is_modifying = False

        self.db_obj = db_obj

        loop.run_until_complete(self.initialize())

    def wait_until_not_modifying(self):
        while self.is_modifying:
            pass

        return

    async def initialize(self):
        if not self.db_obj: # For making sure it doesnt have too many connections and traffic and to handle TooManyConnectionsError.
            while True:
                try:
                    self.db = await asyncpg.create_pool(self.uri)
                except asyncpg.exceptions._base.InterfaceError:
                    await asyncio.sleep(5)
                    pass
                else:
                    break
        else:
            self.db = self.db_obj
        
        while True:
            try:
                async with self.db.acquire() as conn:
                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS hexadecimal_counter(
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
                    x = await conn.fetchrow("SELECT * FROM hexadecimal_counter")
                    if not x:
                        await conn.execute("INSERT INTO hexadecimal_counter VALUES ($1)", 0)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.execute("""
                    CREATE TABLE IF NOT EXISTS hexadecimal_counter_lb(
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
                    x = await conn.fetchrow("SELECT * FROM hexadecimal_counter")
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
                    await conn.execute("UPDATE hexadecimal_counter SET count = $1", int(num))
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.fetchrow("SELECT * FROM hexadecimal_counter_lb WHERE user_id = $1", int(author.id))
                    if x:
                        await conn.execute(
                            "UPDATE hexadecimal_counter_lb SET counts = $2, recent_counts = $3 WHERE user_id = $1", 
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
                            "INSERT INTO hexadecimal_counter_lb VALUES ($1, $2, $3)",
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

class OctalDatabase:
    def __init__(self, loop, db_uri, db_obj = None):
        self.uri = str(db_uri)
        self.db = None

        self.is_modifying = False

        self.db_obj = db_obj

        loop.run_until_complete(self.initialize())

    def wait_until_not_modifying(self):
        while self.is_modifying:
            pass

        return

    async def initialize(self):
        if not self.db_obj: # For making sure it doesnt have too many connections and traffic and to handle TooManyConnectionsError.
            while True:
                try:
                    self.db = await asyncpg.create_pool(self.uri)
                except asyncpg.exceptions._base.InterfaceError:
                    await asyncio.sleep(5)
                    pass
                else:
                    break
        else:
            self.db = self.db_obj
        
        while True:
            try:
                async with self.db.acquire() as conn:
                    await conn.execute("""
                    CREATE TABLE IF NOT EXISTS octal_counter(
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
                    x = await conn.fetchrow("SELECT * FROM octal_counter")
                    if not x:
                        await conn.execute("INSERT INTO octal_counter VALUES ($1)", 0)
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.execute("""
                    CREATE TABLE IF NOT EXISTS octal_counter_lb(
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
                    x = await conn.fetchrow("SELECT * FROM octal_counter")
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
                    await conn.execute("UPDATE octal_counter SET count = $1", int(num))
            except asyncpg.exceptions._base.InterfaceError:
                await asyncio.sleep(5)
                pass
            else:
                break

        while True:
            try:
                async with self.db.acquire() as conn:
                    x = await conn.fetchrow("SELECT * FROM octal_counter_lb WHERE user_id = $1", int(author.id))
                    if x:
                        await conn.execute(
                            "UPDATE octal_counter_lb SET counts = $2, recent_counts = $3 WHERE user_id = $1", 
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
                            "INSERT INTO octal_counter_lb VALUES ($1, $2, $3)",
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

class Database:
    def __init__(self, *args, **kwargs):
        self.roman = RomanDatabase(*args, **kwargs)

        kwargs['db_obj'] = self.roman.db

        self.binary = BinaryDatabase(*args, **kwargs)
        self.hexadecimal = HexadecimalDatabase(*args, **kwargs)
        self.octal = OctalDatabase(*args, **kwargs)