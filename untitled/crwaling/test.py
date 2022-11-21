import pymongo
import time
client = pymongo.MongoClient('mongodb://%s:%s' % ('192.168.0.36','27017'))
db = client['crwaling']
collection = db['coll']
collection.insert_one({'test' : '1'})
