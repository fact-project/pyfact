/*
 * DNA (Delphi Network Access) implements the network layer for the DIM
 * (Delphi Information Managment) System.
 *
 * Started           : 10-11-91
 * Last modification : 29-07-94
 * Written by        : C. Gaspar
 * Adjusted by       : G.C. Ballintijn
 *
 */

/*
#define DEBUG
*/

#ifdef WIN32
#define FD_SETSIZE      16384
#define poll(pfd,nfds,timeout)	WSAPoll(pfd,nfds,timeout)
#define ioctl ioctlsocket

#define closesock myclosesocket
#define readsock recv
#define writesock send

#define EINTR WSAEINTR
#define EADDRNOTAVAIL WSAEADDRNOTAVAIL
#define EWOULDBLOCK WSAEWOULDBLOCK
#define ECONNREFUSED WSAECONNREFUSED
#define HOST_NOT_FOUND	WSAHOST_NOT_FOUND
#define NO_DATA	WSANO_DATA

#else
/*
#define closesock(s) shutdown(s,2)
*/
#define closesock(s) close(s)
#define readsock(a,b,c,d) read(a,b,c)

#if defined(__linux__) && !defined (darwin)
#define writesock(a,b,c,d) send(a,b,c,MSG_NOSIGNAL)
#else
#define writesock(a,b,c,d) write(a,b,c)
#endif

#ifdef solaris
#define BSD_COMP
/*
#include <thread.h>
*/
#endif

#ifdef LYNXOS
#ifdef RAID
typedef int pid_t;
#endif
#endif

#include <ctype.h>
#include <sys/socket.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <errno.h>
#include <netdb.h>

#endif

#ifdef __linux__
#include <poll.h>
#define MY_FD_ZERO(set)	
#define MY_FD_SET(fd, set)		poll_add(fd)
#define MY_FD_CLR(fd, set)
#define MY_FD_ISSET(fd, set)	poll_test(fd)
#else
#define MY_FD_ZERO(set)			FD_ZERO(set)
#define MY_FD_SET(fd, set)		FD_SET(fd, set)
#define MY_FD_CLR(fd, set)		FD_CLR(fd, set)
#define MY_FD_ISSET(fd, set)	FD_ISSET(fd, set)
#endif

#include <stdio.h>
#include <time.h>
#define DIMLIB
#include <dim.h>

#define ushort unsigned short

static int Threads_on = 0;

static int init_done = FALSE;		/* Is this module initialized? */
static int	queue_id = 0;

#ifdef WIN32
static struct sockaddr_in DIM_sockname;
#endif

static int DIM_IO_path[2] = {-1,-1};
static int DIM_IO_Done = 0;
static int DIM_IO_valid = 1;

static int Listen_backlog = SOMAXCONN;
static int Keepalive_timeout_set = 0;
static int Write_timeout = WRITE_TMOUT;
static int Write_timeout_set = 0;
static int Write_buffer_size = TCP_SND_BUF_SIZE;
static int Read_buffer_size = TCP_RCV_BUF_SIZE;

int Tcpip_max_io_data_write = TCP_SND_BUF_SIZE - 16;
int Tcpip_max_io_data_read = TCP_RCV_BUF_SIZE - 16;

void dim_set_listen_backlog(int size)
{
	Listen_backlog = size;
}

int dim_get_listen_backlog()
{
	return(Listen_backlog);
}

void dim_set_keepalive_timeout(int secs)
{
	Keepalive_timeout_set = secs;
}

int dim_get_keepalive_timeout()
{
	int ret;
	extern int get_keepalive_tmout();

	if(!(ret = Keepalive_timeout_set))
	{
		ret = get_keepalive_tmout();
		Keepalive_timeout_set = ret;
	}
	return(ret);
}

void dim_set_write_timeout(int secs)
{
	Write_timeout = secs;
	Write_timeout_set = 1;
}

int dim_get_write_timeout()
{
	int ret;
	extern int get_write_tmout();

	if(!Write_timeout_set)
	{
		if((ret = get_write_tmout()))
			Write_timeout = ret;
	}
	return(Write_timeout);
}

int dim_set_write_buffer_size(int size)
{
	if(size >= TCP_SND_BUF_SIZE)
	{
		Write_buffer_size = size;
		Tcpip_max_io_data_write = size - 16;
		return(1);
	}
	return(0);
}

int dim_get_write_buffer_size()
{
	return(Write_buffer_size);
}

int dim_set_read_buffer_size(int size)
{
	if(size >= TCP_RCV_BUF_SIZE)
	{
		Read_buffer_size = size;
		Tcpip_max_io_data_read = size - 16;
		return(1);
	}
	return(0);
}

int dim_get_read_buffer_size()
{
	return(Read_buffer_size);
}

#ifdef WIN32
int init_sock()
{
	WORD wVersionRequested;
	WSADATA wsaData;
	int err;
	static int sock_init_done = 0;

	if(sock_init_done) return(1);
 	wVersionRequested = MAKEWORD( 2, 0 );
	err = WSAStartup( wVersionRequested, &wsaData );

	if ( err != 0 ) 
	{
    	return(0);
	}

	/* Confirm that the WinSock DLL supports 2.0.*/
	/* Note that if the DLL supports versions greater    */
	/* than 2.0 in addition to 2.0, it will still return */
	/* 2.0 in wVersion since that is the version we      */
	/* requested.                                        */

	if ( LOBYTE( wsaData.wVersion ) != 2 ||
        HIBYTE( wsaData.wVersion ) != 0 ) 
	{
	    WSACleanup( );
    	return(0); 
	}
	sock_init_done = 1;
	return(1);
}

int myclosesocket(int path)
{
	int code, ret;
	code = WSAGetLastError();
	ret = closesocket(path);
	WSASetLastError(code);
	return ret;
}
#endif

int dim_tcpip_init(int thr_flag)
{
#ifdef WIN32
	int addr, flags = 1;
/*
    void tcpip_task();
*/
	void create_io_thread(void);
#else
	struct sigaction sig_info;
	sigset_t set;
	void io_sig_handler();
	void dummy_io_sig_handler();
	void tcpip_pipe_sig_handler();
#endif
	extern int get_write_tmout();

	if(init_done) 
		return(1);

	dim_get_write_timeout();
#ifdef WIN32
	init_sock();
	Threads_on = 1;
#else
	if(thr_flag)
	{
		Threads_on = 1;
	}
	else
	{
		sigemptyset(&set);

		sigaddset(&set,SIGALRM);
	    sig_info.sa_handler = io_sig_handler;
	    sig_info.sa_mask = set;
#ifndef LYNXOS
	    sig_info.sa_flags = SA_RESTART;
#else
	    sig_info.sa_flags = 0;
#endif
  
		if( sigaction(SIGIO, &sig_info, 0) < 0 ) 
		{
			perror( "sigaction(SIGIO)" );
			exit(1);
		}
	      
	    sigemptyset(&set);
	    sig_info.sa_handler = tcpip_pipe_sig_handler;
	    sig_info.sa_mask = set;
#ifndef LYNXOS 
	    sig_info.sa_flags = SA_RESTART;
#else
	    sig_info.sa_flags = 0;
#endif

	    if( sigaction(SIGPIPE, &sig_info, 0) < 0 ) {
			perror( "sigaction(SIGPIPE)" );
			exit(1);
	    }
	  
	}
#endif
	if(Threads_on)
	{
#ifdef WIN32
		if(DIM_IO_path[0] == -1)
		{
			if( (DIM_IO_path[0] = (int)socket(AF_INET, SOCK_STREAM, 0)) == -1 ) 
			{
				perror("socket");
				return(0);
			}
		
			DIM_sockname.sin_family = PF_INET;
			addr = 0;
			DIM_sockname.sin_addr = *((struct in_addr *) &addr);
			DIM_sockname.sin_port = htons((ushort) 2000); 
			ioctl(DIM_IO_path[0], FIONBIO, &flags);
		}
#else
		if(DIM_IO_path[0] == -1)
		{
			pipe(DIM_IO_path);
		}
#endif
	}
	if(!queue_id)
		queue_id = dtq_create();

#ifdef WIN32
/*
#ifndef STDCALL
	tid = _beginthread((void *)(void *)tcpip_task,0,NULL);
#else
	tid = _beginthreadex(NULL, NULL,
			tcpip_task,0,0,NULL);
#endif
*/
	create_io_thread();
#endif
	init_done = 1;
	return(1);
}

void dim_tcpip_stop()
{
#ifdef WIN32
	closesock(DIM_IO_path[0]);
#else
	close(DIM_IO_path[0]);
	close(DIM_IO_path[1]);
#endif
	DIM_IO_path[0] = -1;
	DIM_IO_path[1] = -1;
	DIM_IO_Done = 0;
	init_done = 0;
}

static int enable_sig(int conn_id)
{
	int ret = 1, flags = 1;
#ifndef WIN32
	int pid;
#endif

#ifdef DEBUG
	if(!Net_conns[conn_id].channel)
	{
	    printf("Enabling signals on channel 0\n");
	    fflush(stdout);
	}
#endif

	if(!init_done)
	{
		dim_tcpip_init(0);
	}
	if(Threads_on)
	{
#ifdef WIN32
		DIM_IO_valid = 0;
/*
		ret = connect(DIM_IO_path[0], (struct sockaddr*)&DIM_sockname, sizeof(DIM_sockname));
*/
		closesock(DIM_IO_path[0]);
		DIM_IO_path[0] = -1;
		if( (DIM_IO_path[0] = (int)socket(AF_INET, SOCK_STREAM, 0)) == -1 ) 
		{
			perror("socket");
			return(1);
		}		
		ret = ioctl(DIM_IO_path[0], FIONBIO, &flags);
		if(ret != 0)
		{
			perror("ioctlsocket");
		}
		DIM_IO_valid = 1;
#else
		if(DIM_IO_path[1] != -1)
		{
			if(!DIM_IO_Done)
			{
				DIM_IO_Done = 1;
				write(DIM_IO_path[1], &flags, 4);
			}
		}
#endif
	}
#ifndef WIN32
	if(!Threads_on)
	{
	    pid = getpid();

#ifndef __linux__
		ret = ioctl(Net_conns[conn_id].channel, SIOCSPGRP, &pid );
#else
	    ret = fcntl(Net_conns[conn_id].channel,F_SETOWN, pid);
#endif
	    if(ret == -1)
	    {
#ifdef DEBUG
	        printf("ioctl returned -1\n");
#endif
			return(ret);
	    }
	}
	ret = ioctl(Net_conns[conn_id].channel, FIOASYNC, &flags );
	if(ret == -1)
	{
#ifdef DEBUG
		printf("ioctl1 returned -1\n");
#endif
		return(ret);
	}
	
    flags = fcntl(Net_conns[conn_id].channel,F_GETFD,0);
#ifdef DEBUG
    if(flags == -1)
    {
		printf("error\n");
    }
#endif
    ret = fcntl(Net_conns[conn_id].channel,F_SETFD, flags | FD_CLOEXEC );
    if(ret == -1)
    {
#ifdef DEBUG
		printf("ioctl2 returned -1\n");
#endif
		return(ret);
    }
#endif
	return(1);
}

#ifdef __linux__
int tcpip_get_send_space(int conn_id)
{
	int ret, n_bytes;
		
	ret = ioctl(Net_conns[conn_id].channel, TIOCOUTQ, &n_bytes );
	if(ret == -1) 
	{
#ifdef DEBUG
		printf("Couln't get send buffer free size, ret =  %d\n", ret);
#endif
		return(0);
	}
/*
	printf("tcpip_get_send_space %d\n", Write_buffer_size - n_bytes);
*/
	return(Write_buffer_size - n_bytes);
}
#endif

/*
static void dump_list()
{
	int	i;

	for( i = 1; i < Curr_N_Conns; i++ )
		if( Dna_conns[i].busy ) {
			printf( "dump_list: conn_id=%d reading=%d\n",
				i, Net_conns[i].reading );
		}
}
*/

#ifdef __linux__
static struct pollfd *Pollfds = 0;
static int Pollfd_size = 0;

static int poll_create()
{
	int i;
	if(Pollfd_size == 0)
	{
		Pollfd_size = Curr_N_Conns;
		Pollfds = malloc(Pollfd_size * sizeof(struct pollfd));
		Pollfds[0].fd = -1;
		for(i = 0; i < Pollfd_size; i++)
		{
			Pollfds[i].events = POLLIN;
		}
	}
	else if(Pollfd_size < Curr_N_Conns)
	{
		free(Pollfds);
		Pollfd_size = Curr_N_Conns;
		Pollfds = malloc(Pollfd_size * sizeof(struct pollfd));
		Pollfds[0].fd = -1;
		for(i = 0; i < Pollfd_size; i++)
		{
			Pollfds[i].events = POLLIN;
		}
	}
	return 1;
}

static int poll_add(int fd)
{
	Pollfds[0].fd = fd;
	return 1;
}

static int poll_test(int fd)
{
	if(Pollfds[0].fd == fd)
	{
		if( (Pollfds[0].revents & POLLIN) || (Pollfds[0].revents & POLLHUP) ) 
		{
		    Pollfds[0].revents = 0;
			return 1;
		}
	}
	return 0;
}
#endif

static int list_to_fds( fd_set *fds )
{
	int	i;
	int found = 0;

	DISABLE_AST
#ifdef __linux__
	if(fds) {}
	poll_create();
#else
	FD_ZERO( fds ) ;
#endif
	for( i = 1; i < Curr_N_Conns; i++ )
    {
#ifdef __linux__
		Pollfds[i].fd = -1;
#endif
		if( Dna_conns[i].busy )
		{
			if(Net_conns[i].channel)
			{
				found = 1;
#ifdef __linux__
				Pollfds[i].fd = Net_conns[i].channel;
#else
				FD_SET( Net_conns[i].channel, fds );
#endif

			}
		}
	}
	ENABLE_AST
	return(found);
}

static int fds_get_entry( fd_set *fds, int *conn_id ) 
{
	int	i;

#ifdef __linux__
	int index = *conn_id;
	if(fds) {}
	index++;
	for( i = index; i < Pollfd_size; i++ )
	{
		if( Dna_conns[i].busy && (
		    (Pollfds[i].revents & POLLIN) || (Pollfds[i].revents & POLLHUP) ) ) 
		{
		    Pollfds[i].revents = 0;
		    if(Net_conns[i].channel)
		    {
				*conn_id = i;
				return 1;
			}
		}
	}
	return 0;
#else
	for( i = 1; i < Curr_N_Conns; i++ )
	{
		if( Dna_conns[i].busy &&
		    FD_ISSET(Net_conns[i].channel, fds) )
		{
			if(Net_conns[i].channel)
		    {
				*conn_id = i;
				return 1;
			}
		}
	}
	return 0;
#endif
}

#if defined(__linux__) && !defined (darwin)

void tcpip_set_keepalive( int channel, int tmout )
{
   int val;

   /* Enable keepalive for the given channel */
   val = 1;
   setsockopt(channel, SOL_SOCKET, SO_KEEPALIVE, (char*)&val, sizeof(val));

   /* Set the keepalive poll interval to something small.
      Warning: this section may not be portable! */
   val = tmout;
   setsockopt(channel, IPPROTO_TCP, TCP_KEEPIDLE, (char*)&val, sizeof(val));
   val = 3;
   setsockopt(channel, IPPROTO_TCP, TCP_KEEPCNT, (char*)&val, sizeof(val));
   val = tmout/3;
   setsockopt(channel, IPPROTO_TCP, TCP_KEEPINTVL, (char*)&val, sizeof(val));
}

#else

static void tcpip_test_write( int conn_id )
{
	/* Write to every socket we use, which uses the TCPIP protocol,
	 * which has an established connection (reading), which is currently
	 * not writing data, so we can check if it is still alive.
	 */
	time_t cur_time;
	
	if(strcmp(Net_conns[conn_id].node,"MYNODE"))
	{
		cur_time = time(NULL);
		if( cur_time - Net_conns[conn_id].last_used > Net_conns[conn_id].timeout )
		{
			dna_test_write( conn_id );
		}
	}
}

#endif

void tcpip_set_test_write(int conn_id, int timeout)
{

#if defined(__linux__) && !defined (darwin)
	tcpip_set_keepalive(Net_conns[conn_id].channel, timeout);
#else

	Net_conns[conn_id].timr_ent = dtq_add_entry( queue_id, timeout, 
		tcpip_test_write, conn_id );
	Net_conns[conn_id].timeout = timeout;
	Net_conns[conn_id].last_used = time(NULL);

#endif

}

void tcpip_rem_test_write(int conn_id)
{
	if(Net_conns[conn_id].timr_ent)
	{
		dtq_rem_entry(queue_id, Net_conns[conn_id].timr_ent);
		Net_conns[conn_id].timr_ent = NULL;
	}
	Net_conns[conn_id].last_used = time(NULL);
}

void tcpip_pipe_sig_handler( int num )
{
	if(num){}
/*
	printf( "*** pipe_sig_handler called ***\n" );
*/
}

static int get_bytes_to_read(int conn_id)
{
	int i, ret, count = 0;
	
	for(i = 0; i < 3; i++)
	{
		ret = ioctl( Net_conns[conn_id].channel, FIONREAD, &count );
	    if( ret != 0)
		{
			count = 0;
			break;
	    }
	    if(count > 0)
	    {
			break;
	    }
	}
	return(count);
}

static int do_read( int conn_id )
{
	/* There is 'data' pending, read it.
	 */
	int	len, totlen, size, count;
	char	*p;

	count = get_bytes_to_read(conn_id);
	if(!count)
	{
/*
		dna_report_error(conn_id, -1,
			"Connection closed by remote peer", DIM_ERROR, DIMTCPRDERR);
		printf("conn_id %d\n", conn_id);
*/
		Net_conns[conn_id].read_rout( conn_id, -1, 0 );
		return 0;
	}

	size = Net_conns[conn_id].size;
	p = Net_conns[conn_id].buffer;
	totlen = 0;
/*
	count = 1;
*/
	while( size > 0 && count > 0 )
	{
/*
		would this be better? not sure afterwards...
		nbytes = (size < count) ? size : count;
		if( (len = readsock(Net_conns[conn_id].channel, p, (size_t)nbytes, 0)) <= 0 ) 
*/
		if( (len = (int)readsock(Net_conns[conn_id].channel, p, (size_t)size, 0)) <= 0 ) 
		{	/* Connection closed by other side. */
			Net_conns[conn_id].read_rout( conn_id, -1, 0 );
			return 0;
		} 
		else 
		{
			
			/*
			printf("tcpip: read %d bytes:\n",len); 
			printf( "buffer[0]=%d\n", vtohl((int *)p[0]));
			printf( "buffer[1]=%d\n", vtohl((int *)p[1]));
			printf( "buffer[2]=%x\n", vtohl((int *)p[2]));
			*/
			totlen += len;
			size -= len;
			p += len;
		}
		if(size)
			count = get_bytes_to_read(conn_id);
	}

	Net_conns[conn_id].last_used = time(NULL);
	Net_conns[conn_id].read_rout( conn_id, 1, totlen );
	return 1;
}


void do_accept( int conn_id )
{
	/* There is a 'connect' pending, serve it.
	 */
	struct sockaddr_in	other;
	int			othersize;

	othersize = sizeof(other);
	memset( (char *) &other, 0, (size_t)othersize );
	Net_conns[conn_id].mbx_channel = (int)accept( Net_conns[conn_id].channel,
						 (struct sockaddr*)&other, (unsigned int *)&othersize );
	if( Net_conns[conn_id].mbx_channel < 0 ) 
	{
		return;
	}
/*
	else
	{
			int all, a, b, c, d;
			char *pall;

			all = other.sin_addr.s_addr;
			pall = &all;
			a = pall[0];
			a &= 0x000000ff;
			b = pall[1];
			b &= 0x000000ff;
			c = pall[2];
			c &= 0x000000ff;
			d = pall[3];
			d &= 0x000000ff;
printf("TCPIP got %d.%d.%d.%d \n",
		a,b,c,d);
		if((a == 134) && (b == 79) && (c == 157) && (d == 40))
		{
			closesock(Net_conns[conn_id].mbx_channel);
			return;
		}
	}
*/

	Net_conns[conn_id].last_used = time(NULL);
	Net_conns[conn_id].read_rout( Net_conns[conn_id].mbx_channel,
				      conn_id, TCPIP );
}

void io_sig_handler(int num)
{
    fd_set	rfds;
    int	conn_id, ret, selret, count;
	struct timeval	timeout;

	if(num){}
	do
	{
		timeout.tv_sec = 0;		/* Don't wait, just poll */
		timeout.tv_usec = 0;
		list_to_fds( &rfds );
#ifdef __linux__
		selret = poll(Pollfds, Pollfd_size, 0);
#else
		selret = select(FD_SETSIZE, &rfds, NULL, NULL, &timeout);
#endif
		if(selret > 0)
		{
			conn_id = 0;
			while( (ret = fds_get_entry( &rfds, &conn_id )) > 0 ) 
			{
				if( Net_conns[conn_id].reading )
				{
					count = 0;
					do
					{
						if(Net_conns[conn_id].channel)
						{
							do_read( conn_id );
							count = get_bytes_to_read(conn_id);
						}
						else
						{
							count = 0;
						}
					}while(count > 0 );
				}
				else
				{
					do_accept( conn_id );
				}
				MY_FD_CLR( (unsigned)Net_conns[conn_id].channel, &rfds );
	    	}
		}
	}while(selret > 0);
}

void tcpip_task( void *dummy)
{
	/* wait for an IO signal, find out what is happening and
	 * call the right routine to handle the situation.
	 */
	fd_set	rfds, *pfds;
#ifndef __linux__
	fd_set efds;
#endif
	int	conn_id, ret, count;
#ifndef WIN32
	int data;
#endif
	if(dummy){}
	while(1)
	{
		while(!DIM_IO_valid)
			dim_usleep(1000);

		list_to_fds( &rfds );
		MY_FD_ZERO(&efds);
#ifdef WIN32
		pfds = &efds;
#else
		pfds = &rfds;
#endif
		MY_FD_SET( DIM_IO_path[0], pfds );
#ifdef __linux__
		ret = poll(Pollfds, Pollfd_size, -1);
#else
		ret = select(FD_SETSIZE, &rfds, NULL, &efds, NULL);
#endif
		if(ret <= 0)
		  {
		    printf("poll returned %d, errno %d\n", ret, errno);
		  }
		if(ret > 0)
		{
			if(MY_FD_ISSET(DIM_IO_path[0], pfds) )
			{
#ifndef WIN32
				read(DIM_IO_path[0], &data, 4);
				DIM_IO_Done = 0;
#endif
				MY_FD_CLR( (unsigned)DIM_IO_path[0], pfds );
			}
/*
			{
			DISABLE_AST
*/
			conn_id = 0;
			while( (ret = fds_get_entry( &rfds, &conn_id )) > 0 ) 
			{
				if( Net_conns[conn_id].reading )
				{
					count = 0;
					do
					{
						DISABLE_AST
						if(Net_conns[conn_id].channel)
						{
							do_read( conn_id );
							count = get_bytes_to_read(conn_id);
						}
						else
						{
							count = 0;
						}
						ENABLE_AST
					}while(count > 0 );
				}
				else
				{
					DISABLE_AST
					do_accept( conn_id );
					ENABLE_AST
				}
				MY_FD_CLR( (unsigned)Net_conns[conn_id].channel, &rfds );
			}
/*
			ENABLE_AST
			}
*/
#ifndef WIN32
			return;
#endif
		}
	}
}

int tcpip_start_read( int conn_id, char *buffer, int size, void (*ast_routine)() )
{
	/* Install signal handler stuff on the socket, and record
	 * some necessary information: we are reading, and want size
	 * as size, and use buffer.
	 */

	Net_conns[conn_id].read_rout = ast_routine;
	Net_conns[conn_id].buffer = buffer;
	Net_conns[conn_id].size = size;
	if(Net_conns[conn_id].reading == -1)
	{
		if(enable_sig( conn_id ) == -1)
		{
#ifdef DEBUG
			printf("START_READ - enable_sig returned -1\n");
#endif
			return(0);
		}
	}
	Net_conns[conn_id].reading = TRUE;
	return(1);
}

int check_node_addr( char *node, unsigned char *ipaddr)
{
unsigned char *ptr;
int ret;

	ptr = (unsigned char *)node+(int)strlen(node)+1;
    ipaddr[0] = *ptr++;
    ipaddr[1] = *ptr++;
    ipaddr[2] = *ptr++;
    ipaddr[3] = *ptr++;
	if( (ipaddr[0] == 0xff) &&
		(ipaddr[1] == 0xff) &&
		(ipaddr[2] == 0xff) &&
		(ipaddr[3] == 0xff) )
	{
		errno = ECONNREFUSED;	/* fake an error code */
#ifdef WIN32
		WSASetLastError(errno);
#endif
		return(0);
	}
	if( gethostbyaddr(ipaddr, sizeof(ipaddr), AF_INET) == (struct hostent *)0 )
	{
#ifndef WIN32
		ret = h_errno;
#else
		ret = WSAGetLastError();
#endif
		if((ret == HOST_NOT_FOUND) || (ret == NO_DATA))
				return(0);
/*		
		errno = ECONNREFUSED;
#ifdef WIN32
		WSASetLastError(errno);
#endif
		return(0);
*/
	}
	return(1);
}

int tcpip_open_client( int conn_id, char *node, char *task, int port )
{
	/* Create connection: create and initialize socket stuff. Try
	 * and make a connection with the server.
	 */
	struct sockaddr_in sockname;
#ifndef VxWorks
	struct hostent *host = 0;
#else
	int host_addr;
#endif
	int path, val, ret_code, ret;
	int a,b,c,d;
/* Fix for gcc 4.6 "dereferencing type-punned pointer will break strict-aliasing rules"?!*/
	unsigned char ipaddr_buff[4];
	unsigned char *ipaddr = ipaddr_buff;
	int host_number = 0;

    dim_tcpip_init(0);
	if(isdigit(node[0]))
	{
		sscanf(node,"%d.%d.%d.%d",&a, &b, &c, &d);
	    ipaddr[0] = (unsigned char)a;
	    ipaddr[1] = (unsigned char)b;
	    ipaddr[2] = (unsigned char)c;
	    ipaddr[3] = (unsigned char)d;
	    host_number = 1;
/*
#ifndef VxWorks
		if( gethostbyaddr(ipaddr, sizeof(ipaddr), AF_INET) == (struct hostent *)0 )
		{
#ifndef WIN32
			ret = h_errno;
#else
			ret = WSAGetLastError();
#endif
//			if((ret == HOST_NOT_FOUND) || (ret == NO_DATA))
//			{
//				if(!check_node_addr(node, ipaddr))
//					return(0);
//			}
		}
#endif
*/
	}
#ifndef VxWorks
	else if( (host = gethostbyname(node)) == (struct hostent *)0 ) 
	{
		if(!check_node_addr(node, ipaddr))
			return(0);
		host_number = 1;
/*
          ptr = (unsigned char *)node+(int)strlen(node)+1;
          ipaddr[0] = *ptr++;
          ipaddr[1] = *ptr++;
          ipaddr[2] = *ptr++;
          ipaddr[3] = *ptr++;
          host_number = 1;
		  if( (ipaddr[0] == 0xff) &&
			  (ipaddr[1] == 0xff) &&
			  (ipaddr[2] == 0xff) &&
			  (ipaddr[3] == 0xff) )
		  {
			  errno = ECONNREFUSED;
#ifdef WIN32
			  WSASetLastError(errno);
#endif
			  return(0);
		  }
		  if( gethostbyaddr(ipaddr, sizeof(ipaddr), AF_INET) == (struct hostent *)0 )
		  {
			  errno = ECONNREFUSED;
#ifdef WIN32
			  WSASetLastError(errno);
#endif
			  return(0);
		  }
*/
	}
#else
	*(strchr(node,'.')) = '\0';
	host_addr = hostGetByName(node);
	printf("node %s addr: %x\n",node, host_addr);
#endif

	if( (path = (int)socket(AF_INET, SOCK_STREAM, 0)) == -1 ) 
	{
		perror("socket");
		return(0);
	}

	val = 1;
      
	if ((ret_code = setsockopt(path, IPPROTO_TCP, TCP_NODELAY, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set TCP_NODELAY\n");
#endif
		closesock(path); 
		return(0);
	}

	val = Write_buffer_size;      
	if ((ret_code = setsockopt(path, SOL_SOCKET, SO_SNDBUF, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_SNDBUF\n");
#endif
		closesock(path); 
		return(0);
	}

	val = Read_buffer_size;
	if ((ret_code = setsockopt(path, SOL_SOCKET, SO_RCVBUF, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_RCVBUF\n");
#endif
		closesock(path); 
		return(0);
	}

#if defined(__linux__) && !defined (darwin)
	val = 2;
	if ((ret_code = setsockopt(path, IPPROTO_TCP, TCP_SYNCNT, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set TCP_SYNCNT\n");
#endif
	}
#endif

	sockname.sin_family = PF_INET;
#ifndef VxWorks
    if(host_number)
		sockname.sin_addr = *((struct in_addr *) ipaddr);
    else
		sockname.sin_addr = *((struct in_addr *) host->h_addr);
#else
    if(host_number)
		sockname.sin_addr = *((struct in_addr *) ipaddr);
    else
		sockname.sin_addr = *((struct in_addr *) &host_addr);
#endif
	sockname.sin_port = htons((ushort) port); /* port number to send to */
	while((ret = connect(path, (struct sockaddr*)&sockname, sizeof(sockname))) == -1 )
	{
		if(errno != EINTR)
		{
			closesock(path);
			return(0);
		}
	}
	strcpy( Net_conns[conn_id].node, node );
	strcpy( Net_conns[conn_id].task, task );
	Net_conns[conn_id].channel = path;
	Net_conns[conn_id].port = port;
	Net_conns[conn_id].last_used = time(NULL);
	Net_conns[conn_id].reading = -1;
	Net_conns[conn_id].timr_ent = NULL;
	Net_conns[conn_id].write_timedout = 0;
	return(1);
}

int tcpip_open_server( int conn_id, char *task, int *port )
{
	/* Create connection: create and initialize socket stuff,
	 * find a free port on this node.
	 */
	struct sockaddr_in sockname;
	int path, val, ret_code, ret;

    dim_tcpip_init(0);
	if( (path = (int)socket(AF_INET, SOCK_STREAM, 0)) == -1 ) 
	{
		return(0);
	}

	val = 1;
	if ((ret_code = setsockopt(path, IPPROTO_TCP, TCP_NODELAY, 
			(char*)&val, sizeof(val))) == -1 ) 

	{
#ifdef DEBUG
		printf("Couln't set TCP_NODELAY\n");
#endif
		closesock(path); 
		return(0);
	}

	val = Write_buffer_size;
	if ((ret_code = setsockopt(path, SOL_SOCKET, SO_SNDBUF, 
			(void *)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_SNDBUF\n");
#endif
		closesock(path); 
		return(0);
	}
/*
	sval1 = sizeof(val1);
	if ((ret_code = getsockopt(path, SOL_SOCKET, SO_SNDBUF, 
			(void *)&val1, &sval1)) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_SNDBUF\n");
#endif
		closesock(path); 
		return(0);
	}
printf("Set size to %d, got size %d\n", val, val1);
*/
	val = Read_buffer_size;
	if ((ret_code = setsockopt(path, SOL_SOCKET, SO_RCVBUF, 
			(void *)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_RCVBUF\n");
#endif
		closesock(path); 
		return(0);
	}

	if( *port == SEEK_PORT ) 
	{	/* Search a free one. */
		*port = START_PORT_RANGE - 1;
		do 
		{
			(*port)++;
			sockname.sin_family = AF_INET;
			sockname.sin_addr.s_addr = INADDR_ANY;
			sockname.sin_port = htons((ushort) *port);
			if( *port > STOP_PORT_RANGE ) {
				errno = EADDRNOTAVAIL;	/* fake an error code */
				closesock(path);
#ifdef WIN32
				WSASetLastError(errno);
#endif
				return(0);
			}
			ret = bind(path, (struct sockaddr*)&sockname, sizeof(sockname));
/*
printf("Trying port %d, ret = %d\n", *port, ret);
*/
		} while( ret == -1 );
/*
		} while( bind(path, (struct sockaddr*)&sockname, sizeof(sockname)) == -1 );
*/
	} else {
#ifndef WIN32
		val = 1;
		if( setsockopt(path, SOL_SOCKET, SO_REUSEADDR, (char*)&val, 
			sizeof(val)) == -1 )
		{
#ifdef DEBUG
			printf("Couln't set SO_REUSEADDR\n");
#endif
			closesock(path); 
			return(0);
		}
#endif
		sockname.sin_family = AF_INET;
		sockname.sin_addr.s_addr = INADDR_ANY;
		sockname.sin_port = htons((ushort) *port);
		if( (ret = bind(path, (struct sockaddr*) &sockname, sizeof(sockname))) == -1 )
		{
			closesock(path);
			return(0);
		}
	}

	if( (ret = listen(path, Listen_backlog)) == -1 )
	{
		closesock(path);
		return(0);
	}

	strcpy( Net_conns[conn_id].node, "MYNODE" );
	strcpy( Net_conns[conn_id].task, task );
	Net_conns[conn_id].channel = path;
	Net_conns[conn_id].port = *port;
	Net_conns[conn_id].last_used = time(NULL);
	Net_conns[conn_id].reading = -1;
	Net_conns[conn_id].timr_ent = NULL;
	Net_conns[conn_id].write_timedout = 0;
	return(1);
}


int tcpip_start_listen( int conn_id, void (*ast_routine)() )
{
	/* Install signal handler stuff on the socket, and record
	 * some necessary information: we are NOT reading, thus
	 * no size.
	 */

	Net_conns[conn_id].read_rout = ast_routine;
	Net_conns[conn_id].size = -1;
	if(Net_conns[conn_id].reading == -1)
	{
		if(enable_sig( conn_id ) == -1)
		{
#ifdef DEBUG
			printf("START_LISTEN - enable_sig returned -1\n");
#endif
			return(0);
		}
	}
	Net_conns[conn_id].reading = FALSE;
	return(1);
}


int tcpip_open_connection( int conn_id, int path )
{
	/* Fill in/clear some fields, the node and task field
	 * get filled in later by a special packet.
	 */
	int val, ret_code;


	val = 1;
	if ((ret_code = setsockopt(path, IPPROTO_TCP, TCP_NODELAY, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set TCP_NODELAY\n");
#endif
		closesock(path); 
		return(0);
	}
	val = Write_buffer_size;      
	if ((ret_code = setsockopt(path, SOL_SOCKET, SO_SNDBUF, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_SNDBUF\n");
#endif
		closesock(path); 
		return(0);
	}

	val = Read_buffer_size;
	if ((ret_code = setsockopt(path, SOL_SOCKET, SO_RCVBUF, 
			(char*)&val, sizeof(val))) == -1 ) 
	{
#ifdef DEBUG
		printf("Couln't set SO_RCVBUF\n");
#endif
		closesock(path); 
		return(0);
	}

	Net_conns[conn_id].channel = path;
	Net_conns[conn_id].node[0] = 0;
	Net_conns[conn_id].task[0] = 0;
	Net_conns[conn_id].port = 0;
	Net_conns[conn_id].reading = -1;
	Net_conns[conn_id].timr_ent = NULL;
	Net_conns[conn_id].write_timedout = 0;
	return(1);
}


void tcpip_get_node_task( int conn_id, char *node, char *task )
{
	strcpy( node, Net_conns[conn_id].node );
	strcpy( task, Net_conns[conn_id].task );
}

int tcpip_write( int conn_id, char *buffer, int size )
{
	/* Do a (synchronous) write to conn_id.
	 */
	int	wrote;

	wrote = (int)writesock( Net_conns[conn_id].channel, buffer, (size_t)size, 0 );
	if( wrote == -1 ) {
/*
		Net_conns[conn_id].read_rout( conn_id, -1, 0 );
*/
		dna_report_error(conn_id, 0,
			"Writing (blocking) to", DIM_ERROR, DIMTCPWRRTY);
		return(0);
	}
	return(wrote);
}

int set_non_blocking(int channel)
{
  int ret, flags = 1;
	ret = ioctl(channel, FIONBIO, &flags );
	if(ret == -1)
	{
#ifdef DEBUG
	    printf("ioctl non block returned -1\n");
#endif
		return(ret);
	}
	return(1);
}

int set_blocking(int channel)
{
  int ret, flags = 0;
	ret = ioctl(channel, FIONBIO, &flags );
	if(ret == -1)
	{
#ifdef DEBUG
	    printf("ioctl block returned -1\n");
#endif
		return(ret);
	}
	return(1);
}

int tcpip_write_nowait( int conn_id, char *buffer, int size )
{
	/* Do a (asynchronous) write to conn_id.
	 */
	int	wrote, ret, selret;
	int tcpip_would_block();
#ifdef __linux__
	struct pollfd pollitem;
#else
	struct timeval	timeout;
	fd_set wfds;
#endif
	
	set_non_blocking(Net_conns[conn_id].channel);
/*
#ifdef __linux__
	tcpip_get_send_space(conn_id);
#endif
*/
	wrote = (int)writesock( Net_conns[conn_id].channel, buffer, (size_t)size, 0 );
#ifndef WIN32
	ret = errno;
#else
	ret = WSAGetLastError();
#endif
/*
	if((wrote == -1) && (!tcpip_would_block(ret)))
	{
	dna_report_error(conn_id, 0,
			"Writing (non-blocking) to", DIM_ERROR, DIMTCPWRRTY);
printf("Writing %d, ret = %d\n", size, ret);
	}
*/
	set_blocking(Net_conns[conn_id].channel);
	if(wrote == -1)
	{
		if(tcpip_would_block(ret))
		{
#ifdef __linux__
		  pollitem.fd = Net_conns[conn_id].channel;
		  pollitem.events = POLLOUT;
		  pollitem.revents = 0;
		  selret = poll(&pollitem, 1, Write_timeout*1000);
#else
			timeout.tv_sec = Write_timeout;
			timeout.tv_usec = 0;
			FD_ZERO(&wfds);
			FD_SET( Net_conns[conn_id].channel, &wfds);
			selret = select(FD_SETSIZE, NULL, &wfds, NULL, &timeout);
#endif
			if(selret > 0)
			{
				wrote = (int)writesock( Net_conns[conn_id].channel, buffer, (size_t)size, 0 );
				if( wrote == -1 ) 
				{
					dna_report_error(conn_id, 0,
						"Writing to", DIM_ERROR, DIMTCPWRRTY);
					return(0);
				}
			}
		}
		else
		{
			dna_report_error(conn_id, 0,
				"Writing (non-blocking) to", DIM_ERROR, DIMTCPWRRTY);
			return(0);
		}
	}
	if(wrote == -1)
	{
		Net_conns[conn_id].write_timedout = 1;
	}
	return(wrote);
}

int tcpip_close( int conn_id )
{
	int channel;
	/* Clear all traces of the connection conn_id.
	 */
	if(Net_conns[conn_id].timr_ent)
	{
		dtq_rem_entry(queue_id, Net_conns[conn_id].timr_ent);
		Net_conns[conn_id].timr_ent = NULL;
	}
	channel = Net_conns[conn_id].channel;
	Net_conns[conn_id].channel = 0;
	Net_conns[conn_id].port = 0;
	Net_conns[conn_id].node[0] = 0;
	Net_conns[conn_id].task[0] = 0;
	if(channel)
	{
		if(Net_conns[conn_id].write_timedout)
		{
			Net_conns[conn_id].write_timedout = 0;
#if defined(__linux__) && !defined (darwin)
			shutdown(channel, 2);
#endif
		}
		closesock(channel);
	}
	return(1);
}


int tcpip_failure( int code )
{
	return(!code);
}

int tcpip_would_block( int code )
{
   if(code == EWOULDBLOCK)
		return(1);
    return(0);
}

void tcpip_report_error( int code )
{
#ifndef WIN32
	if(code){}
	perror("tcpip");
#else
	int my_perror();

	my_perror("tcpip", code);
#endif
}

#ifdef WIN32
int my_perror(char *str, int error)
{
int code;

	if(error <= 0)
		code = WSAGetLastError();
	else
		code = error;
	printf("new - %s\n",strerror(code));
	printf("%s: ",str);
	switch(code)
	{
		case WSAEWOULDBLOCK:
			printf("Operation would block");
			break;
		case WSAEINPROGRESS:
			printf("Operation now in progress");
			break;
		case WSAEALREADY:
			printf("Operation already in progress");
			break;
		case WSAENOTSOCK:
			printf("Socket operation on non-socket");
			break;
		case WSAEDESTADDRREQ:
			printf("Destination address required");
			break;
		case WSAEMSGSIZE:
			printf("Message too long");
			break;
		case WSAEPROTOTYPE:
			printf("Protocol wrong type for socket");
			break;
		case WSAENOPROTOOPT:
			printf("Protocol not available");
			break;
		case WSAEPROTONOSUPPORT:
			printf("Protocol not supported");
			break;
		case WSAESOCKTNOSUPPORT:
			printf("Socket type not supported");
			break;
		case WSAEOPNOTSUPP:
			printf("Operation not supported on transport endpoint");
			break;
		case WSAEPFNOSUPPORT:
			printf("Protocol family not supported");
			break;
		case WSAEAFNOSUPPORT:
			printf("Address family not supported by protocol");
			break;
		case WSAEADDRINUSE:
			printf("Address already in use");
			break;
		case WSAEADDRNOTAVAIL:
			printf("Cannot assign requested address");
			break;
		case WSAENETDOWN:
			printf("Network is down");
			break;
		case WSAENETUNREACH:
			printf("Network is unreachable");
			break;
		case WSAENETRESET:
			printf("Network dropped connection because of reset");
			break;
		case WSAECONNABORTED:
			printf("Software caused connection abort");
			break;
		case WSAECONNRESET:
			printf("Connection reset by peer");
			break;
		case WSAENOBUFS:
			printf("No buffer space available");
			break;
		case WSAEISCONN:
			printf("Transport endpoint is already connected");
			break;
		case WSAENOTCONN:
			printf("Transport endpoint is not connected");
			break;
		case WSAESHUTDOWN:
			printf("Cannot send after transport endpoint shutdown");
			break;
		case WSAETOOMANYREFS:
			printf("Too many references: cannot splice");
			break;
		case WSAETIMEDOUT:
			printf("Connection timed out");
			break;
		case WSAECONNREFUSED:
			printf("Connection refused");
			break;
		case WSAELOOP:
			printf("Too many symbolic links encountered");
			break;
		case WSAENAMETOOLONG:
			printf("File name too long");
			break;
		case WSAEHOSTDOWN:
			printf("Host is down");
			break;
		case WSAEHOSTUNREACH:
			printf("No route to host");
			break;
		case WSAENOTEMPTY:
			printf("Directory not empty");
			break;
		case WSAEUSERS:
			printf("Too many users");
			break;
		case WSAEDQUOT:
			printf("Quota exceeded");
			break;
		case WSAESTALE:
			printf("Stale NFS file handle");
			break;
		case WSAEREMOTE:
			printf("Object is remote");
			break;
		case WSAHOST_NOT_FOUND:
			printf("Host not found");
			break;
		case WSATRY_AGAIN:
			printf("Host not found, or SERVERFAIL");
			break;
		case WSANO_RECOVERY:
			printf("Non recoverable errors, FORMERR, REFUSED, NOTIMP");
			break;
		case WSANO_DATA:
			printf("Valid name, no data record of requested type");
			break;
		default:
			printf("Unknown error %d",code);
	}
	printf("\n");
	return(1);
}

void my_strerror(int error, char *msg)
{
int code;
char str[128];

	if(error <= 0)
		code = WSAGetLastError();
	else
		code = error;
	switch(code)
	{
		case WSAEWOULDBLOCK:
			sprintf(str,"Operation would block");
			break;
		case WSAEINPROGRESS:
			sprintf(str,"Operation now in progress");
			break;
		case WSAEALREADY:
			sprintf(str,"Operation already in progress");
			break;
		case WSAENOTSOCK:
			sprintf(str,"Socket operation on non-socket");
			break;
		case WSAEDESTADDRREQ:
			sprintf(str,"Destination address required");
			break;
		case WSAEMSGSIZE:
			sprintf(str,"Message too long");
			break;
		case WSAEPROTOTYPE:
			sprintf(str,"Protocol wrong type for socket");
			break;
		case WSAENOPROTOOPT:
			sprintf(str,"Protocol not available");
			break;
		case WSAEPROTONOSUPPORT:
			sprintf(str,"Protocol not supported");
			break;
		case WSAESOCKTNOSUPPORT:
			sprintf(str,"Socket type not supported");
			break;
		case WSAEOPNOTSUPP:
			sprintf(str,"Operation not supported on transport endpoint");
			break;
		case WSAEPFNOSUPPORT:
			sprintf(str,"Protocol family not supported");
			break;
		case WSAEAFNOSUPPORT:
			sprintf(str,"Address family not supported by protocol");
			break;
		case WSAEADDRINUSE:
			sprintf(str,"Address already in use");
			break;
		case WSAEADDRNOTAVAIL:
			sprintf(str,"Cannot assign requested address");
			break;
		case WSAENETDOWN:
			sprintf(str,"Network is down");
			break;
		case WSAENETUNREACH:
			sprintf(str,"Network is unreachable");
			break;
		case WSAENETRESET:
			sprintf(str,"Network dropped connection because of reset");
			break;
		case WSAECONNABORTED:
			sprintf(str,"Software caused connection abort");
			break;
		case WSAECONNRESET:
			sprintf(str,"Connection reset by peer");
			break;
		case WSAENOBUFS:
			sprintf(str,"No buffer space available");
			break;
		case WSAEISCONN:
			sprintf(str,"Transport endpoint is already connected");
			break;
		case WSAENOTCONN:
			sprintf(str,"Transport endpoint is not connected");
			break;
		case WSAESHUTDOWN:
			sprintf(str,"Cannot send after transport endpoint shutdown");
			break;
		case WSAETOOMANYREFS:
			sprintf(str,"Too many references: cannot splice");
			break;
		case WSAETIMEDOUT:
			sprintf(str,"Connection timed out");
			break;
		case WSAECONNREFUSED:
			sprintf(str,"Connection refused");
			break;
		case WSAELOOP:
			sprintf(str,"Too many symbolic links encountered");
			break;
		case WSAENAMETOOLONG:
			sprintf(str,"File name too long");
			break;
		case WSAEHOSTDOWN:
			sprintf(str,"Host is down");
			break;
		case WSAEHOSTUNREACH:
			sprintf(str,"No route to host");
			break;
		case WSAENOTEMPTY:
			sprintf(str,"Directory not empty");
			break;
		case WSAEUSERS:
			sprintf(str,"Too many users");
			break;
		case WSAEDQUOT:
			sprintf(str,"Quota exceeded");
			break;
		case WSAESTALE:
			sprintf(str,"Stale NFS file handle");
			break;
		case WSAEREMOTE:
			sprintf(str,"Object is remote");
			break;
		case WSAHOST_NOT_FOUND:
			sprintf(str,"Host not found");
			break;
		case WSATRY_AGAIN:
			sprintf(str,"Host not found, or SERVERFAIL");
			break;
		case WSANO_RECOVERY:
			sprintf(str,"Non recoverable errors, FORMERR, REFUSED, NOTIMP");
			break;
		case WSANO_DATA:
			sprintf(str,"Valid name, no data record of requested type");
			break;
		default:
			sprintf(str,"Unknown error %d",code);
	}
	strcpy(msg, str);
}
#endif

void tcpip_get_error( char *str, int code )
{
	DISABLE_AST
#ifndef WIN32
	if(code){}
	if((errno == 0) && (h_errno == HOST_NOT_FOUND))
		strcpy(str,"Host not found");
	else
		strcpy(str, strerror(errno));
#else
	my_strerror(code, str);
#endif
	ENABLE_AST
}
