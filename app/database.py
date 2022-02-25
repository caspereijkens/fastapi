import psycopg2
from psycopg2.extras import RealDictCursor
import json
from time import sleep

with open('/etc/config_fastapi.json') as config_file:
    config = json.load(config_file)

# Connect to db
while True:
    try:
        conn = psycopg2.connect(
            host=config["HOST"],
            database=config["DB_NAME"],
            user=config["DB_USER"],
            password=config["DB_PASS"],
            cursor_factory=RealDictCursor,
        )
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)
        sleep(2)
