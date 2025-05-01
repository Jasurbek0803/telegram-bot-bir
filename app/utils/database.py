import sqlite3
from asyncio.log import logger
from datetime import datetime



class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        conn = sqlite3.connect(self.path_to_db)
        conn.execute("PRAGMA foreign_keys = ON")  # Foreign keylarni yoqish
        return conn

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        cursor = connection.cursor()
        data = None
        try:
            cursor.execute(sql, parameters)
            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            connection.close()
        return data

    # --- CREATE TABLES ---
    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(sql, commit=True)

    def create_table_tests(self):
        sql = """
        CREATE TABLE IF NOT EXISTS tests (
            code INTEGER PRIMARY KEY,
            answers TEXT NOT NULL,
            center_name TEXT NOT NULL,
            author TEXT NOT NULL,
            author_id INTEGER NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
        """
        self.execute(sql, commit=True)

    def create_table_results(self):
        sql = """
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            code INTEGER NOT NULL,
            correct_answer INTEGER NOT NULL,
            incorrect_answer INTEGER NOT NULL,
            percentage REAL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(sql, commit=True)

    def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        self.execute(sql, commit=True)

    def create_table_superadmins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS superadmins (
            user_id INTEGER PRIMARY KEY,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """
        self.execute(sql, commit=True)

    def create_all_tables(self):
        self.create_table_users()
        self.create_table_tests()
        self.create_table_results()
        self.create_table_admins()
        self.create_table_superadmins()

    # --- CRUD EXAMPLES ---

    def get_test_results_by_author_id(self, author_id: int) -> list[tuple]:
        sql = """
              SELECT u.full_name, r.code, r.correct_answer, r.incorrect_answer, r.percentage
                FROM results r
                JOIN tests t ON r.code = t.code
                Join users u On r.user_id = u.user_id
                WHERE t.author_id = ?
              """
        return self.execute(sql, (author_id,),fetchall=True)

    def get_best_result(self, user_id: int):
        sql = """
                SELECT u.full_name, r.percentage, r.user_id, code
                FROM results r
                Join users u ON u.user_id == r.user_id
                WHERE r.user_id = ? AND percentage >= 60
                ORDER BY percentage DESC
                LIMIT 1
            """
        return self.execute(sql, (user_id,),fetchone=True)


    def add_user(self, user_id: int, full_name: str, phone: str):
        sql = """
            INSERT INTO users (user_id, full_name, phone)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                phone = excluded.phone;
        """
        self.execute(sql, parameters=(user_id, full_name, phone), commit=True)

    def add_test(self, code: int, answers: str, center_name: str, author: str, author_id: int):
        sql = "INSERT OR REPLACE INTO tests(code, answers, center_name, author, author_id) VALUES (?, ?, ?, ?, ?);"
        self.execute(sql, parameters=(code, answers, center_name, author, author_id), commit=True)

    def add_result(self, full_name: str, user_id: int, code: int, correct: int, incorrect: int, percentage: float):
        sql = """
        INSERT INTO results(full_name, user_id, code, correct_answer, incorrect_answer, percentage)
        VALUES (?, ?, ?, ?, ?, ?);
        """
        self.execute(sql, parameters=(full_name, user_id, code, correct, incorrect, percentage), commit=True)

    def add_admin(self, user_id: int, full_name: str):
        sql = """
        INSERT OR REPLACE INTO admins (user_id, full_name) VALUES (?, ?);
        """
        self.execute(sql, parameters=(user_id, full_name), commit=True)

    def remove_admin(self, user_id: int):
        sql = """
              DELETE \
              FROM admins \
              WHERE user_id = ?; \
              """
        self.execute(sql, parameters=(user_id,), commit=True)

    def get_user_by_id(self, user_id: int):
        sql = "SELECT * FROM users WHERE user_id = ?;"
        return self.execute(sql, parameters=(user_id,), fetchone=True)
    def get_user_full_name(self, user_id: int):
        sql = "SELECT fullname FROM users WHERE user_id = ?;"
        return self.execute(sql, parameters=(user_id,), fetchone=True)

    def get_admin_ids(self) -> list:
        sql = "SELECT user_id FROM admins;"
        rows = self.execute(sql, fetchall=True)
        return [row[0] for row in rows]

    def get_superadmin_ids(self) -> list:
        sql = "SELECT user_id FROM superadmins;"
        rows = self.execute(sql, fetchall=True)
        return [row[0] for row in rows]

    def is_admin(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM admins WHERE user_id = ?;"
        return self.execute(sql, parameters=(user_id,), fetchone=True) is not None

    def is_superadmin(self, user_id: int) -> bool:
        sql = "SELECT 1 FROM superadmins WHERE user_id = ?;"
        return self.execute(sql, parameters=(user_id,), fetchone=True) is not None

    def get_test_author_id(self, code: int) -> int | None:
        sql = "SELECT author_id FROM tests WHERE code = ?;"
        result = self.execute(sql, parameters=(code,), fetchone=True)
        return result[0] if result else None
    def get_test_author(self, code: int) -> int | None:
        sql = "SELECT author FROM tests WHERE code = ?;"
        result = self.execute(sql, parameters=(code,), fetchone=True)
        return result[0] if result else None

    def delete_test_by_code(self, code: int) -> bool:
        sql = "DELETE FROM tests WHERE code = ?;"
        self.execute(sql, parameters=(code,), commit=True)
        return True

    def delete_test_if_allowed(self, code: int, user_id: int, is_superadmin: bool) -> bool:
        answer = False

        sql_check = "SELECT author_id FROM tests WHERE code = ?"
        result = self.execute(sql_check, (code,), fetchone=True)

        if not result:
            return answer  # Test mavjud emas

        author_id = result[0]
        if is_superadmin or author_id == user_id: #DELETE FROM tests WHERE code = ?
            sql_delete = "DELETE FROM tests WHERE code = ?; "
            self.execute(sql_delete, (code,), commit=True)
            answer = True
        return answer

    def get_all_user(self):
        sql = "SELECT * FROM users"
        return self.execute(sql, fetchall=True)

    # ✅ Testni code orqali topish
    def get_test_by_code(self, code: int):
        sql = "SELECT * FROM tests WHERE code = ?;"
        return self.execute(sql, parameters=(code,), fetchone=True)

    # ✅ Foydalanuvchi test yechganmi
    def has_user_taken_test(self, user_id: int, code: str):
        return self.execute("SELECT 1 FROM results WHERE user_id = ? AND code = ?", (user_id, code), fetchone=True)

        # ✅ Natijani saqlash
    def save_result(self, full_name, user_id, code, correct, incorrect, percentage):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.execute("""
                         INSERT INTO results (full_name, user_id, code, correct_answer, incorrect_answer, percentage,
                                              timestamp)
                         VALUES (?, ?, ?, ?, ?, ?, ?)
                         """, (full_name, user_id, code, correct, incorrect, percentage, timestamp), commit=True)

    def get_results_by_user(self, user_id: int):
        sql = "SELECT * FROM results WHERE user_id = ? ORDER BY timestamp DESC;"
        return self.execute(sql, parameters=(user_id,), fetchall=True)

    def get_all_tests(self):
        sql = "SELECT * FROM tests"
        return self.execute(sql, fetchall=True)

    def delete_test(self, code: int):
        sql = "DELETE FROM tests WHERE code = ?;"
        self.execute(sql, parameters=(code,), commit=True)




