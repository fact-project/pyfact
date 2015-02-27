/*
 * DIS (Delphi Information Server) Package implements a library of
 * routines to be used by servers.
 *
 * Started on		 : 10-11-91
 * Last modification : 28-07-94
 * Written by		 : C. Gaspar
 * Adjusted by	     : G.C. Ballintijn
 *
 */

#ifdef VMS
#	include <lnmdef.h>
#	include <ssdef.h>
#	include <descrip.h>
#	include <cfortran.h>
#endif
/*
#define DEBUG
*/
#include <time.h>
#ifdef VAX
#include <timeb.h>
#else
#include <sys/timeb.h>
#endif

#define DIMLIB
#include <dim.h>
#include <dis.h>

#define ALL 0
#define MORE 1
#define NONE 2

typedef struct dis_dns_ent {
	struct dis_dns_ent *next;
	struct dis_dns_ent *prev;
	dim_long dnsid;
	char task_name[MAX_NAME];
	TIMR_ENT *dns_timr_ent;
	DIS_DNS_PACKET dis_dns_packet;
	int dis_n_services;
	int dns_dis_conn_id;
	int dis_first_time;
	int serving;
	unsigned int dis_service_id;
	unsigned int dis_client_id;
	int updating_service_list;
} DIS_DNS_CONN;

typedef struct req_ent {
	struct req_ent *next;
	struct req_ent *prev;
	int conn_id;
	int service_id;
	int req_id;
	int type;
	struct serv *service_ptr;
	int timeout;
	int format;
	int first_time;
	int delay_delete;
	int to_delete;
	TIMR_ENT *timr_ent;
	struct reqp_ent *reqpp;
} REQUEST;

typedef struct serv {
	struct serv *next;
	struct serv *prev;
	char name[MAX_NAME];
	int id;
	int type;
	char def[MAX_NAME];
	FORMAT_STR format_data[MAX_NAME/4];
	int *address;
	int size;
	void (*user_routine)();
	dim_long tag;
	int registered;
	int quality;
	int user_secs;
	int user_millisecs;
	int tid;
	REQUEST *request_head;
	DIS_DNS_CONN *dnsp;
	int delay_delete;
	int to_delete;
} SERVICE;

typedef struct reqp_ent {
	struct reqp_ent *next;
	struct reqp_ent *prev;
	REQUEST *reqp;
} REQUEST_PTR;

typedef struct cli_ent {
	struct cli_ent *next;
	struct cli_ent *prev;
	int conn_id;
	REQUEST_PTR *requestp_head; 
	DIS_DNS_CONN *dnsp;
} CLIENT;

static CLIENT *Client_head = (CLIENT *)0;	

static DIS_DNS_CONN *DNS_head = (DIS_DNS_CONN *)0;	

/*
static char Task_name[MAX_NAME];
static TIMR_ENT *Dns_timr_ent = (TIMR_ENT *)0;
static DIS_DNS_PACKET Dis_dns_packet = {0, 0, {0}};
static int Dis_n_services = 0;
*/
static int Dis_first_time = 1;
/*
static int Dns_dis_conn_id = 0;
*/
static int Protocol;
static int Port_number;
static int Dis_conn_id = 0;
static int Curr_conn_id = 0;
static int Serving = 0;
static void (*Client_exit_user_routine)() = 0;
static void (*Exit_user_routine)() = 0;
static void (*Error_user_routine)() = 0;
static int Error_conn_id = 0;
DIS_DNS_CONN *Default_DNS = 0;

typedef struct exit_ent {
	struct exit_ent *next;
	int conn_id;
	int exit_id;
	char node[MAX_NODE_NAME];
	char task[MAX_TASK_NAME];
} EXIT_H;

static EXIT_H *Exit_h_head = (EXIT_H *)0;

/* Do not forget to increase when this file is modified */
static int Version_number = DIM_VERSION_NUMBER;
static int Dis_timer_q = 0;
static int Threads_off = 0;
/*
static unsigned int Dis_service_id, Dis_client_id;
static int Updating_service_list = 0;
*/
static int Last_client;
static int Last_n_clients;


#ifdef DEBUG
static int Debug_on = 1;
#else
static int Debug_on = 0;
#endif

_DIM_PROTO( static void dis_insert_request, (int conn_id, DIC_PACKET *dic_packet,
				  int size, int status ) );
_DIM_PROTO( int execute_service,	(int req_id) );
_DIM_PROTO( void execute_command,	(SERVICE *servp, DIC_PACKET *packet) );
_DIM_PROTO( void register_dns_services,  (int flag) );
_DIM_PROTO( void register_services,  (DIS_DNS_CONN *dnsp, int flag, int dns_flag) );
_DIM_PROTO( void std_cmnd_handler,   (dim_long *tag, int *cmnd_buff, int *size) );
_DIM_PROTO( void client_info,		(dim_long *tag, int **bufp, int *size) );
_DIM_PROTO( void service_info,	   (dim_long *tag, int **bufp, int *size) );
_DIM_PROTO( void add_exit_handler,   (int *tag, int *bufp, int *size) );
_DIM_PROTO( static void exit_handler,	   (int *tag, int *bufp, int *size) );
_DIM_PROTO( static void error_handler,	   (int conn_id, int severity, int errcode, char *reason) );
_DIM_PROTO( SERVICE *find_service,   (char *name) );
_DIM_PROTO( CLIENT *find_client,   (int conn_id) );
_DIM_PROTO( static int get_format_data, (FORMAT_STR *format_data, char *def) );
_DIM_PROTO( static int release_conn, (int conn_id, int print_flag, int dns_flag) );
_DIM_PROTO( SERVICE *dis_hash_service_exists, (char *name) );
_DIM_PROTO( SERVICE *dis_hash_service_get_next, (int *start, SERVICE *prev, int flag) );
_DIM_PROTO( static unsigned do_dis_add_service_dns, (char *name, char *type, void *address, int size, 
								   void (*user_routine)(), dim_long tag, dim_long dnsid ) );
_DIM_PROTO( static DIS_DNS_CONN *create_dns, (dim_long dnsid) );

void dis_set_debug_on()
{
	Debug_on = 1;
}

void dis_set_debug_off()
{
	Debug_on = 0;
}

void dis_no_threads()
{
	Threads_off = 1;
}

static DIS_STAMPED_PACKET *Dis_packet = 0;
static int Dis_packet_size = 0;

int dis_set_buffer_size(int size)
{
	if(Dis_packet_size)
		free(Dis_packet);
	Dis_packet = (DIS_STAMPED_PACKET *)malloc((size_t)(DIS_STAMPED_HEADER + size));
	if(Dis_packet)
	{
		Dis_packet_size = DIS_STAMPED_HEADER + size;
		return(1);
	}
	else
		return(0);
}

static int check_service_name(char *name)
{
	if((int)strlen(name) > (MAX_NAME - 1))
		return(0);
	return(1);
}

void dis_init()
{
	int dis_hash_service_init();
	void dis_dns_init();

	dis_dns_init();
	{
	DISABLE_AST
	dis_hash_service_init();
	ENABLE_AST
	}
}

static unsigned do_dis_add_service_dns( char *name, char *type, void *address, int size, 
								   void (*user_routine)(), dim_long tag, dim_long dnsid )
{
	register SERVICE *new_serv;
	register int service_id;
	char str[512];
	int dis_hash_service_insert();
	DIS_DNS_CONN *dnsp;
	extern DIS_DNS_CONN *dis_find_dns(dim_long);

	dis_init();
	{
	DISABLE_AST
	if(Serving == -1)
	{
		ENABLE_AST
		return((unsigned) 0);
	}
	if(!check_service_name(name))
	{
		strcpy(str,"Service name too long: ");
		strcat(str,name);
		error_handler(0, DIM_ERROR, DIMSVCTOOLG, str, -1);
		ENABLE_AST
		return((unsigned) 0);
	}
	if( find_service(name) )
	{
		strcpy(str,"Duplicate Service: ");
		strcat(str,name);
		error_handler(0, DIM_ERROR, DIMSVCDUPLC, str, -1);
		ENABLE_AST
		return((unsigned) 0);
	}
	new_serv = (SERVICE *)malloc( sizeof(SERVICE) );
	strncpy( new_serv->name, name, (size_t)MAX_NAME );
	if(type != (char *)0)
	{
		if ((int)strlen(type) >= MAX_NAME)
		{
			strcpy(str,"Format String Too Long: ");
			strcat(str,name);
			error_handler(0, DIM_ERROR, DIMSVCFORMT, str, -1);
			free(new_serv);
			ENABLE_AST
			return((unsigned) 0);
		}
		if (! get_format_data(new_serv->format_data, type))
		{
			strcpy(str,"Bad Format String: ");
			strcat(str,name);
			error_handler(0, DIM_ERROR, DIMSVCFORMT, str, -1);
			free(new_serv);
			ENABLE_AST
			return((unsigned) 0);
		}
		strcpy(new_serv->def,type); 
	}
	else
	{
		new_serv->format_data[0].par_bytes = 0;
		new_serv->def[0] = '\0';
	}
	new_serv->type = 0;
	new_serv->address = (int *)address;
	new_serv->size = size;
	new_serv->user_routine = user_routine;
	new_serv->tag = tag;
	new_serv->registered = 0;
	new_serv->quality = 0;
	new_serv->user_secs = 0;
	new_serv->tid = 0;
	new_serv->delay_delete = 0;
	new_serv->to_delete = 0;
	dnsp = dis_find_dns(dnsid);
	if(!dnsp)
		dnsp = create_dns(dnsid);
	new_serv->dnsp = dnsp;
	service_id = id_get((void *)new_serv, SRC_DIS);
	new_serv->id = service_id;
	new_serv->request_head = (REQUEST *)malloc(sizeof(REQUEST));
	dll_init( (DLL *) (new_serv->request_head) );
	dis_hash_service_insert(new_serv);
/*
	Dis_n_services++;
*/
	dnsp->dis_n_services++;
	ENABLE_AST
	}
	return((unsigned)service_id);
}

static unsigned do_dis_add_service( char *name, char *type, void *address, int size, 
								   void (*user_routine)(), dim_long tag )
{
	return do_dis_add_service_dns( name, type, address, size, 
								   user_routine, tag, 0 );
}

#ifdef VxWorks
void dis_destroy(int tid)
{
register SERVICE *servp, *prevp;
int n_left = 0;

	prevp = 0;
	while( servp = dis_hash_service_get_next(prevp))
	{
		if(servp->tid == tid)
		{
			dis_remove_service(servp->id);
		}
		else
		{
			prevp = servp;
			n_left++;
		}
	}
	if(n_left == 5)
	{
		prevp = 0;
		while( servp = dis_hash_service_get_next(prevp))
		{
			dis_remove_service(servp->id);
		}
		dna_close(Dis_conn_id);
		dna_close(Dns_dis_conn_id);
		Dns_dis_conn_id = 0;
		Dis_first_time = 1;
		dtq_rem_entry(Dis_timer_q, Dns_timr_ent);
		Dns_timr_ent = NULL;
	}
}


#endif

unsigned dis_add_service( char *name, char *type, void *address, int size, 
						 void (*user_routine)(), dim_long tag)
{
	unsigned ret;
#ifdef VxWorks
	register SERVICE *servp;
#endif
/*
	DISABLE_AST
*/
	ret = do_dis_add_service( name, type, address, size, user_routine, tag);
#ifdef VxWorks
	servp = (SERVICE *)id_get_ptr(ret, SRC_DIS);
	servp->tid = taskIdSelf();
#endif
/*
	ENABLE_AST
*/
	return(ret);
}

unsigned dis_add_service_dns( dim_long dnsid, char *name, char *type, void *address, int size, 
							 void (*user_routine)(), dim_long tag)
{
	unsigned ret;
#ifdef VxWorks
	register SERVICE *servp;
#endif
/*
	DISABLE_AST
*/
	ret = do_dis_add_service_dns( name, type, address, size, user_routine, tag, dnsid);
#ifdef VxWorks
	servp = (SERVICE *)id_get_ptr(ret, SRC_DIS);
	servp->tid = taskIdSelf();
#endif
/*
	ENABLE_AST
*/
	return(ret);
}

static unsigned do_dis_add_cmnd_dns( char *name, char *type, void (*user_routine)(), dim_long tag, dim_long dnsid )
{
	register SERVICE *new_serv;
	register int service_id;
	char str[512];
	int dis_hash_service_insert();
	DIS_DNS_CONN *dnsp;
	extern DIS_DNS_CONN *dis_find_dns(dim_long);

	dis_init();
	{
	DISABLE_AST
	if(Serving == -1)
	{
		ENABLE_AST
		return((unsigned) 0);
	}
	if(!check_service_name(name))
	{
		strcpy(str,"Command name too long: ");
		strcat(str,name);
		error_handler(0, DIM_ERROR, DIMSVCTOOLG, str, -1);
		ENABLE_AST
		return((unsigned) 0);
	}
	if( find_service(name) )
	{
		ENABLE_AST
		return((unsigned) 0);
	}
	new_serv = (SERVICE *)malloc(sizeof(SERVICE));
	strncpy(new_serv->name, name, (size_t)MAX_NAME);
	if(type != (char *)0)
	{
		if( !get_format_data(new_serv->format_data, type))
		{
			ENABLE_AST
			return((unsigned) 0);
		}
		strcpy(new_serv->def,type); 
	}
	else
	{
		new_serv->format_data[0].par_bytes = 0;
		new_serv->def[0] = '\0';
	}
	new_serv->type = COMMAND;
	new_serv->address = 0;
	new_serv->size = 0;
	if(user_routine)
		new_serv->user_routine = user_routine;
	else
		new_serv->user_routine = std_cmnd_handler;
	new_serv->tag = tag;
	new_serv->tid = 0;
	new_serv->registered = 0;
	new_serv->quality = 0;
	new_serv->user_secs = 0;
	new_serv->delay_delete = 0;
	new_serv->to_delete = 0;
	service_id = id_get((void *)new_serv, SRC_DIS);
	new_serv->id = service_id;
	dnsp = dis_find_dns(dnsid);
	if(!dnsp)
		dnsp = create_dns(dnsid);
	new_serv->dnsp = dnsp;
	new_serv->request_head = (REQUEST *)malloc(sizeof(REQUEST));
	dll_init( (DLL *) (new_serv->request_head) );
	dis_hash_service_insert(new_serv);
/*
	Dis_n_services++;
*/
	dnsp->dis_n_services++;
	ENABLE_AST
	}
	return((unsigned) service_id);
}

static unsigned do_dis_add_cmnd( char *name, char *type, void (*user_routine)(), dim_long tag)
{
	return do_dis_add_cmnd_dns(name, type, user_routine, tag, 0);
}

unsigned dis_add_cmnd( char *name, char *type, void (*user_routine)(), dim_long tag ) 
{
	unsigned ret;

/*
	DISABLE_AST
*/
	ret = do_dis_add_cmnd( name, type, user_routine, tag );
/*
	ENABLE_AST
*/
	return(ret);
}

unsigned dis_add_cmnd_dns( dim_long dnsid, char *name, char *type, void (*user_routine)(), dim_long tag ) 
{
	unsigned ret;

	/*
	DISABLE_AST
	*/
	ret = do_dis_add_cmnd_dns( name, type, user_routine, tag, dnsid );
	/*
	ENABLE_AST
	*/
	return(ret);
}

void dis_add_client_exit_handler( void (*user_routine)()) 
{

	DISABLE_AST
	Client_exit_user_routine = user_routine;
	ENABLE_AST
}

void dis_add_exit_handler( void (*user_routine)()) 
{

	DISABLE_AST
	Exit_user_routine = user_routine;
	ENABLE_AST
}

void dis_add_error_handler( void (*user_routine)())
{

	DISABLE_AST
	Error_user_routine = user_routine;
	ENABLE_AST
}

static int get_format_data(FORMAT_STR *format_data, char *def)
{
	register char code, last_code = 0;
	int num;

	code = *def;
	while(*def)
	{
		if(code != last_code)
		{
			format_data->par_num = 0;
			format_data->flags = 0;
			switch(code)
			{
				case 'i':
				case 'I':
				case 'l':
				case 'L':
					format_data->par_bytes = SIZEOF_LONG;
					format_data->flags |= SWAPL;
					break;
				case 'x':
				case 'X':
					format_data->par_bytes = SIZEOF_DOUBLE;
					format_data->flags |= SWAPD;
					break;
				case 's':
				case 'S':
					format_data->par_bytes = SIZEOF_SHORT;
					format_data->flags |= SWAPS;
					break;
				case 'f':
				case 'F':
					format_data->par_bytes = SIZEOF_FLOAT;
					format_data->flags |= SWAPL;
#ifdef vms      	
					format_data->flags |= IT_IS_FLOAT;
#endif
					break;
				case 'd':
				case 'D':
					format_data->par_bytes = SIZEOF_DOUBLE;
					format_data->flags |= SWAPD;
#ifdef vms
					format_data->flags |= IT_IS_FLOAT;
#endif
					break;
				case 'c':
				case 'C':
				case 'b':
				case 'B':
				case 'v':
				case 'V':
					format_data->par_bytes = SIZEOF_CHAR;
					format_data->flags |= NOSWAP;
					break;
			}
		}
		def++;
		if(*def != ':')
		{
			if(*def)
			{
/*
				printf("Bad service definition parsing\n");
				fflush(stdout);

				error_handler("Bad service definition parsing",2);
*/
				return(0);
			}
			else
				format_data->par_num = 0;
		}
		else
		{
			def++;
			sscanf(def,"%d",&num);
			format_data->par_num += num;
			while((*def != ';') && (*def != '\0'))
				def++;
			if(*def)
				def++;
		}
		last_code = code;
		code = *def;
		if(code != last_code)
			format_data++;
	}
	format_data->par_bytes = 0;
	return(1);
}

void recv_dns_dis_rout( int conn_id, DNS_DIS_PACKET *packet, int size, int status )
{
	char str[128];
	int dns_timr_time;
	extern int rand_tmout(int, int);
	extern int open_dns(dim_long, void (*)(), void (*)(), int, int, int);
	extern DIS_DNS_CONN *find_dns_by_conn_id(int);
	extern void do_register_services(DIS_DNS_CONN *);
	extern void do_dis_stop_serving_dns(DIS_DNS_CONN *);
	DIS_DNS_CONN *dnsp;
	int type, exit_code;

	if(size){}
	dnsp = find_dns_by_conn_id(conn_id);
	if(!dnsp)
	{
		return;
	}
	switch(status)
	{
	case STA_DISC:	   /* connection broken */
		if( dnsp->dns_timr_ent ) {
			dtq_rem_entry( Dis_timer_q, dnsp->dns_timr_ent );
			dnsp->dns_timr_ent = NULL;
		}

		if(dnsp->dns_dis_conn_id > 0)
			dna_close(dnsp->dns_dis_conn_id);
		if(Serving == -1)
			return;
		if(dnsp->serving)
		{
			dnsp->dns_dis_conn_id = open_dns(dnsp->dnsid, recv_dns_dis_rout, error_handler,
					DIS_DNS_TMOUT_MIN, DIS_DNS_TMOUT_MAX, SRC_DIS );
			if(dnsp->dns_dis_conn_id == -2)
				error_handler(0, DIM_FATAL, DIMDNSUNDEF, "DIM_DNS_NODE undefined", -1);
		}
		break;
	case STA_CONN:		/* connection received */
		if(dnsp->serving)
		{
			dnsp->dns_dis_conn_id = conn_id;
			register_services(dnsp, ALL, 0);
			dns_timr_time = rand_tmout(WATCHDOG_TMOUT_MIN, 
							 WATCHDOG_TMOUT_MAX);
			dnsp->dns_timr_ent = dtq_add_entry( Dis_timer_q,
						  dns_timr_time,
						  do_register_services, dnsp ); 
		}
		else
		{
			dna_close(conn_id);
		}
		break;
	default :	   /* normal packet */
		if(vtohl(packet->size) != DNS_DIS_HEADER)
			break;
		type = vtohl(packet->type);
		exit_code = (type >> 16) & 0xFFFF;
		type &= 0xFFFF;
		switch(type)
		{
		case DNS_DIS_REGISTER :
			sprintf(str, 
				"%s: Watchdog Timeout, DNS requests registration",
				dnsp->task_name);
			error_handler(0, DIM_WARNING, DIMDNSTMOUT, str, -1);
			register_services(dnsp, ALL, 0);
			break;
		case DNS_DIS_KILL :
			sprintf(str,
				"%s: Some Services already known to DNS",
				dnsp->task_name);
			/*
			exit(2);
			*/
			Serving = -1;
			error_handler(0, DIM_FATAL, DIMDNSDUPLC, str, -1);
			/*
			do_dis_stop_serving_dns(dnsp);
			dis_stop_serving();
			*/
/*
			exit_tag = 0;
			exit_code = 2;
			exit_size = sizeof(int);
			exit_handler(&exit_tag, &exit_code, &exit_size);
*/
			break;
		case DNS_DIS_STOP :
			sprintf(str, 
				"%s: DNS refuses connection",dnsp->task_name);
/*
			exit(2);
*/
			Serving = -1;
			error_handler(0, DIM_FATAL, DIMDNSREFUS, str, -1);
			/*
			do_dis_stop_serving_dns(dnsp);
			dis_stop_serving();
			*/
/*
			exit_tag = 0;
			exit_code = 2;
			exit_size = sizeof(int);
			exit_handler(&exit_tag, &exit_code, &exit_size);
*/
			break;
		case DNS_DIS_EXIT :
			sprintf(str, 
				"%s: DNS requests Exit",dnsp->task_name);
/*
			Serving = -1;
*/
			error_handler(0, DIM_FATAL, DIMDNSEXIT, str, -1);
			break;
		case DNS_DIS_SOFT_EXIT :
			sprintf(str, 
				"%s: DNS requests Exit(%d)",dnsp->task_name, exit_code);
/*
			Serving = -1;
*/
			error_handler(0, DIM_FATAL, DIMDNSEXIT, str, exit_code);
			break;
		}
		break;
	}
}


/* register services within the name server
 *
 * Send services uses the DNA package. services is a linked list of services
 * stored by add_service.
 */

int send_dns_update_packet(DIS_DNS_CONN *dnsp)
{
  DIS_DNS_PACKET *dis_dns_p = &(dnsp->dis_dns_packet);
  int n_services;
  SERVICE_REG *serv_regp;

  n_services = 1;
  dis_dns_p->n_services = htovl(n_services);
  dis_dns_p->size = htovl(DIS_DNS_HEADER +
					n_services * (int)sizeof(SERVICE_REG));
  serv_regp = dis_dns_p->services;
  strcpy( serv_regp->service_name, "DUMMY_UPDATE_PACKET" );
  if(dnsp->dns_dis_conn_id > 0)
  {
if(Debug_on)
{
dim_print_date_time();
 printf("Sending UpdatePacket to dns %d as %s@%s, %d services\n",
	dnsp->dns_dis_conn_id,
	(&(dnsp->dis_dns_packet))->task_name, (&(dnsp->dis_dns_packet))->node_name, n_services);
}
      if( !dna_write(dnsp->dns_dis_conn_id, &(dnsp->dis_dns_packet),
		     DIS_DNS_HEADER + n_services * (int)sizeof(SERVICE_REG)))
	  {
		release_conn(dnsp->dns_dis_conn_id, 0, 1);
	  }
  }
  return(1);
}

void do_register_services(DIS_DNS_CONN *dnsp)
{
	register_services(dnsp, NONE, 0);
}

void register_services(DIS_DNS_CONN *dnsp, int flag, int dns_flag)
{
	register DIS_DNS_PACKET *dis_dns_p = &(dnsp->dis_dns_packet);
	register int n_services, tot_n_services;
	register SERVICE *servp;
	register SERVICE_REG *serv_regp;
	int hash_index, new_entries;
	extern int get_node_addr();
	int dis_hash_service_registered();

	if(!dis_dns_p->src_type)
	{
		get_node_name( dis_dns_p->node_name );
/*
		strcpy( dis_dns_p->task_name, Task_name );
*/
		strncpy( dis_dns_p->task_name, dnsp->task_name,
			(size_t)(MAX_TASK_NAME-4) );
		dis_dns_p->task_name[MAX_TASK_NAME-4-1] = '\0';
		get_node_addr( dis_dns_p->node_addr );
/*
		dis_dns_p->port = htovl(Port_number);
*/
		dis_dns_p->pid = htovl(getpid());
		dis_dns_p->protocol = htovl(Protocol);
		dis_dns_p->src_type = htovl(SRC_DIS);
		dis_dns_p->format = htovl(MY_FORMAT);
if(Debug_on)
{
dim_print_date_time();
 printf("Registering as %d %s@%s\n",
	dis_dns_p->pid, dis_dns_p->task_name, dis_dns_p->node_name);
}
	
	}

	dis_dns_p->port = htovl(Port_number);
	serv_regp = dis_dns_p->services;
	n_services = 0;
	tot_n_services = 0;
	if( flag == NONE ) {
		dis_dns_p->n_services = htovl(n_services);
		dis_dns_p->size = htovl( DIS_DNS_HEADER + 
			(n_services*(int)sizeof(SERVICE_REG)));
		if(dnsp->dns_dis_conn_id > 0)
		{
if(Debug_on)
{
dim_print_date_time();
 printf("Sending NONE to dns %d as %s@%s, %d services\n",
	dnsp->dns_dis_conn_id,
	(&(dnsp->dis_dns_packet))->task_name, (&(dnsp->dis_dns_packet))->node_name, n_services);
}
			if(!dna_write(dnsp->dns_dis_conn_id, &(dnsp->dis_dns_packet), 
				DIS_DNS_HEADER + n_services*(int)sizeof(SERVICE_REG)))
			{
				release_conn(dnsp->dns_dis_conn_id, 0, 1);
			}
		}
		return;
	}
	if(flag == ALL)
	{
		servp = 0;
		hash_index = -1;
		while( (servp = dis_hash_service_get_next(&hash_index, servp, 0)))
		{
			if(servp->dnsp == dnsp)
				servp->registered  = 0;
		}
	}
	servp = 0;
	hash_index = -1;
	new_entries = 0;
	if(flag == MORE)
		new_entries = 1;
	while( (servp = dis_hash_service_get_next(&hash_index, servp, new_entries)))
	{
		if( flag == MORE ) 
		{
			if( servp->registered )
			{
				continue;
			}
		}

		if(servp->dnsp != dnsp)
			continue;

if(Debug_on)
{
dim_print_date_time();
 printf("Registering %s\n",
	servp->name);
}
		strcpy( serv_regp->service_name, servp->name );
		strcpy( serv_regp->service_def, servp->def );
		if(servp->type == COMMAND)
			serv_regp->service_id = htovl( servp->id | 0x10000000);
		else
			serv_regp->service_id = htovl( servp->id );

		serv_regp++;
		n_services++;
		dis_hash_service_registered(hash_index, servp);
		if( n_services == MAX_SERVICE_UNIT )
		{
			dis_dns_p->n_services = htovl(n_services);
			dis_dns_p->size = (int)htovl(DIS_DNS_HEADER +
				n_services * (int)sizeof(SERVICE_REG));
			if(dnsp->dns_dis_conn_id > 0)
			{
if(Debug_on)
{
dim_print_date_time();
 printf("Sending MAX_SERVICE_UNIT to dns %d as %s@%s, %d services\n",
	dnsp->dns_dis_conn_id,
	(&(dnsp->dis_dns_packet))->task_name, (&(dnsp->dis_dns_packet))->node_name, n_services);
}
				if( !dna_write(dnsp->dns_dis_conn_id,
					   &(dnsp->dis_dns_packet), 
					   DIS_DNS_HEADER + n_services *
						(int)sizeof(SERVICE_REG)) )
				{
					release_conn(dnsp->dns_dis_conn_id, 0, 1);
				}
			}
			serv_regp = dis_dns_p->services;
			tot_n_services += MAX_SERVICE_UNIT;
			n_services = 0;
			continue;
		}
	}
	if( n_services ) 
	{
		dis_dns_p->n_services = htovl(n_services);
		dis_dns_p->size = htovl(DIS_DNS_HEADER +
					n_services * (int)sizeof(SERVICE_REG));
		if(dnsp->dns_dis_conn_id > 0)
		{
if(Debug_on)
{
dim_print_date_time();
 printf("Sending to dns %d as %s@%s, %d services\n",
	dnsp->dns_dis_conn_id,
	(&(dnsp->dis_dns_packet))->task_name, (&(dnsp->dis_dns_packet))->node_name, n_services);
}
			if( !dna_write(dnsp->dns_dis_conn_id, &(dnsp->dis_dns_packet),
				DIS_DNS_HEADER + n_services * (int)sizeof(SERVICE_REG)))
			{
				release_conn(dnsp->dns_dis_conn_id, 0, 1);
			}

		}
		tot_n_services += n_services;
	}
	if(!dns_flag)
	{
		if(tot_n_services >= MAX_REGISTRATION_UNIT)
		{
			send_dns_update_packet(dnsp);
		}
	}
}

void unregister_service(DIS_DNS_CONN *dnsp, SERVICE *servp)
{
	register DIS_DNS_PACKET *dis_dns_p = &(dnsp->dis_dns_packet);
	register int n_services;
	register SERVICE_REG *serv_regp;
	extern int get_node_addr();

	if(dnsp->dns_dis_conn_id > 0)
	{
		if(!dis_dns_p->src_type)
		{
			get_node_name( dis_dns_p->node_name );
/*
			strcpy( dis_dns_p->task_name, Task_name );
*/
			strncpy( dis_dns_p->task_name, dnsp->task_name,
				(size_t)(MAX_TASK_NAME-4) );
			dis_dns_p->task_name[MAX_TASK_NAME-4-1] = '\0';
			get_node_addr( dis_dns_p->node_addr );
			dis_dns_p->port = htovl(Port_number);
			dis_dns_p->protocol = htovl(Protocol);
			dis_dns_p->src_type = htovl(SRC_DIS);
			dis_dns_p->format = htovl(MY_FORMAT);
		}
		serv_regp = dis_dns_p->services;
		strcpy( serv_regp->service_name, servp->name );
		strcpy( serv_regp->service_def, servp->def );
		serv_regp->service_id = (int)htovl( (unsigned)servp->id | 0x80000000);
		serv_regp++;
		n_services = 1;
		servp->registered = 0;
		dis_dns_p->n_services = htovl(n_services);
		dis_dns_p->size = htovl(DIS_DNS_HEADER +
				n_services * (int)sizeof(SERVICE_REG));

if(Debug_on)
{
dim_print_date_time();
 printf("Sending UNREGISTER to dns %d as %s@%s, %d services\n",
	dnsp->dns_dis_conn_id,
	(&(dnsp->dis_dns_packet))->task_name, (&(dnsp->dis_dns_packet))->node_name, n_services);
}
		if( !dna_write(dnsp->dns_dis_conn_id, &(dnsp->dis_dns_packet), 
			DIS_DNS_HEADER + n_services * (int)sizeof(SERVICE_REG)) )
		{
			release_conn(dnsp->dns_dis_conn_id, 0, 1);
		}
		if(dnsp->dis_service_id)
			dis_update_service(dnsp->dis_service_id);
	}
}

void do_update_service_list(DIS_DNS_CONN *dnsp)
{
	dnsp->updating_service_list = 0;
	if(dnsp->dis_service_id)
		dis_update_service(dnsp->dis_service_id);
}

/* start serving client requests
 *
 * Using the DNA package start accepting requests from clients.
 * When a request arrives the routine "dis_insert_request" will be executed.
 */

int dis_start_serving(char *task)
{
	return dis_start_serving_dns(0, task);
}

static DIS_DNS_CONN *create_dns(dim_long dnsid)
{
	DIS_DNS_CONN *dnsp;

	dnsp = malloc(sizeof(DIS_DNS_CONN));
	dnsp->dns_timr_ent = (TIMR_ENT *)0;
	dnsp->dis_n_services = 0;
	dnsp->dns_dis_conn_id = 0;
	dnsp->dis_first_time = 1;
	dnsp->serving = 0;
	dnsp->dis_dns_packet.size = 0;
	dnsp->dis_dns_packet.src_type = 0;
	dnsp->dis_dns_packet.node_name[0] = 0;
	dnsp->updating_service_list = 0;
	dnsp->dnsid = dnsid;
	dll_insert_queue( (DLL *) DNS_head, (DLL *) dnsp );
	return dnsp;
}

void dis_dns_init()
{
	static int done = 0;
	DIS_DNS_CONN *dnsp;
	void dim_init_threads(void);

	if(!done)
	{
		if(!Threads_off)
		{
			dim_init_threads();
		}
		{
		DISABLE_AST
		if(!DNS_head) 
		{
			DNS_head = (DIS_DNS_CONN *)malloc(sizeof(DIS_DNS_CONN));
			dll_init( (DLL *) DNS_head );
		}
		dnsp = create_dns(0);
		Default_DNS = dnsp;
		done = 1;
		ENABLE_AST
		}
	}
}

int dis_start_serving_dns(dim_long dnsid, char *task/*, int *idlist*/)
{
	char str0[MAX_NAME], str1[MAX_NAME],str2[MAX_NAME],
	  str3[MAX_NAME],str4[MAX_NAME];
	char task_name_aux[MAX_TASK_NAME];
	extern int open_dns();
	extern DIS_DNS_CONN *dis_find_dns(dim_long);
	DIS_DNS_CONN *dnsp;
	unsigned int more_ids[10] = {0};

	dis_init();
	{
	DISABLE_AST
	if(Serving == -1)
	{
		ENABLE_AST
		return(0);
	}
	  /*
#ifdef VxWorks
	taskDeleteHookAdd(remove_all_services);
	printf("Adding delete hook\n");
#endif
*/

	if(!Client_head) 
	{
		Client_head = (CLIENT *)malloc(sizeof(CLIENT));
		dll_init( (DLL *) Client_head );
	}
	if(dnsid == 0)
	{
		dnsp = Default_DNS;
	}
	else if(!(dnsp = dis_find_dns(dnsid)))
	{
		dnsp = create_dns(dnsid);
	}
	dnsp->serving = 1;
	Serving = 1;
	if(Dis_first_time)
	{
		strncpy( task_name_aux, task, (size_t)MAX_TASK_NAME );
		task_name_aux[MAX_TASK_NAME-1] = '\0';
		Port_number = SEEK_PORT;
if(Debug_on)
{
dim_print_date_time();
 printf("Opening Server Connection %s\n",task_name_aux);
}
		if( !(Dis_conn_id = dna_open_server( task_name_aux, dis_insert_request, 
			&Protocol, &Port_number, error_handler) ))
		{
			ENABLE_AST
			return(0);
		}
		Dis_first_time = 0;
	}
	if(dnsp->dis_first_time)
	{
		dnsp->dis_first_time = 0;

		sprintf(str0, "%s/VERSION_NUMBER", task);
		sprintf(str1, "%s/CLIENT_LIST", task);
		sprintf(str2, "%s/SERVICE_LIST", task);
		sprintf(str3, "%s/SET_EXIT_HANDLER", task);
		sprintf(str4, "%s/EXIT", task);

		more_ids[0] = do_dis_add_service_dns( str0, "L", &Version_number,
						sizeof(Version_number), 0, 0, dnsid );

		more_ids[1] = do_dis_add_service_dns( str1, "C", 0, 0, client_info, (dim_long)dnsp, dnsid );
		dnsp->dis_client_id = more_ids[1];
		more_ids[2] = do_dis_add_service_dns( str2, "C", 0, 0, service_info, (dim_long)dnsp, dnsid );
		dnsp->dis_service_id = more_ids[2];
		more_ids[3] = do_dis_add_cmnd_dns( str3, "L:1", add_exit_handler, 0, dnsid );
		more_ids[4] = do_dis_add_cmnd_dns( str4, "L:1", exit_handler, 0, dnsid );
		more_ids[5] = 0;
		strcpy( dnsp->task_name, task );
if(Debug_on)
{
dim_print_date_time();
 printf("start serving %s\n",task);
}
	}
/*
	if(idlist)
	{
		for(i = 0; idlist[i]; i++)
		{
			servp = (SERVICE *)id_get_ptr(idlist[i], SRC_DIS);
			if(servp)
			{
				servp->dnsp = dnsp;
				n_services++;
			}
		}
	}
	if(dnsp != Default_DNS)
	{
		for(i = 0; more_ids[i]; i++)
		{
			servp = (SERVICE *)id_get_ptr(more_ids[i], SRC_DIS);
			if(servp)
			{
				servp->dnsp = dnsp;
				n_services++;
			}
		}
		dnsp->dis_n_services += n_services;
		Dis_n_services -= n_services;
	}
*/
	if(!Dis_timer_q)
		Dis_timer_q = dtq_create();
	if( !dnsp->dns_dis_conn_id )
	{
		if(!strcmp(task,"DIS_DNS"))
		{
			register_services(dnsp, ALL, 1);
			ENABLE_AST
			return(id_get(&(dnsp->dis_dns_packet), SRC_DIS));
		}
		else
		{
		
			dnsp->dns_dis_conn_id = open_dns(dnsid, recv_dns_dis_rout, error_handler,
					DIS_DNS_TMOUT_MIN, DIS_DNS_TMOUT_MAX, SRC_DIS );
			if(dnsp->dns_dis_conn_id == -2)
				error_handler(0, DIM_FATAL, DIMDNSUNDEF, "DIM_DNS_NODE undefined", -1);
		}
	}
	else
	{
		register_services(dnsp, MORE, 0);
		if(dnsp->dis_service_id)
		{
/*
			dis_update_service(Dis_service_id);
*/
			if(!dnsp->updating_service_list)
			{
				dtq_start_timer(1, do_update_service_list, dnsp);
				dnsp->updating_service_list = 1;
			}
		}
	}
	ENABLE_AST
	}
	return(1);
}


/* asynchrounous reception of requests */
/*
	Called by DNA package.
	A request has arrived, queue it to process later - dis_ins_request
*/
static void dis_insert_request(int conn_id, DIC_PACKET *dic_packet, int size, int status)
{
	register SERVICE *servp;
	register REQUEST *newp, *reqp;
	CLIENT *clip, *create_client();
	REQUEST_PTR *reqpp;
	int type, new_client = 0, found = 0;
	int find_release_request();
	DIS_DNS_CONN *dnsp;

	if(size){}
	/* status = 1 => new connection, status = -1 => conn. lost */
	if(!Client_head) 
	{
		Client_head = (CLIENT *)malloc(sizeof(CLIENT));
		dll_init( (DLL *) Client_head );
	}
	if(status != 0)
	{
		if(status == -1) /* release all requests from conn_id */
		{
if(Debug_on)
{
dim_print_date_time();
printf("Received Disconnection %d, from %s@%s\n",
	   conn_id, 
	   Net_conns[conn_id].task, Net_conns[conn_id].node);
}
			release_conn(conn_id, 0, 0);
		}
		else
		{
if(Debug_on)
{
dim_print_date_time();
printf("Received Connection %d, from %s@%s\n",
	   conn_id, 
	   Net_conns[conn_id].task, Net_conns[conn_id].node);
}
		}  
	} 
	else 
	{
if(Debug_on)
{
dim_print_date_time();
printf("Received Request for %s, from %d  %s@%s\n",
	   dic_packet->service_name, conn_id, 
	   Net_conns[conn_id].task, Net_conns[conn_id].node);
}
		dic_packet->type = vtohl(dic_packet->type);
		type = dic_packet->type & 0xFFF;
		/*
		if(type == COMMAND) 
		{
			Curr_conn_id = conn_id;
			execute_command(servp, dic_packet);
			Curr_conn_id = 0;
			return;
		}
		*/
		if(type == DIM_DELETE) 
		{
			find_release_request(conn_id, vtohl(dic_packet->service_id));
			return;
		}
		if(!(servp = find_service(dic_packet->service_name)))
		{
			release_conn(conn_id, 0, 0);
			return;
		}
		newp = (REQUEST *)/*my_*/malloc(sizeof(REQUEST));
		newp->service_ptr = servp;
		newp->service_id = vtohl(dic_packet->service_id);
		newp->type = dic_packet->type;
		newp->timeout = vtohl(dic_packet->timeout);
		newp->format = vtohl(dic_packet->format);
		newp->conn_id = conn_id;
		newp->first_time = 1;
		newp->delay_delete = 0;
		newp->to_delete = 0;
		newp->timr_ent = 0;
		newp->req_id = id_get((void *)newp, SRC_DIS);
		newp->reqpp = 0;
		if(type == ONCE_ONLY) 
		{
			execute_service(newp->req_id);
			id_free(newp->req_id, SRC_DIS);
			free(newp);
			clip = create_client(conn_id, servp, &new_client);
			return;
		}
		if(type == COMMAND) 
		{
			Curr_conn_id = conn_id;
			execute_command(servp, dic_packet);
			Curr_conn_id = 0;
			reqp = servp->request_head;
			while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
				(DLL *) reqp)) ) 
			{
				if(reqp->conn_id == conn_id)
				{
					id_free(newp->req_id, SRC_DIS);
					free(newp);
					found = 1;
					break;
				}
			}
			if(!found)
				dll_insert_queue( (DLL *) servp->request_head, (DLL *) newp );
			clip = create_client(conn_id, servp, &new_client);
			return;
		}
		dll_insert_queue( (DLL *) servp->request_head, (DLL *) newp );
		clip = create_client(conn_id, servp, &new_client);
		reqpp = (REQUEST_PTR *)malloc(sizeof(REQUEST_PTR));
		reqpp->reqp = newp;
		dll_insert_queue( (DLL *) clip->requestp_head, (DLL *) reqpp );
		newp->reqpp = reqpp;
		if((type != MONIT_ONLY) && (type != UPDATE))
		{
			execute_service(newp->req_id);
		}
		if((type != MONIT_ONLY) && (type != MONIT_FIRST))
		{
			if(newp->timeout != 0)
			{
				newp->timr_ent = dtq_add_entry( Dis_timer_q,
							newp->timeout, 
							execute_service,
							newp->req_id );
			}
		}
		if(new_client)
		{
			Last_client = conn_id;
			dnsp = clip->dnsp;
			if(dnsp->dis_client_id)
			  dis_update_service(dnsp->dis_client_id);
		}
	}
}

/* A timeout for a timed or monitored service occured, serve it. */

int execute_service( int req_id )
{
	int *buffp, size;
	register REQUEST *reqp;
	register SERVICE *servp;
	char str[80], def[MAX_NAME];
	int conn_id, last_conn_id;
	int *pkt_buffer, header_size, aux;
#ifdef WIN32
	struct timeb timebuf;
#else
	struct timeval tv;
	struct timezone *tz;
#endif
	FORMAT_STR format_data_cp[MAX_NAME/4];

	reqp = (REQUEST *)id_get_ptr(req_id, SRC_DIS);
	if(!reqp)
		return(0);
	if(reqp->to_delete)
		return(0);
	reqp->delay_delete++;
	servp = reqp->service_ptr;
	conn_id = reqp->conn_id;

if(Debug_on)
{
dim_print_date_time();
printf("Updating %s for %s@%s (req_id = %d)\n",
	   servp->name, 
	   Net_conns[conn_id].task, Net_conns[conn_id].node, 
	   reqp->req_id);
}

	last_conn_id = Curr_conn_id;
	Curr_conn_id = conn_id;
	if(servp->type == COMMAND)
	{
		sprintf(str,"This is a COMMAND Service");
		buffp = (int *)str;
		size = 26;
		sprintf(def,"c:26");
	}
	else if( servp->user_routine != 0 ) 
	{
		if(reqp->first_time)
		{
			Last_n_clients = dis_get_n_clients(servp->id);
		}
		(servp->user_routine)( &servp->tag, &buffp, &size,
					&reqp->first_time );
		reqp->first_time = 0;
		
	} 
	else 
	{
		buffp = servp->address;
		size = servp->size;
	}
	Curr_conn_id = last_conn_id;
/* send even if no data but not if negative */
	if( size  < 0)
	{
		reqp->delay_delete--;
		return(0);
	}
	if( DIS_STAMPED_HEADER + size > Dis_packet_size ) 
	{
		if( Dis_packet_size )
			free( Dis_packet );
		Dis_packet = (DIS_STAMPED_PACKET *)malloc((size_t)(DIS_STAMPED_HEADER + size));
		if(!Dis_packet)
		{
			reqp->delay_delete--;
			return(0);
		}
		Dis_packet_size = DIS_STAMPED_HEADER + size;
	}
	Dis_packet->service_id = htovl(reqp->service_id);
	if((reqp->type & 0xFF000) == STAMPED)
	{
		pkt_buffer = ((DIS_STAMPED_PACKET *)Dis_packet)->buffer;
		header_size = DIS_STAMPED_HEADER;
		if(!servp->user_secs)
		{
#ifdef WIN32
			ftime(&timebuf);
			aux = timebuf.millitm;
			Dis_packet->time_stamp[0] = htovl(aux);
			Dis_packet->time_stamp[1] = htovl((int)timebuf.time);
#else
			tz = 0;
		        gettimeofday(&tv, tz);
			aux = (int)tv.tv_usec / 1000;
			Dis_packet->time_stamp[0] = htovl(aux);
			Dis_packet->time_stamp[1] = htovl((int)tv.tv_sec);
#endif
		}
		else
		{
			aux = /*0xc0de0000 |*/ servp->user_millisecs;
			Dis_packet->time_stamp[0] = htovl(aux);
			Dis_packet->time_stamp[1] = htovl(servp->user_secs);
		}
		Dis_packet->reserved[0] = (int)htovl(0xc0dec0de);
		Dis_packet->quality = htovl(servp->quality);
	}
	else
	{
		pkt_buffer = ((DIS_PACKET *)Dis_packet)->buffer;
		header_size = DIS_HEADER;
	}
	memcpy(format_data_cp, servp->format_data, sizeof(format_data_cp));
	size = copy_swap_buffer_out(reqp->format, format_data_cp, 
		pkt_buffer,
		buffp, size);
	Dis_packet->size = htovl(header_size + size);
	if( !dna_write_nowait(conn_id, Dis_packet, header_size + size) ) 
	{
		if(Net_conns[conn_id].write_timedout)
		{
			dim_print_date_time();
			if(reqp->delay_delete > 1)
			{
				printf(" Server (Explicitly) Updating Service %s: Couldn't write to Conn %3d : Client %s@%s\n",
					servp->name, conn_id,
					Net_conns[conn_id].task, Net_conns[conn_id].node);
			}
			else
			{
				printf(" Server Updating Service %s: Couldn't write to Conn %3d : Client %s@%s\n",
					servp->name, conn_id,
					Net_conns[conn_id].task, Net_conns[conn_id].node);
			}
			fflush(stdout);
		}
		if(reqp->delay_delete > 1)
		{
			reqp->to_delete = 1;
		}
		else
		{
			reqp->delay_delete = 0;
			release_conn(conn_id, 1, 0);
		}
	}
/*
	else
	{
		if((reqp->type & 0xFFF) == MONITORED)
		{
			if(reqp->timr_ent)
				dtq_clear_entry(reqp->timr_ent);
		}
	}
*/
	if(reqp->delay_delete > 0)
		reqp->delay_delete--;
	return(1);
}

void remove_service( int req_id )
{
	register REQUEST *reqp;
	static DIS_PACKET *dis_packet;
	static int packet_size = 0;
	int service_id;

	reqp = (REQUEST *)id_get_ptr(req_id, SRC_DIS);
	if(!reqp)
		return;
	if( !packet_size ) {
		dis_packet = (DIS_PACKET *)malloc((size_t)DIS_HEADER);
		packet_size = DIS_HEADER;
	}
	service_id = (int)((unsigned)reqp->service_id | 0x80000000);
	dis_packet->service_id = htovl(service_id);
	dis_packet->size = htovl(DIS_HEADER);
/*
	if( !dna_write_nowait(reqp->conn_id, dis_packet, DIS_HEADER) ) 
Has to be dna_write otherwise the client gets the message much before the DNS
*/
	if( !dna_write(reqp->conn_id, dis_packet, DIS_HEADER) ) 
	{
		dim_print_date_time();
		printf(" Server Removing Service: Couldn't write to Conn %3d : Client %s@%s\n",
			reqp->conn_id, Net_conns[reqp->conn_id].task, Net_conns[reqp->conn_id].node);
		fflush(stdout);
		release_conn(reqp->conn_id, 0, 0);
	}
}

void execute_command(SERVICE *servp, DIC_PACKET *packet)
{
	int size;
	int format;
	FORMAT_STR format_data_cp[MAX_NAME/4], *formatp;
	static int *buffer;
	static int buffer_size = 0;
	int add_size;

	size = vtohl(packet->size) - DIC_HEADER;
	add_size = size + (size/2);
	if(!buffer_size)
	{
		buffer = (int *)malloc((size_t)add_size);
		buffer_size = add_size;
	} 
	else 
	{
		if( add_size > buffer_size ) 
		{
			free(buffer);
			buffer = (int *)malloc((size_t)add_size);
			buffer_size = add_size;
		}
	}

	dis_set_timestamp(servp->id, 0, 0);
	if(servp->user_routine != 0)
	{
		format = vtohl(packet->format);
		memcpy(format_data_cp, servp->format_data, sizeof(format_data_cp));
		if((format & 0xF) == ((MY_FORMAT) & 0xF)) 
		{
			for(formatp = format_data_cp; formatp->par_bytes; formatp++)
			{
				if(formatp->flags & IT_IS_FLOAT)
					formatp->flags |= ((short)format & (short)0xf0);
				formatp->flags &= (short)0xFFF0;	/* NOSWAP */
			}
		}
		else
		{
			for(formatp = format_data_cp; formatp->par_bytes; formatp++)
			{
				if(formatp->flags & IT_IS_FLOAT)
					formatp->flags |= ((short)format & (short)0xf0);
			}
		}
		size = copy_swap_buffer_in(format_data_cp, 
						 buffer, 
						 packet->buffer, size);
		(servp->user_routine)(&servp->tag, buffer, &size);
	}
}

void dis_report_service(char *serv_name)
{
	register SERVICE *servp;
	register REQUEST *reqp;
	int to_delete = 0, more;

	
	DISABLE_AST
	servp = find_service(serv_name);
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) )
	{
		if((reqp->type & 0xFFF) != TIMED_ONLY)
		{
			execute_service(reqp->req_id);
			if(reqp->to_delete)
				to_delete = 1;
		}
	}
	if(to_delete)
	{
		do
		{
			more = 0;
			reqp = servp->request_head;
			while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
				(DLL *) reqp)) )
			{
				if(reqp->to_delete)
				{
					more = 1;
					release_conn(reqp->conn_id, 1, 0);
					break;
				}
			}
		}while(more);
	}
	ENABLE_AST
}

int dis_update_service(unsigned service_id)
{
int do_update_service();

	return(do_update_service(service_id,0));
}

int dis_selective_update_service(unsigned service_id, int *client_ids)
{
int do_update_service();

	return(do_update_service(service_id, client_ids));
}

int check_client(REQUEST *reqp, int *client_ids)
{
	if(!client_ids)
		return(1);
	while(*client_ids)
	{
		if(reqp->conn_id == *client_ids)
		{
			return(1);
		}
		client_ids++;
	}
	return(0);
}

int do_update_service(unsigned service_id, int *client_ids)
{
	register REQUEST *reqp;
	register SERVICE *servp;
	REQUEST_PTR *reqpp;
	CLIENT *clip;
	register int found = 0;
	int to_delete = 0, more, conn_id;
	char str[128];
	int release_request();
	int n_clients = 0;

	DISABLE_AST
	if(Serving == -1)
	{
		ENABLE_AST
		return(found);
	}
	if(!service_id)
	{
		sprintf(str, "Update Service - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
		ENABLE_AST
		return(found);
	}
	servp = (SERVICE *)id_get_ptr(service_id, SRC_DIS);
	if(!servp)
	{
		ENABLE_AST
		return(found);
	}
	if(servp->id != (int)service_id)
	{
		ENABLE_AST
		return(found);
	}
	servp->delay_delete = 1;
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) ) 
	{
/*
if(Debug_on)
{
dim_print_date_time();
printf("Updating %s (id = %d, ptr = %08lX) for %s@%s (req_id = %d, req_ptr = %08lX)\n",
	   servp->name, (int)service_id, (unsigned dim_long)servp, 
	   Net_conns[reqp->conn_id].task, Net_conns[reqp->conn_id].node, reqp->req_id, (unsigned dim_long)reqp);
}
*/
		if(check_client(reqp, client_ids))
		{
			reqp->delay_delete = 1;
			n_clients++;
		}
	}
	ENABLE_AST
	{
	DISABLE_AST
	Last_n_clients = n_clients;
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) ) 
	{
		if(reqp->delay_delete && ((reqp->type & 0xFFF) != COMMAND))
		{
		if(check_client(reqp, client_ids))
		{
			if( (reqp->type & 0xFFF) != TIMED_ONLY ) 
			{
/*
				DISABLE_AST
*/
				execute_service(reqp->req_id);
				found++;
				ENABLE_AST
				{
				DISABLE_AST
				}
			}
		}
		}
	}
	ENABLE_AST
	}
	{
	DISABLE_AST
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) ) 
	{
		if(check_client(reqp, client_ids))
		{
			reqp->delay_delete = 0;
			if(reqp->to_delete)
				to_delete = 1;
		}
	}
	ENABLE_AST
	}
	if(to_delete)
	{
		DISABLE_AST
		do
		{
			more = 0;
			reqp = servp->request_head;
			while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
				(DLL *) reqp)) ) 
			{
				if(reqp->to_delete & 0x1)
				{
					more = 1;
					reqp->to_delete = 0;
					release_conn(reqp->conn_id, 1, 0);
					break;
				}
				else if(reqp->to_delete & 0x2)
				{
					more = 1;
					reqp->to_delete = 0;
					reqpp = reqp->reqpp;
					conn_id = reqp->conn_id;
					release_request(reqp, reqpp, 1);
					clip = find_client(conn_id);
					if(clip)
					{
						if( dll_empty((DLL *)clip->requestp_head) ) 
						{
							release_conn( conn_id, 0, 0);
						}
					}
					break;
				}
			}
		}while(more);
		ENABLE_AST
	}
	{
	DISABLE_AST
	servp->delay_delete = 0;
	if(servp->to_delete)
	{
		dis_remove_service(servp->id);
	}
	ENABLE_AST
	}

	return(found);
}

int dis_get_n_clients(unsigned service_id)
{
	register REQUEST *reqp;
	register SERVICE *servp;
	register int found = 0;
	char str[128];

	DISABLE_AST
	if(!service_id)
	{
		sprintf(str, "Service Has Clients- Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
		ENABLE_AST
		return(found);
	}
	servp = (SERVICE *)id_get_ptr(service_id, SRC_DIS);
	if(!servp)
	{
		ENABLE_AST
		return(found);
	}
	if(servp->id != (int)service_id)
	{
		ENABLE_AST
		return(found);
	}
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) ) 
	{
		found++;
	}
	ENABLE_AST
	return found;
}

int dis_get_timeout(unsigned service_id, int client_id)
{
	register REQUEST *reqp;
	register SERVICE *servp;
	char str[128];

	if(!service_id)
	{
		sprintf(str,"Get Timeout - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
		return(-1);
	}
	servp = (SERVICE *)id_get_ptr(service_id, SRC_DIS);
	if(!servp)
	{
		return(-1);
	}
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) ) 
	{
		if(reqp->conn_id == client_id)
			return(reqp->timeout);
	}
	return(-1);
}

void dis_set_quality( unsigned serv_id, int quality )
{
	register SERVICE *servp;
	char str[128];

	DISABLE_AST
	if(!serv_id)
	{
		sprintf(str,"Set Quality - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
	    ENABLE_AST
		return;
	}
	servp = (SERVICE *)id_get_ptr(serv_id, SRC_DIS);
	if(!servp)
	{
	    ENABLE_AST
		return;
	}
	if(servp->id != (int)serv_id)
	{
	    ENABLE_AST
		return;
	}
	servp->quality = quality;
	ENABLE_AST
}

int dis_set_timestamp( unsigned serv_id, int secs, int millisecs )
{
	register SERVICE *servp;
	char str[128];
#ifdef WIN32
	struct timeb timebuf;
#else
	struct timeval tv;
	struct timezone *tz;
#endif

	DISABLE_AST
	if(!serv_id)
	{
		sprintf(str,"Set Timestamp - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
	    ENABLE_AST
		return(0);
	}
	servp = (SERVICE *)id_get_ptr(serv_id, SRC_DIS);
	if(!servp)
	{
	    ENABLE_AST
		return(0);
	}
	if(servp->id != (int)serv_id)
	{
	    ENABLE_AST
		return(0);
	}
	if(secs == 0)
	{
#ifdef WIN32
			ftime(&timebuf);
			servp->user_secs = (int)timebuf.time;
			servp->user_millisecs = timebuf.millitm;
#else
			tz = 0;
		    gettimeofday(&tv, tz);
			servp->user_secs = (int)tv.tv_sec;
			servp->user_millisecs = (int)tv.tv_usec / 1000;
#endif
	}
	else
	{
		servp->user_secs = secs;
/*
		servp->user_millisecs = (millisecs & 0xffff);
*/
		servp->user_millisecs = millisecs;
	}
	ENABLE_AST
	return(1);
}

int dis_get_timestamp( unsigned serv_id, int *secs, int *millisecs )
{
	register SERVICE *servp;
	char str[128];

	DISABLE_AST
	*secs = 0;
	*millisecs = 0;
	if(!serv_id)
	{
		sprintf(str,"Get Timestamp - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
	    ENABLE_AST
		return(0);
	}
	servp = (SERVICE *)id_get_ptr(serv_id, SRC_DIS);
	if(!servp)
	{
	    ENABLE_AST
		return(0);
	}
	if(servp->id != (int)serv_id)
	{
	    ENABLE_AST
		return(0);
	}
	if(servp->user_secs)
	{
		*secs = servp->user_secs;
		*millisecs = servp->user_millisecs;
	}
/*
	else
	{
		*secs = 0;
		*millisecs = 0;
	}
*/
	ENABLE_AST
	return(1);
}

void dis_send_service(unsigned service_id, int *buffer, int size)
{
	register REQUEST *reqp, *prevp;
	register SERVICE *servp;
	static DIS_PACKET *dis_packet;
	static int packet_size = 0;
	int conn_id;
	char str[128];

	DISABLE_AST
	if( !service_id ) {
		sprintf(str,"Send Service - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
		ENABLE_AST
		return;
	}
	servp = (SERVICE *)id_get_ptr(service_id, SRC_DIS);
	if(!servp)
	{
		ENABLE_AST
		return;
	}
	if(!packet_size)
	{
		dis_packet = (DIS_PACKET *)malloc((size_t)(DIS_HEADER+size));
		packet_size = DIS_HEADER + size;
	} 
	else 
	{
		if( DIS_HEADER+size > packet_size ) 
		{
			free(dis_packet);
			dis_packet = (DIS_PACKET *)malloc((size_t)(DIS_HEADER+size));
			packet_size = DIS_HEADER+size;
		}
	}
	prevp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) prevp)) ) 
	{
		dis_packet->service_id = htovl(reqp->service_id);
		memcpy(dis_packet->buffer, buffer, (size_t)size);
		dis_packet->size = htovl(DIS_HEADER + size);

		conn_id = reqp->conn_id;
		if( !dna_write_nowait(conn_id, dis_packet, size + DIS_HEADER) )
		{
			dim_print_date_time();
			printf(" Server Sending Service: Couldn't write to Conn %3d : Client %s@%s\n",conn_id,
				Net_conns[conn_id].task, Net_conns[conn_id].node);
			fflush(stdout);
			release_conn(conn_id, 1, 0);
		}
		else
			prevp = reqp;
	}
	ENABLE_AST
}

int dis_remove_service(unsigned service_id)
{
	register REQUEST *reqp, *auxp;
	register SERVICE *servp;
	REQUEST_PTR *reqpp;
	int found = 0;
	char str[128];
	int release_request();
	int dis_hash_service_remove();
	DIS_DNS_CONN *dnsp;
	int n_services;
	void do_dis_stop_serving_dns(DIS_DNS_CONN *);

	DISABLE_AST
	if(!service_id)
	{
		sprintf(str,"Remove Service - Invalid service id");
		error_handler(0, DIM_ERROR, DIMSVCINVAL, str, -1);
		ENABLE_AST
		return(found);
	}
	servp = (SERVICE *)id_get_ptr(service_id, SRC_DIS);
	if(!servp)
	{
		ENABLE_AST
		return(found);
	}
	if(servp->id != (int)service_id)
	{
		ENABLE_AST
		return(found);
	}
if(Debug_on)
{
dim_print_date_time();
 printf("Removing service %s, delay_delete = %d\n",
	servp->name, servp->delay_delete);
}
	if(servp->delay_delete)
	{
		servp->to_delete = 1;
		ENABLE_AST
		return(found);
	}
	/* remove from name server */
	
	dnsp = servp->dnsp;
	unregister_service(dnsp, servp);
	/* Release client requests and remove from actual clients */
	reqp = servp->request_head;
	while( (reqp = (REQUEST *) dll_get_next((DLL *)servp->request_head,
		(DLL *) reqp)) )
	{
		remove_service(reqp->req_id);
		auxp = reqp->prev;
		reqpp = (REQUEST_PTR *) reqp->reqpp;
		release_request(reqp, reqpp, 1);
		found = 1;
		reqp = auxp;
	}
	if(servp->id == (int)dnsp->dis_service_id)
	  dnsp->dis_service_id = 0;
	if(servp->id == (int)dnsp->dis_client_id)
	  dnsp->dis_client_id = 0;
	dis_hash_service_remove(servp);
	id_free(servp->id, SRC_DIS);
	free(servp->request_head);
	free(servp);
/*
	if(dnsp != Default_DNS)
	{
		dnsp->dis_n_services--;
		n_services = dnsp->dis_n_services;
	}
	else
	{
		Dis_n_services--;
		n_services = Dis_n_services;
	}
*/
	dnsp->dis_n_services--;
	n_services = dnsp->dis_n_services;

	if(dnsp->serving)
	{
		if(n_services == 5)
		{
			if(Dis_conn_id)
			{
				dna_close(Dis_conn_id);
				Dis_conn_id = 0;
			}
			ENABLE_AST
/*
			dis_stop_serving();
*/
			do_dis_stop_serving_dns(dnsp);
		}
		else
		{
			ENABLE_AST
		}
	}
	else
	{
		ENABLE_AST
	}
	return(found);
}

void do_dis_stop_serving_dns(DIS_DNS_CONN *dnsp)
{
register SERVICE *servp, *prevp;
void dim_stop_threads(void);
int dis_no_dns();
int hash_index, old_index;
extern int close_dns(dim_long, int);
CLIENT *clip, *cprevp;

	dnsp->serving = 0;
	dis_init();
/*
	dis_hash_service_init();
	prevp = 0;
	if(Dis_conn_id)
	{
		dna_close(Dis_conn_id);
		Dis_conn_id = 0;
	}
*/
	{
	DISABLE_AST
	if(dnsp->dns_timr_ent)
	{
		dtq_rem_entry(Dis_timer_q, dnsp->dns_timr_ent);
		dnsp->dns_timr_ent = NULL;
	}
	if(dnsp->dns_dis_conn_id)
	{
		dna_close(dnsp->dns_dis_conn_id);
		dnsp->dns_dis_conn_id = 0;
	}
	ENABLE_AST
	}
	{
	DISABLE_AST
	prevp = 0;
	hash_index = -1;
	old_index = -1;
	while( (servp = dis_hash_service_get_next(&hash_index, prevp, 0)) )
	{
		if(servp->dnsp == dnsp)
		{
			ENABLE_AST
			dis_remove_service((unsigned)servp->id);
			{
			DISABLE_AST
			if(old_index != hash_index)
				prevp = 0;
			}
		}
		else
		{
			prevp = servp;
			old_index = hash_index;
		}
	}
	ENABLE_AST
	}
	{
	DISABLE_AST
	cprevp = Client_head;
	while( (clip = (CLIENT *)dll_get_next( (DLL *) Client_head, 
			(DLL*) cprevp)) )
	{
		if(clip->dnsp != dnsp)
		{
			cprevp = clip;
			continue;
		}
		if( dll_empty((DLL *)clip->requestp_head) ) 
		{
if(Debug_on)
{
dim_print_date_time();
printf("Releasing conn %d, to %s@%s\n",
	   clip->conn_id, 
	   Net_conns[clip->conn_id].task, Net_conns[clip->conn_id].node);
}
			release_conn( clip->conn_id, 0, 0);
		}
		else
		{
			cprevp = clip;
		}
	}
	ENABLE_AST
	}
if(Debug_on)
{
dim_print_date_time();
printf("Cleaning dnsp variables\n");
}

	dnsp->dis_first_time = 1;
	dnsp->dis_n_services = 0;
	dnsp->dis_dns_packet.size = 0;
	dnsp->dis_dns_packet.src_type = 0;
	close_dns(dnsp->dnsid, SRC_DIS);
/*
	if(dnsp != Default_DNS)
	{
		dll_remove(dnsp);
		free(dnsp);
	}
*/
/*
	if(dll_empty(DNS_head))
*/
	if(dis_no_dns())
		dis_stop_serving();
}

void dis_stop_serving_dns(dim_long dnsid)
{
	DIS_DNS_CONN *dnsp, *dis_find_dns();

	dnsp = dis_find_dns(dnsid);
	do_dis_stop_serving_dns(dnsp);
}

void dis_stop_serving()
{
register SERVICE *servp, *prevp;
void dim_stop_threads(void);
int dis_find_client_conns();
int hash_index;

/*
	if(Serving != -1)
*/
	Serving = 0;
	dis_init();
	if(Dis_conn_id)
	{
		dna_close(Dis_conn_id);
		Dis_conn_id = 0;
	}
/*
	if(Dns_dis_conn_id)
	{
		dna_close(Dns_dis_conn_id);
		Dns_dis_conn_id = 0;
	}
*/
	{
	DISABLE_AST
	prevp = 0;
	hash_index = -1;
	while( (servp = dis_hash_service_get_next(&hash_index, prevp, 0)) )
	{
		ENABLE_AST
		dis_remove_service((unsigned)servp->id);
		{
		DISABLE_AST
		prevp = 0;
		}
	}
	ENABLE_AST
	}
/*
	if(Dis_conn_id)
		dna_close(Dis_conn_id);
	if(Dns_dis_conn_id)
		dna_close(Dns_dis_conn_id);
	Dns_dis_conn_id = 0;
*/
	Dis_first_time = 1;
/*
	if(Dns_timr_ent)
	{
		dtq_rem_entry(Dis_timer_q, Dns_timr_ent);
		Dns_timr_ent = NULL;
	}
*/
	dtq_delete(Dis_timer_q);
	Dis_timer_q = 0;
/*
	if(Serving != -1)
*/
	if(!dis_find_client_conns())
		dim_stop_threads();
}

int dis_find_client_conns()
{
	int i;
	int n = 0;

	for( i = 0; i< Curr_N_Conns; i++ )
	{
		if(Net_conns[i].channel != 0)
		{
			if(Dna_conns[i].read_ast == dis_insert_request)
			{
				dna_close(i);
			}
			else
			{
				n++;
			}
		}
	}
	return(n);
}

/* find service by name */
SERVICE *find_service(char *name)
{
	return(dis_hash_service_exists(name));
}

CLIENT *create_client(int conn_id, SERVICE *servp, int *new_client)
{
	CLIENT *clip;

	*new_client = 0;
	if(!(clip = find_client(conn_id)))
	{
		/*
		dna_set_test_write(conn_id, 15);
		*/
		clip = (CLIENT *)malloc(sizeof(CLIENT));
		clip->conn_id = conn_id;
		clip->dnsp = servp->dnsp;
		clip->requestp_head = (REQUEST_PTR *)malloc(sizeof(REQUEST_PTR));
		dll_init( (DLL *) clip->requestp_head );
		dll_insert_queue( (DLL *) Client_head, (DLL *) clip );
		*new_client = 1;
	}
	return clip;
}

CLIENT *find_client(int conn_id)
{
	register CLIENT *clip;

	clip = (CLIENT *)
			dll_search( (DLL *) Client_head, &conn_id, sizeof(conn_id));
	return(clip);
}

void release_all_requests(int conn_id, CLIENT *clip)
{
	register REQUEST_PTR *reqpp, *auxp;
	register REQUEST *reqp;
    int found = 0;
	int release_request();
	DIS_DNS_CONN *dnsp = 0;

	DISABLE_AST;
	if(clip)
	{
		reqpp = clip->requestp_head;
		while( (reqpp = (REQUEST_PTR *) dll_get_next((DLL *)clip->requestp_head,
			(DLL *) reqpp)) )
		{
			auxp = reqpp->prev;
			reqp = (REQUEST *) reqpp->reqp;
			release_request(reqp, reqpp, 0);
			found = 1;
			reqpp = auxp;
		}
		dnsp = clip->dnsp;
		dll_remove(clip);
		free(clip->requestp_head);
		free(clip);
	}
	if(found)
	{
		Last_client = -conn_id;
		if(dnsp->dis_client_id)
		  dis_update_service(dnsp->dis_client_id);
	}
	dna_close(conn_id);
	ENABLE_AST;
}

CLIENT *check_delay_delete(int conn_id)
{
	register REQUEST_PTR *reqpp;
	register CLIENT *clip;
	register REQUEST *reqp;
	int found = 0;

	DISABLE_AST;
	clip = find_client(conn_id);
	if(clip)
	{
		reqpp = clip->requestp_head;
		while( (reqpp = (REQUEST_PTR *) dll_get_next((DLL *)clip->requestp_head,
			(DLL *) reqpp)) )
		{
			reqp = (REQUEST *) reqpp->reqp;
			if(reqp->delay_delete)
			{
				reqp->to_delete = 1;
				found = 1;
			}
		}
	}
	ENABLE_AST;
	if(found)
	{
		return((CLIENT *)-1);
	}
	return(clip);
}

char *dis_get_error_services()
{
	return(dis_get_client_services(Error_conn_id));
}

char *dis_get_client_services(int conn_id)
{
	register REQUEST_PTR *reqpp;
	register CLIENT *clip;
	register REQUEST *reqp;
	register SERVICE *servp;

	int n_services = 0;
	int max_size;
	static int curr_allocated_size = 0;
	static char *service_info_buffer;
	char *buff_ptr;


	if(!conn_id)
		return((char *)0);
	{
	DISABLE_AST;
	clip = find_client(conn_id);
	if(clip)
	{
		reqpp = clip->requestp_head;
		while( (reqpp = (REQUEST_PTR *) dll_get_next((DLL *)clip->requestp_head,
			(DLL *) reqpp)))
		{
			n_services++;
		}
		if(!n_services)
		{
			ENABLE_AST
			return((char *)0);
		}
		max_size = n_services * MAX_NAME;
		if(!curr_allocated_size)
		{
			service_info_buffer = (char *)malloc((size_t)max_size);
			curr_allocated_size = max_size;
		}
		else if (max_size > curr_allocated_size)
		{
			free(service_info_buffer);
			service_info_buffer = (char *)malloc((size_t)max_size);
			curr_allocated_size = max_size;
		}
		service_info_buffer[0] = '\0';
		buff_ptr = service_info_buffer;
		reqpp = clip->requestp_head;
		while( (reqpp = (REQUEST_PTR *) dll_get_next((DLL *)clip->requestp_head,
			(DLL *) reqpp)) )
		{
			reqp = (REQUEST *) reqpp->reqp;
			servp = reqp->service_ptr;
			strcat(buff_ptr, servp->name);
			strcat(buff_ptr, "\n");
			buff_ptr += (int)strlen(buff_ptr);
		}
	}
	else
	{
		ENABLE_AST
		return((char *)0);
	}
	ENABLE_AST;
	}
/*
	dim_print_date_time();
	dna_get_node_task(conn_id, node, task);
	printf("Client %s@%s uses services: \n", task, node);
	printf("%s\n",service_info_buffer);
*/
	return(service_info_buffer);
}

int find_release_request(int conn_id, int service_id)
{
	register REQUEST_PTR *reqpp, *auxp;
	register CLIENT *clip;
	register REQUEST *reqp;
	int release_request();

	DISABLE_AST
	clip = find_client(conn_id);
	if(clip)
	{
		reqpp = clip->requestp_head;
		while( (reqpp = (REQUEST_PTR *) dll_get_next((DLL *)clip->requestp_head,
			(DLL *) reqpp)) )
		{
			reqp = (REQUEST *) reqpp->reqp;
			if(reqp->service_id == service_id)
			{
				if(reqp->delay_delete)
				{
					reqp->to_delete += 0x2;
				}
				else
				{
					auxp = reqpp->prev;
					release_request(reqp, reqpp, 0);
					reqpp = auxp;
				}
			}
		}
/* The client should close the connection (there may be commands)
		if( dll_empty((DLL *)clip->requestp_head) ) 
		{
			release_conn( conn_id, 0, 0 );
		}
*/
	}
	ENABLE_AST
	return(1);
}

int release_request(REQUEST *reqp, REQUEST_PTR *reqpp, int remove)
{
	int conn_id;
	CLIENT *clip;

	DISABLE_AST
	conn_id = reqp->conn_id;
	if(reqpp)
		dll_remove((DLL *)reqpp);
	dll_remove((DLL *)reqp);
	if(reqp->timr_ent)
		dtq_rem_entry(Dis_timer_q, reqp->timr_ent);
	id_free(reqp->req_id, SRC_DIS);
	free(reqp);
	if(reqpp)
		free(reqpp);
/* Would do it too early, the client will disconnect anyway
*/
	if((remove) && (Serving == 0))
	{
		clip = find_client(conn_id);
		if(clip)
		{
			if( dll_empty((DLL *)clip->requestp_head) ) 
			{
				release_conn( conn_id, 0, 0);
			}
		}
	}

	ENABLE_AST
	return(1);
}

static int release_conn(int conn_id, int print_flg, int dns_flag)
{
	static int releasing = 0;
	CLIENT *clip;
	int do_exit_handler();

	DISABLE_AST
	if(print_flg){}
	if(dns_flag)
	{
		recv_dns_dis_rout( conn_id, 0, 0, STA_DISC );
		ENABLE_AST
		return(0);
	}
#ifdef VMS
	if(print_flg)
	{
		dim_print_date_time();
		dna_get_node_task(conn_id, node, task);
		printf(" Couldn't write to client %s@%s, releasing connection %d\n",
			task, node, conn_id);
		fflush(stdout);
	}
#endif
	clip = check_delay_delete(conn_id);
	if(clip != (CLIENT *)-1)
	{
		if( Client_exit_user_routine != 0 ) 
		{
			releasing++;
			Curr_conn_id = conn_id;
			do_exit_handler(conn_id);
			releasing--;
		}
		if(!releasing)
		{
			release_all_requests(conn_id, clip);
		}
	}
	ENABLE_AST
	return(1);
}

typedef struct cmnds{
	struct cmnds *next;
	dim_long tag;
	int size;
	int buffer[1];
} DIS_CMND;

static DIS_CMND *Cmnds_head = (DIS_CMND *)0;

void std_cmnd_handler(dim_long *tag, int *cmnd_buff, int *size)
{
	register DIS_CMND *new_cmnd;
/* queue the command */

	if(!Cmnds_head)
	{
		Cmnds_head = (DIS_CMND *)malloc(sizeof(DIS_CMND));
		sll_init((SLL *) Cmnds_head);
	}
	new_cmnd = (DIS_CMND *)malloc((size_t)((*size)+12));
	new_cmnd->next = 0;
	new_cmnd->tag = *tag;
	new_cmnd->size = *size;
	memcpy(new_cmnd->buffer, cmnd_buff, (size_t)*size);
	sll_insert_queue((SLL *) Cmnds_head, (SLL *) new_cmnd);
}

int dis_get_next_cmnd(dim_long *tag, int *buffer, int *size)
{
	register DIS_CMND *cmndp;
	register int ret_val = -1;

	DISABLE_AST
	if(!Cmnds_head)
	{
		Cmnds_head = (DIS_CMND *)malloc(sizeof(DIS_CMND));
		sll_init((SLL *) Cmnds_head);
	}
	if(*size == 0)
	{
		if( (cmndp = (DIS_CMND *) sll_get_head((SLL *) Cmnds_head)))
		{
			if(cmndp->size > 0)
			{
				*size = cmndp->size;
				*tag = cmndp->tag;
				ENABLE_AST
				return(-1);
			}
		}
	}
	if( (cmndp = (DIS_CMND *) sll_remove_head((SLL *) Cmnds_head)) )
	{
		if (*size >= cmndp->size)
		{
			*size = cmndp->size;
			ret_val = 1;
		}
		memcpy(buffer, cmndp->buffer, (size_t)*size);
		*tag = cmndp->tag;
		free(cmndp);
		ENABLE_AST
		return(ret_val);
	}
	ENABLE_AST
	return(0);
}

int dis_get_conn_id()
{
	return(Curr_conn_id);
}

int dis_get_client(char *name)
{
	int ret = 0;
	char node[MAX_NODE_NAME], task[MAX_TASK_NAME];

	DISABLE_AST

	if(Curr_conn_id)
	{
		dna_get_node_task(Curr_conn_id, node, task);
		strcpy(name,task);
		strcat(name,"@");
		strcat(name,node);
		ret = Curr_conn_id;
	}
	ENABLE_AST
	return(ret);
}

#ifdef VMS
dis_convert_str(c_str, for_str)
char *c_str;
struct dsc$descriptor_s *for_str;
{
	int i;

	strcpy(for_str->dsc$a_pointer, c_str);
	for(i = (int)strlen(c_str); i< for_str->dsc$w_length; i++)
		for_str->dsc$a_pointer[i] = ' ';
}
#endif

void client_info(dim_long *tag, int **bufp, int *size, int *first_time)
{
	register CLIENT *clip;
	int curr_conns[MAX_CONNS];
	int i, index, max_size;
	static int curr_allocated_size = 0;
	static char *dns_info_buffer;
	register char *dns_client_info;
	char node[MAX_NODE_NAME], task[MAX_TASK_NAME];
	DIS_DNS_CONN *dnsp = (DIS_DNS_CONN *)*tag;

	max_size = sizeof(DNS_CLIENT_INFO);
	if(!curr_allocated_size)
	{
		dns_info_buffer = malloc((size_t)max_size);
		curr_allocated_size = max_size;
	}
	dns_client_info = dns_info_buffer;
	dns_client_info[0] = '\0';
	index = 0;
	if(*first_time)
	{
		clip = Client_head;
		while( (clip = (CLIENT *)dll_get_next( (DLL *) Client_head, 
			(DLL*) clip)) )
		{
			if(clip->dnsp != dnsp)
				continue;
			curr_conns[index++] = clip->conn_id;
		}
		max_size = (index+1)*(int)sizeof(DNS_CLIENT_INFO);
		if (max_size > curr_allocated_size)
		{
			free(dns_info_buffer);
			dns_info_buffer = malloc((size_t)max_size);
			curr_allocated_size = max_size;
		}
		dns_client_info = dns_info_buffer;
		dns_client_info[0] = '\0';
	}
	else
	{
		if(Last_client > 0)
		{
			strcat(dns_client_info,"+");
			curr_conns[index++] = Last_client;
		}
		else
		{
			strcat(dns_client_info,"-");
			curr_conns[index++] = -Last_client;
		}
	}
	
	for(i=0; i<index;i++)
	{
		dna_get_node_task(curr_conns[i], node, task);
		strcat(dns_client_info,task);
		strcat(dns_client_info,"@");
		strcat(dns_client_info,node);
		strcat(dns_client_info,"|");
	}
	if(index)
		dns_client_info[(int)strlen(dns_client_info)-1] = '\0';
	*bufp = (int *)dns_info_buffer;
	*size = (int)strlen(dns_info_buffer)+1;
}

void append_service(char *service_info_buffer, SERVICE *servp)		
{
	char name[MAX_NAME], *ptr;

		if(strstr(servp->name,"/RpcIn"))
		{
			strcpy(name,servp->name);
			ptr = (char *)strstr(name,"/RpcIn");
			*ptr = 0;
			strcat(service_info_buffer, name);
			strcat(service_info_buffer, "|");
			if(servp->def[0])
			{
				strcat(service_info_buffer, servp->def);
			}
			strcat(name,"/RpcOut");
			if( (servp = find_service(name)) )
			{
				strcat(service_info_buffer, ",");
				if(servp->def[0])
				{
					strcat(service_info_buffer, servp->def);
				}
			}
			strcat(service_info_buffer, "|RPC");
			strcat(service_info_buffer, "\n");
		}
		else if(strstr(servp->name,"/RpcOut"))
		{
/*
			if(servp->def[0])
			{
				strcat(service_info_buffer, servp->def);
			}
			strcat(service_info_buffer, "|RPC");
			strcat(service_info_buffer, "\n");

*/
		}
		else
		{
			strcat(service_info_buffer, servp->name);
			strcat(service_info_buffer, "|");
			if(servp->def[0])
			{
				strcat(service_info_buffer, servp->def);
			}
			strcat(service_info_buffer, "|");
			if(servp->type == COMMAND)
			{
				strcat(service_info_buffer, "CMD");
			}
			strcat(service_info_buffer, "\n");
		}
}

void service_info(dim_long *tag, int **bufp, int *size, int *first_time)
{
	register SERVICE *servp;
	int max_size, done = 0;
	static int curr_allocated_size = 0;
	static char *service_info_buffer;
	char *buff_ptr;
	DIS_DNS_CONN *dnsp = (DIS_DNS_CONN *)*tag;
	int hash_index;

	DISABLE_AST
	max_size = (dnsp->dis_n_services+10) * (MAX_NAME*2 + 4);
	if(!curr_allocated_size)
	{
		service_info_buffer = (char *)malloc((size_t)max_size);
		curr_allocated_size = max_size;
	}
	else if (max_size > curr_allocated_size)
	{
		free(service_info_buffer);
		service_info_buffer = (char *)malloc((size_t)max_size);
		curr_allocated_size = max_size;
	}
	service_info_buffer[0] = '\0';
	buff_ptr = service_info_buffer;
	servp = 0;
	hash_index = -1;
	if(*first_time)
	{
		while( (servp = dis_hash_service_get_next(&hash_index, servp, 0)) )
		{
			if(servp->dnsp != dnsp)
				continue;
			if(servp->registered)
			{
/*
				servp->registered = 2;
*/
				if((dnsp->updating_service_list) && (Last_n_clients > 1) && 
					(servp->registered == 1))
					continue;
				servp->registered = Last_n_clients+1;
				append_service(buff_ptr, servp);
				buff_ptr += (int)strlen(buff_ptr);
			}
		}
	}
	else
	{
		while( (servp = dis_hash_service_get_next(&hash_index, servp, 0)) )
		{
			if(servp->dnsp != dnsp)
				continue;
/*
			if(servp->registered == 1)
*/
			if(servp->registered == 0)
			{
				strcat(buff_ptr, "-");
				buff_ptr += (int)strlen(buff_ptr);
				append_service(buff_ptr, servp);
				buff_ptr += (int)strlen(buff_ptr);
			}
			else if(servp->registered < (Last_n_clients+1))
			{
				if(!done)
				{
					strcat(buff_ptr, "+");
					buff_ptr += (int)strlen(buff_ptr);
					done = 1;
				}
				append_service(buff_ptr, servp);
				buff_ptr += (int)strlen(buff_ptr);
/*
				servp->registered = 2;
*/
				servp->registered++;
			}
		}
	}
	*bufp = (int *)service_info_buffer;
	*size = (int)(buff_ptr - service_info_buffer+1);
	if(*size == 1)
		*size = -1;
	ENABLE_AST
}
	
static void add_exit_handler_item(int conn_id, int tag)
{
	EXIT_H *newp;

	DISABLE_AST
	if(!Exit_h_head) 
	{
		Exit_h_head = (EXIT_H *)malloc(sizeof(EXIT_H));
		sll_init( (SLL *) Exit_h_head );
	}
	if( (newp = (EXIT_H *)sll_search((SLL *) Exit_h_head, 
		(char *)&conn_id, 4)) )
	{
		newp->conn_id = conn_id;
		newp->exit_id = tag;
		strcpy(newp->node, Net_conns[conn_id].node);
		strcpy(newp->task, Net_conns[conn_id].task);
	}
	else
	{
		newp = (EXIT_H *)malloc(sizeof(EXIT_H));
		newp->conn_id = conn_id;
		newp->exit_id = tag;
		strcpy(newp->node, Net_conns[conn_id].node);
		strcpy(newp->task, Net_conns[conn_id].task);
		sll_insert_queue( (SLL *) Exit_h_head, (SLL *) newp );
	}
	ENABLE_AST
}

static void rem_exit_handler_item(EXIT_H *exitp)
{

	DISABLE_AST
	if(!Exit_h_head) 
	{
		ENABLE_AST
		return;
	}
	sll_remove( (SLL *) Exit_h_head, (SLL *) exitp );
	free(exitp);
	ENABLE_AST
}

static EXIT_H *find_exit_handler_item(int conn_id)
{
	EXIT_H *exitp;

	DISABLE_AST;
	if(!Exit_h_head)
	{
		ENABLE_AST;
		return((EXIT_H *)0);
	}
	if( (exitp = (EXIT_H *) sll_search((SLL *) Exit_h_head, (char *) &conn_id, 4)) )
	{
		ENABLE_AST;
		return(exitp);
	}
	ENABLE_AST;
	return((EXIT_H *)0);
}

static int check_exit_handler_item(EXIT_H *exitp, int conn_id)
{
	if( (!strcmp(exitp->node, Net_conns[conn_id].node)) &&
		(!strcmp(exitp->task, Net_conns[conn_id].task)))
	{
		return exitp->exit_id;
	}
	return 0;
}

void add_exit_handler(int *tag, int *bufp, int *size)
{
	EXIT_H *exitp;

	if(size){}
	if(tag){}
	if(*bufp)
	{
		add_exit_handler_item(Curr_conn_id, *bufp);
	}
	else
	{
		if((exitp = find_exit_handler_item(Curr_conn_id)))
			rem_exit_handler_item(exitp);
	}
}

void dis_set_client_exit_handler(int conn_id, int tag)
{
	EXIT_H *exitp;

	if(tag)
	{
		add_exit_handler_item(conn_id, tag);
	}
	else
	{
		if((exitp = find_exit_handler_item(conn_id)))
			rem_exit_handler_item(exitp);
	}
}


int do_exit_handler(int conn_id)
{
	register EXIT_H *exitp;
	int exit_id;

	DISABLE_AST;
	if((exitp = find_exit_handler_item(conn_id)))
	{
		if((exit_id = check_exit_handler_item(exitp, conn_id)))
		{
			(Client_exit_user_routine)( &exit_id );
		}
		else
		{
			rem_exit_handler_item(exitp);
		}
	}
/*
	if(!Exit_h_head)
	{
		ENABLE_AST;
		return(0);
	}
	while( (exitp = (EXIT_H *) sll_search_next_remove((SLL *) Exit_h_head,
							 0, (char *) &conn_id, 4)) )
	{
		(Client_exit_user_routine)( &exitp->exit_id );
		free(exitp);
	}
*/
	ENABLE_AST
	return(1);
}

static void exit_handler(int *tag, int *bufp, int *size)
{

	if(size){}
	if(tag){}
	if(Exit_user_routine)
		(Exit_user_routine)( bufp );
	else
	{
/*
		printf("%s PID %d Exiting!\n", Task_name, getpid());
*/
		exit(*bufp);
	}
}

static void error_handler(int conn_id, int severity, int errcode, char *reason, int exit)
{
	int exit_tag, exit_code, exit_size;
	int last_conn_id;

	if(Error_user_routine)
	{
			Error_conn_id = conn_id;
			last_conn_id = Curr_conn_id;
			Curr_conn_id = conn_id;
			(Error_user_routine)( severity, errcode, reason);
			Error_conn_id = 0;
			Curr_conn_id = last_conn_id;
	}
	else
	{
		dim_print_msg(reason, severity);
	}
	if(severity == DIM_FATAL)
	{
		exit_tag = 0;
		if(exit == -1)
			exit_code = errcode;
		else
			exit_code = exit;
		exit_size = sizeof(int);
		exit_handler(&exit_tag, &exit_code, &exit_size);
	}
}
/*
#define MAX_HASH_ENTRIES 2000
*/
#define MAX_HASH_ENTRIES 5000

static SERVICE *Service_hash_table[MAX_HASH_ENTRIES];
static int Service_new_entries[MAX_HASH_ENTRIES];

int dis_hash_service_init()
{

  int i;
  static int done = 0;

  if(!done)
  {
	for( i = 0; i < MAX_HASH_ENTRIES; i++ ) 
	{
/*
		Service_hash_table[i] = (SERVICE *) malloc(sizeof(SERVICE));
		dll_init((DLL *) Service_hash_table[i]);
*/
		Service_hash_table[i] = 0;
		Service_new_entries[i] = 0;
	}
	done = 1;
  }

  return(1);
}

int dis_hash_service_insert(SERVICE *servp)
{
	int index;
	index = HashFunction(servp->name, MAX_HASH_ENTRIES);
	if(!Service_hash_table[index])
	{
		Service_hash_table[index] = (SERVICE *) malloc(sizeof(SERVICE));
		dll_init((DLL *) Service_hash_table[index]);
	}
	Service_new_entries[index]++;
	dll_insert_queue((DLL *) Service_hash_table[index], 
			 (DLL *) servp);
	return(1);
}

int dis_hash_service_registered(int index, SERVICE *servp)
{
	servp->registered = 1;
	Service_new_entries[index]--;
	if(Service_new_entries[index] < 0)
		Service_new_entries[index] = 0;
	return 1;
}

int dis_hash_service_remove(SERVICE *servp)
{
	int index;
	index = HashFunction(servp->name, MAX_HASH_ENTRIES);
	if(!Service_hash_table[index])
	{
		return(0);
	}
	dll_remove( (DLL *) servp );
	return(1);
}


SERVICE *dis_hash_service_exists(char *name)
{
	int index;
	SERVICE *servp;

	index = HashFunction(name, MAX_HASH_ENTRIES);
	if(!Service_hash_table[index])
	{
		return((SERVICE *)0);
	}
	if( (servp = (SERVICE *) dll_search(
					(DLL *) Service_hash_table[index],
			      		name, (int)strlen(name)+1)) )
	{
		return(servp);
	}
	return((SERVICE *)0);
}			

SERVICE *dis_hash_service_get_next(int *curr_index, SERVICE *prevp, int new_entries)
{
	int index;
	SERVICE *servp = 0;
/*
	if(!prevp)
	{
		index = -1;
	}
*/
	index = *curr_index;
	if(index == -1)
	{
		index++;
		prevp = Service_hash_table[index];
	}
	if(!prevp)
	{
		prevp = Service_hash_table[index];
	}
	do
	{
		if(prevp)
		{
			if((!new_entries) || (Service_new_entries[index] > 0))
			{
				servp = (SERVICE *) dll_get_next(
						(DLL *) Service_hash_table[index],
						(DLL *) prevp);
				if(servp)
					break;
			}
		}
		index++;
		if(index == MAX_HASH_ENTRIES)
		{
			*curr_index = -1;
			return((SERVICE *) 0);
		}
		prevp = Service_hash_table[index];
	} while(!servp);
	*curr_index = index;
	return(servp);
}

DIS_DNS_CONN *dis_find_dns(dim_long dnsid)
{
	DIS_DNS_CONN *dnsp;

	dnsp = (DIS_DNS_CONN *)
			dll_search( (DLL *) DNS_head, &dnsid, sizeof(dnsid));
/*
	if(!dnsp)
	{
		dnsp = create_dns(dnsid);
	}
*/
	return dnsp;
}

int dis_no_dns()
{
	DIS_DNS_CONN *dnsp;

	dnsp = (DIS_DNS_CONN *) DNS_head;
	while ( (dnsp = (DIS_DNS_CONN *) dll_get_next( (DLL *) DNS_head, (DLL *) dnsp)))
	{
/*
		if(dnsp != Default_DNS)
			return 0;
*/
		if(dnsp->serving)
			return 0;
	}
	return 1;
}

DIS_DNS_CONN *find_dns_by_conn_id(int conn_id)
{
	DIS_DNS_CONN *dnsp;
	extern dim_long dns_get_dnsid();
	dim_long dnsid;

	dnsid = dns_get_dnsid(conn_id, SRC_DIS);
	dnsp = dis_find_dns(dnsid);
	if(!dnsp)
		dnsp = Default_DNS;
	return (DIS_DNS_CONN *)dnsp;
}

void dis_print_hash_table()
{
	SERVICE *servp;
	int i;
	int n_entries, max_entry_index = 0;
	int max_entries = 0;

	for( i = 0; i < MAX_HASH_ENTRIES; i++ ) 
	{
		n_entries = 0;
		servp = Service_hash_table[i];
		while( (servp = (SERVICE *) dll_get_next(
						(DLL *) Service_hash_table[i],
						(DLL *) servp)) )
		{
			n_entries++;
			if(n_entries == 1)
				printf("    Name = %s\n",servp->name);
		}
		if(n_entries != 0)
			printf("HASH[%d] - %d entries\n", i, n_entries);
		if(n_entries > max_entries)
		{
			max_entries = n_entries;
			max_entry_index = i;
		}
	}
	printf("Maximum : HASH[%d] - %d entries\n", max_entry_index, max_entries);  
	fflush(stdout);
}

void dis_hash_print()
{
	SERVICE *servp;
	int hash_index;

	servp = 0;
	hash_index = -1;
	while( (servp = dis_hash_service_get_next(&hash_index, servp, 0)) )
	{
		printf("Name = %s\n",servp->name);
	}
}

#ifdef VMS
/* CFORTRAN WRAPPERS */
FCALLSCFUN1(INT, dis_start_serving, DIS_START_SERVING, dis_start_serving,
				 STRING)
FCALLSCFUN3(INT, dis_get_next_cmnd, DIS_GET_NEXT_CMND, dis_get_next_cmnd,
				 PINT, PVOID, PINT)
FCALLSCFUN1(INT, dis_get_client, DIS_GET_CLIENT, dis_get_client,
				 PSTRING)
FCALLSCFUN6(INT, dis_add_service, DIS_ADD_SERVICE, dis_add_service,
				 STRING, PVOID, PVOID, INT, PVOID, INT)
FCALLSCSUB4(	 dis_add_cmnd, DIS_ADD_CMND, dis_add_cmnd,
				 STRING, PVOID, PVOID, INT)
FCALLSCSUB1(	 dis_add_client_exit_handler, DIS_ADD_CLIENT_EXIT_HANDLER, 
				 dis_add_client_exit_handler,
				 PVOID)
FCALLSCSUB2(	 dis_set_client_exit_handler, DIS_SET_CLIENT_EXIT_HANDLER, 
				 dis_set_client_exit_handler,
				 INT, INT)
FCALLSCSUB1(	 dis_add_exit_handler, DIS_ADD_EXIT_HANDLER, 
				 dis_add_exit_handler,
				 PVOID)
FCALLSCSUB1(	 dis_report_service, DIS_REPORT_SERVICE, dis_report_service,
				 STRING)
FCALLSCSUB2(	 dis_convert_str, DIS_CONVERT_STR, dis_convert_str,
				 PVOID, PVOID)
FCALLSCFUN1(INT, dis_update_service, DIS_UPDATE_SERVICE, dis_update_service,
				 INT)
FCALLSCFUN1(INT, dis_remove_service, DIS_REMOVE_SERVICE, dis_remove_service,
				 INT)
FCALLSCSUB3(	 dis_send_service, DIS_SEND_SERVICE, dis_send_service,
				 INT, PVOID, INT)
FCALLSCSUB2(	 dis_set_quality, DIS_SET_QUALITY, dis_set_quality,
                 INT, INT)
FCALLSCSUB3(INT, dis_set_timestamp, DIS_SET_TIMESTAMP, dis_set_timestamp,
                 INT, INT, INT)
FCALLSCFUN2(INT, dis_selective_update_service, DIS_SELECTIVE_UPDATE_SERVICE, 
				 dis_selective_update_service,
				 INT, PINT)
FCALLSCSUB3(INT, dis_get_timestamp, DIS_GET_TIMESTAMP, dis_get_timestamp,
                 INT, PINT, PINT)
#endif
