# -*- coding: utf-8 -*-
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


uri = "mongodb://127.0.0.1:27017"

__MONGO_CLIENT = MongoClient(uri, server_api=ServerApi("1"))

def get_mongo_client():
    return __MONGO_CLIENT
