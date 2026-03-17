# Run this ONCE to upload your CSV to MongoDB
import os, sys, json
import certifi
import pandas as pd
import numpy as np
import pymongo
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

MONGO_DB_URL = os.getenv('MONGO_DB_URL')

class NetworkDataExtract:
    def __init__(self):
        pass

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_mongodb(self, records, database, collection):
        try:
            ca = certifi.where()
            mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            db           = mongo_client[database]
            col          = db[collection]
            col.insert_many(records)
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == '__main__':
    FILE_PATH  = 'Network_Data/phisingData.csv'
    DATABASE   = 'KRISHAI'
    COLLECTION = 'NetworkData'
    obj        = NetworkDataExtract()
    records    = obj.csv_to_json_convertor(file_path=FILE_PATH)
    count      = obj.insert_data_mongodb(records, DATABASE, COLLECTION)
    print(f'Inserted {count} records into MongoDB.')
