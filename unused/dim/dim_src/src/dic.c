
/*
 * DIC (Delphi Information Client) Package implements a library of
 * routines to be used by clients.
 *
 * Started on        : 10-11-91
 * Last modification : 10-08-94
 * Written by        : C. Gaspar
 * Adjusted by       : G.C. Ballintijn
 *
 */

#ifdef VMS
#	include <cfortran.h>
#	include <assert.h>
#endif

#define DIMLIB
#include <dim.h>
#include <dic.h>

/*
#define DEBUG
*/

#ifdef VMS
#define TMP_ENABLE_AST      long int ast_enable = sys$setast(1);
#define TMP_DISABLE_AST     if (ast_enable != SS$_WASSET) sys$setast(0);
#endif

#define BAD_CONN_TIMEOUT 2


typedef struct bad_conn {
	struct bad_conn *next;
	struct bad_conn *prev;
	DIC_CONNECTION conn;
	int n_retries;
	int retrying;
} DIC_BAD_CONNECTION;

static DIC_SERVICE *Service_pend_head = 0;
static DIC_SERVICE *Cmnd_head = 0;
static DIC_SERVICE *Current_server = 0;
static DIC_BAD_CONNECTION *Bad_connection_head = 0;
static int Dic_timer_q = 0;
static int Dns_dic_conn_id = 0;
static TIMR_ENT *Dns_dic_timr = NULL;
static int Tmout_max = 0;
static int Tmout_min = 0;
static int Threads_off = 0;

static void (*Error_user_routine)() = 0;
static int Error_conn_id = 0;
static int Curr_conn_id = 0;

#ifdef DEBUG
static int Debug_on = 1;
#else
static int Debug_on = 0;
#endif

_DIM_PROTO( unsigned request_service, (char *service_name, int req_type,
				    int req_timeout, void *service_address,
				    int service_size, void (*usr_routine)(void*,void*,int*),
				    dim_long tag, void *fill_addr, int fill_size, int stamped) );
_DIM_PROTO( int request_command,      (char *service_name, void *service_address,
				    int service_size, void (*usr_routine)(void*,int*),
				    dim_long tag, int stamped) );
_DIM_PROTO( DIC_SERVICE *insert_service, (int type, int timeout, char *name,
				  int *address, int size, void (*routine)(),
				  dim_long tag, int *fill_addr, int fill_size,
				  int pending, int stamped ) );
_DIM_PROTO( void modify_service, (DIC_SERVICE *servp, int timeout,
				  int *address, int size, void (*routine)(),
				  dim_long tag, int *fill_addr, int fill_size, int stamped) );
_DIM_PROTO( DIC_SERVICE *locate_command, (char *serv_name) );
_DIM_PROTO( DIC_SERVICE *locate_pending, (char *serv_name) );
_DIM_PROTO( DIC_BAD_CONNECTION *locate_bad, (char *node, char *task, int port) );
_DIM_PROTO( void service_tmout,      (int serv_id) );
_DIM_PROTO( static void request_dns_info,      (int retry) );
_DIM_PROTO( static int handle_dns_info,      (DNS_DIC_PACKET *) );
_DIM_PROTO( void close_dns_conn,     (void) );
_DIM_PROTO( static void release_conn, (int conn_id) );
_DIM_PROTO( static void get_format_data, (int format, FORMAT_STR *format_data, 
					char *def) );
_DIM_PROTO( static void execute_service,      (DIS_PACKET *packet, 
					DIC_SERVICE *servp, int size) );

void print_packet(DIS_PACKET *packet)
{
	dim_print_date_time();
	printf("Bad ID received from server -> Packet received:\n");
	printf("\tpacket->size = %d\n",vtohl(packet->size));
	printf("\tpacket->service_id = %d\n",vtohl(packet->service_id));
}

void dic_set_debug_on()
{
	Debug_on = 1;
}

void dic_set_debug_off()
{
	Debug_on = 0;
}

void dic_no_threads()
{
	Threads_off = 1;
}

void dic_add_error_handler( void (*user_routine)()) 
{

	DISABLE_AST
	Error_user_routine = user_routine;
	ENABLE_AST
}

static void error_handler(int conn_id, int severity, int errcode, char *reason)
{
	int last_conn_id;

	if(Error_user_routine)
	{
			Error_conn_id = conn_id;
			last_conn_id = Curr_conn_id;
			(Error_user_routine)(severity, errcode, reason);
			Error_conn_id = 0;
			Curr_conn_id = last_conn_id;
	}
	else
	{
		dim_print_msg(reason, severity);
		if(severity == 3)
		{
			printf("Exiting!\n");
			exit(2);
		}
	}
}

static void recv_rout( int conn_id, DIS_PACKET *packet, int size, int status )
{
	register DIC_SERVICE *servp, *auxp;
	register DIC_CONNECTION *dic_connp;
	int service_id, once_only, found = 0;
	char node[MAX_NODE_NAME], task[MAX_TASK_NAME];
	void move_to_notok_service();
	void do_cmnd_callback();
	void dim_panic(char *);

	dic_connp = &Dic_conns[conn_id] ;
	switch( status )
	{
	case STA_DISC:
		if(Debug_on)
		{
			dna_get_node_task(conn_id, node, task);
			dim_print_date_time();
			printf("Conn %d: Server %s on node %s Disconnected\n",
				conn_id, task, node);
			fflush(stdout);
		}
		if( !(servp = (DIC_SERVICE *) dic_connp->service_head) )
		{
			release_conn( conn_id );
			break;
		}
		while( (servp = (DIC_SERVICE *) dll_get_next(
					(DLL *) dic_connp->service_head,
				 	(DLL *) servp)) )
		{
#ifdef DEBUG
			printf("\t %s was in the service list\n",servp->serv_name);
			fflush(stdout);
#endif
/*
	Will be done later by the DNS answer
			service_tmout( servp->serv_id );
*/
			if(!strcmp(dic_connp->task_name,"DIS_DNS"))
			{
				service_tmout( servp->serv_id );
			}
			else if(Dns_dic_conn_id <= 0)
			{
				service_tmout( servp->serv_id );
			}
/*
			servp->pending = WAITING_DNS_UP;
			servp->conn_id = 0;
*/
			auxp = servp->prev;
			move_to_notok_service( servp );
			servp = auxp;
		}		
		if( (servp = (DIC_SERVICE *) Cmnd_head) ) 
		{
			while( (servp = (DIC_SERVICE *) dll_get_next(
							(DLL *) Cmnd_head,
							(DLL *) servp)) )
			{
				if( servp->conn_id == conn_id )
				{
#ifdef DEBUG
					printf("\t%s was in the Command list\n", servp->serv_name);
					printf("servp = %x, type = %d, pending = %d\n",servp, servp->type, servp->pending);
					fflush(stdout);
#endif
					auxp = servp->prev;
					if( (servp->type == ONCE_ONLY ) &&
						(servp->pending == WAITING_SERVER_UP))
					{
						service_tmout( servp->serv_id );
					}
					else if( (servp->type == COMMAND ) &&
						(servp->pending == WAITING_CMND_ANSWER))
					{
						service_tmout( servp->serv_id );
					}
					else 
					{
						servp->pending = WAITING_DNS_UP;
						dic_release_service( (unsigned)servp->serv_id );
					}
					servp = auxp;
				}
			}
		}
		release_conn( conn_id );
		request_dns_info(0);
		break;
	case STA_DATA:
		if( !(DIC_SERVICE *) dic_connp->service_head )
			break;
		service_id = vtohl(packet->service_id);
		if((unsigned)service_id & 0x80000000)  /* Service removed by server */
		{
			service_id &= 0x7fffffff;
			if( (servp = (DIC_SERVICE *) id_get_ptr(service_id, SRC_DIC))) 
			{
				if( servp->type != COMMAND )
				{
					service_tmout( servp->serv_id );
/*
					servp->pending = WAITING_DNS_UP;
					servp->conn_id = 0;
*/
					move_to_notok_service( servp );
				}
				else
				{
					service_tmout( servp->serv_id );
					break;
				}
			}
			else
			{
/*
				print_packet(packet);
*/
				if( (servp = (DIC_SERVICE *) Cmnd_head) ) 
				{
					while( (servp = (DIC_SERVICE *) dll_get_next(
							(DLL *) Cmnd_head,
							(DLL *) servp)) )
					{
						if( servp->conn_id == conn_id )
						{
#ifdef DEBUG
							printf("\t%s was in the Command list\n", servp->serv_name);
							fflush(stdout);
#endif
							auxp = servp->prev;
							if( (servp->type == ONCE_ONLY ) &&
								(servp->pending == WAITING_SERVER_UP))
							{
								service_tmout( servp->serv_id );
							}
							else if( (servp->type == COMMAND ) &&
								(servp->pending == WAITING_CMND_ANSWER))
							{
								service_tmout( servp->serv_id );
							}
							else 
							{
								servp->pending = WAITING_DNS_UP;
								dic_release_service( (unsigned)servp->serv_id );
							}
							servp = auxp;
						}
					}
				}
			}			
			if( dll_empty((DLL *)dic_connp->service_head) ) {
				if( (servp = (DIC_SERVICE *) Cmnd_head) ) {
					while( (servp = (DIC_SERVICE *) dll_get_next(
							(DLL *) Cmnd_head,
							(DLL *) servp)) )
					{
						if( servp->conn_id == conn_id)
							found = 1;
					}
				}
				if( !found)
				{
					release_conn( conn_id );
				}
			}
			request_dns_info(0);
			break;
		}
		if( (servp = (DIC_SERVICE *) id_get_ptr(service_id, SRC_DIC)))
		{
			if(servp->serv_id == service_id)
			{
				once_only = 0;
				if(servp->type == ONCE_ONLY)
					once_only = 1;
				else 
				{
					if( servp->timeout > 0 ) 
					{
						if(servp->timer_ent)
							dtq_clear_entry( servp->timer_ent );
					}
				}
				Curr_conn_id = conn_id;
				execute_service(packet, servp, size);
				Curr_conn_id = 0;
				if( once_only )
				{
					auxp = locate_command(servp->serv_name);
					if((auxp) && (auxp != servp))
					{
						servp->pending = WAITING_DNS_UP;
						dic_release_service( (unsigned)servp->serv_id );
					}
					else
					{
						servp->pending = NOT_PENDING;
						servp->tmout_done = 0;
						if( servp->timer_ent )
						{
							dtq_rem_entry( Dic_timer_q, servp->timer_ent );
							servp->timer_ent = 0;
						}
					}
				}
			}
		}
/*
		else
		{
			print_packet(packet);
			if(Error_user_routine)
				(Error_user_routine)( packet->buffer );
		}
*/
		break;
	case STA_CONN:
		if(Debug_on)
		{
			dna_get_node_task(conn_id, node, task);
			dim_print_date_time();
			printf("Conn %d: Server %s on node %s Connected\n",
				conn_id, task, node);
			fflush(stdout);
		}
		break;
	default:	dim_panic( "recv_rout(): Bad switch" );
	}
}

static void execute_service(DIS_PACKET *packet, DIC_SERVICE *servp, int size)
{
	int format;
	FORMAT_STR format_data_cp[MAX_NAME/4], *formatp;
	static int *buffer;
	static int buffer_size = 0;
	int add_size;
	int *pkt_buffer, header_size;

	Current_server = servp;
	format = servp->format;
	memcpy(format_data_cp, servp->format_data, sizeof(format_data_cp));
	if((format & 0xF) == ((MY_FORMAT) & 0xF)) 
	{
		for(formatp = format_data_cp; formatp->par_bytes; formatp++)
			formatp->flags &= (short)0xFFF0;    /* NOSWAP */
	}
	if( servp->stamped)
	{
		pkt_buffer = ((DIS_STAMPED_PACKET *)packet)->buffer;
		header_size = DIS_STAMPED_HEADER;
		servp->time_stamp[0] = vtohl(((DIS_STAMPED_PACKET *)packet)->time_stamp[0]);
		if(((unsigned)servp->time_stamp[0] & 0xFFFF0000) == 0xc0de0000)
		{
/*
			servp->time_stamp[0] &= 0x0000FFFF;
*/
			servp->time_stamp[1] = vtohl(((DIS_STAMPED_PACKET *)packet)->time_stamp[1]);
			servp->quality = vtohl(((DIS_STAMPED_PACKET *)packet)->quality);
		}
		else if((vtohl(((DIS_STAMPED_PACKET *)packet)->reserved[0])) == (int)0xc0dec0de)
		{
/*
			servp->time_stamp[0] &= 0x0000FFFF;
*/
			servp->time_stamp[1] = vtohl(((DIS_STAMPED_PACKET *)packet)->time_stamp[1]);
			servp->quality = vtohl(((DIS_STAMPED_PACKET *)packet)->quality);
		}
		else
		{
			pkt_buffer = ((DIS_PACKET *)packet)->buffer;
			header_size = DIS_HEADER;
		}
	}
	else
	{
		pkt_buffer = ((DIS_PACKET *)packet)->buffer;
		header_size = DIS_HEADER;
	}
	size -= header_size;
	if( servp->serv_address ) 
	{
		if( size > servp->serv_size ) 
			size = servp->serv_size; 
		add_size = copy_swap_buffer_in(format_data_cp, 
						 servp->serv_address, 
						 pkt_buffer, size);
		if( servp->user_routine )
			(servp->user_routine)(&servp->tag, servp->serv_address, &add_size );
	} 
	else 
	{
		if( servp->user_routine )
		{
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
			add_size = copy_swap_buffer_in(format_data_cp, 
						 buffer, 
						 pkt_buffer, size);
			(servp->user_routine)( &servp->tag, buffer, &add_size );
		}
	}
	Current_server = 0;
}

static void recv_dns_dic_rout( int conn_id, DNS_DIC_PACKET *packet, int size, int status )
{
	register DIC_SERVICE *servp, *auxp;
	void dim_panic(char *);

	if(size){}
	switch( status )
	{
	case STA_DISC:       /* connection broken */
		servp = Service_pend_head;
		while( (servp = (DIC_SERVICE *) dll_get_next(
						(DLL *) Service_pend_head,
						(DLL *) servp)) )
		{
			if( (servp->pending == WAITING_DNS_ANSWER) ||
			    (servp->pending == WAITING_SERVER_UP))
			{
				if(( servp->type == COMMAND )||( servp->type == ONCE_ONLY ))
				{
					auxp = servp->prev;
					servp->pending = WAITING_DNS_UP;
					service_tmout( servp->serv_id );
					servp = auxp;
				}
				else
				{
					servp->pending = WAITING_DNS_UP;
				}
			}
		}
		dna_close( Dns_dic_conn_id );
		Dns_dic_conn_id = 0;
		request_dns_info(0);
		break;
	case STA_CONN:        /* connection received */
		if(Dns_dic_conn_id < 0)
		{
			Dns_dic_conn_id = conn_id;
			request_dns_info(0);

		}
		break;
	case STA_DATA:       /* normal packet */
		if( vtohl(packet->size) == DNS_DIC_HEADER )
		{
			handle_dns_info( packet );
		}
		break;
	default:	dim_panic( "recv_dns_dic_rout(): Bad switch" );
	}
}


void service_tmout( int serv_id )
{
	int once_only, size = 0;
	register DIC_SERVICE *servp;
	
/*
dim_print_date_time();
printf("In service tmout\n");
*/
	servp=(DIC_SERVICE *)id_get_ptr(serv_id, SRC_DIC);
	if(!servp)
		return;
	if(servp->tmout_done)
		return;
/*
dim_print_date_time();
printf("In service tmout %s\n", servp->serv_name);
*/
	servp->tmout_done = 1;
	Curr_conn_id = servp->conn_id;
/*
	if( servp->type == UPDATE )
		return;
*/
	if( servp->type == COMMAND )
	{
		if( servp->user_routine )
		{
			if(servp->pending == WAITING_CMND_ANSWER)
				size = 1;
			else
				size = 0;
			(servp->user_routine)( &servp->tag, &size );
		}
		dic_release_service( (unsigned)servp->serv_id );
		Curr_conn_id = 0;
		return;
	}
	once_only = 0;
	if(servp->type == ONCE_ONLY)
		once_only = 1;
/*
	if( servp->fill_address )
*/
	if( servp->fill_size >= 0 )
	{
		size = servp->fill_size;
		if( servp->serv_address )
		{
			if( size > servp->serv_size ) 
				size = servp->serv_size; 
			memcpy(servp->serv_address, servp->fill_address, (size_t)size);
			if( servp->user_routine )
				(servp->user_routine)( &servp->tag, servp->serv_address, &size);
		}
		else
		{
			if( servp->user_routine )
				(servp->user_routine)( &servp->tag, servp->fill_address, &size);
		}
	}
	if( once_only )
	{
		dic_release_service( (unsigned)servp->serv_id );
	}
	Curr_conn_id = 0;
}


unsigned dic_info_service( char *serv_name, int req_type, int req_timeout, void *serv_address,
			   int serv_size, void (*usr_routine)(), dim_long tag, void *fill_addr, int fill_size )
{
	unsigned ret;

	ret = request_service( serv_name, req_type, req_timeout, 
		serv_address, serv_size, usr_routine, tag, 
		fill_addr, fill_size, 0 ); 

	return(ret);
}

unsigned dic_info_service_stamped( char *serv_name, int req_type, int req_timeout, void *serv_address,
			   int serv_size, void (*usr_routine)(), dim_long tag, void *fill_addr, int fill_size )
{
	unsigned ret;

	ret = request_service( serv_name, req_type, req_timeout, 
		serv_address, serv_size, usr_routine, tag, 
		fill_addr, fill_size, 1 ); 

	return(ret);
}

unsigned request_service( char *serv_name, int req_type, int req_timeout, void *serv_address,
			   int serv_size, void (*usr_routine)(), dim_long tag, void *fill_addr, int fill_size, int stamped )
{
	register DIC_SERVICE *servp;
	int conn_id;
	int send_service();
	int locate_service();
	void dim_init_threads(void);

	if(!Threads_off)
	{
		dim_init_threads();
	}
	{
	DISABLE_AST
	/* create a timer queue for timeouts if not yet done */
	if( !Dic_timer_q ) {
		conn_arr_create( SRC_DIC );
		Dic_timer_q = dtq_create();
	}

	/* store_service */
	if(req_timeout < 0)
		req_timeout = 0;
	if(req_type == ONCE_ONLY)
	{
		if( !Cmnd_head ) {
			Cmnd_head = (DIC_SERVICE *) malloc(sizeof(DIC_SERVICE) );
			dll_init( (DLL *) Cmnd_head );
			Cmnd_head->serv_id = 0;
		}
		if( (servp = locate_command(serv_name)) ) 
		{
			if( (conn_id = servp->conn_id) ) 
			{
				if(servp->pending == NOT_PENDING)
				{
					modify_service( servp, req_timeout,
						(int *)serv_address, serv_size, usr_routine, tag,
						(int *)fill_addr, fill_size, stamped);
					servp->pending = WAITING_SERVER_UP;
					if(send_service(conn_id, servp))
					{
						ENABLE_AST
						return(1);
					}
				}
			}	
		}
	}
	servp = insert_service( req_type, req_timeout,
			serv_name, (int *)serv_address, serv_size, usr_routine, tag,
			(int *)fill_addr, fill_size, WAITING_DNS_UP, stamped );
            
	/* get_address of server from name_server */
   
	if( locate_service(servp) <= 0)
	{
/*
		service_tmout( servp->serv_id );
*/
		dtq_start_timer( 0, service_tmout, servp->serv_id);
	}
	ENABLE_AST
	}
	return((unsigned) servp->serv_id);
}


int dic_cmnd_service( char *serv_name, void *serv_address, int serv_size )
{
	int ret;

	ret = request_command( serv_name, serv_address, serv_size, 
		0, 0, 0 ); 

	return(ret ? 1 : 0);

}

int dic_cmnd_service_stamped( char *serv_name, void *serv_address, int serv_size )
{
	int ret;

	ret = request_command( serv_name, serv_address, serv_size, 
		0, 0, 1 ); 

	return(ret ? 1 : 0);

}

int dic_cmnd_callback( char *serv_name, void *serv_address, int serv_size, 
					  void (*usr_routine)(), dim_long tag )
{
	int ret;

	ret = request_command( serv_name, serv_address, serv_size, 
		usr_routine, tag, 0 ); 
	return(ret ? 1 : 0);
}

int dic_cmnd_callback_stamped( char *serv_name, void *serv_address, int serv_size, 
					  void (*usr_routine)(), dim_long tag )
{
	int ret;

	ret = request_command( serv_name, serv_address, serv_size, 
		usr_routine, tag, 1 ); 
	return(ret ? 1 : 0);
}

int request_command(char *serv_name, void *serv_address, int serv_size, 
					  void (*usr_routine)(), dim_long tag, int stamped)
{
	int conn_id, ret;
	register DIC_SERVICE *servp, *testp;
	int *fillp;
	int send_command();
	int end_command();
	void dim_init_threads(void);
	int locate_service();

	if(!Threads_off)
	{
		dim_init_threads();
	}
	{
	DISABLE_AST
	/* create a timer queue for timeouts if not yet done */
	if( !Dic_timer_q ) {
		conn_arr_create( SRC_DIC );
		Dic_timer_q = dtq_create();
	}

	/* store_service */
	if( !Cmnd_head ) {
		Cmnd_head = (DIC_SERVICE *) malloc(sizeof(DIC_SERVICE) );
		dll_init( (DLL *) Cmnd_head );
		Cmnd_head->serv_id = 0;
	}
	if( (servp = locate_command(serv_name)) ) 
	{
		if(!(testp = locate_pending(serv_name)))
		{
			if( (conn_id = servp->conn_id) ) 
			{
				if(servp->fill_size > 0)
					free( servp->fill_address );
				fillp = serv_address;
				if(serv_size > 0)
				{
					fillp = (int *)malloc((size_t)serv_size);
					memcpy( (char *)fillp, (char *)serv_address, (size_t)serv_size );
				}
				servp->fill_address = fillp;
				servp->fill_size = serv_size;
/*
				servp->fill_address = (int *)serv_address;
				servp->fill_size = serv_size;
*/
				servp->user_routine = usr_routine;
				servp->tag = tag;
				ret = send_command(conn_id, servp);
				end_command(servp, ret);
				ENABLE_AST
				return(1);
			}
		}	
	}
	servp = insert_service( COMMAND, 0,
				serv_name, 0, 0, usr_routine, tag, 
				(int *)serv_address, serv_size,
				WAITING_DNS_UP, stamped );	
	if( locate_service(servp) <= 0)
	{
/*
		service_tmout( servp->serv_id );
*/
		dtq_start_timer( 0, service_tmout, servp->serv_id);
	}
	ENABLE_AST
	}
	return(-1);
}

DIC_SERVICE *insert_service( int type, int timeout, char *name, int *address, int size, 
							void (*routine)(), dim_long tag, int *fill_addr, int fill_size, 
							int pending, int stamped)
{
	register DIC_SERVICE *newp;
	int *fillp;
	int service_id;
	int tout;
	float ftout;

	DISABLE_AST
	newp = (DIC_SERVICE *) malloc(sizeof(DIC_SERVICE));
	newp->pending = 0;
	strncpy( newp->serv_name, name, (size_t)MAX_NAME );
	newp->type = type;
	newp->timeout = timeout;
	newp->serv_address = address;
	newp->serv_size = size;
	newp->user_routine = routine;
	newp->tag = tag;
	fillp = fill_addr;
	if(fill_size > 0)
	{
		fillp = (int *)malloc((size_t)fill_size);
		memcpy( (char *) fillp, (char *) fill_addr, (size_t)fill_size );
	}
	newp->fill_address = fillp;
	newp->fill_size = fill_size;
	newp->conn_id = 0;
	newp->format_data[0].par_bytes = 0;
	newp->next = (DIC_SERVICE *)0;
	service_id = id_get((void *)newp, SRC_DIC);
	newp->serv_id = service_id;
	if( !Service_pend_head )
	{
		Service_pend_head = (DIC_SERVICE *) malloc(sizeof(DIC_SERVICE));
		dll_init( (DLL *) Service_pend_head );
		Service_pend_head->serv_id = 0;
	}
	dll_insert_queue( (DLL *) Service_pend_head, (DLL *)newp );
	newp->timer_ent = NULL;
	if(type != MONIT_FIRST)
	{
		if( timeout ) 
		{
			tout = timeout;
			if(type != ONCE_ONLY)
			{
				if(tout < 10) 
					tout = 10;
				ftout = (float)tout * (float)1.5;
				tout = (int)ftout;
			}
			newp->curr_timeout = tout;
			newp->timer_ent = dtq_add_entry( Dic_timer_q,
						newp->curr_timeout,
						service_tmout, newp->serv_id );
		}
	}
	newp->pending = pending;
	newp->tmout_done = 0;
	newp->stamped = stamped;
	newp->time_stamp[0] = 0;
	newp->time_stamp[1] = 0;
	newp->quality = 0;
	newp->def[0] = '\0';
#ifdef VxWorks
	newp->tid = taskIdSelf();
#endif
	ENABLE_AST
	return(newp);
}


void modify_service( DIC_SERVICE *servp, int timeout, int *address, int size, void (*routine)(), 
			 dim_long tag, int *fill_addr, int fill_size, int stamped)
{
	int *fillp;

	if( servp->timer_ent )
	{
		dtq_rem_entry( Dic_timer_q, servp->timer_ent );
		servp->timer_ent = 0;
	}
	servp->timeout = timeout;
	servp->serv_address = address;
	servp->serv_size = size;
	servp->user_routine = routine;
	servp->tag = tag;
	if(servp->fill_size > 0)
		free( servp->fill_address );
	fillp = fill_addr;
	if(fill_size > 0)
	{
		fillp = (int *)malloc((size_t)fill_size);
		memcpy( (char *) fillp, (char *) fill_addr, (size_t)fill_size );
	}
	servp->fill_address = fillp;
	servp->fill_size = fill_size;
	servp->stamped = stamped;
	if(timeout)
	{
		servp->curr_timeout = timeout;
		servp->timer_ent = dtq_add_entry( Dic_timer_q,
						servp->curr_timeout,
						service_tmout, servp->serv_id );
	}
	else
		servp->timer_ent = NULL;
}

void dic_change_address( unsigned serv_id, void *serv_address, int serv_size)
{
	register DIC_SERVICE *servp;

	DISABLE_AST
	if( serv_id == 0 )
	  {
	        ENABLE_AST
		return;
	  }
	servp = (DIC_SERVICE *)id_get_ptr(serv_id, SRC_DIC);
	servp->serv_address = (int *)serv_address;
	servp->serv_size = serv_size;
	ENABLE_AST
}

int dic_get_quality( unsigned serv_id )
{
	register DIC_SERVICE *servp;

	DISABLE_AST
	if( serv_id == 0 )
	{
		if(Current_server)
			servp = Current_server;
		else
		{

	    	ENABLE_AST
			return(-1);
		}
	}
	else
	{
		servp = (DIC_SERVICE *)id_get_ptr(serv_id, SRC_DIC);
	}
	ENABLE_AST
	return(servp->quality);
}

char *dic_get_format( unsigned serv_id )
{
	register DIC_SERVICE *servp;

	DISABLE_AST
	if( serv_id == 0 )
	{
		if(Current_server)
			servp = Current_server;
		else
		{
	    	ENABLE_AST
			return((char *) 0);
		}
	}
	else
	{
		servp = (DIC_SERVICE *)id_get_ptr(serv_id, SRC_DIC);
	}
	ENABLE_AST
	return(servp->def);
}

int dic_get_timestamp( unsigned serv_id, int *secs, int *milisecs )
{
	register DIC_SERVICE *servp;

	DISABLE_AST
	*secs = 0;
	*milisecs = 0;
	if( serv_id == 0 )
	{
		if(Current_server)
			servp = Current_server;
		else
		{
	    	ENABLE_AST
			return(-1);
		}
	}
	else
	{
		servp = (DIC_SERVICE *)id_get_ptr(serv_id, SRC_DIC);
	}
	ENABLE_AST
	if(servp->time_stamp[1])
	{
		*secs = servp->time_stamp[1];
		if(((unsigned)servp->time_stamp[0] & 0xFFFF0000) == 0xc0de0000)
			*milisecs = servp->time_stamp[0] & 0x0000FFFF;
		else
			*milisecs = servp->time_stamp[0];
		return(1);
	}
	else
	{
/*
		*secs = 0;
		*milisecs = 0;
*/
		return(0);
	}
}

void dic_release_service( unsigned service_id )
{
	register DIC_SERVICE *servp;
	register int conn_id, pending;
	static DIC_PACKET *dic_packet;
	static int packet_size = 0;
	DIC_DNS_PACKET dic_dns_packet;
	register DIC_DNS_PACKET *dic_dns_p = &dic_dns_packet;
	SERVICE_REQ *serv_reqp;
	int release_service();

	DISABLE_AST
	if( !packet_size ) {
		dic_packet = (DIC_PACKET *)malloc((size_t)DIC_HEADER);
		packet_size = DIC_HEADER;
	}
	if( service_id == 0 )
	{
	    ENABLE_AST
		return;
	}
	servp = (DIC_SERVICE *)id_get_ptr(service_id, SRC_DIC);
	if( servp == 0 )
	{
	    ENABLE_AST
		return;
	}
	if(servp->serv_id != (int)service_id)
	{
	    ENABLE_AST
		return;
	}
	pending = servp->pending;
	switch( pending )
	{
	case NOT_PENDING :
		conn_id = servp->conn_id;
		strncpy(dic_packet->service_name, servp->serv_name, (size_t)MAX_NAME); 
		dic_packet->type = htovl(DIM_DELETE);
		dic_packet->service_id = (int)htovl(service_id);
		dic_packet->size = htovl(DIC_HEADER);
		dna_write_nowait( conn_id, dic_packet, DIC_HEADER );
		release_service( servp );
		break;
	case WAITING_SERVER_UP :
		if( ( servp->type == COMMAND )||( servp->type == ONCE_ONLY ) )
		{
			servp->pending = DELETED;
			break;
		}
		if( Dns_dic_conn_id > 0) {
			dic_dns_p->size = htovl(sizeof(DIC_DNS_PACKET));
			dic_dns_p->src_type = htovl(SRC_DIC);
			serv_reqp = &dic_dns_p->service;
			strcpy( serv_reqp->service_name, servp->serv_name );
			serv_reqp->service_id = (int)htovl((unsigned)servp->serv_id | 0x80000000);
			dna_write( Dns_dic_conn_id, dic_dns_p,
				  sizeof(DIC_DNS_PACKET) );
		}
		release_service( servp );
		break;
	case WAITING_CMND_ANSWER :
	case WAITING_DNS_UP :
		release_service( servp );
		break;
	case WAITING_DNS_ANSWER :
		servp->pending = DELETED;
		break;
	}
	ENABLE_AST
}


int release_service( DIC_SERVICE *servicep )
{
	register DIC_SERVICE *servp;
	register int conn_id = 0;
	register int found = 0;
	register DIC_CONNECTION *dic_connp;
	char name[MAX_NAME], *ptr;
	int id;

	id = servicep->serv_id;
	servicep->serv_id = 0;
	conn_id = servicep->conn_id;
	dic_connp = &Dic_conns[conn_id] ;
	dll_remove( (DLL *) servicep );
	if( servicep->timer_ent )
	{
		dtq_rem_entry( Dic_timer_q, servicep->timer_ent );
	}
/*
	if(servicep->type != COMMAND)
*/
	if(servicep->fill_size > 0)
		free( servicep->fill_address );
	if(strstr(servicep->serv_name,"/RpcOut"))
	{
		strcpy(name, servicep->serv_name);
	}
	else
		name[0] = '\0';
	free( servicep );
	if( conn_id && dic_connp->service_head )
	{
		if( dll_empty((DLL *)dic_connp->service_head) ) 
		{
			if( (servp = (DIC_SERVICE *) Cmnd_head) ) 
			{
				while( (servp = (DIC_SERVICE *) dll_get_next(
						(DLL *) Cmnd_head,
						(DLL *) servp)) )
				{
					if( servp->conn_id == conn_id)
						found = 1;
				}
			}
			if( !found)
			{
				if(Debug_on)
				{
					dim_print_date_time();
					printf("Conn %d, Server %s on node %s released\n",
						conn_id, dic_connp->task_name, dic_connp->node_name);
					fflush(stdout);
				}
				release_conn( conn_id );
			}
		}
	}
	if(name[0])
	{
		ptr = strstr(name,"/RpcOut");
		strcpy(ptr + 4, "In"); 
		if( (servp = locate_command(name)) )
			release_service(servp); 
	}
	id_free(id, SRC_DIC);
	return(1);
}


int locate_service( DIC_SERVICE *servp )
{
	extern int open_dns(dim_long, void (*)(), void (*)(), int, int, int);

	if(!strcmp(servp->serv_name,"DIS_DNS/SERVER_INFO"))
	{
		Tmout_min = DID_DNS_TMOUT_MIN;
		Tmout_max = DID_DNS_TMOUT_MAX;
	}
	if(Tmout_min == 0)
	{
		Tmout_min = DIC_DNS_TMOUT_MIN;
		Tmout_max = DIC_DNS_TMOUT_MAX;
	}
	if( !Dns_dic_conn_id )
	  {
	    DISABLE_AST;
		Dns_dic_conn_id = open_dns( 0, recv_dns_dic_rout, error_handler,
					Tmout_min,
					Tmout_max,
					SRC_DIC);
		if(Dns_dic_conn_id == -2)
			error_handler(0, DIM_FATAL, DIMDNSUNDEF, "DIM_DNS_NODE undefined");
		ENABLE_AST;
	  }
	if( Dns_dic_conn_id > 0)
	{
	    DISABLE_AST;
		request_dns_info(servp->prev->serv_id);
		ENABLE_AST;
	}

	return(Dns_dic_conn_id);
}

DIC_SERVICE *locate_command( char *serv_name )
{
	register DIC_SERVICE *servp;

	if(!Cmnd_head)
		return((DIC_SERVICE *)0);
	if( (servp = (DIC_SERVICE *) dll_search( (DLL *) Cmnd_head, serv_name,
					    (int)strlen(serv_name)+1)) )
		return(servp);
	return((DIC_SERVICE *)0);
}

DIC_SERVICE *locate_pending( char *serv_name )
{
	register DIC_SERVICE *servp;

	if(!Service_pend_head)
		return((DIC_SERVICE *)0);
	if( (servp = (DIC_SERVICE *) dll_search( (DLL *) Service_pend_head, serv_name,
					    (int)strlen(serv_name)+1)) )
		return(servp);
	return((DIC_SERVICE *)0);
}

DIC_BAD_CONNECTION *locate_bad(char *node, char *task, int port)
{
	DIC_BAD_CONNECTION *bad_connp;

	if(!Bad_connection_head)
		return((DIC_BAD_CONNECTION *)0);
	bad_connp = Bad_connection_head;
	while( (bad_connp = (DIC_BAD_CONNECTION *) dll_get_next(
						(DLL *) Bad_connection_head,
						(DLL *) bad_connp)) )
	{
		if((!strcmp(bad_connp->conn.node_name, node)) &&
			(!strcmp(bad_connp->conn.task_name, task)) &&
			(bad_connp->conn.port == port) )
		return(bad_connp);
	}
	return((DIC_BAD_CONNECTION *)0);
}

static void request_dns_info(int id)
{
	DIC_SERVICE *servp, *ptr;
	int n_pend = 0;
	int request_dns_single_info();
	extern int open_dns();

	DISABLE_AST
    if( Dns_dic_conn_id <= 0)
	{
		Dns_dic_conn_id = open_dns( 0, recv_dns_dic_rout, error_handler,
					   Tmout_min,
					   Tmout_max,
					   SRC_DIC);
		if(Dns_dic_conn_id == -2)
			error_handler(0, DIM_FATAL, DIMDNSUNDEF, "DIM_DNS_NODE undefined");
	}
	if( Dns_dic_conn_id > 0)
	{
		servp = Service_pend_head;
		if(id > 0)
		{
			ptr = (DIC_SERVICE *)id_get_ptr(id, SRC_DIC);
			if(ptr)
			{
				if((ptr->serv_id == id) && (ptr->pending != NOT_PENDING))
					servp = ptr;
			}
		}

		while( (servp = (DIC_SERVICE *) dll_get_next(
						(DLL *) Service_pend_head,
						(DLL *) servp)) )
		{
			if( servp->pending == WAITING_DNS_UP)
			{
				if(!request_dns_single_info( servp ))
				{
					ENABLE_AST
					return;
			    }
				n_pend++;
			}
			if(n_pend == 1000)
			{
				dtq_start_timer( 0, request_dns_info, servp->serv_id);
				ENABLE_AST
				return;
			}
		}
	}
	else
	{
		servp = Service_pend_head;
		while( (servp = (DIC_SERVICE *) dll_get_next(
						(DLL *) Service_pend_head,
						(DLL *) servp)) )
		{
			if( servp->pending == WAITING_DNS_UP)
			{
				if(( servp->type != COMMAND )&&( servp->type != ONCE_ONLY ))
					service_tmout( servp->serv_id );
			}
		}
	}
	ENABLE_AST
}


int request_dns_single_info( DIC_SERVICE *servp )
{
	static DIC_DNS_PACKET Dic_dns_packet;
	static SERVICE_REQ *serv_reqp;
	int ret = 1;

	if( Dns_dic_conn_id > 0)
	{
	        if(Debug_on)
			{
				dim_print_date_time();
				printf("Requesting DNS Info for %s, id %d\n",
					servp->serv_name, servp->serv_id);
			}
	  
		Dic_dns_packet.src_type = htovl(SRC_DIC);
		serv_reqp = &Dic_dns_packet.service;
		strcpy( serv_reqp->service_name, servp->serv_name );
		serv_reqp->service_id = htovl(servp->serv_id);
		servp->pending = WAITING_DNS_ANSWER;
		Dic_dns_packet.size = htovl(sizeof(DIC_DNS_PACKET));
		if(!dna_write( Dns_dic_conn_id, &Dic_dns_packet,
				      sizeof(DIC_DNS_PACKET) ) )
		  {
		    ret = 0;
		  }

	}
	return ret;
}


static int handle_dns_info( DNS_DIC_PACKET *packet )
{
	int conn_id, service_id;
	DIC_SERVICE *servp;
	char *node_name, *task_name;
	char node_info[MAX_NODE_NAME+4];
	int i, port, protocol, format, pid;
	register DIC_CONNECTION *dic_connp ;
	DIC_DNS_PACKET dic_dns_packet;
	register DIC_DNS_PACKET *dic_dns_p = &dic_dns_packet;
	SERVICE_REQ *serv_reqp;
	DIC_BAD_CONNECTION *bad_connp;
	int retrying = 0;
	int tmout;
	int send_service_command();
	int find_connection();
	void move_to_bad_service();
	void retry_bad_connection();

	service_id = vtohl(packet->service_id);

	servp = (DIC_SERVICE *)id_get_ptr(service_id, SRC_DIC);
	if(!servp)
		return(0);
	if(servp->serv_id != service_id)
		return(0);
	if(Debug_on)
	{
		dim_print_date_time();
		printf("Receiving DNS Info for service %s, id %d\n",servp->serv_name,
			vtohl(packet->service_id));
	}
	node_name = packet->node_name; 
	if(node_name[0] == (char)0xFF)
	{
		error_handler(0, DIM_FATAL, DIMDNSREFUS, "DIM_DNS refuses connection");
		return(0);
	}
	
	task_name =  packet->task_name;
	strcpy(node_info,node_name);
	for(i = 0; i < 4; i ++)
		node_info[(int)strlen(node_name)+i+1] = packet->node_addr[i];
	port = vtohl(packet->port); 
	pid = vtohl(packet->pid); 
	protocol = vtohl(packet->protocol);
	format = vtohl(packet->format);

	if( Dns_dic_timr )
		dtq_clear_entry( Dns_dic_timr );
	if( servp->pending == DELETED ) {
		if( Dns_dic_conn_id > 0) {
			dic_dns_p->size = htovl(sizeof(DIC_DNS_PACKET));
			dic_dns_p->src_type = htovl(SRC_DIC);
			serv_reqp = &dic_dns_p->service;
			strcpy( serv_reqp->service_name, servp->serv_name );
			serv_reqp->service_id = (int)htovl((unsigned)servp->serv_id | 0x80000000);
			dna_write( Dns_dic_conn_id, dic_dns_p,
				  sizeof(DIC_DNS_PACKET) );
		}
		release_service( servp );	
		return(0);
	}
	if( !node_name[0] ) 
	{
		servp->pending = WAITING_SERVER_UP;
		service_tmout( servp->serv_id ); 
		if( servp->pending == DELETED ) 
		{
			if( Dns_dic_conn_id > 0) 
			{
				dic_dns_p->size = htovl(sizeof(DIC_DNS_PACKET));
				dic_dns_p->src_type = htovl(SRC_DIC);
				serv_reqp = &dic_dns_p->service;
				strcpy( serv_reqp->service_name, servp->serv_name );
				serv_reqp->service_id = (int)htovl((unsigned)servp->serv_id | 0x80000000);
				dna_write( Dns_dic_conn_id, dic_dns_p,
					sizeof(DIC_DNS_PACKET) );
			}
			release_service( servp );
		}
		return(0);
	}
#ifdef OSK
	{
		register char *ptr;

		if(strncmp(node_name,"fidel",5))
		{
			for(ptr = node_name; *ptr; ptr++)
			{
				if(*ptr == '.')
				{
					*ptr = '\0';
					break;
				}
			}
		}
	}
#endif
	if( !(conn_id = find_connection(node_name, task_name, port)) ) 
	{
	  bad_connp = locate_bad(node_name, task_name, port);
	  if(bad_connp)
		  retrying = bad_connp->retrying;
	  if((!bad_connp) || (retrying))
	  {	
		if( (conn_id = dna_open_client(node_info, task_name, port,
					      protocol, recv_rout, error_handler, SRC_DIC)) )
		{
/*
#ifndef VxWorks
			if(format & MY_OS9)
			{
				dna_set_test_write(conn_id, TEST_TIME_OSK);
				format &= 0xfffff7ff;
			}
			else
			{
				dna_set_test_write(conn_id, TEST_TIME_VMS);
			}
#endif
*/
			dna_set_test_write(conn_id, dim_get_keepalive_timeout());
			dic_connp = &Dic_conns[conn_id];
			strncpy( dic_connp->node_name, node_name,
				 (size_t)MAX_NODE_NAME); 
			strncpy( dic_connp->task_name, task_name,
				 (size_t)MAX_TASK_NAME);
			dic_connp->port = port;
			dic_connp->pid = pid;
			if(Debug_on)
			{
				dim_print_date_time();
				printf("Conn %d, Server %s on node %s Connecting\n",
					conn_id, dic_connp->task_name, dic_connp->node_name);
				fflush(stdout);
			}

			dic_connp->service_head = 
						malloc(sizeof(DIC_SERVICE));
			dll_init( (DLL *) dic_connp->service_head);
			((DIC_SERVICE *)(dic_connp->service_head))->serv_id = 0;
			if(retrying)
			{
				dll_remove((DLL *)bad_connp->conn.service_head);
				free(bad_connp->conn.service_head);
				dll_remove((DLL *)bad_connp);
				free(bad_connp);
			}
		} 
		else 
		{
			if(!retrying)
			{
				if( !Bad_connection_head )
				{
					Bad_connection_head = (DIC_BAD_CONNECTION *) malloc(sizeof(DIC_BAD_CONNECTION));
					dll_init( (DLL *) Bad_connection_head );
					Bad_connection_head->conn.service_head = 0;
				}
				bad_connp = (DIC_BAD_CONNECTION *) malloc(sizeof(DIC_BAD_CONNECTION));
				bad_connp->n_retries = 0;
				bad_connp->conn.service_head = malloc(sizeof(DIC_SERVICE));
				dll_init( (DLL *) bad_connp->conn.service_head);

				dll_insert_queue( (DLL *) Bad_connection_head, (DLL *) bad_connp );
				if(Debug_on)
				{
					dim_print_date_time();
					printf("Failed connecting to Server %s on node %s port %d\n",
						task_name, node_name, port);
					fflush(stdout);
				}
				service_tmout( servp->serv_id );
			}
			bad_connp->n_retries++;
			bad_connp->retrying = 0;
			strncpy( bad_connp->conn.node_name, node_name, (size_t)MAX_NODE_NAME); 
			strncpy( bad_connp->conn.task_name, task_name, (size_t)MAX_TASK_NAME);
			bad_connp->conn.port = port;
			tmout = BAD_CONN_TIMEOUT * (bad_connp->n_retries - 1);
			if(tmout > 120)
				tmout = 120;
/* Can not be 0, the callback of dtq_start_timer(0) is not protected */
			if(tmout == 0)
				tmout = 1;
			dtq_start_timer(tmout, retry_bad_connection, (dim_long)bad_connp);
			if(( servp->type == COMMAND )||( servp->type == ONCE_ONLY ))
				return(0);
			move_to_bad_service(servp, bad_connp);
/*			
			((DIC_SERVICE *)(dic_connp->service_head))->serv_id = 0;

			servp = Service_pend_head;
			while( (servp = (DIC_SERVICE *) dll_get_next(
						(DLL *) Service_pend_head,
						(DLL *) servp)) )
			{
				if( (servp->pending == WAITING_DNS_ANSWER) ||
					(servp->pending == WAITING_SERVER_UP))
						servp->pending = WAITING_DNS_UP;
			}
			dna_close( Dns_dic_conn_id );
			Dns_dic_conn_id = 0;
			request_dns_info(0);
*/
			return(0);
		}
	  }
	  else
	  {
			if(!retrying)
				service_tmout( servp->serv_id );
			if(( servp->type == COMMAND )||( servp->type == ONCE_ONLY ))
				return(0);
			move_to_bad_service(servp, bad_connp);
			return(0);
	  }
	}
	strcpy(servp->def, packet->service_def);
	get_format_data(format, servp->format_data, servp->def);
	servp->format = format;
	servp->conn_id = conn_id;

	send_service_command( servp );
/*
	if( ret == 1)
	{
		if(servp->pending != WAITING_CMND_ANSWER)
			servp->pending = NOT_PENDING;
		servp->tmout_done = 0;
	}
*/
	return(1);
}

void retry_bad_connection(DIC_BAD_CONNECTION *bad_connp)
{
DIC_SERVICE *servp, *auxp;
int found = 0;
void move_to_notok_service();

	if(!bad_connp)
		return;
	servp = (DIC_SERVICE *)bad_connp->conn.service_head;
	while( (servp = (DIC_SERVICE *) dll_get_next(
					(DLL *) bad_connp->conn.service_head,
				 	(DLL *) servp)) )
	{
/*
		servp->pending = WAITING_DNS_UP;
		servp->conn_id = 0;
*/
		auxp = servp->prev;
		move_to_notok_service( servp );
		servp = auxp;
		found = 1;
	}
	bad_connp->retrying = 1;
	if(found)
		request_dns_info(0);
}

void move_to_ok_service( DIC_SERVICE *servp, int conn_id )
{
	if(Dic_conns[conn_id].service_head)
	{
		DISABLE_AST
/*
printf("move_to_ok %s\n",servp->serv_name);
*/
		servp->pending = NOT_PENDING;
		servp->tmout_done = 0;
		dll_remove( (DLL *) servp );
		dll_insert_queue( (DLL *) Dic_conns[conn_id].service_head,
			  (DLL *) servp );
		ENABLE_AST
	}
}

void move_to_bad_service( DIC_SERVICE *servp, DIC_BAD_CONNECTION *bad_connp)
{
	DISABLE_AST
/*
printf("move_to_bad %s\n",servp->serv_name);
*/
	servp->pending = WAITING_DNS_UP;
	dll_remove( (DLL *) servp );
	dll_insert_queue( (DLL *) bad_connp->conn.service_head, (DLL *) servp );
	ENABLE_AST
}

void move_to_cmnd_service( DIC_SERVICE *servp )
{
/*
	if(servp->pending != WAITING_CMND_ANSWER)
*/
	DISABLE_AST
/*
printf("move_to_cmnd %s\n",servp->serv_name);
*/
	servp->pending = NOT_PENDING;
	servp->tmout_done = 0;
	dll_remove( (DLL *) servp );
	dll_insert_queue( (DLL *) Cmnd_head, (DLL *) servp );
	ENABLE_AST
}

void move_to_notok_service(DIC_SERVICE *servp )
{
	DISABLE_AST
/*
printf("move_to_notok %s\n",servp->serv_name);
*/
	servp->pending = WAITING_DNS_UP;
	servp->conn_id = 0;
	dll_remove( (DLL *) servp );
	dll_insert_queue( (DLL *) Service_pend_head, (DLL *) servp );
	ENABLE_AST
}

static void get_format_data(int format, FORMAT_STR *format_data, char *def)
{
	register FORMAT_STR *formatp = format_data;
	register char code, last_code = 0;
	int num;
	char *ptr = def;

	if(format){}
	while(*ptr)
	{
		switch(*ptr)
		{
			case 'i':
			case 'I':
			case 'l':
			case 'L':
				*ptr = 'I';
				break;
			case 'x':
			case 'X':
				*ptr = 'X';
				break;
			case 's':
			case 'S':
				*ptr = 'S';
				break;
			case 'f':
			case 'F':
				*ptr = 'F';
				break;
			case 'd':
			case 'D':
				*ptr = 'D';
				break;
			case 'c':
			case 'C':
				*ptr = 'C';
				break;
		}
		ptr++;
	}
	code = *def;
	while(*def)
	{
		if(code != last_code)
		{
			formatp->par_num = 0;
			formatp->flags = 0;
			switch(code)
			{
				case 'i':
				case 'I':
				case 'l':
				case 'L':
					formatp->par_bytes = SIZEOF_LONG;
					formatp->flags |= SWAPL;
					break;
				case 'x':
				case 'X':
					formatp->par_bytes = SIZEOF_DOUBLE;
					formatp->flags |= SWAPD;
					break;
				case 's':
				case 'S':
					formatp->par_bytes = SIZEOF_SHORT;
					formatp->flags |= SWAPS;
					break;
				case 'f':
				case 'F':
					formatp->par_bytes = SIZEOF_LONG;
					formatp->flags |= SWAPL;
#ifdef vms
/*
					if((format & 0xF0) != (MY_FORMAT & 0xF0))
*/
					formatp->flags |= (format & 0xF0);
					formatp->flags |= IT_IS_FLOAT;
#endif
					break;
				case 'd':
				case 'D':
					formatp->par_bytes = SIZEOF_DOUBLE;
					formatp->flags |= SWAPD;
#ifdef vms
/*             	
			  		if((format & 0xF0) != (MY_FORMAT & 0xF0))
*/
					formatp->flags |= (format & 0xF0);
					formatp->flags |= IT_IS_FLOAT;
#endif
					break;
				case 'c':
				case 'C':
				case 'b':
				case 'B':
				case 'v':
				case 'V':
					formatp->par_bytes = SIZEOF_CHAR;
					formatp->flags |= NOSWAP;
					break;
			}
		}
		def++;
		if(*def != ':')
		{
/* tested by the server
			if(*def)
			{
				printf("Bad service definition parsing\n");
				fflush(stdout);
   	    	}
			else
*/
				formatp->par_num = 0;
		}
		else
		{
			def++;
			sscanf(def,"%d",&num);
			formatp->par_num += num;
			while((*def != ';') && (*def != '\0'))
				def++;
			if(*def)
	       	    def++;
		}
		last_code = code;
		code = *def;
		if(code != last_code)
			formatp++;
	}
	formatp->par_bytes = 0;
/*
	if((format & 0xF) == (MY_FORMAT & 0xF)) 
	{
		for(i = 0, formatp = format_data; i<index;i++, formatp++)
			formatp->flags &= 0xF0;  
	}
*/
}

int end_command(DIC_SERVICE *servp, int ret)
{
	DIC_SERVICE *aux_servp;
	DIC_CONNECTION *dic_connp;

	DISABLE_AST
	dic_connp = &Dic_conns[servp->conn_id];
	if(servp->pending != WAITING_CMND_ANSWER)
	{
		if((!ret) || (!dic_connp->service_head))
		{
			servp->pending = WAITING_DNS_UP;
			dic_release_service( (unsigned)servp->serv_id );
		}
		else
		{
			aux_servp = locate_command(servp->serv_name);
			if( !aux_servp ) 
			{
				move_to_cmnd_service( servp );
			}
			else
			{
				if(aux_servp != servp)
				{
					servp->pending = WAITING_DNS_UP;
					dic_release_service( (unsigned)servp->serv_id );
				}
			}
		}
	}
	ENABLE_AST
	return(ret);
}

int send_service_command(DIC_SERVICE *servp)
{
    int ret = 1;
	int conn_id;
	int send_command();
	int send_service();

	conn_id = servp->conn_id;
	if( servp->type == COMMAND ) 
	{
		ret = send_command(conn_id, servp);
		end_command(servp, ret);
	} 
	else 
	{
		if( send_service(conn_id, servp))
		{
			if( servp->type == ONCE_ONLY ) 
			{
				if( !locate_command(servp->serv_name) ) 
				{
					move_to_cmnd_service( servp );	
				}
			}
			else
				move_to_ok_service( servp, conn_id );
		}
		else
		{
			if( servp->type == ONCE_ONLY ) 
			{
				servp->pending = WAITING_DNS_UP;
				dic_release_service( (unsigned)servp->serv_id );
			}
			else
			{
				servp->pending = WAITING_DNS_UP;
				servp->conn_id = 0;
/*
				release_conn(conn_id);
*/
				request_dns_info(0);
			}
		}
	}
	return(ret);
}	

int send_service(int conn_id, DIC_SERVICE *servp)
{
	static DIC_PACKET *dic_packet;
	static int serv_packet_size = 0;
    int type, ret;

	if( !serv_packet_size ) {
		dic_packet = (DIC_PACKET *)malloc((size_t)DIC_HEADER);
		serv_packet_size = DIC_HEADER;
	}

	strncpy( dic_packet->service_name, servp->serv_name, (size_t)MAX_NAME ); 
	type = servp->type;
	if(servp->stamped)
		type |= STAMPED;
	dic_packet->type = htovl(type);
	dic_packet->timeout = htovl(servp->timeout);
	dic_packet->service_id = htovl(servp->serv_id);
	dic_packet->format = htovl(MY_FORMAT);
	dic_packet->size = htovl(DIC_HEADER);
	ret = dna_write_nowait(conn_id, dic_packet, DIC_HEADER);
	if(!ret)
	{
		dim_print_date_time();
		printf(" Client Sending Service Request: Couldn't write to Conn %3d : Server %s@%s service %s\n",
			conn_id, Net_conns[conn_id].task, Net_conns[conn_id].node, servp->serv_name);
		fflush(stdout);
	}
	return(ret);
}

typedef struct
{
	int ret_code;
	int serv_id;
} CMNDCB_ITEM;

void do_cmnd_callback(CMNDCB_ITEM *itemp)
{

	DIC_SERVICE *servp;
	int ret, serv_id;
/*
	itemp = (CMNDCB_ITEM *)id_get_ptr(id, SRC_DIC);
*/
	serv_id = itemp->serv_id;
	ret = itemp->ret_code;
	servp = (DIC_SERVICE *)id_get_ptr(serv_id, SRC_DIC);
	if(servp)
	{
		if(servp->serv_id == serv_id)
		{
			Curr_conn_id = servp->conn_id;
			(servp->user_routine)( &servp->tag, &ret );
			servp->pending = NOT_PENDING;
			end_command(servp, ret);
			Curr_conn_id = 0;
		}
	}
/*
	id_free(id, SRC_DIC);
*/
	free(itemp);
}

int send_command(int conn_id, DIC_SERVICE *servp)
{
	static DIC_PACKET *dic_packet;
	static int cmnd_packet_size = 0;
	register int size;
	int ret;
	CMNDCB_ITEM *itemp;

	size = servp->fill_size;

	if(size < 0)
		return(1);

	if( !cmnd_packet_size ) {
		dic_packet = (DIC_PACKET *)malloc((size_t)(DIC_HEADER + size));
		cmnd_packet_size = DIC_HEADER + size;
	}
	else
	{
		if( DIC_HEADER + size > cmnd_packet_size ) {
			free( dic_packet );
			dic_packet = (DIC_PACKET *)malloc((size_t)(DIC_HEADER + size));
			cmnd_packet_size = DIC_HEADER + size;
		}
	}

	strncpy(dic_packet->service_name, servp->serv_name, (size_t)MAX_NAME); 
	dic_packet->type = htovl(COMMAND);
	dic_packet->timeout = htovl(0);
	dic_packet->format = htovl(MY_FORMAT);

	dic_packet->service_id = /*id_get((void *)servp)*/servp->serv_id;

	size = copy_swap_buffer_out(servp->format, servp->format_data, 
					 dic_packet->buffer, servp->fill_address, 
					 size);
	dic_packet->size = htovl( size + DIC_HEADER);
	if( servp->user_routine )
	{
		servp->pending = WAITING_CMND_ANSWER;
		ret = dna_write_nowait(conn_id, dic_packet, DIC_HEADER + size);
		itemp = (CMNDCB_ITEM *)malloc(sizeof(CMNDCB_ITEM));
		itemp->serv_id = servp->serv_id;
		itemp->ret_code = ret;
/*
		id = id_get((void *)itemp, SRC_DIC);
*/
		dtq_start_timer(0, do_cmnd_callback, (dim_long)itemp);
/*
		(servp->user_routine)( &servp->tag, &ret );
*/
	}
	else
	{
		ret = dna_write_nowait(conn_id, dic_packet, DIC_HEADER + size);
	}
/*
	if(!ret)
	{
		servp->pending = WAITING_DNS_UP;
		dic_release_service( (unsigned)servp->serv_id );
	}
*/
	/*
	ret = dna_write_nowait(conn_id, dic_packet, DIC_HEADER + size);
	if(!ret)
	{
		servp->pending = WAITING_DNS_UP;
		dic_release_service( (unsigned)servp->serv_id );
	}
	else
	{
		dim_usleep(5000);
		if( servp->user_routine )
			(servp->user_routine)( &servp->tag, &ret );
	}
*/
	if(!ret)
	{
		dim_print_date_time();
		printf(" Client Sending Command: Couldn't write to Conn %3d : Server %s@%s\n",conn_id,
			Net_conns[conn_id].task, Net_conns[conn_id].node);
		fflush(stdout);
	}
	return(ret);
}

int find_connection(char *node, char *task, int port)
{
	register int i;
	register DIC_CONNECTION *dic_connp;

	if(task){}
	for( i=0, dic_connp = Dic_conns; i<Curr_N_Conns; i++, dic_connp++ )
	{
/*
		if((!strcmp(dic_connp->task_name, task))
			&&(!strcmp(dic_connp->node_name, node)))
*/
		if((!strcmp(dic_connp->node_name, node)) 
			&& (dic_connp->port == port))
		return(i);
	}
	return(0);
}

int dic_get_id(char *name)
{
	extern int get_proc_name(char *name);

	get_proc_name(name);
	strcat(name,"@");
	get_node_name(&name[(int)strlen(name)]);
	return(1);
}
	
#ifdef VxWorks
void dic_destroy(int tid)
{
	register int i;
	register DIC_CONNECTION *dic_connp;
	register DIC_SERVICE *servp, *auxp;
	int found = 0;

	if(!Dic_conns)
	  return;
	for( i=0, dic_connp = Dic_conns; i<Curr_N_Conns; i++, dic_connp++ )
	{
	        if(servp = (DIC_SERVICE *) dic_connp->service_head)
		  {
		    while( servp = (DIC_SERVICE *) dll_get_next(
					(DLL *) dic_connp->service_head,
				 	(DLL *) servp) )
		      {
			if( servp->tid == tid )
			  {
			    auxp = servp->prev;
			    dic_release_service( (unsigned)servp->serv_id );
			    servp = auxp;
			    if(!dic_connp->service_head)
			      break; 
			  }
			else
			  found = 1;
		    }
		}
	}
	if(!found)
	  {
	    if(Dns_dic_conn_id > 0)
	      {
		dna_close( Dns_dic_conn_id );
		Dns_dic_conn_id = 0;
	      }
	  }
}

void DIMDestroy(int tid)
{
  dis_destroy(tid);
  dic_destroy(tid);
}

#endif

static void release_conn(int conn_id)
{
	register DIC_CONNECTION *dic_connp = &Dic_conns[conn_id];

	if(Debug_on)
	{
		dim_print_date_time();
		printf("Conn %d, Server %s on node %s completely released\n",
			conn_id, dic_connp->task_name, dic_connp->node_name);
		fflush(stdout);
	}
	dic_connp->task_name[0] = '\0';
	dic_connp->port = 0;
	if(dic_connp->service_head)
	{
		free((DIC_SERVICE *)dic_connp->service_head);
		dic_connp->service_head = (char *)0;
	}
	dna_close(conn_id);
}	

void dic_close_dns()
{
	register DIC_SERVICE *servp, *auxp;
		
	if(Dns_dic_conn_id > 0)
	{
		if( (servp = (DIC_SERVICE *) Cmnd_head) ) 
		{
			while( (servp = (DIC_SERVICE *) dll_get_next(
							(DLL *) Cmnd_head,
							(DLL *) servp)) )
			{
#ifdef DEBUG
					printf("\t%s was in the Command list\n", servp->serv_name);
					printf("type = %d, pending = %d\n",servp->type, servp->pending);
					fflush(stdout);
#endif
				auxp = servp->prev;
				if( (servp->type == ONCE_ONLY ) &&
					(servp->pending == WAITING_SERVER_UP))
				{
					service_tmout( servp->serv_id );
				}
				else if( (servp->type == COMMAND ) &&
					(servp->pending == WAITING_CMND_ANSWER))
				{
					service_tmout( servp->serv_id );
				}
				else 
				{
					servp->pending = WAITING_DNS_UP;
					dic_release_service( (unsigned)servp->serv_id );
				}
				servp = auxp;
			}
		}
		dna_close( Dns_dic_conn_id );
		Dns_dic_conn_id = 0;
	}
}
/*
append_service(service_info_buffer, servp)		
char *service_info_buffer;
SERVICE *servp;
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
		if(servp = find_service(name))
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
*/

char *dic_get_error_services()
{
	return(dic_get_server_services(Error_conn_id));
}

char *dic_get_server_services(int conn_id)
{
	DIC_SERVICE *servp;
	DIC_CONNECTION *dic_connp;
	int n_services = 0;
	int max_size;
	static int curr_allocated_size = 0;
	static char *service_info_buffer;
	char *buff_ptr;


	if(!conn_id)
		return((char *)0);			
	dic_connp = &Dic_conns[conn_id];
	if( (servp = (DIC_SERVICE *) dic_connp->service_head) )
	{
		while( (servp = (DIC_SERVICE *) dll_get_next(
					(DLL *) dic_connp->service_head,
				 	(DLL *) servp)) )
		{
			n_services++;
		}
		if(!n_services)
			return((char *)0);			
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

		servp = (DIC_SERVICE *) dic_connp->service_head;
		while( (servp = (DIC_SERVICE *) dll_get_next(
					(DLL *) dic_connp->service_head,
				 	(DLL *) servp)) )
		{
			strcat(buff_ptr, servp->serv_name);
			strcat(buff_ptr, "\n");
			buff_ptr += (int)strlen(buff_ptr);
		}
	}
	else
	{
		return((char *)0);			
	}
/*
	dim_print_date_time();
	printf("Server %s@%s provides services:\n",
			dic_connp->task_name, dic_connp->node_name);
	printf("%s\n",service_info_buffer);
*/
	return(service_info_buffer);
}

int dic_get_conn_id()
{
	return(Curr_conn_id);
}

int dic_get_server(char *name)
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

int dic_get_server_pid(int *pid)
{
	int ret = 0;

	DISABLE_AST

	*pid = 0;
	if(Curr_conn_id)
	{
		*pid = Dic_conns[Curr_conn_id].pid;
		ret = Curr_conn_id;
	}
	ENABLE_AST
	return(ret);
}

void dic_stop()
{
	int dic_find_server_conns();

	dtq_delete(Dic_timer_q);
	dic_close_dns();
	if(!dic_find_server_conns())
		dim_stop();
}

int dic_find_server_conns()
{
	int i;
	int n = 0;

	for( i = 0; i< Curr_N_Conns; i++ )
	{
		if(Net_conns[i].channel != 0)
		{
			if(Dna_conns[i].read_ast == recv_rout)
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

#ifdef VMS
/* CFORTRAN WRAPPERS */
FCALLSCFUN9(INT, dic_info_service, DIC_INFO_SERVICE, dic_info_service,
                 STRING, INT, INT, PVOID, INT, PVOID, INT, PVOID, INT)
FCALLSCFUN9(INT, dic_info_service_stamped, DIC_INFO_SERVICE_STAMPED, 
				 dic_info_service_stamped,
                 STRING, INT, INT, PVOID, INT, PVOID, INT, PVOID, INT)
FCALLSCFUN3(INT, dic_cmnd_service, DIC_CMND_SERVICE, dic_cmnd_service,
                 STRING, PVOID, INT)
FCALLSCFUN5(INT, dic_cmnd_callback, DIC_CMND_CALLBACK, dic_cmnd_callback,
                 STRING, PVOID, INT, PVOID, INT)
FCALLSCFUN3(INT, dic_cmnd_service_stamped, DIC_CMND_SERVICE_STAMPED, 
				 dic_cmnd_service_stamped,
                 STRING, PVOID, INT)
FCALLSCFUN5(INT, dic_cmnd_callback_stamped, DIC_CMND_CALLBACK_STAMPED, 
				 dic_cmnd_callback_stamped,
                 STRING, PVOID, INT, PVOID, INT)
FCALLSCSUB3(     dic_change_address, DIC_CHANGE_ADDRESS, dic_change_address,
                 INT, PVOID, INT)
FCALLSCSUB1(     dic_release_service, DIC_RELEASE_SERVICE, dic_release_service,
                 INT)
FCALLSCFUN1(INT, dic_get_quality, DIC_GET_QUALITY, dic_get_quality,
                 INT)
FCALLSCFUN3(INT, dic_get_timestamp, DIC_GET_TIMESTAMP, dic_get_timestamp,
                 INT,PINT,PINT)
FCALLSCFUN1(INT, dic_get_id, DIC_GET_ID, dic_get_id,
                 PSTRING)
FCALLSCFUN1(STRING, dic_get_format, DIC_GET_FORMAT, dic_get_format,
                 INT)
#endif
