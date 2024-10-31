import os
import time

import psycopg
from alembic import command
from alembic.config import Config
from sqlalchemy.exc import OperationalError


def create_db():
    # if database {DB_NAME} does not exist create it
    # establishing the connection
    reconnect = 5
    conn = None
    while True:
        try:
            print("trying to connect to db...")
            conn = psycopg.connect(
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                host=os.environ["DB_HOST"],
                port=os.environ["DB_PORT"],
            )
            break
        except Exception as e:
            print(e)
            print(f"reconnect: {reconnect}")
            time.sleep(1)
            reconnect -= 1
            if reconnect == 0:
                break

    if conn is None:
        print("failed to connect to db")
        return
    conn.autocommit = True

    # Creating a cursor object using the cursor() method
    cursor = conn.cursor()
    print(f'creating {os.environ["DB_NAME"]}')
    try:
        # Creating a database
        cursor.execute(f'CREATE database {os.environ["DB_NAME"]}')
        print("Database created successfully........")
    # if the database already exist ignore
    except Exception:
        print("Database already there........")

    # Closing the connection
    conn.close()


def run_migration():
    app_name = os.getenv("APP_NAME")
    print("running migration for app :", app_name)
    app_config = Config("alembic.ini")
    app_config.set_main_option("script_location", "./app/alembic")
    command.upgrade(config=app_config, revision="head")


try:
    run_migration()
except OperationalError as e:
    if e.code != "e3q8":
        raise e

    create_db()
    run_migration()
