/*
 * DNA (Delphi Network Access) implements the network layer for the DIM
 * (Delphi Information Managment) System.
 *
 * Started date   : 10-11-91
 * Written by     : C. Gaspar
 * UNIX adjustment: G.C. Ballintijn
 *
 */

#include <sys/types.h>
#ifndef WIN32
#include <netinet/in.h>
#include <netdb.h>
#endif
#include <string.h>
#include <time.h>
#include <sys/timeb.h>
#define DIMLIB
#include <dim.h>

int get_proc_name(char *proc_name)
{
#ifndef VxWorks
	sprintf( proc_name, "%d", getpid() );
#else
	sprintf( proc_name, "%d", taskIdSelf() );      
#endif
	return(1);
}


int get_node_name(char *node_name)
{
#ifndef VxWorks
struct hostent *host;
#endif
char *p;
int	i;
#ifdef WIN32
extern void init_sock();
#endif

	DISABLE_AST
#ifdef WIN32
	init_sock();
#endif
	if( (p = getenv("DIM_HOST_NODE")) != NULL )
	{
		strcpy( node_name, p );
		ENABLE_AST
		return(1);
	}
	if((gethostname(node_name, MAX_NODE_NAME)) == -1)
	{
		ENABLE_AST
		return(0);
	}
#ifndef VxWorks
#ifndef RAID
	if(!strchr(node_name,'.'))
	{
		if ((host = gethostbyname(node_name)) != (struct hostent *)0) 
		{		
			strcpy(node_name,host->h_name);
			if(!strchr(node_name,'.'))
			{
				if(host->h_aliases)
				{
					if(host->h_aliases[0])
					{
						for(i = 0; host->h_aliases[i]; i++)
						{
							p = host->h_aliases[i];
							if(strchr(p,'.'))
							{
								strcpy(node_name,p);
								break;
							}
						}
					}
				}
		    }
		}
	}
#endif
#endif
	ENABLE_AST
	return(1);
}

/* 
Bug or Feature? 
get_node_addr returns the "default" interface address, not the one chosen by 
DIM_HOST_NODE. This makes the DNS or a DIM server respond to both interfaces 
*/

int get_node_addr(char *node_addr)
{
#ifndef VxWorks
struct hostent *host;
#endif
char node_name[MAX_NODE_NAME];
char *ptr;

#ifdef WIN32
	init_sock();
#endif
	gethostname(node_name, MAX_NODE_NAME);
#ifndef VxWorks
	if ((host = (struct hostent *)gethostbyname(node_name)) == (struct hostent *)0)
	{
		node_addr[0] = 0;
		node_addr[1] = 0;
		node_addr[2] = 0;
		node_addr[3] = 0;
		return(0);
	}
    ptr = (char *)host->h_addr;
    node_addr[0] = *ptr++;
    node_addr[1] = *ptr++;
    node_addr[2] = *ptr++;
    node_addr[3] = *ptr++;
    return(1);
#else
    node_addr[0] = 0;
    node_addr[1] = 0;
    node_addr[2] = 0;
    node_addr[3] = 0;
	return(0);
#endif
}

void dim_print_date_time()
{
	time_t t;
	char str[128];

	t = time((time_t *)0);
/*
#ifdef WIN32
	strcpy(str, ctime(&t));
#else
#ifdef LYNXOS
	ctime_r(&t, str, 128);
#else
	ctime_r(&t, str);
#endif
#endif
*/
	my_ctime(&t, str, 128);
	str[(int)strlen(str)-1] = '\0';
	printf("PID %d - ",getpid());
	printf("%s - ",str );
}

void dim_print_date_time_millis()
{
	int millies;

#ifdef WIN32
	struct timeb timebuf;
#else
	struct timeval tv;
	struct timezone *tz;
#endif

#ifdef WIN32
	ftime(&timebuf);
	millies = timebuf.millitm;
#else
	tz = 0;
	gettimeofday(&tv, tz);
	millies = (int)tv.tv_usec / 1000;
#endif
	dim_print_date_time();
	printf("milliseconds: %d ", millies);
}

void dim_print_msg(char *msg, int severity)
{
	dim_print_date_time();
	switch(severity)
	{
		case 0: printf("(INFO) ");
			break;
		case 1: printf("(WARNING) ");
			break;
		case 2: printf("(ERROR) ");
			break;
		case 3: printf("(FATAL) ");
			break;
	}
	printf("%s\n",msg);
	fflush(stdout);
}

void dim_panic( char *s )
{
	printf( "\n\nDNA library panic: %s\n\n", s );
	exit(0);
}

int get_dns_node_name( char *node_name )
{
	char	*p;

	if( (p = getenv("DIM_DNS_NODE")) == NULL )
		return(0);
	else {
		strcpy( node_name, p );
		return(1);
	}
}

int get_dns_port_number()
{
	char	*p;

	if( (p = getenv("DIM_DNS_PORT")) == NULL )
		return(DNS_PORT);
	else {
		return(atoi(p));
	}
}

int dim_get_env_var( char *env_var, char *value, int len )
{
	char	*p;
	int tot, sz;

	if( (p = getenv(env_var)) == NULL )
		return(0);
	else {
		tot = (int)strlen(p)+1;
		if(value != 0)
		{
			sz = tot;
			if(sz > len)
				sz = len;
			strncpy(value, p, (size_t)sz);
			if((sz == len) && (len > 0))
				value[sz-1] = '\0';
		}
		return(tot);
	}
}

int get_dns_accepted_domains( char *domains )
{
	char	*p;
	int append = 0;

	if(get_dns_accepted_nodes(domains))
		append = 1;
	if( (p = getenv("DIM_DNS_ACCEPTED_DOMAINS")) == NULL )
	{
		if(!append)
			return(0);
		else
			return(1);
	}
	else {
		if(!append)
			strcpy( domains, p );
		else
		{
			strcat( domains, ",");
			strcat( domains, p);
		}
		return(1);
	}
}

int get_dns_accepted_nodes( char *nodes )
{
	char	*p;

	if( (p = getenv("DIM_DNS_ACCEPTED_NODES")) == NULL )
		return(0);
	else {
		strcpy( nodes, p );
		return(1);
	}
}

int get_keepalive_tmout()
{
	char	*p;

	if( (p = getenv("DIM_KEEPALIVE_TMOUT")) == NULL )
		return(TEST_TIME_OSK);
	else {
		return(atoi(p));
	}
}

int get_write_tmout()
{
	char	*p;

	if( (p = getenv("DIM_WRITE_TMOUT")) == NULL )
		return(0);
	else {
		return(atoi(p));
	}
}
