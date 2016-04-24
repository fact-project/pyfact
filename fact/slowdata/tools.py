""" library of (hopefully) useful functions for the slow data DB interface
"""
import numpy as np
import pymongo


def cursor_to_rec_array(cursor):
    """ convert a pymongo.cursor.Cursor to an numpz recarray
    """
    array = cursor_to_structured_array(cursor)
    return array.view(np.recarray)


def cursor_to_structured_array(cursor):
    """ convert a pymongo.cursor.Cursor to an numpy structured array
    """
    number_of_docs = cursor.count()
    # if number_of_docs > 1000:
    #    logging.warning("loading {} documents form database"
    #                 " .. might take a while".format(number_of_docs))

    structured_array_dtype = make_numpy_dtype_from_cursor(cursor)
    array = np.zeros(number_of_docs, structured_array_dtype)

    for counter, document in enumerate(cursor):
        for field_name in structured_array_dtype.names:
            try:
                array[field_name][counter] = document[field_name]
            except KeyError:
                array[field_name][counter] = np.nan

    return array


def make_numpy_dtype_from_cursor(cursor):
    """ infer datatype of structured array from document(s) from a cursor
    """
    collection_of_this_cursor = cursor.collection
    # get the newest entry from this collection
    # this one defines the dtype of the numpy array,
    # and we want to stick to the newest format.
    example_document = collection_of_this_cursor.find_one(
        {},
        sort=[("Time", pymongo.DESCENDING)]
    )
    example_document = cursor[0]

    if example_document is None:
        # collection is empty
        raise LookupError('associated collection of cursor is empty.')

    return make_numpy_dtype_from_document(example_document)


def make_numpy_dtype_from_document(doc):
    """ infer datatype of structured array from document
    """
    list_of_names_n_types = []
    for field_name in doc:
        if '_id' in field_name:
            continue
        element = doc[field_name]
        element_array = np.array(element)
        list_of_names_n_types.append(
            (str(field_name),
             element_array.dtype.str,
             element_array.shape)
        )

    return np.dtype(list_of_names_n_types)
