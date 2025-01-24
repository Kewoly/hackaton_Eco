from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

class Config:
    """ Configurations for the application """
    def __init__(self):
        # Application configurations
        self.version = "0.0.1",
        self.name = "GameAPI",

        # # Database configurations
        # self.mongo_url = os.getenv("MONGO_URL") + "?authSource=admin" # pymongo cuts off parameters after the first "&"
        # self.database = os.getenv("DATABASE_NAME")
        
        # # connect to the database
        # self.client = MongoClient(self.mongo_url)
        # self.db = self.client[self.database]