from pymongo import MongoClient

def get_db_connection():
    client = MongoClient('mongodb+srv://bingemovies:CWuhFDboOssypOfD@binge.qvrdf.mongodb.net/')
    return client['BINGE']

def get_collection(db, collection_name):
    return db[collection_name]
