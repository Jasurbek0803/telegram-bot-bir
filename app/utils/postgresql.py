from typing import Union, Optional, List
from datetime import datetime
import logging
import asyncpg
from asyncpg import Pool

from app.config import Config

# Logger sozlash
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

config = Config()


class Database:
    def __init__(self):
        self.pool: Optional[Pool] = None

    async def create(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=config.DB_USER,
                password=config.DB_PASS,
                host=config.DB_HOST,
                database=config.DB_NAME,
            )
            logger.info("✅ Database pool muvaffaqiyatli yaratildi.")
        except Exception as e:
            logger.error(f"❌ Database pool yaratishda xatolik: {e}")
            raise

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        if self.pool is None:
            logger.critical("❌ self.pool hali yaratilmagan. `create()` metodi chaqirilmagan!")
            raise RuntimeError("Database pool is not initialized. Did you forget to call `create()`?")

        try:
            async with self.pool.acquire() as connection:
                async with connection.transaction():
                    if fetch:
                        result = await connection.fetch(command, *args)
                    elif fetchval:
                        result = await connection.fetchval(command, *args)
                    elif fetchrow:
                        result = await connection.fetchrow(command, *args)
                    elif execute:
                        result = await connection.execute(command, *args)
                    else:
                        result = None
            return result
        except Exception as e:
            logger.error(f"❌ SQL xatolik: {e} | SQL: {command} | args: {args}")
            raise

    async def create_all_tables(self):
        logger.info("▶️ Barcha jadval(lar) yaratilmoqda...")
        await self.create_table_users()
        await self.create_table_tests()
        await self.create_table_results()
        await self.create_table_admins()
        await self.create_table_superadmins()
        logger.info("✅ Barcha jadvallar yaratildi.")

    async def create_table_users(self):
        sql = """
              CREATE TABLE IF NOT EXISTS users \
              ( \
                  user_id       BIGINT PRIMARY KEY, \
                  full_name     TEXT NOT NULL, \
                  phone         TEXT NOT NULL, \
                  registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              ); \
              """
        await self.execute(sql, execute=True)

    async def create_table_tests(self):
        sql = """
              CREATE TABLE IF NOT EXISTS tests \
              ( \
                  code        BIGINT PRIMARY KEY, \
                  answers     TEXT NOT NULL, \
                  center_name TEXT NOT NULL, \
                  author      TEXT NOT NULL, \
                  author_id   BIGINT, \
                  FOREIGN KEY (author_id) REFERENCES users (user_id) ON DELETE SET NULL
              ); \
              """
        await self.execute(sql, execute=True)

    async def create_table_results(self):
        sql = """
              CREATE TABLE IF NOT EXISTS results \
              ( \
                  id               SERIAL PRIMARY KEY, \
                  full_name        TEXT    NOT NULL, \
                  user_id          BIGINT  NOT NULL, \
                  code             BIGINT  NOT NULL, \
                  correct_answer   INTEGER NOT NULL, \
                  incorrect_answer INTEGER NOT NULL, \
                  percentage       REAL, \
                  timestamp        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
              ); \
              """
        await self.execute(sql, execute=True)

    async def create_table_admins(self):
        sql = """
              CREATE TABLE IF NOT EXISTS admins \
              ( \
                  user_id   BIGINT PRIMARY KEY, \
                  full_name TEXT NOT NULL, \
                  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
              ); \
              """
        await self.execute(sql, execute=True)

    async def create_table_superadmins(self):
        sql = """
              CREATE TABLE IF NOT EXISTS superadmins \
              ( \
                  user_id BIGINT PRIMARY KEY, \
                  FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
              ); \
              """
        await self.execute(sql, execute=True)


    # CRUD METHODS
    async def get_test_results_by_author_id(self, author_id: int):
        sql = """
        SELECT u.full_name, r.code, r.correct_answer, r.incorrect_answer, r.percentage, r.timestamp
        FROM results r
        JOIN tests t ON r.code = t.code
        JOIN users u ON r.user_id = u.user_id
        WHERE t.author_id = $1
        ORDER BY r.code, r.percentage DESC, r.timestamp ASC;
        """
        return await self.execute(sql, author_id, fetch=True)

    async def get_best_result(self, user_id: int):
        sql = """
        SELECT u.full_name, r.percentage, r.user_id, code
        FROM results r
        JOIN users u ON u.user_id = r.user_id
        WHERE r.user_id = $1 AND percentage >= 60
        ORDER BY percentage DESC
        LIMIT 1;
        """
        return await self.execute(sql, user_id, fetchrow=True)

    async def add_user(self, user_id: int, full_name: str, phone: str):
        sql = """
        INSERT INTO users (user_id, full_name, phone)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            phone = EXCLUDED.phone;
        """
        await self.execute(sql, user_id, full_name, phone, execute=True)

    async def add_test(self, code: int, answers: str, center_name: str, author: str, author_id: int):
        sql = """
        INSERT INTO tests(code, answers, center_name, author, author_id)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (code) DO UPDATE SET
            answers = EXCLUDED.answers,
            center_name = EXCLUDED.center_name,
            author = EXCLUDED.author,
            author_id = EXCLUDED.author_id;
        """
        await self.execute(sql, code, answers, center_name, author, author_id, execute=True)

    async def add_result(self, full_name: str, user_id: int, code: int, correct: int, incorrect: int, percentage: float):
        sql = """
        INSERT INTO results(full_name, user_id, code, correct_answer, incorrect_answer, percentage)
        VALUES ($1, $2, $3, $4, $5, $6);
        """
        await self.execute(sql, full_name, user_id, code, correct, incorrect, percentage, execute=True)

    async def add_admin(self, user_id: int, full_name: str):
        sql = """
        INSERT INTO admins (user_id, full_name)
        VALUES ($1, $2)
        ON CONFLICT (user_id) DO UPDATE SET full_name = EXCLUDED.full_name;
        """
        await self.execute(sql, user_id, full_name, execute=True)

    async def remove_admin(self, user_id: int):
        sql = "DELETE FROM admins WHERE user_id = $1;"
        await self.execute(sql, user_id, execute=True)

    async def get_user_by_id(self, user_id: int):
        sql = "SELECT * FROM users WHERE user_id = $1;"
        return await self.execute(sql, user_id, fetchrow=True)

    async def get_user_full_name(self, user_id: int):
        sql = "SELECT full_name FROM users WHERE user_id = $1;"
        return await self.execute(sql, user_id, fetchval=True)

    async def get_admin_ids(self) -> List[int]:
        sql = "SELECT user_id FROM admins;"
        rows = await self.execute(sql, fetch=True)
        return [row['user_id'] for row in rows]

    async def get_superadmin_ids(self) -> List[int]:
        sql = "SELECT user_id FROM superadmins;"
        rows = await self.execute(sql, fetch=True)
        return [row['user_id'] for row in rows]

    async def is_admin(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM admins WHERE user_id = $1;"
        return await self.execute(sql, user_id, fetchval=True) is not None

    async def is_superadmin(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM superadmins WHERE user_id = $1;"
        return await self.execute(sql, user_id, fetchval=True) is not None

    async def get_test_author_id(self, code: int) -> Optional[int]:
        sql = "SELECT author_id FROM tests WHERE code = $1;"
        result = await self.execute(sql, code, fetchrow=True)
        return result['author_id'] if result else None

    async def get_test_author(self, code: int) -> Optional[str]:
        sql = "SELECT author FROM tests WHERE code = $1;"
        result = await self.execute(sql, code, fetchrow=True)
        return result['author'] if result else None

    async def delete_test_by_code(self, code: int) -> bool:
        sql = "DELETE FROM tests WHERE code = $1;"
        await self.execute(sql, code, execute=True)
        return True

    async def delete_test_if_allowed(self, code: int, user_id: int, is_superadmin: bool) -> bool:
        sql_check = "SELECT author_id FROM tests WHERE code = $1;"
        result = await self.execute(sql_check, code, fetchrow=True)

        if not result:
            return False

        author_id = result['author_id']
        if is_superadmin or author_id == user_id:
            sql_delete = "DELETE FROM tests WHERE code = $1;"
            await self.execute(sql_delete, code, execute=True)
            return True
        return False

    async def get_all_user(self):
        sql = "SELECT * FROM users;"
        return await self.execute(sql, fetch=True)

    async def get_all_user_id(self):
        sql = "SELECT user_id FROM users;"
        return await self.execute(sql, fetch=True)

    async def get_test_by_code(self, code: int):
        sql = "SELECT * FROM tests WHERE code = $1;"
        return await self.execute(sql, code, fetchrow=True)

    async def has_user_taken_test(self, user_id: int, code: int):
        sql = "SELECT 1 FROM results WHERE user_id = $1 AND code = $2;"
        return await self.execute(sql, user_id, code, fetchval=True) is not None

    async def save_result(self, full_name: str, user_id: int, code: int, correct: int, incorrect: int, percentage: float):
        timestamp = datetime.now()
        sql = """
        INSERT INTO results (full_name, user_id, code, correct_answer, incorrect_answer, percentage, timestamp)
        VALUES ($1, $2, $3, $4, $5, $6, $7);
        """
        await self.execute(sql, full_name, user_id, code, correct, incorrect, percentage, timestamp, execute=True)

    async def get_results_by_user(self, user_id: int):
        sql = "SELECT * FROM results WHERE user_id = $1 ORDER BY timestamp DESC;"
        return await self.execute(sql, user_id, fetch=True)

    async def get_all_tests(self):
        sql = "SELECT * FROM tests;"
        return await self.execute(sql, fetch=True)

    async def delete_test(self, code: int):
        sql = "DELETE FROM tests WHERE code = $1;"
        await self.execute(sql, code, execute=True)


