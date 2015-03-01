#define DIMC_MODULE
#include <cctype>
#include <cstdlib>
#include <cstdio>
#include <map>
#include <string>

#ifndef _WIN32
#include <unistd.h>
#include <pthread.h>
#else
#define HOST_NAME_MAX 256
#include <winsock.h>
#endif

extern "C" {
#include <Python.h>
#include "dic.h"
#include "dis.h"
#include "dim_common.h"
}
#include "pydim_utils.cpp"

using namespace std;
static char server_name[HOST_NAME_MAX + 1];
typedef void* func(int*);

/******************************************************************************/
/* DIS containers for callbacks*/
/******************************************************************************/

typedef struct {
  char *name;
  char *format;
  PyObject *pyTag;
  PyObject *pyFunc;
} CmndCallback;
typedef CmndCallback* CmndCallbackPtr;

map<string, CmndCallbackPtr> cmndName2PythonFunc;
map<long, CmndCallbackPtr> cmndUniqueTag2PythonFunc;

typedef struct {
  char *name;
  char *format;
  char *buffer;
  unsigned int bufferSize;
  bool isUpdated;
  bool firstCall;
  long pyTag;
  PyObject *pyFunc;
} ServiceCallback;

typedef ServiceCallback *ServiceCallbackPtr;
map<unsigned int, ServiceCallbackPtr> serviceID2Callback;

static void dim_callbackCommandFunc(void*, void*, int*);

/******************************************************************************/
/* DIC containers for callbacks and function prototypes                       */
/******************************************************************************/
struct _dic_info_service_callback{
  PyObject* pyFunc;
  char* name;
  char* format;
  PyObject* pyDefaultArg;
  long pyTag;
  int service_id;
};

struct _dic_cmnd_callback {
  PyObject* pyFunc;
  long pyTag;
};

unsigned long _dic_cmnd_callback_ID;


static map<string,_dic_info_service_callback*>_dic_info_service_name2Callback;
static map<unsigned int, _dic_info_service_callback*>_dic_info_service_id2Callback;
static map<long, _dic_cmnd_callback*> _dic_cmnd_callback_tag2Callback;

void _dic_error_user_routine_dummy(int, int, char*);
void _dic_info_service_dummy (void*, void*, int*);
void _dic_cmnd_callback_dummy(void*, int*);
void _dic_error_user_routine_dummy(int, int, char*);

/******************************************************************************/


/** \defgroup dim DIM interface functions
 * @{
 */

static PyObject*
dim_dis_start_serving (PyObject* /* self */, PyObject *args)  {
  /** Calls dis_start_serving.
   * @param server_name The name under which the server is going to be
   * registered in the DIM DNS. If not specified the hostname is used.
   */
  char *name = NULL;
  int ret;

  if (!PyArg_ParseTuple(args, "|s", &name)) {
    PyErr_SetString(PyExc_RuntimeError, "Invalid server name.");
    return NULL;
  }
  if (name)
    strncpy(server_name, name, HOST_NAME_MAX + 1);
  else {
    gethostname(server_name, HOST_NAME_MAX);
    debug("No server name specified. Using machine hostname...\n");
  }
  Py_BEGIN_ALLOW_THREADS	
  ret = dis_start_serving(server_name);
  Py_END_ALLOW_THREADS

  return Py_BuildValue("i", ret);
}

static PyObject*
dim_dis_stop_serving(PyObject* /* self */, PyObject* /* args */) {
  /** Calls void dis_stop_serving(void)
  */
  Py_BEGIN_ALLOW_THREADS	
  dis_stop_serving();
  Py_END_ALLOW_THREADS
  Py_RETURN_NONE;
}


static PyObject*
dim_dis_set_dns_node(PyObject* /* self */, PyObject* args) {
  /**
   * Calls dis_set_dns_node(char* node)
   *
   * @param dns_node_name The name of the DNS server
   * @return DIM return code (1 for success)
   */
  char* name = NULL;
  int ret;

  if ( !PyArg_ParseTuple(args, "s", &name) ) {
    PyErr_SetString(PyExc_RuntimeError, "Invalid DNS name");
    return NULL;
  }
  ret = dis_set_dns_node(name);

  return Py_BuildValue("i", ret);
}


static PyObject*
dim_dis_get_dns_node(PyObject* /* self */, PyObject* /* args */) {
  /* calls dis_get_dns_node(char* node)
     the function should return the DNS node
     */
  char names[256];
  if ( !dis_get_dns_node(names) ) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to get DNS node name");
    return NULL;
  }
  return Py_BuildValue("s", names);
}


static PyObject*
dim_dis_set_dns_port(PyObject* /* self */, PyObject* args) {
  /**
   * Calls dis_set_dns_port(int port).
   *
   * @param dim_dns_port (unsigned integer)
   * @return DIM return code (1 for success)
   */
  unsigned int port;
  int ret;

  if (!PyArg_ParseTuple(args, "I", &port)) {
    PyErr_SetString(PyExc_TypeError,
        "Argument 'port' must be a pozitive integer");
    return NULL;
  }
  ret = dis_set_dns_port(port);

  return Py_BuildValue("i", ret);
}

static PyObject*
dim_dis_get_dns_port(PyObject* /* self */, PyObject* /* args */) {
  /**
   * Calls dis_get_dns_port().
   * @return port The DIM DNS port.
   */
  int port;
  port = dis_get_dns_port();
  return Py_BuildValue("i", port);
}


typedef struct {
  PyObject* self;
  PyObject* func;
} PyCallback; //for Python callbacks

static PyCallback dis_callbackExitHandler_func,
                  dis_callbackErrorHandler_func,
                  dis_callbackClientExitHandler_func;

static PyCallback _dic_callback_errorHandler_func;

static void
dim_dis_callbackExitHandler(int* code) {
  /**
   * NOTE: this function does not have the interpretor lock when called.
   * @param code The exit code passed by the DIM library.
   */
  PyObject *arg, *res;
  PyGILState_STATE gstate;

  if ( dis_callbackExitHandler_func.func ) {
    gstate = PyGILState_Ensure();
    arg = Py_BuildValue("i", *code);
    res = PyEval_CallObject(dis_callbackExitHandler_func.func, arg);
    Py_DECREF(arg);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
  } else {
    debug("Could not find any registered Python function. "\
        "Dropping DIM exit callback.");
  }
}


static void
dim_dis_callbackErrorHandler(int severity, int error_code, char* message) {
  /**
   * NOTE: this function does not have the interpretor lock when called.
   * @param code The error code passed by the DIM library.
   */
  PyObject *arg, *res;
  PyGILState_STATE gstate;

  if (dis_callbackErrorHandler_func.func) {
    gstate = PyGILState_Ensure();
    arg = Py_BuildValue("iis", severity, error_code, message);
    res = PyEval_CallObject(dis_callbackErrorHandler_func.func, arg);
    Py_DECREF(arg);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
  } else {
    debug("Could not find any registered Python function. "\
        "Dropping DIM error callback.");
  }
}


static void
dim_dis_callbackClientExitHandler(int* tag) {
  /*Interface function with signature: void client_exit_user_routine (int* tag)
    Calls the associated Python function.
    */
  PyObject *arg, *res;
  PyGILState_STATE gstate;

  if (dis_callbackClientExitHandler_func.func) {
    gstate = PyGILState_Ensure();
    arg = Py_BuildValue("i", *tag);
    res = PyEval_CallObject(dis_callbackClientExitHandler_func.func, arg);
    Py_DECREF(arg);
    Py_XDECREF(res);
    PyGILState_Release(gstate);
  } else {
    debug("Could not find any registered Python function. "\
        "Dropping DIM client exit callback.");
  }
}


static PyObject*
dim_dis_add_exit_handler(PyObject* self, PyObject* args) {
  /**
   * Calls dis_add_exit_handler
   * @param callback A callable Python object.
   */
  PyObject *temp;

  if (!PyArg_ParseTuple(args, "O:set_callback", &temp) ||
      !PyCallable_Check(temp))
  {
    PyErr_SetString(PyExc_TypeError, "Expected a callable Python object");
    return NULL;
  }

  Py_XINCREF(temp);
  Py_XINCREF(self);
  /* Dispose of previous callback */
  Py_XDECREF(dis_callbackExitHandler_func.self);
  Py_XDECREF(dis_callbackExitHandler_func.func);
  dis_callbackExitHandler_func.self = self;
  dis_callbackExitHandler_func.func = temp;
  dis_add_exit_handler(dim_dis_callbackExitHandler);

  Py_RETURN_NONE;
}


static PyObject*
dim_dis_add_error_handler(PyObject* self, PyObject* args) {
  /**
   * Calls dis_add_error_handler
   * @param callback A callable Python object.
   */
  PyObject *temp;

  if (!PyArg_ParseTuple(args, "O:set_callback", &temp) ||
      !PyCallable_Check(temp))
  {
    PyErr_SetString(PyExc_TypeError, "Expected a callable Python object");
    return NULL;
  }
  /* Add a reference to new callback */
  Py_XINCREF(temp);
  Py_XINCREF(self);
  /* Dispose of previous callback */
  Py_XDECREF(dis_callbackErrorHandler_func.self);
  Py_XDECREF(dis_callbackErrorHandler_func.func);
  dis_callbackErrorHandler_func.self = self;
  dis_callbackErrorHandler_func.func = temp;
  dis_add_error_handler(dim_dis_callbackErrorHandler);

  Py_RETURN_NONE;
}

static PyObject*
dim_dis_add_client_exit_handler(PyObject* self, PyObject* args) {
  /**
   * Calls dis_add_client_exit_handler
   * @param callback A callable Python object.
   */
  PyObject *temp;

  if (!PyArg_ParseTuple(args, "O:set_callback", &temp) ||
      !PyCallable_Check(temp))
  {
    PyErr_SetString(PyExc_TypeError, "Expected a callable Python object");
    return NULL;
  }
  /* Add a reference to new callback */
  Py_XINCREF(temp);
  Py_XINCREF(self);
  /* Dispose of previous callback */
  Py_XDECREF(dis_callbackClientExitHandler_func.self);
  Py_XDECREF(dis_callbackClientExitHandler_func.func);
  dis_callbackClientExitHandler_func.self = self;
  dis_callbackClientExitHandler_func.func = temp;
  dis_add_client_exit_handler(dim_dis_callbackClientExitHandler);

  Py_RETURN_NONE;
}


static PyObject*
dim_dis_selective_update_service(PyObject* /* self */, PyObject* args) {
  /**
   *  Calls int dis_selective_update_service (int service_id, int** client_ids)
   */
  int* client_ids=NULL, res;
  PyObject* listOrTuple;
  int service_id;

  if (!PyArg_ParseTuple(args, "iO;list or tuple", &service_id, &listOrTuple)) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid arguments: expected and integer and a list/tuple of integers");
    return NULL;
  }
  if (!listOrTuple2Int(listOrTuple, &client_ids)) {
    PyErr_SetString(PyExc_TypeError,
        "Second argument must a list/tuple of integers"
        );
    return NULL;
  }
  res = dis_selective_update_service(service_id, client_ids);

  return Py_BuildValue("i", res);
}


static PyObject*
dim_dis_set_quality(PyObject* /* self */, PyObject* args) {
  /**
   * Calls void dis_set_quality (service_id, quality)
   * @param service_id The service ID returned by dis_add_service().
   * @param quality A flag for the quality of a service.
   */
  unsigned int service_id;
  int quality;

  if (!PyArg_ParseTuple(args, "Ii", &service_id, &quality)) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid arguments: expected an unsigned integer and an integer");
    return NULL;
  }
  dis_set_quality(service_id, quality);

  Py_RETURN_NONE;
}


static PyObject*
dim_dis_set_timestamp(PyObject* /* self */, PyObject* args) {
  /**
   * Calls void dis_set_timestamp(unsigned int service_id,
   *                              int secs,
   *                              int milisecs)
   * @param service_id
   * @param secs
   * @param milisecs
   */
  unsigned int service_id;
  int secs, milisecs;

  if (!PyArg_ParseTuple(args, "Iii", &service_id, &secs, &milisecs)) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid arguments: expected an unsigned integer and two integers");
    return NULL;
  }
  dis_set_timestamp(service_id, secs, milisecs);

  Py_RETURN_NONE;
}


static PyObject*
dim_dis_remove_service(PyObject* /* self */, PyObject* args) {
  /**
   * Call int dis_remove_service (unsigned int service_id)
   * @param service_id
   */
  unsigned int service_id;
  int res;

  if ( !PyArg_ParseTuple(args, "I", &service_id) ) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid argument: expected an unsigned integer");
    return NULL;
  }
  res = dis_remove_service(service_id);

  return Py_BuildValue("i", res);
}


static PyObject*
dim_dis_get_next_cmnd(PyObject* /* self */, PyObject* args) {
  /**
   * Calls int dis_get_next_cmnd (long* tag, int* buffer, int* size)
   *
   * TODO: Make sure this actually works
   * Problem: the way the results are received is not done in a "pythonic" way.
   * Better to return a tuple with all the results.
   *
   * INFO: the DIM function implementation does not define a value for buffer,
   * size or tag in case a command is not found.
   *
   * @param size The maximum size of the data received by the command
   */
  int res=0, *buffer, size;
  long tag=0;
  PyObject* tmp;

  if ( !PyArg_ParseTuple(args, "I", &size) ) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid argument: expected an unsigned integer");
    return NULL;
  }
  buffer = (int*)malloc(size*sizeof(int));
  res = dis_get_next_cmnd(&tag, buffer, &size);
  tmp = Py_BuildValue("(iis#)", res, tag, buffer, size);
  free(buffer);

  return tmp;
}


static PyObject*
dim_dis_get_client(PyObject* /* self */, PyObject* args) {
  /**
   * Calls: int dis_get_client (char* name)
   */
  char* name; int res;

  if ( !PyArg_ParseTuple(args, "s", &name) ) {
    PyErr_SetString(PyExc_TypeError, "Invalid argument: expected an string");
    return NULL;
  }
  res = dis_get_client(name);

  return Py_BuildValue("i", res);
}


static PyObject*
dim_dis_get_conn_id(PyObject* /* self */, PyObject* /* args */) {
  /**
   * Calls: int dis_get_conn_id()
   */
  int res;
  res = dis_get_conn_id();
  return Py_BuildValue("i", res);
}


static PyObject*
dim_dis_get_timeout(PyObject* /* self */, PyObject* args) {
  /**
   * Calls: int dis_get_timeout (unsigned int service_id, int client_id)
   * @param service_id The service_id returned by dis_add_service or by
   * dis_add_cmnd.
   * @param client_id The connection ID of a DIM client as obtained by
   * the routine dis_get_conn_id.
   */
  unsigned int service_id;
  int client_id, res;

  if ( !PyArg_ParseTuple(args, "Ii", &service_id, &client_id) ) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid argument: expected an unsigned int and an int");
    return NULL;
  }
  res = dis_get_timeout(service_id, client_id);

  return Py_BuildValue("i", res);
}


static PyObject*
dim_dis_get_client_services(PyObject* /* self */, PyObject* args) {
  /**
   * Calls: char* dis_get_client_services (int conn_id)
   *
   * @param conn_id The connection ID to a client.
   */
  char* res=NULL;
  int conn_id;

  if ( !PyArg_ParseTuple(args, "i", &conn_id) ) {
    PyErr_SetString(PyExc_TypeError, "Invalid argument: expected an int");
    return NULL;
  }
  res = dis_get_client_services(conn_id);

  return Py_BuildValue("s", res);
}


static PyObject*
dim_dis_set_client_exit_handler(PyObject* /* self */, PyObject* args) {
  /**
   * Calls: void dis_set_client_exit_handler (int conn_id, int tag)
   */
  int conn_id, tag;

  if ( !PyArg_ParseTuple(args, "ii", &conn_id, &tag) ) {
    PyErr_SetString(PyExc_TypeError, "Invalid argument: expected two ints");
    return NULL;
  }
  dis_set_client_exit_handler(conn_id, tag);

  Py_RETURN_NONE;
}


static PyObject*
dim_dis_get_error_services(PyObject* /* self */, PyObject* /* args */) {
  /**
   * Calls: char* dis_get_error_services (int conn_id)
   */
  char* res=NULL;
  res = dis_get_error_services();
  return Py_BuildValue("s", res);
}


static PyObject*
dim_dis_add_cmnd(PyObject* /* self */, PyObject* args) {
  /* @param name
   * @param description
   * @param py_function
   * @param tag
   * @return DIM integer status code (1 for success)
   *
   * Implementation details: in order to preserve the C interface, unique
   * tags are generated for each call. The original tags are preserved with
   * the python function pointer and passed back when doing a callback.
   *
   * Proxy function for:
   *         unsigned int dis_add_cmnd(name,description,cmnd_user_routine,tag)
   * Where:
   *         char* name - the name of the command. Will be used for identifing the
   *                 python callback
   *         char* description - the command format
   *         void cmnd_user_routine (long* tag, int* address, int* size) - The
   *                 long pointer will be transformed in A long Python object
   *                 for the callback. The address will become a string long
   *                 tag - will be passed back to the Python callback
   */
  unsigned int res=0;
  char *name = NULL, *format = NULL;
  PyObject *tag = NULL;
  int sizeFormat, sizeName;
  PyObject *pyFunc;
  CmndCallback *callback, *oldCallback;
  string s;

  if (!PyArg_ParseTuple(args, "s#s#O|O",
        &name, &sizeName, &format, &sizeFormat, &pyFunc, &tag)
      || !PyCallable_Check(pyFunc) )
  {
    PyErr_SetString(PyExc_TypeError,
                     "Invalid arguments: expected two strings, "
		             "a callable object and an integer");
    return NULL;
  }
  debug("Adding command name %s, format %s and tag %p", name, format, tag);
  callback = (CmndCallback*)malloc(sizeof(CmndCallback));
  callback->format = (char*)malloc(sizeof(char)*sizeFormat);
  callback->name = (char*)malloc(sizeof(char)*sizeName);
  callback->pyFunc = pyFunc;	
  if (tag) { 
	Py_INCREF(tag);
	callback->pyTag = tag;
  }	
  strcpy(callback->format, format);
  strcpy(callback->name, name);
  /* TODO: The following portion is inherently unsafe. If a command comes
   * between the adding the command to the lookup tables and the actual
   * DIM registration of the new command, then results are undefined. The
   * portion of code bellow relies at least that the type of the commands will
   * be the same. The alternative is to become 'smart' and remove the command
   * first using dis_remove_service and then add it again.
   * TODO: check that res below is actually <= 0 if a command is registered
   * twice.
   */
  oldCallback = cmndName2PythonFunc[name];
  cmndUniqueTag2PythonFunc[(long)callback] = callback;
  cmndName2PythonFunc[name] = callback;
  res = dis_add_cmnd(name, format, dim_callbackCommandFunc, (long)callback);
  if (oldCallback && res<1) {
    Py_XDECREF(oldCallback->pyFunc);
	Py_XDECREF(oldCallback->pyTag);
    free(oldCallback->name);
    free(oldCallback->format);
    free(oldCallback);
  }

  return Py_BuildValue("i", res);
}


void
serviceProxy(void *tagp, void **buf, int *size, int * /*first_time*/) {
  /** Internal function for returning the data buffer for a service.
   * A DIM service functions in two ways:
   *   - by specifying a pointer to a fixed size structure at creation time
   *   - by specifying a callback that is done when a service is updated
   * In order to pass variable length parameters (the only really useful
   * situation), the second approach is needed. On the other hand, the user code
   * will become harder to understant if the parameters can only be supplied
   * by the means of a callback function. For this a DIM 'extension' was made
   * to allow variable lenght parameters in both cases:
   *   1. When a service is created on the C world, the pointer to the service
   * structure is registered as a tag. The actual tag given in python is saved
   * to the service data structure.
   *   2. In case the arguments are specified when the python function
   * dis_update_service is called, they are converted to a buffer and stored
   * in the service structure. The 'serviceProxy' method is going to be called
   * by the DIM 'dis_update_service' (or more exactly the internal funtion
   * 'execute_service') and 'serviceProxy' is going to take the necesarry steps
   * to return the python objects converted to a buffer
   *
   * @param tagp A pointer to the ServiceCallback structure.
   * @param buffer The buffer that should be sent by DIM
   * @param size The total size of the buffer
   * @param first_time Whether the service is called for the first time or not.
   */

  // the implicit assumption is that tagp is a pointer to a ServiceCallback
  ServiceCallback* svc =(ServiceCallback*)(*(long *)tagp);

  if (!svc->isUpdated || !svc->buffer) {
    /* what happens here? we have no data and we can't signal this to
     * DIM.Two options:
     *    - returning NULL + size 0
     *    - return some default data => unpredictable results client side
     */
    print("ERROR: You should not see this message! The service update has failed");
    debug("Could not get data to update service %s, pointer %x. Output buffer is %x with size %d, updated %d",
           svc->name, svc, (long)svc->buffer, svc->bufferSize, svc->isUpdated);
    svc->bufferSize = 0;
    if (svc->buffer) {
      free(svc->buffer);
      svc->buffer = NULL;
    }
  } else if (svc->isUpdated && svc->buffer) {
    /* nothing much to do there, we have everything already */
  }
  *buf = svc->buffer;
  *size = svc->bufferSize;
}


static PyObject*
dim_dis_add_service(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *        unsigned int dis_add_service (char* name,
   *                                      char* description,
   *                                      int*  address,
   *                                      int   size,
   *                                      func  user_routine,
   *                                      long tag)
   *        func = void user_routine(long* tag, int** address, int* size)
   *
   * Observation: the size of the command is calculated using the
   * description parameter so if size is omitted it is considered 1.
   *
   * @param name
   * @param description
   * @param python_function
   * @param tag
   */

  int name_size, format_size, service_id=0;
  char *name, *format;
  long pyTag;
  PyObject *pyFunc;
  ServiceCallback *svc;

  if (!PyArg_ParseTuple(args, "s#s#Ol", &name,
        &name_size,
        &format,
        &format_size,
        &pyFunc,
        &pyTag)
      || !PyCallable_Check(pyFunc))
  {
    PyErr_SetString(PyExc_TypeError,
        "Invalid arguments: expected two strings, a callable object and a long.");
    return NULL;
  }

  Py_INCREF(pyFunc);
  svc = (ServiceCallback*)malloc(sizeof(ServiceCallback));
  svc->name = (char*)malloc(sizeof(char)*name_size);
  svc->format = (char*)malloc(sizeof(char)*format_size);
  if (!svc || !svc->name || !svc->format) goto noMem;
  strcpy(svc->name, name);
  strcpy(svc->format, format);
  svc->pyTag = pyTag;
  svc->pyFunc = pyFunc;
  svc->buffer = NULL;
  svc->bufferSize = 0;

  service_id = dis_add_service(name,
                               format,
                               NULL,
                               0,
                               serviceProxy,
                               (long)svc);
  if (!service_id) {
    PyErr_SetString(PyExc_RuntimeError, "Could not create service");
    return NULL;
  }

  if (serviceID2Callback[service_id]) {
    /* a service with the same name added again? */
    debug("Replacing service %s",svc->name);
    Py_XDECREF(serviceID2Callback[service_id]->pyFunc);
    free(serviceID2Callback[service_id]->name);
    free(serviceID2Callback[service_id]->format);
    free(serviceID2Callback[service_id]->buffer);
    free(serviceID2Callback[service_id]);
  }
  serviceID2Callback[service_id] = svc;
  debug("Service %s added successfully with pointer %x", svc->name, svc);

  return Py_BuildValue("i", service_id);

 noMem:
  PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
  return NULL;
}


static PyObject*
dim_dis_update_service(PyObject* /* self */, PyObject* args) {
  /**
   *  Calls: int dis_update_service (int service_id)
   */
  int service_id, res;
  PyObject *svc_args=NULL, *arg;
  ServiceCallbackPtr svc;
  PyGILState_STATE gstate;

  if ( !PyArg_ParseTuple(args, "i|O", &service_id, &svc_args) ){
      //if ( !PyArg_ParseTuple(args, "i", &service_id) ){
    PyErr_SetString(PyExc_TypeError,
        "Argument error: incorect service ID");
    return NULL;
  }
  svc = serviceID2Callback[service_id];
  if (!svc){
    // Service was not found, already deleted?
    PyErr_SetString(PyExc_RuntimeError,
        "Service ID doesn't match any service");
    return NULL;
  }
  if (!svc_args) {
    if (!svc->pyFunc) {
      PyErr_SetString(PyExc_TypeError,
          "No arguments and no callback function was given");
      return NULL;
    }
    gstate = PyGILState_Ensure();
    arg = Py_BuildValue("(i)", svc->pyTag);
    free(svc_args);
    svc_args = PyEval_CallObject(svc->pyFunc, arg);
    Py_DECREF(arg);
    //Py_DECREF(svc_args); // !!!!!
    PyGILState_Release(gstate);
    if (!svc_args) {
      /* there was an exception raised when calling the python function
       * returning NULL implies the exception will be propageted
       * back to the interpretor
       */
      print("Error in calling python function %p", svc->pyFunc);
      PyErr_Print();
      return NULL;
    }
  }
  /* NOTE: it might not be optimal to allocate a buffer each time */
  if (svc->buffer)
    free(svc->buffer);
  if (!iterator_to_allocated_buffer(svc_args,
                                    svc->format,
                                    &svc->buffer,
                                    &svc->bufferSize) )
  {
    PyErr_SetString(PyExc_TypeError,
        "Arguments do not match initial service format");
    return NULL;
  }
  Py_DECREF(svc_args);
  svc->isUpdated = 1;
  Py_BEGIN_ALLOW_THREADS
  res = dis_update_service(service_id);
  Py_END_ALLOW_THREADS

  return Py_BuildValue("i", res);
}


static void
dim_callbackCommandFunc(void* uTag, void* address, int* size) {
  /** \brief Proxy function for passing the call to Python.
   * It is registered by default when a command service is
   * created.
   */
  CmndCallbackPtr pycall = (CmndCallbackPtr)(*(long *)uTag);
  PyObject *args, *res, *funargs;
  PyGILState_STATE gstate;
  
  gstate = PyGILState_Ensure();
  args = dim_buf_to_tuple(pycall->format, (char*)address, *size);
  if (args) {
    /* performing the Python callback */
	if (pycall->pyTag) {
		funargs = PyTuple_New(2);
		PyTuple_SET_ITEM(funargs, 0, args);
		PyTuple_SET_ITEM(funargs, 1, pycall->pyTag);
	} else {
		funargs = PyTuple_New(1);
		PyTuple_SET_ITEM(funargs, 0, args);
	} 	
    res = PyEval_CallObject(pycall->pyFunc, funargs);
    Py_DECREF(args);
	Py_DECREF(funargs);
    if (!res) {
      /* The Python function called throwed an exception.
       * We can't do much with it so we might as well print it */
      PyErr_Print();
    } else {
      Py_DECREF(res);
    }
  } else {
    print ("Could not convert received DIM buffer to Python objects");
  }
  PyGILState_Release(gstate);
}


/******************************************************************************/
/* DIC interface functions */
/******************************************************************************/
static PyObject*
dim_dic_set_dns_node(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *         dic_set_dns_node(char* node)
   * @param dns_name The name of the new DNS.
   * @return ret_code The DIM return code (1 for success).
   */
  char* name = NULL;
  int i;

  if ( !PyArg_ParseTuple(args, "s", &name) ) {
    PyErr_SetString(PyExc_TypeError, "Invalid DIM DNS name");
    return NULL;
  }
  i = dic_set_dns_node(name);

  return Py_BuildValue("i", i);
}


static PyObject*
dim_dic_get_dns_node(PyObject* /* self */, PyObject* /* args */) {
  /* calls dic_get_dns_node(char* node)
     the function should return the DNS node
     */
  char names[256];

  if ( !dic_get_dns_node(names) ) {
    PyErr_SetString(PyExc_TypeError,
        "Could not get DIM DNS node name.");
    return NULL;
  }

  return Py_BuildValue("s", names);
}


static PyObject*
dim_dic_set_dns_port(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *        dic_set_dns_port(int port)
   * @return return_code The DIM return code (1 for success).
   */
  unsigned int port;
  int i;

  if ( !PyArg_ParseTuple(args, "I", &port) ) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid argument: expected a pozitive integer"
        );
    return NULL;
  }
  i = dic_set_dns_port(port);

  return Py_BuildValue("i", i);
}


static PyObject*
dim_dic_get_dns_port(PyObject* /* self */, PyObject* /* args */) {
  /**
   * Proxy function to:
   *         dis_get_dns_port().
   * @return dns_port The DIM DNS port.
   */
  int port;
  port = dim_get_dns_port();
  return Py_BuildValue("i", port);
}


static PyObject*
dim_dic_get_id(PyObject* /* self */, PyObject* /* args */) {
  /** Proxy function to:
   *         int dic_get_id (char* name)
   * @return client_name The client name or an empty string if the
   *  command was not successful.
   */
  char name[256];
  int res;

  res = dic_get_id(name);
  if (!res)
    name[0] = 0;

  return Py_BuildValue("s", name);
}


static PyObject*
dim_dic_disable_padding(PyObject* /* self */, PyObject* /* args */) {
  /**
   * Proxy function to:
   *         int dic_disable_padding(void)
   */
  dic_disable_padding();
  Py_RETURN_NONE;
}


static PyObject*
dim_dic_get_quality(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *         int dic_get_quality (unsigned int service_id);
   * @return service_quality The service quality (int)
   */
  unsigned int service_id;
  int res;

  if (!PyArg_ParseTuple(args, "I", &service_id) ) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid argument: expected an unsigned integer");
    return NULL;
  }
  res = dic_get_quality(service_id);

  return Py_BuildValue("i", res);
}


static PyObject*
dim_dic_get_timestamp(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *        int dic_get_timestamp (service_id, secs, milisecs).
   *
   * @param service_id (unsigned int)
   * @return timestamp Python tuple with seconds and miliseconds  
   *         returns None, if dic_get_timestamp does not return 1.
   */
  unsigned int service_id;
  int secs, milisecs=0, res=0;

  if (!PyArg_ParseTuple(args, "I", &service_id)) {
    PyErr_SetString(PyExc_TypeError,
        "service id should be an unsigned integer");
    return NULL;
  }
  res = dic_get_timestamp(service_id, &secs, &milisecs);
  if (res==1){
    // res == 1 means, everything went fine
    return Py_BuildValue("ii", secs, milisecs);
  }else{
    // res != 1 means, something did not work. 
    // So we return None
    Py_RETURN_NONE;
  }

}


static PyObject*
dim_dic_get_format(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *        char *dic_get_format (unsigned int service_id)
   * @return format A string containing the format description.
   */
  unsigned int service_id;
  char* format=NULL;

  if (! PyArg_ParseTuple(args, "I", &service_id) ) {
    PyErr_SetString(PyExc_TypeError,
        "Service id should be an unsigned integer");
    return NULL;
  }
  format = dic_get_format(service_id);

  return Py_BuildValue("s", format);
}


static PyObject*
dim_dic_release_service(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function to:
   *        void dic_release_service (unsigned int service_id)
   */
  unsigned int service_id;
  string cppName;
  _dic_info_service_callback *tmp;

  if (!PyArg_ParseTuple(args, "I", &service_id)) {
    debug("Invalid service id specified");
    PyErr_SetString(PyExc_TypeError,
        "Service id should be an unsigned integer");
    return NULL;
  }
	Py_BEGIN_ALLOW_THREADS
  dic_release_service(service_id);
	Py_END_ALLOW_THREADS
  tmp = _dic_info_service_id2Callback[service_id];
  cppName = tmp->name;
  if (!tmp) {
    print("Service with id %d is not known", service_id);
    Py_RETURN_NONE;
  }
  _dic_info_service_name2Callback.erase(cppName);
  _dic_info_service_id2Callback.erase(service_id);
  free(tmp->format);
  free(tmp->name);
  Py_XDECREF(tmp->pyFunc);
  Py_XDECREF(tmp->pyDefaultArg);
  free(tmp);

  Py_RETURN_NONE;
}


static PyObject*
dim_dic_info_service(PyObject* /* self */, PyObject* args) {
  /**
   * @param string_name
   * @param string_format
   * @param callbackFunction A callable Python object
   * @param service_type Optional, default=MONITORED (int)
   * @param timeout Optional, default=0 (int)
   * @param tag Optional, default=0 (int)
   * @param default_value  Optional, default=NULL, (Python object)
   * Proxy function to:
   *         unsigned int dic_info_service (char* name         ,
   *                                        int   type         ,
   *                                        int   timeout      ,
   *                                        int*  address      ,
   *                                        int*  size         ,
   *                                        void* user_routine ,
   *                                        long  tag          ,
   *                                        int*  fill_address ,
   *                                        int   fill_size)
   * @return service_id The id of the newly created service.
   */
  char* name, *format;
  int service_type=MONITORED;
  int timeout=0;
  int tag=0;
  int format_size;
  int name_size;
  unsigned int service_id;
  string cppName;
  PyObject* pyFunc=NULL, *default_value=NULL ;
  _dic_info_service_callback *tmp=NULL, *svc;

  if (!PyArg_ParseTuple(args, "s#s#O|iiiO",
        &name, &name_size,
        &format, &format_size,
        &pyFunc,
        &service_type,
        &timeout,
        &tag,
        &default_value)
      || !PyCallable_Check(pyFunc))
  {
    goto invalid_args;
  }
  /* I am using a map and keys of type char * will not work */
  cppName = name;
  /* increasing the ref count of the python objects */
  Py_INCREF(pyFunc);
  if (default_value) Py_INCREF(default_value);
  /* creating a new service structure and storing all the service
   * details inside
   */
  svc = (_dic_info_service_callback*)malloc(sizeof(_dic_info_service_callback));
  if (!svc) goto no_memory;
  svc->format = (char*)malloc(sizeof(char)*format_size+1);
  svc->name = (char*)malloc(sizeof(char)*name_size+1);
  if (!svc->format || !svc->name) goto no_memory;
  svc->pyDefaultArg = default_value;
  svc->pyTag = tag;
  svc->pyFunc = pyFunc;
  strcpy(svc->name, name);
  strcpy(svc->format, format);

  /* registering the stub function. The C tag is the actual pointer to the
   * service structure
   */
  Py_BEGIN_ALLOW_THREADS	
  service_id = dic_info_service_stamped(name,
                                service_type,
                                timeout,
                                0, 0, /* service buffer and size */
                                _dic_info_service_dummy,
                                (long)svc,
                                0, 0); /* default buffer and size */
  Py_END_ALLOW_THREADS
  if (!service_id) {
    print("Service %s creation failed. Received result %d", name, service_id);
    goto dealocate;
  }
  svc->service_id = service_id;
  tmp = _dic_info_service_name2Callback[cppName];
  if (tmp) {
    free(tmp->format);
    free(tmp->name);
    Py_XDECREF(tmp->pyFunc);
    Py_XDECREF(tmp->pyDefaultArg);
    _dic_info_service_name2Callback.erase(cppName);
    _dic_info_service_id2Callback.erase(tmp->service_id);
    free(_dic_info_service_name2Callback[cppName]);
  }
  _dic_info_service_name2Callback[cppName] = svc;
  _dic_info_service_id2Callback[service_id] = svc;

  return Py_BuildValue("i", service_id);

  /* invalid arguments */
invalid_args:
  PyErr_SetString(PyExc_TypeError,
      "Invalid parameters. Expected:\n"
      "    string name,\n"
      "    string format,\n"
      "    PyObject* callbackFunction,\n"
      "    (optional) int service_type(=MONITORED),\n"
      "    (optional) int timeout(=0),\n"
      "    (optional) int tag(=0),\n"
      "    (optional) PyObject* default_value(=NULL)"
      );
  return NULL;

  /* memory problems */
no_memory:
  PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
  Py_DECREF(pyFunc);
  return NULL;

  /* invalid service registration */
dealocate:
  Py_XDECREF(tmp->pyFunc);
  _dic_info_service_name2Callback.erase(cppName);
  //_dic_info_service_id2Callback.erase(tmp->buffer);
  free(tmp->format);
  free(tmp->name);
  free(tmp);
  return 0;
}


static PyObject*
dim_dic_info_service_stamped(PyObject* self, PyObject* args){
  /* Proxy function to:
   *         to dim_dic_info_service (PyObject* self,
   *                                  PyObject* args,
   *                                  PyObject* keywds
   *                                 )
   * Accepts same arguments and returns the new ID of the created service.
   */
  return dim_dic_info_service(self, args);
}


static PyObject*
dim_dic_get_server(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function for:
   *         dic_get_server(char* name)
   * @return server_id, server_name
   */
  int service_id;
  char server_name[256];

  service_id = dic_get_server(server_name);

  return Py_BuildValue("is", service_id, server_name);
}


static PyObject*
dim_dic_get_conn_id(PyObject* /* self */, PyObject* /* args */) {
  /**
   * Proxy function for:
   *         dic_get_conn_id(char* name)
   * @return connection id
   */
  int service_id;

  service_id = dic_get_conn_id();
  return Py_BuildValue("i", service_id);
}


static PyObject*
dim_dic_get_server_services(PyObject* /* self */, PyObject* args) {
  /**
   * Proxy function for:
   *         dic_get_server_services(int conn_id)
   * @param connection id
   * @return services_list A Python list of services.
   */
  int conn_id;
  char* server_names=NULL;
  PyObject* ret;

  if (!PyArg_ParseTuple(args, "i", &conn_id)) {
    PyErr_SetString(PyExc_TypeError,
        "Invalid parameters. Expected argument:int conn_id");
    return NULL;
  }
  server_names = dic_get_server_services(conn_id);
  ret = stringList_to_tuple(server_names);

  return ret;
}


static PyObject*
dim_dic_get_error_services(PyObject* /* self */, PyObject* args) {
  /** It is meant to be called inside the error handler to determine
   *  what service originated the error.
   *
   * Proxy function for:
   *         dic_get_error_services(int conn_id)
   *
   * @return service_list a python list of services in error.
   */
  char* server_names=NULL;
  PyObject* ret;
  server_names = dic_get_error_services();
  ret = stringList_to_tuple(server_names);
  return args;
}


static PyObject*
dim_dic_add_error_handler(PyObject* self, PyObject* args) {
  /**
   * @param python callback (callable object)
   * It is a stub function for calling:
   *         dic_add_error_handler ( void* error_routine(int, int, char*) )
   * @returns the python None object
   */
  PyObject* pyFunc;

  if (!PyArg_ParseTuple(args, "O:set_callback", &pyFunc)
      || !PyCallable_Check(pyFunc))
  {
    PyErr_SetString(PyExc_TypeError,
        "Invalid parameters. Expected argument: callable object ");
    return NULL;
  }
  Py_XINCREF(pyFunc);
  Py_XINCREF(self);
  /* Dispose of previous callback */
  Py_XDECREF(_dic_callback_errorHandler_func.self);
  Py_XDECREF(_dic_callback_errorHandler_func.func);
  _dic_callback_errorHandler_func.self = self;
  _dic_callback_errorHandler_func.func = pyFunc;

  dic_add_error_handler(_dic_error_user_routine_dummy);

  Py_RETURN_NONE;
}

static PyObject*
dim_dic_cmnd_service(PyObject* /* self */, PyObject* args) {
  /**
   * @param service_name (string),
   * @param command_data (tuple or list),
   * @param format (string)
   * Proxy function for calling:
   *        dic_cmnd_service(char* name, int* address, int size)
   * @return the DIM return code (1 for a successful request)
   */
  char *service_name, *format, *buffer;
  unsigned int buffer_size;
  int res;
  PyObject *pySeq;

  res = PyArg_ParseTuple(args, "sOs", &service_name, &pySeq, &format);
  if (!res)
    goto invalid_arguments;
  /* creating dummy command request */
  if (!iterator_to_allocated_buffer(pySeq, format, &buffer, &buffer_size))
    goto error;
  Py_BEGIN_ALLOW_THREADS
  res = dic_cmnd_service(service_name, buffer, buffer_size);
  Py_END_ALLOW_THREADS
  /* freeing allocated buffer */
  free(buffer);

  return Py_BuildValue("i", res);

invalid_arguments:
  PyErr_SetString(PyExc_TypeError,
      "Invalid parameters. Expected: string service_name (string), "\
      "update_data (tuple or list), format (DIM format string)");
  return NULL;

error:
  PyErr_SetString(PyExc_RuntimeError,
            "Could not serialise provided arguments to a DIM buffer.\n"\
            "Please check that the order/number "\
            "of the argument maches the provided command format.");
  free(buffer);
  return NULL;

}


static PyObject*
dim_dic_cmnd_callback(PyObject* /* self */, PyObject* args) {
  /**
   * @param service_name (string),
   * @param command_data (tuple or list),
   * @param format (string)
   * @param cmnd_callback (callable object)
   * @param tag (int)
   * Stub function for calling:
   *        dic_cmnd_service(char* name,
   *                         int* address,
   *                         int size,
   *                         void* cmd_callback,
   *                         long tag)
   * @return the DIM return code (int) (1 for successful request)
   */
  char *service_name, *format, *buffer;
  unsigned int buffer_size;
  int res;
  long pyTag;
  PyObject *pySeq, *pyFunc;
  _dic_cmnd_callback *callback;

  if (!PyArg_ParseTuple(args, "sOsOl",
        &service_name, &pySeq, &format, &pyFunc, &pyTag)
      || !PyCallable_Check(pyFunc))
  {
    goto invalid_arguments;
  }
  /* saving callback */
  Py_INCREF(pyFunc);
  callback = (_dic_cmnd_callback*)malloc(sizeof(_dic_cmnd_callback));
  if (!callback)
    goto memory_error;
  callback->pyFunc = pyFunc;
  callback->pyTag = pyTag;
  /* creating dummy cmnd_callback request */
  if (!iterator_to_allocated_buffer(pySeq, format, &buffer, &buffer_size)) {
    goto error;
  }
  /* If we don't release the Python lock and if the client is on the
   * same machine we are going to have a deadlock!
   */
  Py_BEGIN_ALLOW_THREADS
  res = dic_cmnd_callback(service_name,
                          buffer,
                          buffer_size,
                          _dic_cmnd_callback_dummy,
                          (long)callback);
  Py_END_ALLOW_THREADS
  /* freeing temporary buffer and returning */
  free(buffer);

  return Py_BuildValue("i", res);

 invalid_arguments:
  PyErr_SetString(PyExc_TypeError,
      "Invalid parameters. "
      "   Expected: service_name (string), \n"\
      "             command_data (a tuple or list of values), \n"\
      "             format (a DIM format string), \n"\
      "             function_callback (a Python callable object) \n"\
      "             int tag"
      );
  return NULL;

 error:
  PyErr_SetString(PyExc_RuntimeError,
            "Could not serialise provided arguments to a DIM buffer.\n"\
            "Please check that the order/number "\
            "of the argument maches the provided command format.");
  return NULL;

 memory_error:
  PyErr_SetString(PyExc_MemoryError, "Could not allocate memory");
  return NULL;
}


/******************************************************************************/
/* DIC interface internal functions */
/******************************************************************************/
void _dic_cmnd_callback_dummy(void *uTag, int* ret_code) {
  /**
   * @param uniqueTagPtr is used to identify the actual Python functions that
   * needs to be called. The tag that might have been speciffied in python is
   * substituted before passing the call.
   *
   * Stub function for passing the callback to the error handler to the Python
   * layer. This functions is registered to DIM instead of the Python function
   * and will forward the call to the interpreter.
   *
   * @return no value is returned
   */
  PyObject* res;
  PyGILState_STATE gstate;
  _dic_cmnd_callback* callback = (_dic_cmnd_callback *)(*(long *)uTag) ;

  /* The python calls to the API are encapsulated by the usual
   * Ensure(), Release()
   */
  gstate = PyGILState_Ensure();
  res = pyCallFunction(callback->pyFunc,
                       Py_BuildValue("li", callback->pyTag, *ret_code));
  Py_DECREF(res);
  Py_DECREF(callback->pyFunc);
  PyGILState_Release(gstate);
  /* delete callback information */
  free(callback);
}


void _dic_error_user_routine_dummy(int severity, int error_code, char* message) {
  /* Stub function for passing the callback to the error handler to the Python
   * layer.
   * To the callback to the python layer the DIM severity, error_code and
   * message are passed.
   * NOTE: When this function is called it does not have the interpretor lock.
   */

  PyObject *arg, *res;
  PyGILState_STATE gstate;
  if ( _dic_callback_errorHandler_func.func ) {
	gstate = PyGILState_Ensure();
	arg = Py_BuildValue("iis", severity, error_code, message);
	res = PyEval_CallObject(_dic_callback_errorHandler_func.func, arg);
	Py_DECREF(arg);
	Py_XDECREF(res);
	PyGILState_Release(gstate);
  } else {
    debug("Could not find any registered Python function. "\
        "Dropping DIM client error callback.");
    PyErr_SetString(PyExc_RuntimeError, "Could not find any registered Python function. "\
        "Dropping DIM client error callback.");
    return;
  }
}


void _dic_info_service_dummy (void* tag, void* buffer, int* size) {
  /** Stub function for passing the received data from a service to a python
   *  callback.
   *
   * @param tag A tag that identifies the service. This parameter is used in
   * the wrapper to identify the update service, convert the buffer to Python
   * objects and pass the call to the interpretor.
   * @param buffer The buffer containing the service update data.
   * @param size The size of the buffer.
   *
   * When this function is called we don't have the interpretor lock. We must
   * ensure that before calling any Python API function we have it! Note also
   * that dim_buf_to_tuple creates Python object so the lock must be held.
   */

  PyObject* args, *res;
  _dic_info_service_callback* svc;
  PyGILState_STATE gstate;

  //debug("Received update for a service with size %d, buffer pointer %x, tag %x",
  //	 *size, (long)buffer, (long *)tag);
  svc = (_dic_info_service_callback*)(*(long *)tag);

  gstate = PyGILState_Ensure();
  if (!(*size)) {
    /* The service update request failed. Passing default argument */
    args = svc->pyDefaultArg;
  } else {
    args = dim_buf_to_tuple(svc->format, (char*)buffer, *size);
  }
  if (args) {
//    Py_INCREF(args);
    res = PyEval_CallObject(svc->pyFunc, args);
    if (!res){
      if (PyErr_Occurred() != NULL) {
        PyErr_Print();
      } else {
        print("ERROR: Bad call to Python layer");
      }
    } else {
      /* call succedded */
      Py_DECREF(res);
    }
    Py_XDECREF(args);
  } else {
    /* service failed and a default value was not specified */
    print("ERROR: Could not get new data to update service");
  }
  PyGILState_Release(gstate);
}

/** @}
*/

//---------------------- Dom here ... doing strange things:
// first few lines from https://docs.python.org/3/howto/cporting.html#module-initialization-and-state

struct module_state {
    PyObject *error;
};

#if PY_MAJOR_VERSION >= 3
#define GETSTATE(m) ((struct module_state*)PyModule_GetState(m))
#else // PY_MAJOR_VERSION >= 3
#define GETSTATE(m) (&_state)
static struct module_state _state;
#endif PY_MAJOR_VERSION >= 3

static PyObject *
error_out(PyObject *m) {
    struct module_state *st = GETSTATE(m);
    PyErr_SetString(st->error, "something bad happened");
    return NULL;
}

static PyMethodDef DimMethods[] = {
  {    "dis_start_serving"          ,
    dim_dis_start_serving        ,
    METH_VARARGS                 ,
    "Start providing DIM service"
  },
  {    "dis_stop_serving"           ,
    dim_dis_stop_serving         ,
    METH_VARARGS                 ,
    "Stop DIM service"
  },
  {    "dis_set_dns_node"           ,
    dim_dis_set_dns_node         ,
    METH_VARARGS                 ,
    "Function for setting the DNS node"
  },
  {    "dis_get_dns_node"           ,
    dim_dis_get_dns_node         ,
    METH_VARARGS                 ,
    "Function for getting the DNS node"
  },
  {    "dis_set_dns_port"           ,
    dim_dis_set_dns_port         ,
    METH_VARARGS                 ,
    "Function for setting the DNS port"
  },
  {    "dis_get_dns_port"           ,
    dim_dis_get_dns_port         ,
    METH_VARARGS                 ,
    "Function for getting the DNS port"
  },
  {    "dis_add_exit_handler"       ,
    dim_dis_add_exit_handler     ,
    METH_VARARGS                 ,
    "Function for setting the DIM exit handler"
  },
  {    "dis_add_error_handler"      ,
    dim_dis_add_error_handler    ,
    METH_VARARGS                 ,
    "Function for setting the DIM error handler"
  },
  {    "dis_add_client_exit_handler"  ,
    dim_dis_add_client_exit_handler,
    METH_VARARGS                   ,
    "Function for setting the DIM Client exit handler"
  },
  {    "dis_update_service"           ,
    dim_dis_update_service         ,
    METH_VARARGS                   ,
    "Function for updating the specified service"
  },
  {    "dis_selective_update_service"  ,
    dim_dis_selective_update_service,
    METH_VARARGS                    ,
    "Function for updating the specified service and clients"
  },
  {    "dis_set_quality"               ,
    dim_dis_set_quality             ,
    METH_VARARGS                    ,
    "Function for setting the quality of a service"
  },
  {    "dis_set_timestamp"             ,
    dim_dis_set_timestamp           ,
    METH_VARARGS                    ,
    "Function for setting the the timestamp of a service"
  },
  {    "dis_remove_service"            ,
    dim_dis_remove_service          ,
    METH_VARARGS                    ,
    "Function for removing a service"
  },
  {    "dis_get_next_cmnd"             ,
    dim_dis_get_next_cmnd           ,
    METH_VARARGS                    ,
    "Get a command from the list of waiting command requests"
  },
  {    "dis_remove_service"            ,
    dim_dis_remove_service          ,
    METH_VARARGS                    ,
    "Remove a Service from the list of provided services"
  },
  {    "dis_get_client"                ,
    dim_dis_get_client              ,
    METH_VARARGS                    ,
    "Gets the process identification of the current DIM client"
  },
  {    "dis_get_conn_id"               ,
    dim_dis_get_conn_id             ,
    METH_VARARGS                    ,
    "Gets the connection ID of the current DIM client"
  },
  {    "dis_get_timeout"               ,
    dim_dis_get_timeout             ,
    METH_VARARGS                    ,
    "Gets the update rate that was specified by a client for a specific service"
  },
  {    "dis_get_client_services"       ,
    dim_dis_get_client_services     ,
    METH_VARARGS                    ,
    "Gets the services of a DIM client, which has subscribed to this DIM server"
  },
  {    "dis_set_client_exit_handler"   ,
    dim_dis_set_client_exit_handler ,
    METH_VARARGS                    ,
    "Activates the client exit handler for a specific client and a specific service"
  },
  {    "dis_get_error_services"        ,
    dim_dis_get_error_services      ,
    METH_VARARGS                    ,
    "Gets the names of DIM services that have an error"
  },
  {    "dis_add_cmnd"                  ,
    dim_dis_add_cmnd                ,
    METH_VARARGS                    ,
    "Adds a new command"
  },
  {    "dis_add_service"               ,
    dim_dis_add_service             ,
    METH_VARARGS                    ,
    "Adds a new service"
  },
  {    "dic_set_dns_node"              ,
    dim_dic_set_dns_node            ,
    METH_VARARGS                    ,
    "Function for setting the DNS node"
  },
  {    "dic_get_dns_node"              ,
    dim_dic_get_dns_node            ,
    METH_VARARGS                    ,
    "Function for getting the DNS node"
  },
  {    "dic_set_dns_port"              ,
    dim_dic_set_dns_port            ,
    METH_VARARGS                    ,
    "Function for setting the DNS port"
  },
  {    "dic_get_dns_port"              ,
    dim_dic_get_dns_port            ,
    METH_VARARGS                    ,
    "Function for getting the DNS port"
  },
  {    "dic_get_id"                    ,
    dim_dic_get_id                  ,
    METH_VARARGS                    ,
    "Gets the process identification of this DIM client."
  },
  {    "dic_disable_padding"           ,
    dim_dic_disable_padding         ,
    METH_VARARGS                    ,
    "Disable padding of received services."
  },
  {    "dic_get_quality"               ,
    dim_dic_get_quality             ,
    METH_VARARGS                    ,
    "Gets the quality of  a received service."
  },
  {    "dic_get_timestamp"             ,
    dim_dic_get_timestamp           ,
    METH_VARARGS                    ,
    "Gets the time stamp of a received service."
  },
  {    "dic_get_format"                ,
    dim_dic_get_format              ,
    METH_VARARGS                    ,
    "Gets the format description of a received service."
  },
  {    "dic_release_service"           ,
    dim_dic_release_service         ,
    METH_VARARGS                    ,
    "Called by a client when a service is not needed anymore."
  },
  {    "dic_info_service"               ,
    dim_dic_info_service,
    METH_VARARGS | METH_KEYWORDS     ,
    "Called by a client for subscribing to a service."
  },
  {    "dic_cmnd_service"        ,
    dim_dic_cmnd_service      ,
    METH_VARARGS              ,
    "Request the execution of a command by a server."
  },
  {    "dic_cmnd_callback"       ,
    dim_dic_cmnd_callback     ,
    METH_VARARGS              ,
    "Request the execution of a command and registers a completion callback."
  },
  {    "dic_info_service_stamped"       ,
    dim_dic_info_service_stamped  ,
    METH_VARARGS              ,
    "Request a time stamped (and quality flagged) information service from a server"
  },
  {    "dic_get_server"          ,
    dim_dic_get_server        ,
    METH_VARARGS              ,
    "Gets the process identification of the current DIM server"
  },
  {    "dic_get_conn_id"          ,
    dim_dic_get_conn_id        ,
    METH_VARARGS               ,
    "Gets the connection ID of the current DIM server"
  },
  {    "dic_get_server_services"          ,
    dim_dic_get_server_services     ,
    METH_VARARGS              ,
    "Gets the services of a DIM server to which the client has subscribed."
  },
  {    "dic_get_error_services"          ,
    dim_dic_get_error_services       ,
    METH_VARARGS              ,
    "Gets the names of DIM services that have an error."
  },
  {    "dic_add_error_handler"          ,
    dim_dic_add_error_handler   ,
    METH_VARARGS              ,
    "Adds an error handler to this client."
  },
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

// --- Dom here putting more crazy stuff from here: https://docs.python.org/3/howto/cporting.html#module-initialization-and-state

#if PY_MAJOR_VERSION >= 3

static int myextension_traverse(PyObject *m, visitproc visit, void *arg) {
    Py_VISIT(GETSTATE(m)->error);
    return 0;
}

static int myextension_clear(PyObject *m) {
    Py_CLEAR(GETSTATE(m)->error);
    return 0;
}

static struct PyModuleDef moduledef = {
        PyModuleDef_HEAD_INIT,
        "dimc",
        "module dimc docstring ... :-|",
        sizeof(struct module_state),
        DimMethods,
        NULL,
        myextension_traverse,
        myextension_clear,
        NULL
};

#define INITERROR return NULL

PyObject *
PyInit_dimc(void)

#else //PY_MAJOR_VERSION >= 3

#define INITERROR return

#ifndef _WIN32
static pthread_t maintid;
static pthread_mutex_t pydimlock = PTHREAD_MUTEX_INITIALIZER; 
#endif // _WIN32
  PyMODINIT_FUNC
initdimc(void)
#endif // PY_MAJOR_VERSION >= 3
{

#if PY_MAJOR_VERSION >= 3
    PyObject *module = PyModule_Create(&moduledef);
#else // PY_MAJOR_VERSION >= 3

  PyObject *module;
  PyEval_InitThreads();
  debug("Initializing the C DIM interface... \n");
  module = Py_InitModule3("dimc", DimMethods, "DIM methods");

  if (module == NULL)
    return;
#ifndef _WIN32
  maintid = pthread_self();
#endif
  //Add constants for service type definitions
  PyModule_AddIntConstant (module, "ONCE_ONLY", ONCE_ONLY);
  PyModule_AddIntConstant (module, "TIMED", TIMED);
  PyModule_AddIntConstant (module, "MONITORED", MONITORED);
  PyModule_AddIntConstant (module, "COMMAND", COMMAND);
  PyModule_AddIntConstant (module, "DIM_DELETE", DIM_DELETE);
  PyModule_AddIntConstant (module, "MONIT_ONLY", MONIT_ONLY);
  PyModule_AddIntConstant (module, "UPDATE", UPDATE);
  PyModule_AddIntConstant (module, "TIMED_ONLY", TIMED_ONLY);
  PyModule_AddIntConstant (module, "MONIT_FIRST", MONIT_FIRST);
  PyModule_AddIntConstant (module, "MAX_TYPE_DEF", MAX_TYPE_DEF);
  PyModule_AddIntConstant (module, "STAMPED", STAMPED);

  dic_disable_padding();
  dis_disable_padding();
#endif // PY_MAJOR_VERSION >= 3

    if (module == NULL)
        INITERROR;
    struct module_state *st = GETSTATE(module);

    st->error = PyErr_NewException("dimc.Error", NULL, NULL);
    if (st->error == NULL) {
        Py_DECREF(module);
        INITERROR;
    }

#if PY_MAJOR_VERSION >= 3
    return module;
#endif // PY_MAJOR_VERSION >= 3
}



#ifdef RINUNX
#include <stdio.h>
#include <dlfcn.h>
#include <errno.h>
#include <string.h>
#include <semaphore.h>

extern sem_t DIM_INIT_Sema;

PyGILState_STATE gilstack[GILSTACKSIZE];
int gilstackp = 0;

void dim_lock()
{
	static void  (*func)(void);
	int v;

    if(!func) {
        func = (void (*)()) dlsym(RTLD_NEXT, "dim_lock");
		if (!func) {
			printf("Couldn't find dim_lock");
			exit(1);
		}
	}
	if (gilstackp == GILSTACKSIZE) {
		printf("ERROR: GILstack overflow");
		exit(1);
	}
	pthread_mutex_lock(&pydimlock);
	if ((pthread_self() != maintid)) {
		gilstack[gilstackp++] = PyGILState_Ensure();
	}
	sem_getvalue(&DIM_INIT_Sema, &v);
	printf("%d\n", v);
	(*func)();
  	printf("dim_lock() is called: %d\n", gilstackp);
	pthread_mutex_unlock(&pydimlock); 
  	return;
}

void dim_unlock()
{
        
  static void  (*func)(void);

  if(!func) {
        func = (void (*)()) dlsym(RTLD_NEXT, "dim_unlock");
		if (!func) {
			printf("Couldn't find dim_unlock");
			exit(1);
		}
	}        
   // gilstackp--;	
	pthread_mutex_lock(&pydimlock);
  	(*func)();
	if ((pthread_self() != maintid)) {
		PyGILState_Release(gilstack[gilstackp--]);
	}           
	pthread_mutex_unlock(&pydimlock);
  	printf("dim_unlock() is called: %d\n", gilstackp); 
  	return;
}

#endif


