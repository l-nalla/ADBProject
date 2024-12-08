from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class MongoDBConnection:
    def __init__(self):
        self.uri = os.getenv('MONGO_URI')
        self.db_name = os.getenv('DATABASE_NAME')
        self.client = None
        self.db = None

    def connect(self):
        if not self.client:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            print("MongoDB connection established")
        return self.db

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")