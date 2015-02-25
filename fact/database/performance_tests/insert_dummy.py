import os
import pyfact as pf
from glob import iglob
import time
from pymongo import MongoClient
import pymongo

import numpy as np
from pprint import pprint

connection = MongoClient('localhost', 27017)
db = connection.test

coll = db.dummy_data
bulk = coll.initialize_ordered_bulk_op()


starttime = time.time()

for i in range(int(100e3)):
    r = np.random.uniform(size=125)
    document = { "numbers":r.tolist() }

    if '_id' in document:
        del document['_id']
    bulk.insert(document)
try:
    bulk.execute({'w':0})
except pymongo.errors.BulkWriteError as bwe:
    pprint(bwe.details)

duration = time.time() - starttime
print "duratio:n", duration
