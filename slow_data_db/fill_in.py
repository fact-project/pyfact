"""Slow Data into Mongo DB Filler.

Usage:
  fill_in.py [--help]
  fill_in.py [--delete_all] [options]

Options:
  -h --help          Show this screen.
  --delete_all       delete all collections prior to filling [default: False].
  --base PATH        base path to slow files [default: /data/fact_aux]

"""
from docopt import docopt
program_options = docopt(__doc__, version='Filler 1')
import os
import pyfact
from glob import glob
import time
import pymongo
import settings


class MyDate(object):
    """ very bad designed Date class

    TODO:
    exchange the use of this class everywhere in the code agains
    the use of date.dateime or time-tuple
    """
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
    def __str__(self):
        return str(self.year, self.month, self.day)


def date_from_path(path):
    """ return MyDate object generated from a pathname, very wrongly implemented
    TODO:
    the path should be taken apart correctly and then the 
    filename should be parsed into a datetime.datetime object or a time-tuple
    """
    year = int(path[15:19])
    month = int(path[20:22])
    day = int(path[23:25])
    return MyDate(year, month, day)


def get_mongo_db_collection_by_name(database, collection_name):
    """ creates collection if it does not yet exist.
        if it exists, it simply returns it.
    """
    return getattr(database, collection_name)


def list_of_services_of_interest():
    """ return a list of service names, which are of interest for us
    """
    return ['AGILENT_CONTROL_24V_DATA',
     'AGILENT_CONTROL_50V_DATA',
     'AGILENT_CONTROL_80V_DATA',
     'BIAS_CONTROL_CURRENT',
     'BIAS_CONTROL_DAC',
     'BIAS_CONTROL_STATE',
     'BIAS_CONTROL_VOLTAGE',
     'DRIVE_CONTROL_POINTING_POSITION',
     'DRIVE_CONTROL_SOURCE_POSITION',
     'DRIVE_CONTROL_STATE',
     'DRIVE_CONTROL_STATUS',
     'DRIVE_CONTROL_TRACKING_POSITION',
     'FAD_CONTROL_CONNECTIONS',
     'FAD_CONTROL_DAC',
     'FAD_CONTROL_DNA',
     'FAD_CONTROL_DRS_RUNS',
     'FAD_CONTROL_EVENTS',
     'FAD_CONTROL_FILE_FORMAT',
     'FAD_CONTROL_FIRMWARE_VERSION',
     'FAD_CONTROL_INCOMPLETE',
     'FAD_CONTROL_PRESCALER',
     'FAD_CONTROL_REFERENCE_CLOCK',
     'FAD_CONTROL_REGION_OF_INTEREST',
     'FAD_CONTROL_RUNS',
     'FAD_CONTROL_RUN_NUMBER',
     'FAD_CONTROL_START_RUN',
     'FAD_CONTROL_STATE',
     'FAD_CONTROL_STATISTICS1',
     'FAD_CONTROL_STATS',
     'FAD_CONTROL_STATUS',
     'FAD_CONTROL_TEMPERATURE',
     'FAD_CONTROL_TRIGGER_COUNTER',
     'FEEDBACK_CALIBRATED_CURRENTS',
     'FEEDBACK_CALIBRATION',
     'FEEDBACK_CALIBRATION_R8',
     'FEEDBACK_CALIBRATION_STEPS',
     'FEEDBACK_STATE',
     'FSC_CONTROL_BIAS_TEMP',
     'FSC_CONTROL_CURRENT',
     'FSC_CONTROL_HUMIDITY',
     'FSC_CONTROL_TEMPERATURE',
     'FSC_CONTROL_VOLTAGE',
     'FTM_CONTROL_COUNTER',
     'FTM_CONTROL_DYNAMIC_DATA',
     'FTM_CONTROL_FTU_LIST',
     'FTM_CONTROL_STATE',
     'FTM_CONTROL_STATIC_DATA',
     'FTM_CONTROL_TRIGGER_RATES',
     'GPS_CONTROL_NEMA',
     'LID_CONTROL_DATA',
     'LID_CONTROL_STATE',
     'MAGIC_WEATHER_DATA',
     'MAGIC_WEATHER_STATE',
     'MCP_CONFIGURATION',
     'MCP_STATE',
     'PWR_CONTROL_DATA',
     'PWR_CONTROL_STATE',
     'RATE_CONTROL_STATE',
     'RATE_CONTROL_THRESHOLD',
     'RATE_SCAN_DATA',
     'RATE_SCAN_PROCESS_DATA',
     'RATE_SCAN_STATE',
     'SQM_CONTROL_DATA',
     'TEMPERATURE_DATA',
     'TIME_CHECK_OFFSET',
     'TNG_WEATHER_DATA',
     'TNG_WEATHER_DUST',
     'TNG_WEATHER_STATE']


def delete_all_collections_from(database, omit=('system.indexes')):
    """ delete all collections from a database

        if name of collection is in omit (default:['system.indexes']), 
        then this collection is not deleted.
    """
    for coll_name in database.collection_names():
        if coll_name in omit:
            continue

        coll = get_mongo_db_collection_by_name(database, coll_name)
        try:
            coll.drop()
        except pymongo.errors.OperationFailure as exeption:
            print ("Was not able to drop collection {}\n"
                    "Exception Details:\n"
                    "args:{ex.args} | details:{ex.details} "
                    "| message:{ex.message} | code:{ex.code}"
                  ).format(coll_name, ex=exeption)
            

def service_name_from_path(path):
    """Grab the service name from a fits_file_path

    path : should be a full file path
    the path is split and then the filename is taken from it by taking characters [9:-5]
    this is a vety bad way to implement this!
    TODO: improve... what if the filename does not look like this: 
        yyyymmdd.SERVICE_NAME.fits, 
    but there is a fits.gz or fits.fz ending?? hu?
    """
    filename = os.path.split(path)[1]
    return filename[9:-5]


def create_mongo_doc(fits_row):
    """ create a document suitable for mongo DB insertion from a fits_file row
    """
    doc = dict()
    for field_name in fits_row:
        cell_content = fits_row[field_name]

        # mongo document fields can contain lists, or scalars, no numpy arrays!
        # fits files only contain 1D numpy arrays 
        # (sometimes with only 1 element)
        # so here I convert them to lists, 
        # and in the 1 element case, to scalars.
        if len(cell_content) > 1:
            doc[field_name] = cell_content.tolist()
        elif len(cell_content) == 1:
            doc[field_name] = float(cell_content[0])
        elif len(cell_content) == 0:
            # pass if we find an empty numpy array, we ignore it.
            pass
        else:
            # negative length can't happen, so
            pass

    return doc


def make_time_index_for_service(fits_file, database):
    """ ensure that Time index exists 

        This simply ensures, that for the collection associated with the dim service,
        which is stored inside the given file, there is indeed an index built for the 'Time' field.

        So in almost all cases, when this method is called nothing will happen, because the index is already there.

        This method only triggers an action on the DB side, when there is a new service being filled in,
        or when for some reason an index was dropped.
    """
    coll = get_mongo_db_collection_by_name(database, 
                                service_name_from_path(fits_file._path))
    coll.ensure_index([("Time", 1)], unique=True, dropDups=True)


def bulk_insert_fits_file(fits_file, collection):
    """ insert contents of fits_file into collection use bulk insert
    """
    bulk = collection.initialize_ordered_bulk_op()
    for row in fits_file:
        doc = create_mongo_doc(row)
        bulk.insert(doc)
    try:
        bulk.execute()
    except pymongo.errors.BulkWriteError as bwe:
        code = bwe.details['writeErrors'][0]['code']
        if not code == 11000:
            raise bwe


def insert_fits_file(fits_file, coll):
    """ insert contents of fits_file into collection, SLOW!
    """
    for row in fits_file:
        doc = create_mongo_doc(row)
        coll.insert(doc)


def insert_fitsfile(fits_file, database):
    """ insert data from fits file into the database
    """
    fits_start_time = fits_file.header['TSTARTI']+fits_file.header['TSTARTF']
    fits_stop_time = fits_file.header['TSTOPI']+fits_file.header['TSTOPF']
    collection = get_mongo_db_collection_by_name(database, 
        service_name_from_path(fits_file._path))

    start_found = False
    stop_found = False
    if not collection.find_one({"Time" : fits_start_time}) is None:
        start_found = True
    if not collection.find_one({"Time" : fits_stop_time})  is None:
        stop_found = True
    if start_found and stop_found:
        return

    bulk_insert_fits_file(fits_file, collection)


def get_report(fits_file, starttime):
    """ creates a textual report about the time
    """
    fits_file_path = fits_file._path
    fits_file = pyfact.Fits(fits_file_path)
    report = ("{time_str} : {d.y}/{d.m}/{d.d}:"
              " {svc_name:.<40} : {len:6d} : {dura:2.3f}".format(
        d=date_from_path(fits_file_path),
        svc_name=service_name_from_path(fits_file_path),
        dura=time.time() - starttime,
        len=fits_file.header["NAXIS2"],
        time_str=time.strftime("%Y/%m/%d-%H:%M:%S")
        ))

    return report


def is_file_intersting(path_):
    """ check if service in file is interesting
    """
    service_name = service_name_from_path(path_)
    service_names_of_interest = list_of_services_of_interest()
    if service_name in service_names_of_interest:
        return True

def list_of_paths(base):
    """ generate list of .fits files below this basepath
    """
    search_path = os.path.join(base, '*/*/*/*.fits')
    all_paths = glob(search_path)
    
    sorted_paths = sorted(all_paths, reverse=True)
    
    for path_ in sorted_paths:
        date = date_from_path(path_)
        if date.year < 2012:
            raise StopIteration()
        yield path_


def insert_service_description(fits_file, database):
    """ insert fits header information into database
    """
    fits_file_path = fits_file._path
    service_name = service_name_from_path(fits_file_path)
    coll = database.service_descriptions

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
    """ main function of this filler
    """
    connection = pymongo.MongoClient(settings.host, settings.port)
    database = getattr(connection, settings.database_name)
    aux_meta = getattr(connection, 'aux_meta')

    if opts['--delete_all']:
        delete_all_collections_from(database)

    for path in list_of_paths(opts['--base']):
        if is_file_intersting(path):
            starttime = time.time()
            try:
                fits_file = pyfact.Fits(path)
                insert_service_description(fits_file, aux_meta)
                insert_fitsfile(fits_file, database)
                make_time_index_for_service(fits_file, database)
                print get_report(fits_file, starttime)
            except TypeError as exception:
                print "TypeError", path, exception

if __name__ == "__main__":
    main(program_options)
