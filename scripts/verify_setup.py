from config import Config
import sqlite3


def verify_database(db_path):
    required_tables = {
        'market_data.db': ['token_metrics'],
        'patterns.db': ['patterns']
    }

    db_name = db_path.name
    print(f"\nVerifying {db_name}:")

    try:
        with Config.db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]

            for req in required_tables[db_name]:
                if req not in tables:
                    print(f"❌ Missing table: {req}")
                    return False
                print(f"✅ Found table: {req}")
        return True
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False


if __name__ == "__main__":
    config = Config()
    all_ok = True

    all_ok &= verify_database(config.LIVE_DB)
    all_ok &= verify_database(config.PATTERN_DB)

    if all_ok:
        print("\n✅ All systems go!")
    else:
        print("\n❌ Setup incomplete! Run: python scripts/setup_db.py")
