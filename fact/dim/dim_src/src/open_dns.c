/*
 * A utility file. 
 *
 * Started date   : 10-11-91
 * Written by     : C. Gaspar
 * UNIX adjustment: G.C. Ballintijn
 *
 */

#define DIMLIB
#include <dim.h>

#define MAX_DNS_NODE 256

typedef struct {
	char node_name[MAX_NODE_NAME];
	char task_name[MAX_TASK_NAME];
	void (*recv_rout)();
	void (*error_rout)();
	TIMR_ENT *timr_ent;
	SRC_TYPES src_type;
} PENDING_CONN;

typedef struct dns_ent{
	struct dns_ent *next;
	struct dns_ent *prev;
	char node_name[MAX_DNS_NODE];
	char task_name[MAX_TASK_NAME];
	int port_number;
	void (*recv_rout)();
	void (*error_rout)();
	TIMR_ENT *timr_ent;
	SRC_TYPES src_type;
	int conn_id;
	int pending;
	int connecting;
} DNS_CONN;

static int Timer_q = 0;
static DNS_CONN *DNS_ids[3] = {0, 0, 0};
static DNS_CONN *DNS_conn_head = (DNS_CONN *)0;	


_DIM_PROTO( void retry_dns_connection,    ( int conn_pend_id ) );
_DIM_PROTO( void init_dns_list,    (  ) );
_DIM_PROTO( void set_dns_pars,    ( DNS_CONN *connp, char *node, int port ) );
_DIM_PROTO( int get_dns_pars,    ( DNS_CONN *connp, char *node, int *port ) );


int dim_set_dns_node(char *node)
{
	init_dns_list();
	set_dns_pars(DNS_ids[SRC_DIS], node, 0);
	set_dns_pars(DNS_ids[SRC_DIC], node, 0);
	return(1);
}

int dic_set_dns_node(char *node)
{
	init_dns_list();
	set_dns_pars(DNS_ids[SRC_DIC], node, 0);
	return(1);
}

int dis_set_dns_node(char *node)
{
	init_dns_list();
	set_dns_pars(DNS_ids[SRC_DIS], node, 0);
	return(1);
}

int dim_get_dns_node(char *node)
{
	register int node_exists;
	int port;
	init_dns_list();
	node_exists = get_dns_pars(DNS_ids[SRC_DIS], node, &port);
	return(node_exists);
}

int dic_get_dns_node(char *node)
{
	register int node_exists;
	int port;
	init_dns_list();
	node_exists = get_dns_pars(DNS_ids[SRC_DIC], node, &port);
	return(node_exists);
}

int dis_get_dns_node(char *node)
{
	register int node_exists;
	int port;
	init_dns_list();
	node_exists = get_dns_pars(DNS_ids[SRC_DIS], node, &port);
	return(node_exists);
}

int dim_set_dns_port(int port)
{
	init_dns_list();
	set_dns_pars(DNS_ids[SRC_DIS], 0, port);
	set_dns_pars(DNS_ids[SRC_DIC], 0, port);
	return(1);
}

int dic_set_dns_port(int port)
{
	init_dns_list();
	set_dns_pars(DNS_ids[SRC_DIC], 0, port);
	return(1);
}

int dis_set_dns_port(int port)
{
	init_dns_list();
	set_dns_pars(DNS_ids[SRC_DIS], 0, port);
	return(1);
}

int dim_get_dns_port()
{
int port;
char node[MAX_DNS_NODE];
	init_dns_list();
	get_dns_pars(DNS_ids[SRC_DIS], node, &port);
	return(port);
}

int dic_get_dns_port()
{
int port;
char node[MAX_DNS_NODE];
	init_dns_list();
	get_dns_pars(DNS_ids[SRC_DIC], node, &port);
	return(port);
}

int dis_get_dns_port()
{
int port;
char node[MAX_DNS_NODE];
	init_dns_list();
	get_dns_pars(DNS_ids[SRC_DIS], node, &port);
	return(port);
}

void rand_tmout_init()
{
	char pid_str[MAX_TASK_NAME];
	int ip, pid;
	extern int get_node_addr();
	extern int get_proc_name();

	get_node_addr((char *)&ip);
	get_proc_name(pid_str);
	sscanf(pid_str,"%d",&pid);
	srand((unsigned)(ip+pid));
}

int rand_tmout( int min, int max )
{
	int aux;

	aux = rand();
	aux %= (max - min);
	aux += min;
	return(aux);
}

void init_dns_list()
{
	char node[MAX_DNS_NODE];
	int port;
	dim_long sid, cid;

	DISABLE_AST
	if(!DNS_conn_head) 
	{
		DNS_conn_head = (DNS_CONN *)malloc(sizeof(DNS_CONN));
		dll_init( (DLL *) DNS_conn_head );
		node[0] = '\0';
		get_dns_node_name(node);
		port = get_dns_port_number();
		sid = dis_add_dns(node, port);
		cid = dic_add_dns(node, port);
		DNS_ids[SRC_DIS] = (DNS_CONN *)sid;
		DNS_ids[SRC_DIC] = (DNS_CONN *)cid;
		rand_tmout_init();
	}
	ENABLE_AST
}

void set_dns_pars(DNS_CONN *connp, char *node, int port)
{
	if(node != 0)
	{
		strcpy(connp->node_name, node);
	}
	if(port != 0)
	{
		connp->port_number = port;
	}
}

int get_dns_pars(DNS_CONN *connp, char *node, int *port)
{
	int exists = 0;

	if(connp->node_name[0])
	{
		strcpy(node, connp->node_name);
		exists = 1;
	}
	*port = connp->port_number;
	return exists;
}

DNS_CONN *find_dns(char *node_name, int port_number, SRC_TYPES src_type)
{
	DNS_CONN *connp;

	connp = DNS_conn_head;
	while( (connp = (DNS_CONN *)dll_get_next( (DLL *) DNS_conn_head, 
			(DLL*) connp)) )
	{
		if(connp->src_type == src_type)
		{
			if((!strcmp(connp->node_name, node_name)) &&
				(connp->port_number == port_number))
				return connp;
		}
	}
	return (DNS_CONN *)0;
}

dim_long dis_add_dns(char *node_name, int port_number)
{
	DNS_CONN *connp;

	init_dns_list();
	if(!(connp = find_dns(node_name, port_number, SRC_DIS)))
	{
		connp = (DNS_CONN *)malloc(sizeof(DNS_CONN));
		strcpy(connp->node_name, node_name);
		connp->port_number = DNS_PORT;
		if(port_number != 0)
			connp->port_number = port_number;
		connp->src_type = SRC_DIS;
		connp->pending = 0;
		connp->conn_id = 0;
		connp->connecting = 0;
		dll_insert_queue( (DLL *) DNS_conn_head, (DLL *) connp );
	}
	return (dim_long)connp;
}

dim_long dic_add_dns(char *node_name, int port_number)
{
	DNS_CONN *connp;

	init_dns_list();
	if(!(connp = find_dns(node_name, port_number, SRC_DIC)))
	{
		connp = (DNS_CONN *)malloc(sizeof(DNS_CONN));
		strcpy(connp->node_name, node_name);
		connp->port_number = DNS_PORT;
		if(port_number != 0)
			connp->port_number = port_number;
		connp->src_type = SRC_DIC;
		connp->pending = 0;
		connp->conn_id = 0;
		connp->connecting = 0;
		dll_insert_queue( (DLL *) DNS_conn_head, (DLL *) connp );
	}
	return (dim_long)connp;
}

DNS_CONN *get_dns(DNS_CONN *connp, SRC_TYPES src_type)
{
	DNS_CONN *p = 0;

	init_dns_list();
	if(connp)
	{
		if(connp->src_type == src_type)
		{
			p = connp;
		}
	}
	else
	{
		p = DNS_ids[src_type];
	}
	return p;
}

int close_dns(dim_long dnsid, SRC_TYPES src_type)
{
	DNS_CONN *connp;

	connp = get_dns((DNS_CONN *)dnsid, src_type);
	if( !Timer_q )
		Timer_q = dtq_create();
	if( connp->pending ) 
	{
		connp->pending = 0;
		dtq_rem_entry( Timer_q, connp->timr_ent );
	}
	return 1;
}

int open_dns(dim_long dnsid, void (*recv_rout)(), void (*error_rout)(), int tmout_min, int tmout_max, SRC_TYPES src_type )
{
	char nodes[MAX_DNS_NODE];
	char node_info[MAX_NODE_NAME+4];
	register char *dns_node, *ptr; 
	register int conn_id;
	register int timeout, node_exists;
	int i, dns_port;
	int rand_tmout();
	DNS_CONN *connp;

	conn_id = 0;
	if( !Timer_q )
		Timer_q = dtq_create();

	connp = get_dns((DNS_CONN *)dnsid, src_type);
	node_exists = get_dns_pars(connp, nodes, &dns_port);
	if( !(connp->pending) ) 
	{
		if(!node_exists)
		{
			return(-2);
		}
		ptr = nodes;			
		while(1)
		{
			dns_node = ptr;
			if( (ptr = (char *)strchr(ptr,',')) )
			{
				*ptr = '\0';			
				ptr++;
			}
			strcpy(node_info,dns_node);
			for(i = 0; i < 4; i ++)
				node_info[(int)strlen(node_info)+i+1] = (char)0xff;
			connp->conn_id = 0;
			connp->connecting = 1;
			conn_id = dna_open_client( node_info, DNS_TASK, dns_port,
						 TCPIP, recv_rout, error_rout, src_type );
			connp->connecting = 0;
			if(conn_id)
				break;
			if( !ptr )
				break;
		}
		connp->conn_id = conn_id;
		if(!conn_id)
		{
			strncpy(connp->task_name, DNS_TASK, (size_t)MAX_TASK_NAME); 
			connp->recv_rout = recv_rout;
			connp->error_rout = error_rout;
			connp->pending = 1;
			timeout = rand_tmout( tmout_min, tmout_max );
			connp->timr_ent = dtq_add_entry( Timer_q, timeout,
				retry_dns_connection,
				connp );
			return( -1);
		}
	}
	else
		return(-1);
	return(conn_id);
}

void retry_dns_connection( DNS_CONN *connp )
{
	char nodes[MAX_DNS_NODE];
	char node_info[MAX_NODE_NAME+4];
	register char *dns_node, *ptr;
	register int conn_id, node_exists;
	static int retrying = 0;
	int i, dns_port;

	if( retrying ) return;
	retrying = 1;

	conn_id = 0;
	node_exists = get_dns_pars(connp, nodes, &dns_port);
	if(node_exists)
	{
		ptr = nodes;			
		while(1)
		{
			dns_node = ptr;
			if( (ptr = (char *)strchr(ptr,',')) )
			{
				*ptr = '\0';			
				ptr++;
			}
			strcpy(node_info,dns_node);
			for(i = 0; i < 4; i ++)
				node_info[(int)strlen(node_info)+i+1] = (char)0xff;
			connp->conn_id = 0;
			connp->connecting = 1;
			conn_id = dna_open_client( node_info, connp->task_name,
					 dns_port, TCPIP,
					 connp->recv_rout, connp->error_rout, connp->src_type );
			connp->connecting = 0;
			if( conn_id )
				break;
			if( !ptr )
				break;
		}
	}
	connp->conn_id = conn_id;
	if(conn_id)
	{
		connp->pending = 0;
		dtq_rem_entry( Timer_q, connp->timr_ent );
	}
	retrying = 0;
}	

dim_long dns_get_dnsid(int conn_id, SRC_TYPES src_type)
{
	DNS_CONN *connp;
	int found = 0;

	connp = DNS_conn_head;
	while( (connp = (DNS_CONN *)dll_get_next( (DLL *) DNS_conn_head, 
			(DLL*) connp)) )
	{
		if(connp->conn_id == conn_id)
		{
			found = 1;
			break;
		}
		else if((connp->conn_id == 0) && (connp->connecting))
		{
			connp->conn_id = conn_id;
			found = 1;
			break;
		}
	}
	if(found)
	{
		if(connp == DNS_ids[src_type])
		{
			return (dim_long)0;
		}
		else
		{
			return (dim_long)connp;
		}
	}
	return (dim_long)-1;
}
