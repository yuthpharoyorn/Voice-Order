from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import pymysql

connection = pymysql.connect(
    host='localhost',
    user='root',
    password='Roosmile@2004'
)

try:
    with connection.cursor() as cursor:
        cursor.execute("CREATE DATABASE IF NOT EXISTS voice_orders;")
    print("Database created or already exists.")
finally:
    connection.close()


DATABASE_URL =  "mysql+pymysql://root:Roosmile%402004@localhost/voice_orders"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# try:
#     with engine.connect() as connection:
#         print("Connected to MySQL server successfully!")
# except Exception as e:
#     print("Failed to connect to MySQL server:", e)