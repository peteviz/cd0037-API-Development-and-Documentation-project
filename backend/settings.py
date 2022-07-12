from dotenv import load_dotenv
import os
# from env import DB_NAME, DB_USER, DB_PASSWORD
load_dotenv()
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
