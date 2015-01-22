"""Slow Data into Mongo DB Filler.

Usage:
  fill_in.py [--help]
  fill_in.py [--delete_all] [options]

Options:
  -h --help          Show this screen.
  --delete_all       delete all collections prior to filling [default: False].
  --base PATH        base path to slow files (e.g. /fact/aux) [default: /data/fact_aux]

"""
from docopt import docopt
program_options = docopt(__doc__, version='Filler 1')
import os
import pyfact
from glob import glob
import time
import pymongo
from pprint import pprint
import settings
import unittest

class MyDate(object):
    def __init__(self, y, m, d):
        self.y = y
        self.m = m
        self.d = d


def date_from_path(p):
    yyyy = int(p[15:19])
    mm = int(p[20:22])
    dd = int(p[23:25])
    return MyDate(yyyy, mm, dd)


def get_mongo_db_collection_by_name(db, name):
    """ creates collection if it does not yet exist.
        if it exists, it simply returns it.
    """
    c = getattr(db, name)
    return c


def list_of_services_of_interest():
    aux_files_of_interest = """
        AGILENT_CONTROL_24V_DATA
        AGILENT_CONTROL_50V_DATA
        AGILENT_CONTROL_80V_DATA
        BIAS_CONTROL_CURRENT
        BIAS_CONTROL_DAC
        BIAS_CONTROL_STATE
        BIAS_CONTROL_VOLTAGE
        DRIVE_CONTROL_POINTING_POSITION
        DRIVE_CONTROL_SOURCE_POSITION
        DRIVE_CONTROL_STATE
        DRIVE_CONTROL_STATUS
        DRIVE_CONTROL_TRACKING_POSITION
        FAD_CONTROL_CONNECTIONS
        FAD_CONTROL_DAC
        FAD_CONTROL_DNA
        FAD_CONTROL_DRS_RUNS
        FAD_CONTROL_EVENTS
        FAD_CONTROL_FILE_FORMAT
        FAD_CONTROL_FIRMWARE_VERSION
        FAD_CONTROL_INCOMPLETE
        FAD_CONTROL_PRESCALER
        FAD_CONTROL_REFERENCE_CLOCK
        FAD_CONTROL_REGION_OF_INTEREST
        FAD_CONTROL_RUN_NUMBER
        FAD_CONTROL_RUNS
        FAD_CONTROL_START_RUN
        FAD_CONTROL_STATE
        FAD_CONTROL_STATISTICS1
        FAD_CONTROL_STATS
        FAD_CONTROL_STATUS
        FAD_CONTROL_TEMPERATURE
        FAD_CONTROL_TRIGGER_COUNTER
        FEEDBACK_CALIBRATED_CURRENTS
        FEEDBACK_CALIBRATION
        FEEDBACK_CALIBRATION_R8
        FEEDBACK_CALIBRATION_STEPS
        FEEDBACK_STATE
        FSC_CONTROL_BIAS_TEMP
        FSC_CONTROL_CURRENT
        FSC_CONTROL_HUMIDITY
        FSC_CONTROL_TEMPERATURE
        FSC_CONTROL_VOLTAGE
        FTM_CONTROL_COUNTER
        FTM_CONTROL_DYNAMIC_DATA
        FTM_CONTROL_FTU_LIST
        FTM_CONTROL_STATE
        FTM_CONTROL_STATIC_DATA
        FTM_CONTROL_TRIGGER_RATES
        GPS_CONTROL_NEMA
        LID_CONTROL_DATA
        LID_CONTROL_STATE
        MAGIC_WEATHER_DATA
        MAGIC_WEATHER_STATE
        MCP_CONFIGURATION
        MCP_STATE
        PWR_CONTROL_DATA
        PWR_CONTROL_STATE
        RATE_CONTROL_STATE
        RATE_CONTROL_THRESHOLD
        RATE_SCAN_DATA
        RATE_SCAN_PROCESS_DATA
        RATE_SCAN_STATE
        SQM_CONTROL_DATA
        TEMPERATURE_DATA
        TIME_CHECK_OFFSET
        TNG_WEATHER_DATA
        TNG_WEATHER_DUST
        TNG_WEATHER_STATE
    """
    service_names_of_interest = aux_files_of_interest.split()
    return service_names_of_interest


def try_to_delete_all_collections_from(database):
    for coll_name in database.collection_names():
        if 'system.indexes' in coll_name:
            continue
        coll = get_mongo_db_collection_by_name(database, coll_name)


def service_name_from_path(p):
    filename = os.path.split(p)[1]
    service_name = filename[9:-5]
    return service_name


def build_mongo_document_from_current_fits_file_row(fits_file):
    doc = dict()
    for col_name in fits_file.cols:
        cell_content = fits_file.cols[col_name]

        # mongo document fields can contain lists, or scalars, no numpy arrays!
        # fits files only contain 1D numpy arrays (sometimes with only 1 element)
        # so here I convert them to lists, and in the 1 element case, to scalars.
        if len(cell_content) > 1:
            doc[col_name] = cell_content.tolist()
        elif len(cell_content) == 1:
            doc[col_name] = float(cell_content[0])
        elif len(cell_content) == 0:
            # pass if we find an empty numpy array, we ignore it.
            pass
        else:
            # negative length can't happen, so
            pass

    return doc


def make_time_index_for_service(fits_file, db):
    """ This simply ensures, that for the collection associated with the dim service,
        which is stored inside the given file, there is indeed an index built for the 'Time' field.

        So in almost all cases, when this method is called nothing will happen, because the index is already there.

        This method only triggers an action on the DB side, when there is a new service being filled in,
        or when for some reason an index was dropped.
    """
    fits_file_path = fits_file._path
    coll = get_mongo_db_collection_by_name(db, service_name_from_path(fits_file_path))
    coll.ensure_index([("Time", 1)], unique=True, dropDups=True)


def bulk_insert_fits_file_to_collection(fits_file, coll):
    bulk = coll.initialize_ordered_bulk_op()
    for row in fits_file:
        doc = build_mongo_document_from_current_fits_file_row(fits_file)
        bulk.insert(doc)
    try:
        bulk.execute()
    except pymongo.errors.BulkWriteError as bwe:
        code = bwe.details['writeErrors'][0]['code']
        if not code == 11000:
            raise bwe
        #pprint(bwe.details)


def insert_fits_file_to_collection(fits_file, coll):
    for row in fits_file:
        doc = build_mongo_document_from_current_fits_file_row(fits_file)
        coll.insert(doc)


def insert_service_from_fitsfile_into_db(fits_file, db):
    fits_file_path = fits_file._path

    fits_start_time = fits_file.header['TSTARTI']+fits_file.header['TSTARTF']
    fits_stop_time = fits_file.header['TSTOPI']+fits_file.header['TSTOPF']
    coll = get_mongo_db_collection_by_name(db, service_name_from_path(fits_file_path))
    start_found = False
    stop_found = False
    if not coll.find_one({"Time" : fits_start_time}) is None:
        #print "    -> fits_start_time:{0} found".format(fits_start_time)
        start_found = True
    if not coll.find_one({"Time" : fits_stop_time})  is None:
        #print "    -> fits_stop_time:{0} found".format(fits_stop_time)
        stop_found = True
    if start_found and stop_found:
        return
    bulk_insert_fits_file_to_collection(fits_file, coll)
    #insert_fits_file_to_collection(fits_file, coll)


def get_report(fits_file, starttime):
    fits_file_path = fits_file._path
    report = "{time_str} : {d.y}/{d.m}/{d.d}: {svc_name:.<40} : {len:6d} : {dura:2.3f}".format(
        d=date_from_path(fits_file_path),
        svc_name=service_name_from_path(fits_file_path),
        dura=time.time() - starttime,
        len=fits_file.header["NAXIS2"],
        time_str=time.strftime("%Y/%m/%d-%H:%M:%S")
        )

    return report


def is_interesting_for_slow_database(path_):
    service_name = service_name_from_path(path_)
    service_names_of_interest = list_of_services_of_interest()
    if service_name in service_names_of_interest:
        return True

def list_of_paths(base):

    search_path = os.path.join(base, '*/*/*/*.fits')
    all_paths = glob(search_path)
    
    sorted_paths = sorted(all_paths, reverse=True)
    
    for path_ in sorted_paths:
        date = date_from_path(path_)
        yield path_


def insert_service_description_from_fitsfile_into_db(fits_file, db):
    fits_file_path = fits_file._path
    service_name = service_name_from_path(fits_file_path)
    coll = db.service_descriptions

    # only insert this, if it has never been inserted before
    if coll.find({'_id':service_name}).count():
        return

    # document should contain the header information from the fits file.
    header = fits_file.header
    comments = fits_file.header_comments
    doc = {}
    for k in header:
        if k in comments:
            doc[k] = [header[k], comments[k]]
        else:
            doc[k] = header[k]
    doc['_id'] = service_name
    coll.insert(doc)


def main(opts):
    connection = pymongo.MongoClient(settings.host, settings.port)
    db = getattr(connection, settings.database_name)
    aux_meta = getattr(connection, 'aux_meta')

    if opts['--delete_all']:
        try_to_delete_all_collections_from(db)

    for path in list_of_paths(opts['--base']):
        if is_interesting_for_slow_database(path):
            starttime = time.time()
            try:
                fits_file = pyfact.Fits(path)
                insert_service_description_from_fitsfile_into_db(fits_file, aux_meta)
                insert_service_from_fitsfile_into_db(fits_file, db)
                make_time_index_for_service(fits_file, db)
                print get_report(fits_file, starttime)
            except TypeError as e:
                print "TypeError", path, e
        #TODO:
        # Store also the **header** of the fits file to the mongo DB, so the **types** of
        # the data in the databse.
        # The header information **should** be identical for all instances of a certain service
        # so only one header per service is needed.
        # but one can never be sure. So

class Sometests(unittest.TestCase):

    def test_something():
        pass

if __name__ == "__main__":
    main(program_options)
