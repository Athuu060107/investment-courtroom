"""
Phase 0 verification script.
Checks that: required packages are installed, and Python can connect to MySQL.
Run this from the project root with: python tests/verify_setup.py
"""

import sys

def check_imports():
    required = ["pandas", "numpy", "mysql.connector", "plotly", "streamlit", "dotenv"]
    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"❌ Missing packages: {missing}")
        print("   Run: pip install -r requirements.txt")
        return False
    print("✅ All required packages are installed.")
    return True


def check_mysql_connection():
    import os
    from dotenv import load_dotenv
    import mysql.connector
    from mysql.connector import Error

    load_dotenv()

    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        if connection.is_connected():
            db_info = connection.get_server_info()
            print(f"✅ Connected to MySQL server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print(f"✅ Connected to database: {db_name[0]}")
            cursor.close()
            connection.close()
            return True
    except Error as e:
        print(f"❌ MySQL connection failed: {e}")
        print("   Check your .env file values and that MySQL server is running.")
        return False


if __name__ == "__main__":
    print("Running Phase 0 verification...\n")
    imports_ok = check_imports()
    print()
    db_ok = check_mysql_connection() if imports_ok else False

    print()
    if imports_ok and db_ok:
        print("🎉 Phase 0 complete. You're ready for Phase 1 (data collection).")
        sys.exit(0)
    else:
        print("⚠️ Fix the issues above before moving to Phase 1.")
        sys.exit(1)
