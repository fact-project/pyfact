#ifndef __DIMDEFS
#define __DIMDEFS
/*
 * DNA (Delphi Network Access) implements the network layer for the DIM
 * (Delphi Information Managment) System.
 *
 * Started           : 10-11-91
 * Last modification : 03-08-94
 * Written by        : C. Gaspar
 * Adjusted by       : G.C. Ballintijn
 *
 */

#include "dim_common.h"

#define DIM_VERSION_NUMBER 2013


#define MY_LITTLE_ENDIAN	0x1
#define MY_BIG_ENDIAN 		0x2

#define VAX_FLOAT		0x10
#define IEEE_FLOAT 		0x20
#define AXP_FLOAT		0x30

#define MY_OS9			0x100
#define IT_IS_FLOAT		0x1000

#ifdef VMS
#include <ssdef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <starlet.h>
#include <time.h>
#define DIM_NOSHARE noshare
#define RE_ENABLE_AST   long int ast_enable = sys$setast(1);
#define RE_DISABLE_AST  if (ast_enable != SS$_WASSET) sys$setast(0);
#define	vtohl(l)	(l)
#define	htovl(l)	(l)
#ifdef __alpha
#define MY_FORMAT MY_LITTLE_ENDIAN+AXP_FLOAT
#else
#define MY_FORMAT MY_LITTLE_ENDIAN+VAX_FLOAT
#endif
#endif

#ifdef __unix__
#include <unistd.h>
#include <sys/time.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#ifdef VxWorks
#include <sigLib.h>
#endif
#define DIM_NOSHARE 
#define RE_ENABLE_AST   sigset_t set, oset;sigemptyset(&set);sigaddset(&set,SIGIO);sigaddset(&set,SIGALRM);sigprocmask(SIG_UNBLOCK,&set,&oset);
#define RE_DISABLE_AST  sigprocmask(SIG_SETMASK,&oset,0);
#ifdef MIPSEL
#define	vtohl(l)	(l)
#define	htovl(l)	(l)
#define MY_FORMAT MY_LITTLE_ENDIAN+IEEE_FLOAT
#endif
#ifdef MIPSEB
#define	vtohl(l)	_swapl(l)
#define	htovl(l)	_swapl(l)
#define	vtohs(s)	_swaps(s)
#define	htovs(s)	_swaps(s)
#define MY_FORMAT MY_BIG_ENDIAN+IEEE_FLOAT
#endif
_DIM_PROTO( int _swapl,  (int l) );
_DIM_PROTO( short _swaps,   (short s) );

#endif

#ifdef WIN32
#include <windows.h>
#include <process.h>
#include <io.h>
#include <fcntl.h>
#include <Winsock.h>
#include <stddef.h>
#include <stdlib.h>
#include <stdio.h>
#define DIM_NOSHARE 
#define RE_ENABLE_AST     
#define RE_DISABLE_AST    
#ifdef MIPSEL
#define	vtohl(l)	(l)
#define	htovl(l)	(l)
#define MY_FORMAT MY_LITTLE_ENDIAN+IEEE_FLOAT
#endif
#ifdef MIPSEB
#define	vtohl(l)	_swapl(l)
#define	htovl(l)	_swapl(l)
#define	vtohs(s)	_swaps(s)
#define	htovs(s)	_swaps(s)
#define MY_FORMAT MY_BIG_ENDIAN+IEEE_FLOAT
#endif
_DIM_PROTO( int _swapl,  (int l) );
_DIM_PROTO( short _swaps,   (short s) );
#endif

#ifdef OSK
#include <types.h>
#ifndef _UCC
#include <machine/types.h>
#else
#define register
#endif
#include <inet/in.h>
#include <time.h>
#include <stdio.h>
#include <string.h>
#define DIM_NOSHARE 
#define RE_ENABLE_AST      sigmask(DEC_LEVEL);
#define RE_DISABLE_AST     sigmask(INC_LEVEL);
#define	vtohl(l)	_swapl(l)
#define	htovl(l)	_swapl(l)
#define	vtohs(s)	_swaps(s)
#define	htovs(s)	_swaps(s)
#define MY_FORMAT MY_BIG_ENDIAN+IEEE_FLOAT+MY_OS9
typedef unsigned short	ushort;
_DIM_PROTO( char *getenv,  (char *name) );
_DIM_PROTO( void *malloc,  (unsigned size) );
_DIM_PROTO( void *realloc, (void *ptr, unsigned size) );
_DIM_PROTO( int _swapl,   (int l) );
_DIM_PROTO( short _swaps,   (short s) );
#endif

#define	TRUE	1
#define	FALSE	0

#define DNS_TASK	"DIM_DNS"
#define DNS_PORT	2505			/* Name server port          */
#define SEEK_PORT	0			/* server should seek a port */

#define MIN_BIOCNT	 	50
#ifdef OSK
#define DIS_DNS_TMOUT_MIN	5
#define DIS_DNS_TMOUT_MAX	10
#define DIC_DNS_TMOUT_MIN	5
#define DIC_DNS_TMOUT_MAX	10
#define MAX_SERVICE_UNIT 	32
#define MAX_REGISTRATION_UNIT 100
#define CONN_BLOCK		32
#define MAX_CONNS		32
#define ID_BLOCK		64
#define TCP_RCV_BUF_SIZE	4096
#define TCP_SND_BUF_SIZE	4096
#else
#define DIS_DNS_TMOUT_MIN	5
#define DIS_DNS_TMOUT_MAX	10
#define DIC_DNS_TMOUT_MIN	5
#define DIC_DNS_TMOUT_MAX	10
#define MAX_SERVICE_UNIT 	100
#define MAX_REGISTRATION_UNIT 100
#define CONN_BLOCK		256
#define MAX_CONNS		1024
#define ID_BLOCK		512
#define TCP_RCV_BUF_SIZE	/*16384*//*32768*/65536
#define TCP_SND_BUF_SIZE	/*16384*//*32768*/65536
#endif
#define DID_DNS_TMOUT_MIN	5
#define DID_DNS_TMOUT_MAX	10
/*
#define WATCHDOG_TMOUT_MIN	120
#define WATCHDOG_TMOUT_MAX	180
*/
#define WATCHDOG_TMOUT_MIN	60
#define WATCHDOG_TMOUT_MAX	90
/*
#define WATCHDOG_TMOUT_MIN	15
#define WATCHDOG_TMOUT_MAX	25
*/
#define MAX_NODE_NAME		40
#define MAX_TASK_NAME		40
#define MAX_NAME 		132
/*
#define MAX_CMND 		16384
#define MAX_IO_DATA 	65535
#define MAX_IO_DATA		(TCP_SND_BUF_SIZE - 16)
*/
typedef enum { DNS_DIS_REGISTER, DNS_DIS_KILL, DNS_DIS_STOP, 
			   DNS_DIS_EXIT, DNS_DIS_SOFT_EXIT } DNS_DIS_TYPES;
typedef enum { RD_HDR, RD_DATA, RD_DUMMY } CONN_STATE;
typedef enum { NOSWAP, SWAPS, SWAPL, SWAPD} SWAP_TYPE;

#define DECNET			0		/* Decnet as transport layer */
#define TCPIP			1		/* Tcpip as transport layer  */
#define BOTH			2		/* Both protocols allowed    */

#define	STA_DISC		(-1)		/* Connection lost           */
#define	STA_DATA		0		/* Data received             */
#define	STA_CONN		1		/* Connection made           */

#define	START_PORT_RANGE	5100		/* Lowest port to use        */
#define	STOP_PORT_RANGE		10000		/* Highest port to use       */
#define	TEST_TIME_OSK		15		/* Interval to test conn.    */
#define	TEST_TIME_VMS		30		/* Interval to test conn.    */
#define	TEST_WRITE_TAG		25		/* DTQ tag for test writes   */
#define	WRITE_TMOUT			5		/* Interval to wait while writing.    */

#define	OPN_MAGIC		0xc0dec0de	/* Magic value 1st packet    */
#define	HDR_MAGIC		0xfeadfead	/* Magic value in header     */
#define	LONG_HDR_MAGIC	0xfeadc0de	/* Magic value in long header*/
#define	TST_MAGIC		0x11131517	/* Magic value, test write   */
#define	TRP_MAGIC		0x71513111	/* Magic value, test reply   */

/* String Format */

typedef struct{
	int par_num;
	short par_bytes;
	short flags;     /* bits 0-1 is type of swap, bit 4 id float conversion */
}FORMAT_STR;

/* Packet sent by the client to the server inside DNA */
typedef struct{
	int code;
	char node[MAX_NODE_NAME];
	char task[MAX_TASK_NAME];
} DNA_NET;

/* Packet sent by the client to the server */
typedef struct{
	int size;
	char service_name[MAX_NAME];
	int service_id;
	int type;
	int timeout;
	int format;
	int buffer[1];
} DIC_PACKET;

#define DIC_HEADER		(MAX_NAME + 20)

/* Packets sent by the server to the client */
typedef struct{
	int size;
	int service_id;
	int buffer[1];
} DIS_PACKET;

#define DIS_HEADER		8

typedef struct{
	int size;
	int service_id;
	int time_stamp[2];
	int quality;
	int reserved[3];
	int buffer[1];
} DIS_STAMPED_PACKET;

#define DIS_STAMPED_HEADER		32

/* Packet sent by the server to the name_server */
typedef struct{
	char service_name[MAX_NAME];
	int service_id;
	char service_def[MAX_NAME];
} SERVICE_REG;
	
typedef struct{
	int size;
	SRC_TYPES src_type;
	char node_name[MAX_NODE_NAME];
	char task_name[MAX_TASK_NAME-4];
	char node_addr[4];
	int pid;
	int port;
	int protocol;
	int format;
	int n_services;
	SERVICE_REG services[MAX_SERVICE_UNIT];
} DIS_DNS_PACKET;

#define DIS_DNS_HEADER		(MAX_NODE_NAME + MAX_TASK_NAME + 28) 

/* Packet sent by the name_server to the server */
typedef struct {
	int size;
	int type;
} DNS_DIS_PACKET;

#define DNS_DIS_HEADER		8

/* Packet sent by the client to the name_server */
typedef struct{
	char service_name[MAX_NAME];
	int service_id;
} SERVICE_REQ;
	
typedef struct{
	int size;
	SRC_TYPES src_type;
	SERVICE_REQ service;
} DIC_DNS_PACKET;

/* Packet sent by the name_server to the client */
typedef struct {
	int size;
	int service_id;
	char service_def[MAX_NAME];
	char node_name[MAX_NODE_NAME];
	char task_name[MAX_TASK_NAME-4];
	char node_addr[4];
	int pid;
	int port;
	int protocol;
	int format;
} DNS_DIC_PACKET;

#define DNS_DIC_HEADER		(MAX_NODE_NAME + MAX_TASK_NAME + MAX_NAME + 24) 

typedef struct {
	char name[MAX_NAME];
	char node[MAX_NODE_NAME];
	char task[MAX_TASK_NAME];
	int type;
	int status;
	int n_clients;
} DNS_SERV_INFO;

typedef struct {
	char name[MAX_NAME];
	int type;
	int status;
	int n_clients;
} DNS_SERVICE_INFO;

typedef struct {
	char node[MAX_NODE_NAME];
	char task[MAX_TASK_NAME];
	int pid;
	int n_services;
} DNS_SERVER_INFO;

typedef struct {
	DNS_SERVER_INFO server;
	DNS_SERVICE_INFO services[1];
} DNS_DID;

typedef struct {
	char node[MAX_NODE_NAME];
	char task[MAX_TASK_NAME];
} DNS_CLIENT_INFO;

typedef struct {
	int header_size;
	int data_size;
	int header_magic;
} DNA_HEADER;

typedef struct {
	int header_size;
	int data_size;
	int header_magic;
	int time_stamp[2];
	int quality;
} DNA_LONG_HEADER;

/* Connection handling */

typedef struct timer_entry{
	struct timer_entry *next;
	struct timer_entry *prev;
	struct timer_entry *next_done;
	int time;
	int time_left;
	void (*user_routine)();
	dim_long tag;
} TIMR_ENT;

typedef struct {
	int busy;
	void (*read_ast)();
	void (*error_ast)();
	int *buffer;
	int buffer_size;
	char *curr_buffer;
	int curr_size;
	int full_size;
	int protocol;
	CONN_STATE state;
	int writing;
	int saw_init;
} DNA_CONNECTION;

extern DllExp DIM_NOSHARE DNA_CONNECTION *Dna_conns;

typedef struct {
	int channel;
	int mbx_channel;
	void (*read_rout)();
	char *buffer;
	int size;
/*
	unsigned short *iosb_r;
	unsigned short *iosb_w;
*/
	char node[MAX_NODE_NAME];
	char task[MAX_TASK_NAME];
	int port;
	int reading;
	int timeout;
	int write_timedout;
	TIMR_ENT *timr_ent;
	time_t last_used;
} NET_CONNECTION;
 
extern DllExp DIM_NOSHARE NET_CONNECTION *Net_conns;

typedef struct {
	char node_name[MAX_NODE_NAME];
	char task_name[MAX_TASK_NAME];
	int port;
	int pid;
	char *service_head;
} DIC_CONNECTION;

extern DIM_NOSHARE DIC_CONNECTION *Dic_conns;

typedef struct {
	SRC_TYPES src_type;
	char node_name[MAX_NODE_NAME];
	char task_name[MAX_TASK_NAME-4];
	char node_addr[4];
	int pid;
	int port;
	char *service_head;
	char *node_head;
	int protocol;
	int validity;
	int n_services;
	int old_n_services;
	TIMR_ENT *timr_ent;
	int already;
	char long_task_name[MAX_NAME];
} DNS_CONNECTION;

extern DllExp DIM_NOSHARE DNS_CONNECTION *Dns_conns;

extern DllExp DIM_NOSHARE int Curr_N_Conns;

/* Client definitions needed by dim_jni.c (from H.Essel GSI) */
typedef enum {
	NOT_PENDING, WAITING_DNS_UP, WAITING_DNS_ANSWER, WAITING_SERVER_UP,
	WAITING_CMND_ANSWER, DELETED
} PENDING_STATES;

typedef struct dic_serv {
	struct dic_serv *next;
	struct dic_serv *prev;
	char serv_name[MAX_NAME];
	int serv_id;
	FORMAT_STR format_data[MAX_NAME/4];
	char def[MAX_NAME];
	int format;
	int type;
	int timeout;
	int curr_timeout;
	int *serv_address;
	int serv_size;
	int *fill_address;
	int fill_size;
	void (*user_routine)();
	dim_long tag;
	TIMR_ENT *timer_ent;
	int conn_id;
	PENDING_STATES pending;
	int tmout_done;
	int stamped;
	int time_stamp[2];
	int quality;
    int tid;
} DIC_SERVICE;

/* PROTOTYPES */
#ifdef __cplusplus
extern "C" {
#define __CXX_CONST const
#else
#define __CXX_CONST
#endif

/* DNA */
_DIM_PROTOE( int dna_start_read,    (int conn_id, int size) );
_DIM_PROTOE( void dna_test_write,   (int conn_id) );
_DIM_PROTOE( int dna_write,         (int conn_id, __CXX_CONST void *buffer, int size) );
_DIM_PROTOE( int dna_write_nowait,  (int conn_id, __CXX_CONST void *buffer, int size) );
_DIM_PROTOE( int dna_open_server,   (__CXX_CONST char *task, void (*read_ast)(), int *protocol,
				int *port, void (*error_ast)()) );
_DIM_PROTOE( int dna_get_node_task, (int conn_id, char *node, char *task) );
_DIM_PROTOE( int dna_open_client,   (__CXX_CONST char *server_node, __CXX_CONST char *server_task, int port,
                                int server_protocol, void (*read_ast)(), void (*error_ast)(), SRC_TYPES src_type ));
_DIM_PROTOE( int dna_close,         (int conn_id) );
_DIM_PROTOE( void dna_report_error, (int conn_id, int code, char *routine_name) );


/* TCPIP */
_DIM_PROTOE( int tcpip_open_client,     (int conn_id, char *node, char *task,
                                    int port) );
_DIM_PROTOE( int tcpip_open_server,     (int conn_id, char *task, int *port) );
_DIM_PROTOE( int tcpip_open_connection, (int conn_id, int channel) );
_DIM_PROTOE( int tcpip_start_read,      (int conn_id, char *buffer, int size,
                                    void (*ast_routine)()) );
_DIM_PROTOE( int tcpip_start_listen,    (int conn_id, void (*ast_routine)()) );
_DIM_PROTOE( int tcpip_write,           (int conn_id, char *buffer, int size) );
_DIM_PROTOE( void tcpip_get_node_task,  (int conn_id, char *node, char *task) );
_DIM_PROTOE( int tcpip_close,           (int conn_id) );
_DIM_PROTOE( int tcpip_failure,         (int code) );
_DIM_PROTOE( void tcpip_report_error,   (int code) );


/* DTQ */
_DIM_PROTOE( int dtq_create,          (void) );
_DIM_PROTOE( int dtq_delete,          (int queue_id) );
_DIM_PROTOE( TIMR_ENT *dtq_add_entry, (int queue_id, int time,
                                  void (*user_routine)(), dim_long tag) );
_DIM_PROTOE( int dtq_clear_entry,     (TIMR_ENT *entry) );
_DIM_PROTOE( int dtq_rem_entry,       (int queue_id, TIMR_ENT *entry) );

/* UTIL */
typedef struct dll {
	struct dll *next;
	struct dll *prev;
	char user_info[1];
} DLL;

typedef struct sll {
	struct sll *next;
	char user_info[1];
} SLL;

_DIM_PROTO( void DimDummy,        () );     
_DIM_PROTOE( void conn_arr_create, (SRC_TYPES type) );
_DIM_PROTOE( int conn_get,         (void) );
_DIM_PROTOE( void conn_free,       (int conn_id) );
_DIM_PROTOE( void *arr_increase,   (void *conn_ptr, int conn_size, int n_conns) );
_DIM_PROTOE( void id_arr_create,   () );
_DIM_PROTOE( void *id_arr_increase,(void *id_ptr, int id_size, int n_ids) );

_DIM_PROTOE( void dll_init,         ( DLL *head ) );
_DIM_PROTOE( void dll_insert_queue, ( DLL *head, DLL *item ) );
_DIM_PROTOE( void dll_insert_after, ( DLL *after, DLL *item ) );
_DIM_PROTOE( DLL *dll_search,       ( DLL *head, char *data, int size ) );
_DIM_PROTOE( DLL *dll_get_next,     ( DLL *head, DLL *item ) );
_DIM_PROTOE( DLL *dll_get_prev,     ( DLL *head, DLL *item ) );
_DIM_PROTOE( int dll_empty,         ( DLL *head ) );
_DIM_PROTOE( void dll_remove,       ( DLL *item ) );

_DIM_PROTOE( void sll_init,               ( SLL *head ) );
_DIM_PROTOE( int sll_insert_queue,        ( SLL *head, SLL *item ) );
_DIM_PROTOE( SLL *sll_search,             ( SLL *head, char *data, int size ) );
_DIM_PROTOE( SLL *sll_get_next,           ( SLL *item ) );
_DIM_PROTOE( int sll_empty,               ( SLL *head ) );
_DIM_PROTOE( int sll_remove,              ( SLL *head, SLL *item ) );
_DIM_PROTOE( SLL *sll_remove_head,        ( SLL *head ) );
_DIM_PROTOE( SLL *sll_search_next_remove, ( SLL *item, int offset, char *data, int size ) );
_DIM_PROTOE( SLL *sll_get_head, 		  ( SLL *head ) );

_DIM_PROTOE( int HashFunction,         ( char *name, int max ) );

_DIM_PROTOE( int copy_swap_buffer_out, (int format, FORMAT_STR *format_data, 
					void *buff_out, void *buff_in, int size) );
_DIM_PROTOE( int copy_swap_buffer_in, (FORMAT_STR *format_data, void *buff_out, 
					void *buff_in, int size) );
_DIM_PROTOE( int get_node_name, (char *node_name) );

_DIM_PROTOE( int get_dns_port_number, () );

_DIM_PROTOE( int get_dns_node_name, ( char *node_name ) );

_DIM_PROTOE( int get_dns_accepted_domains, ( char *domains ) );
_DIM_PROTOE( int get_dns_accepted_nodes, ( char *nodes ) );

_DIM_PROTO( double _swapd_by_addr, (double *d) );
_DIM_PROTO( int _swapl_by_addr, (int *l) );
_DIM_PROTO( short _swaps_by_addr, (short *s) );
_DIM_PROTO( void _swapd_buffer, (double *dout, double *din, int n) );
_DIM_PROTO( void _swapl_buffer, (int *lout, int *lin, int n) );
_DIM_PROTO( void _swaps_buffer, (short *sout, short *sin, int n) );

#ifdef __cplusplus
#undef __CXX_CONST
}
#endif


#define SIZEOF_CHAR 1
#define SIZEOF_SHORT 2
#define SIZEOF_LONG 4
#define SIZEOF_FLOAT 4
#define SIZEOF_DOUBLE 8

#if defined(OSK) && !defined(_UCC)
#	define inc_pter(p,i) (char *)p += (i)
#else
#	define inc_pter(p,i) p = (void *)((char *)p + (i))
#endif

#endif
