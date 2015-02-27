import os
import types
from keyword import iskeyword
import time

from sync_calls import dic_sync_info_service, dic_sync_cmnd_service
import dimc

class Dns(object):
    def __init__(self, hostname=None, port=None, timeout=5):
        self.node = hostname
        self.port = port
        self.timeout = timeout

        if hostname is not None:
            dimc.dic_set_dns_node(hostname)
        elif "DIM_DNS_NODE" in os.environ:
            dimc.dic_set_dns_node(os.environ["DIM_DNS_NODE"])
        else:
            dimc.dic_set_dns_node("localhost")
        
        if port is not None:
            dimc.dic_set_dns_port(port)
        elif "DIM_DNS_PORT" in os.environ:
            dimc.dic_set_dns_port(int(os.environ["DIM_DNS_PORT"]))
        else:
            dimc.dic_set_dns_port(2505)

    def servers(self):
        """ create dict of DimServers from DIS_DNS/SERVER_LIST
        """
        server_list_tuple = dic_sync_info_service(
            'DIS_DNS/SERVER_LIST',
            'C',
            timeout=self.timeout)
        #TODO: all pydim_dic... functions have the 'timeout' parameter. (I think)
        #       and for all of them, I have to check if the return value is None.
        #       because if it is None, the function call timed out.
        #       And this often simply shows network problems.
        #       I don't want to write this if ... bla .. raise IOError stuff
        #       everywhere, but I want to write that in one central place...
        if server_list_tuple is None:
            raise IOError(
                "DIS_DNS/SERVER_LIST request "
                "timed out after {0} seconds".format(self.timeout))

        server_list_string = server_list_tuple[0]
        servers_at_hosts, process_ids, __empty__ = server_list_string.split('\x00')

        # servers_at_hosts looks_like "server_name@host1|another_server@host2|..."
        list_of_servers_at_hosts = servers_at_hosts.split('|')
        # process_ids is a string like: "12345|1337|424242|..."
        list_of_process_ids = process_ids.split('|')

        servers = {}
        for server_at_host, process_id in zip(list_of_servers_at_hosts, list_of_process_ids):
            server_name, host_name = server_at_host.split('@')

            servers[server_name] = DimServer(
                name=server_name,
                pid=int(process_id),
                host=host_name)

        return servers
	

class ServiceNameProblem(Exception):
    """ Thrown in case a service has been requested, that does not exist.
        Might be due to a typo, but can also mean, that the server stopped
        supporting this service. (Servers may do so any time)
    """
    pass


class DimService(object):

    def __init__(self, name, fmt, typ):
        self.name = name
        self.fmt = fmt  # format
        self.typ = typ

        self.desc = None

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    def __repr__(self):
        return self.__str__()


class DimServer(object):

    def __init__(self, name, pid, host, timeout=5):
        self.name = name
        self.pid = pid
        self.host = host

        self.timeout = timeout

        self.services = self._fetch_services()
        self._create_methods()
        self._fetch_service_description()

    def __str__(self):
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    def __repr__(self):
        return self.__str__()

    def _fetch_services(self):
        sl_raw = dic_sync_info_service(self.name + '/SERVICE_LIST', 'C', timeout=self.timeout)
        # return value is a tuple with only one element
        sl_raw = sl_raw[0]

        if sl_raw is None:
            raise IOError(
                "{name}/SERVICE_LIST request "
                "timed out after {timout} seconds".format(
                    timeout=self.timeout,
                    name=self.name)
                )

        # now before parsing, I strip off all ASCII zeroes '\x00' and all
        # line breaks off the *end* of the long string of both
        # the service list sl
        # and service description sd
        #
        # I think in sl_raw were alse some '\x00' in the middle .. these
        # are replaced by nothing, in case they are there.
        sl_raw = sl_raw.rstrip('\x00\n')
        sl_raw = sl_raw.replace('\x00', '')

        # The lists are seperated by line breaks, so I split them using this
        sl = sl_raw.split('\n')

        # Now I fill ther services dict. Each server gets a nested dict
        # inside services.
        # Each service is explained in a string with a '|' in between.
        # I use this for spliting.
        # The string look like this
        # SERVER/SERVICE|format-desc-str(e.g. I:2;C)|-empty- or CMD or RPC|

        services = []
        for service in sl:
            service = service.split('|')
            services.append(DimService(name=service[0], fmt=service[1], typ=service[2]))

        services = {svc.name: svc for svc in services}
        return services

    def has_service(self, full_service_name):
        return full_service_name in self.services.keys()

    def _fetch_service_description(self):
        """ FACT dim servers often have a special service called SERVICE_DESC,
            which further describes services.

            server : needed to find out if SERVICE_DESC is really available

        """
        if not self.has_service(self.name+"/SERVICE_DESC"):
            return {}

        sd_raw = self.service_desc()[0]
        sd_raw = sd_raw.rstrip('\x00\n')
        sd = sd_raw.split('\n')

        service_names = [x.split('=', 1)[0] for x in sd]
        rest = [x.split('=', 1)[1] for x in sd]
        # the "rest" consists of a description of the service ... I hope
        descr = [[ x for x in r.split("|") if x] for r in rest]
        sd = {x[0]:x[1] for x in zip(service_names, descr)}
       
        for k in self.services:
            service = self.services[k]
            service.desc = sd.get(k)

    def _create_methods(self):
        for svc in self.services.values():
            try:
                method_name = self.lower_short_service_name(svc)
            except ServiceNameProblem:
                continue

            if svc.typ == 'CMD':
                def dummy_method(self, args, svc=svc):
                    return self._cmd(svc, *args)
            elif svc.typ == '':
                def dummy_method(self, svc=svc):
                    return self._get(svc)

            dummy_method.__name__ = method_name
            dummy_method.__doc__ = str(svc)
            setattr(self, method_name, types.MethodType(dummy_method, self))

    def _cmd(self, svc, *args):
        """ used by all dynamicly created methods, which call a Dim CMD
        """
        fmt = svc.fmt

        # there is a work around for a bug in pydim
        # even if a command needs no argument, and desc is also empty string
        # one has to give one ... need to tell Niko about it.
        if not fmt:
            fmt = 'I'
            args = (1, )
        elif fmt == 'O':
            args = (0, )
        dic_sync_cmnd_service(svc.name, args, fmt, timeout=self.timeout)

    def _get(self, svc):
        """ used by all dynamicly created methods, which get a service
        """
        return dic_sync_info_service(svc.name, svc.fmt, timeout=1)

    def lower_short_service_name(self, svc):
        if not svc.name.find(self.name+'/') == 0:
            raise ServiceNameProblem(
                "not svc.name.find(self.name+'/') == 0: "
                "--> svc.name:{0}, server.name:{1}".format(
                    svc.name,
                    self.name
                    )
                )
        short_name = svc.name.replace(self.name+'/', '').lower()
        if iskeyword(short_name):
            short_name += '_'
        return short_name


def make_doc_string(service):
    doc_string = ""
    doc_string += "Dim Service \n"
    if service.desc:
        doc_string += service.desc
    else:
        doc_string += "--- no SERVICE_DESC available for this service ---\n"
    doc_string += '\n'
    doc_string += str(service)
    return doc_string


def make_method_name_from_service(service):
    meth_name = service.name.split('/')[1].lower()
    if iskeyword(meth_name):
        meth_name += '_get'

    return meth_name


def print_doc_string_to_file(doc_string, f):
    for line in doc_string.split('\n'):
        if '|' in line:
            for subline in line.split('|'):
                if subline:
                    f.write('            ' + subline + '\n')
        else:
            f.write('            ' + line + '\n')


def print_getter(service, f):
    meth_name = make_method_name_from_service(service)
    doc_string = make_doc_string(service)

    f.write("    def " + meth_name + "(self):\n")
    f.write('        """ \n')
    print_doc_string_to_file(doc_string, f)
    f.write('        """ \n')
    f.write('        return self._get("' + meth_name.upper() + '")\n\n')


def print_command(service, f):
    meth_name = make_method_name_from_service(service)
    doc_string = make_doc_string(service)

    f.write("    def " + meth_name + "(self, *args):\n")
    f.write('        """ \n')
    print_doc_string_to_file(doc_string, f)
    f.write('        """ \n')
    f.write('        self._cmd("' + meth_name.upper() + '", *args)\n\n')


class FactDimServer(object):
    def __init__(self, name, services):
        """ sets name of instance to name of server, all uppercase
        """
        self.list_of_states = []
        self.name = name.upper()
        self.print_state = False
        self.print_msg = False
        self.reg_state_cb()
        self.reg_msg_cb()
        self.user_func = None
        self.__delay_between_cmds = 1.0
        self.__delay_between_services = 1.0
        self.__last_cmd_send = -1*float('inf')
        self.__last_service_got = -1*float('inf')
        self.services = services

    def _cmd(self, cmdstr, *args):
        """ used by all dynamicly created methods, which call a Dim CMD
        """
        cmdstr = self.name + '/' + cmdstr.upper()
        desc = self.services[self.name][cmdstr.upper()][0]

        # there is a work around for a bug in pydim
        # even if a command needs no argument, and desc is also empty string
        # one has to give one ... need to tell Niko about it.
        if not desc:
            desc = 'I'
            args = (1, )
        elif desc == 'O':
            args = (0,)
        while not time.time() - self.__last_cmd_send > self.__delay_between_cmds:
            time.sleep(0.5)
        self.__last_cmd_send = time.time()
        dic_sync_cmnd_service(cmdstr, args, desc, timeout=1)

    def _get(self, service):
        """ used by all dynamicly created methods, which get a service
        """
        full_srv_name = self.name+'/'+service.upper()
        desc = self.services[self.name][full_srv_name][0]

        while not time.time() - self.__last_service_got > self.__delay_between_services:
            time.sleep(0.5)
        self.__last_service_got = time.time()
        #print 'full_srv_name',full_srv_name
        #print 'desc', desc
        return dic_sync_info_service(full_srv_name, desc, timeout=1)

    def __call__(self):
        """ Wrapper / For Convenience
            self.state() returns a string (if it exists)
            *returns* numeric state code, parsed from return of self.state()
        """
        if hasattr(self, 'stn'):
            return self.stn
        else:
            raise TypeError(self.name+' has no CMD called STATE')

    def wait(self, state_num, timeout=None):
        """ waits for a certain state
            BLOCKING
            returns True if state was reached
            returns False if timeout occured
            raises TypeError if Server has no method state
        """

        if not hasattr(self, 'stn'):
            raise TypeError(self.name+' has no CMD called STATE')
        if timeout is None:
            timeout = float('inf')
        else:
            timeout = float(timeout)
        start = time.time()
        while not self.stn == state_num:
            time.sleep(0.1)
            if time.time() >= start+timeout:
                return False
        return True

    def state_callback(self, state):
        self.sts = state
        try:
            self.stn = int(state[state.find('[') + 1: state.find(']')])
        except ValueError:
            self.stn = None

        self.last_st_change = time.time()
        self.list_of_states.append((self.last_st_change, self.stn))
        if len(self.list_of_states) > 10000:
            print "list_of_states too long, truncating..."
            self.list_of_states = self.list_of_states[1000:]

        if self.user_func:
            self.user_func(self.stn)

        if self.print_state:
            print state

    def msg_callback(self, msg):
        if self.print_msg:
            print msg

    def reg_state_cb(self):
        if not hasattr(self, 'state'):
            raise TypeError(self.name+' has no CMD called STATE')
        service_name = self.name.upper()+'/STATE'
        self.state_sid = dimc.dic_info_service(service_name, "C", self.state_callback)
        if not self.state_sid:
            del self.state_sid
            raise IOError('could not register STATE client')

    def reg_msg_cb(self):
        if not hasattr(self, 'state'):
            raise TypeError(self.name+' has no CMD called STATE')
        service_name = self.name.upper()+'/MESSAGE'
        self.msg_sid = dimc.dic_info_service(service_name, "C", self.msg_callback)
        if not self.msg_sid:
            del self.msg_sid
            raise IOError('could not register MESSAGE client')

    def unreg_state_cb(self):
        if hasattr(self, 'state_sid'):
            dimc.dic_release_service(self.state_sid)
            del self.state_sid

    def unreg_msg_cb(self):
        if hasattr(self, 'msg_sid'):
            dimc.dic_release_service(self.msg_sid)
            del self.msg_sid

    def __del__(self):
        self.unreg_state_cb()
        self.unreg_msg_cb()



