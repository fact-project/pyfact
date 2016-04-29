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
PROGRAM_OPTIONS = docopt(__doc__, version='Filler 1')
import os
import re
import pyfact
from glob import glob
import time
import pymongo
import settings
import fact


def get_mongo_db_collection_by_name(database, collection_name):
    """ creates collection if it does not yet exist.
        if it exists, it simply returns it.
    """
    return getattr(database, collection_name)


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
            print("Was not able to drop collection {}\n"
                  "Exception Details:\n"
                  "args:{ex.args} | details:{ex.details} "
                  "| message:{ex.message} | code:{ex.code}"
                  ).format(coll_name, ex=exeption)


class Filler(object):
    database_name = settings.database_name
    service_header_DB = "aux_meta"

    def __init__(self, aux_file, connection):
        self.aux_file = aux_file
        self.path = self.aux_file.path
        try:
            self.fits_file = pyfact.Fits(self.path)
        except TypeError:
            # some fits files are apparently broken, we don't
            # freak out about this, but report it nicely and go on.
            self.fits_file = None

        self._connection = connection
        self.aux = getattr(connection, self.database_name)
        self.aux_meta = getattr(self._connection, self.service_header_DB)

    def fill_in(self):
        """ main public method of a Filler
        it does the actual job of filling the data from the fits file into the DB
        """

        if not self.fits_file is None:
            starttime = time.time()
            self.__insert_service_description(self.aux_meta)
            self.__insert_fitsfile(self.aux)
            self.__make_time_index_for_service(self.aux)
            print self.__get_report(starttime)
        else:
            print "TypeError", self.path

    def __make_time_index_for_service(self, database):
        """ ensure that Time index exists

            This simply ensures, that for the collection associated with the dim service,
            which is stored inside the given file, there is indeed an index built for the 'Time' field.

            So in almost all cases, when this method is called nothing will happen, because the index is already there.

            This method only triggers an action on the DB side, when there is a new service being filled in,
            or when for some reason an index was dropped.
        """
        service_name = self.aux_file.service_name
        coll = get_mongo_db_collection_by_name(database, service_name)
        coll.ensure_index([("Time", 1)], unique=True, dropDups=True)

    def __bulk_insert_in_collection(self, collection):
        """ insert contents of fits_file into collection use bulk insert
        """
        bulk = collection.initialize_ordered_bulk_op()
        for _ in self.fits_file:
            doc = self.__create_mongo_doc()
            bulk.insert(doc)
        try:
            bulk.execute()
        except pymongo.errors.BulkWriteError as bwe:
            code = bwe.details['writeErrors'][0]['code']
            if not code == 11000:
                raise bwe

    # DERPECATED: nobody is using this one, because its so slow.
    def __slow_insert_in_collection(self, coll):
        """ insert contents of fits_file into collection, SLOW!
        """
        for _ in self.fits_file:
            doc = self.__create_mongo_doc()
            coll.insert(doc)

    def __create_mongo_doc(self):
        """ create a document suitable for mongo DB insertion from fits_file
        """
        doc = dict()
        for field_name in self.fits_file:
            cell_content = self.fits_file[field_name]

            # mongo document fields can contain lists, or scalars,
            # no numpy arrays!
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

    def __insert_fitsfile(self, database):
        """ insert data from fits file into the database
        """
        fits_start_time = (self.fits_file.header['TSTARTI']
                           + self.fits_file.header['TSTARTF'])
        fits_stop_time = (self.fits_file.header['TSTOPI']
                          + self.fits_file.header['TSTOPF'])
        collection = get_mongo_db_collection_by_name(database,
                                                     self.aux_file.service_name)

        start_found = False
        stop_found = False
        if not collection.find_one({"Time": fits_start_time}) is None:
            start_found = True
        if not collection.find_one({"Time": fits_stop_time}) is None:
            stop_found = True
        if start_found and stop_found:
            return

        self.__bulk_insert_in_collection(collection)

    def __insert_service_description(self, database):
        """ insert fits header information into database
        """
        service_name = self.aux_file.service_name
        coll = database.service_descriptions

        # only insert this, if it has never been inserted before
        if coll.find_one({'_id': service_name}) is not None:
            return

        # document should contain the header information from the fits file.
        header = self.fits_file.header
        comments = self.fits_file.header_comments
        doc = {}
        for k in header:
            if k in comments:
                doc[k] = [header[k], comments[k]]
            else:
                doc[k] = header[k]
        doc['_id'] = service_name
        coll.insert(doc)

    def __get_report(self, starttime):
        """ creates a textual report about the time
        """
        fits_file_path = self.path
        fits_file = pyfact.Fits(fits_file_path)
        report = ("{time_str} : {date.year}/{date.month}/{date.day}:"
                  " {svc_name:.<40} : {len:6d} : {dura:2.3f}".format(
                      date=self.aux_file.date,
                      svc_name=self.aux_file.service_name,
                      dura=time.time() - starttime,
                      len=fits_file.header["NAXIS2"],
                      time_str=time.strftime("%Y/%m/%d-%H:%M:%S")
                  ))

        return report


class AuxFile(object):
    """ can tell:
        it's servicename,
        its date and
        if it is_interesting at all.
    """
    cwd = os.path.dirname(os.path.realpath(__file__))
    whitelist = open(cwd + "/service_whitelist.txt").read().splitlines()

    def __init__(self, path):
        self.path = path

    @property
    def service_name(self):
        """Grab the service name from a fits_file_path

        path : should be a full file path

        service name is defines as any number of characters
        A-Z (or underscore _), which follows the 8-digit date
        any file extension like ".fits", ".fits.gz"
        even no file extension is permitted.
        """
        filename = os.path.split(self.path)[1]
        match = re.match(r"^\d{8}\.([A-Z_]+)", filename)
        return match.group(1)

    @property
    def date(self):
        """ return datetime.datetime object (UTC aware)
        """
        filename = os.path.split(self.path)[1]
        match = re.match(r"^(\d{8})\.([A-Z_]+)", filename)
        return fact.run2dt(match.group(1))

    @property
    def is_interesting(self):
        """ check if service_name of file is in whitelist
        """
        return self.service_name in self.whitelist


def interesting_files_under(base):
    """ generate list of .fits files below this basepath
    """
    search_path = os.path.join(base, '*/*/*/*.fits')
    all_paths = glob(search_path)

    sorted_paths = sorted(all_paths, reverse=True)

    for path in sorted_paths:
        aux_file = AuxFile(path)
        if aux_file.is_interesting:
            yield aux_file


def main(opts):
    """ main function of this filler
    """
    connection = pymongo.MongoClient(settings.host, settings.port)

    if opts['--delete_all']:
        aux = getattr(connection, settings.database_name)
        delete_all_collections_from(aux)

    for aux_file in interesting_files_under(opts['--base']):
        filler = Filler(aux_file, connection)
        filler.fill_in()

if __name__ == "__main__":
    main(PROGRAM_OPTIONS)
