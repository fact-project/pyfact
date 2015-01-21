import numpy as np
import pymongo
import logging

def cursor_to_rec_array(cursor):
	array = cursor_to_structured_array(cursor)
    return array.view(np.recarray)	

def cursor_to_structured_array(cursor):
    N = cursor.count()
    if N > 1000:
        loggin.info("info: loading {} documents form database"
        			" .. might take a while".format(N))

    structured_array_dtype = make_numpy_dtype_from_cursor(cursor)
    array = np.zeros(N, structured_array_dtype)

    for counter, document in enumerate(cursor):
        for field_name in structured_array_dtype.names:
            array[field_name][counter] = document[field_name]

    return array

def make_numpy_dtype_from_cursor(cursor):

	collection_of_this_cursor = cursor.collection
	example_document = collection_of_this_cursor.find_one()
	if example_document is None:
		# collection is empty
		raise LookupError('associated collection of cursor is empty.')

	return make_numpy_dtype_from_document(example_document)

def make_numpy_dtype_from_document(doc):

    list_of_names_n_types = []
    for field_name in doc:
        if '_id' in field_name:
            continue
        element = example_doc[field_name]
        element_array = np.array(element)
        list_of_names_n_types.append(
            (str(field_name), element_array.dtype.str, element_array.shape)
        )

    return structured_array_dtype = np.dtype(list_of_names_n_types)    
    
