# utils/db_setup.py

from app.config import Config

from app.utils.database import Database



db = Database()

def sync_admins_from_config():
    for sa_id in Config.SUPERADMINS:
        db.execute("INSERT OR IGNORE INTO superadmins (user_id) VALUES (?);", parameters=(sa_id,), commit=True)

    for a_id in Config.ADMINS:
        db.execute("INSERT OR IGNORE INTO admins (user_id, full_name) VALUES (?, ?);", parameters=(a_id, "Admin from config"), commit=True)
