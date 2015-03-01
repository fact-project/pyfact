from __future__ import print_function
import dimcpp
import debug


class RpcProxy (dimcpp.DimRpc):
    """
Class that facilitates publishing of random python functions using a single
DIM RPC. At creation it receives a lost of callable objects wo which the calls
will be passed. It creates a single string DIM RPC and accepts a string with
the format:
  'function_name/par1_name=par1_value1,par1_value2/par2_name=par2_value/.../'
or
  'function_name/par1_value,par2_value/.../' for possitional arguments
The appropiate function is called with the appropiate parameters and the
result is returned in the same format.
The special characters (',', '=' and '/') must be excaped.
Identifiers must contain alfanumeric characters plus the '_' and '-' chars.
It makes the assumption that the python functions will return always a tuple
in the format (STATUSCODE, RESULTS). All the return parameters are converted
to a string and are returned to the client.
    """
    def __init__(self, funcs, rpcName='testRPC'):
        #DimRpc.__init__(self, rpcName, 'C', 'C')
        super(RpcProxy, self).__init__(self, rpcName, 'C', 'C')
        self.lastValue = None
        self.funcs = {}
        self.name = rpcName
        if not hasattr(funcs, '__iter__'):
            funcs = [funcs]
        for f in funcs:
            # creating a dictionary of function names and callable objects
            if hasattr(f, '__call__'):
                self.funcs[f.func_name] = f
            else:
                debug.ERROR('Object %s is not callable' % f)
                debug.DEBUG(dir(f))

    def convert(self, args):
        ret = ""
        if not hasattr(args, '__iter__'):
            args = (args,)
        for x in args:
            add = str(x)
            add = add.replace('/', '\/')
            add = add.replace('=', '\=')
            add = add.replace(',', '\,')
            ret += add + ','
        return ret[:-1]

    def split(self, s, sep, exc='\\'):
        args = []
        poz = 0
        while s:
            poz = s.find(sep, poz)
            if poz == 0:
                s = s[1:]
            elif poz == -1:
                args.append(s)
                s = ""
            elif s[poz-1] != exc:
                args.append(s[:poz])
                s = s[poz+1:]
                poz = 0
            else:
                poz += 1
        if len(args) > 1 or len(args) == 0:
            return args
        else:
            return args[0]

    def parse(self, s):
        pozArgs = []
        keyArgs = {}
        args = self.split(s, '/')
        if isinstance(args, (str, basestring)):
            args = (args,)
        debug.DEBUG(args)
        for arg in args:
            #debug.DEBUG(arg)
            poz = arg.find('=')
            if poz > 0 and arg[poz-1] != '\\':
                # we have a named argument
                keyArgs[arg[:poz]] = self.split(arg[poz+1:], ',')
            else:
                pozArgs.append(self.split(arg, ','))
        return pozArgs, keyArgs

    def rpcHandler(self):
        s = self.getString()
        debug.DEBUG("Received: ", s)
        # figuring out which method to call and parsing arguments
        if s.find('/') > -1:
            funcName = s[:s.find('/')]
            s = s[s.find('/'):]
        elif s:
            # we have 0 arguments
            funcName = s
            s = ""
        else:
            self.setData('ERROR: function %s is not registered' % s)
            return
        try:
            funcObj = self.funcs[funcName]
        except KeyError as e:
            debug.ERROR(e)
            self.setData('status=FAIL/error=Could not find function '+str(e))
            return
        #debug.DEBUG(funcName, s)
        pozArgs, keyArgs = self.parse(s)
        #debug.DEBUG(pozArgs, keyArgs)
        ret = funcName + '/'

        try:
            res = funcObj(*pozArgs, **keyArgs)
        except Exception as e:
            # catch all convert it to string and return
            print(type(funcObj))
            ret += 'status=FAIL/error='+str(e)
            debug.DEBUG('Returning exception message: %s' % ret)
        else:
            '''
            We have an result. Converting to a string and returning it.
            There can be two types of returned results: iterables and
            dictionaries. Both results can contain basic types or other
            iterables.
            Iterables: They will be  converted in the equivalent of positional
            arguments for calling a function.
            Dictionaries: Will be converted in the equivalent of named
            arguments.
            '''
            if res[0] == 0:
                ret += 'status=ERROR/'
                try:
                    ret = '%serror=%s/' % (ret, res[1])
                except:
                    pass
            else:
                ret += 'status=SUCCESS/'
                #named = False  #DN: assigned but never used?!
                try:
                    res = res[1]
                except:
                    pass
                else:
                    if isinstance(res, dict):
                        for x in res:
                            ret = "%s%s=%s/" % (ret,
                                                self.convert(x),
                                                self.convert(res[x]))
                    elif hasattr(res, '__iter__'):
                        for x in res:
                            ret = "%s%s/" % (ret, self.convert(x))
                    else:
                        ret = "%s%s/" % (ret, self.convert(res))

        # this is particularly usefull if on the other side are C/C++ clients
        ret += '\0'
        # setting result
        debug.DEBUG('Sending result: %s' % ret)
        self.setData(ret)
