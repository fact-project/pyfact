/*
 * DTQ (Delphi Timer Queue) implements the action scheduling for the DIM
 * (Delphi Information Managment) System.
 * It will be used by servers clients and the Name Server.
 *
 * Started date   : 10-11-91
 * Written by     : C. Gaspar
 * UNIX adjustment: G.C. Ballintijn
 */

/* include files */
#ifndef WIN32
#ifndef NOTHREADS
int DIM_Threads_OFF = 0;
#else
int DIM_Threads_OFF = 1;
#endif
#endif
#include <signal.h>
#include <stdio.h>
#define DIMLIB
#include <dim.h>

#ifdef VxWorks
#include <time.h>
#endif

#include <sys/timeb.h>

/* global definitions */
#define MAX_TIMER_QUEUES	16	/* Number of normal queue's     */
#define SPECIAL_QUEUE		16	/* The queue for the queue-less */
#define WRITE_QUEUE			17 

_DIM_PROTO( static void alrm_sig_handler,  (int num) );
_DIM_PROTO( static void Std_timer_handler, () );
_DIM_PROTO( static int stop_it,			   (int new_time) );
_DIM_PROTO( static int start_it,		   (int new_time) );
_DIM_PROTO( static int scan_it,			   () );
_DIM_PROTO( static int get_minimum,		   (int deltat) );
_DIM_PROTO( int dtq_task, (void *dummy) );
_DIM_PROTO( static int my_alarm, (int secs) );
_DIM_PROTO( int dim_dtq_init,	   (int thr_flag) );
#ifndef WIN32
_DIM_PROTO( static void dummy_alrm_sig_handler, (int num) );
#endif

typedef struct {
	TIMR_ENT *queue_head;
	int remove_entries;
} QUEUE_ENT;


static QUEUE_ENT timer_queues[MAX_TIMER_QUEUES + 2] = { 
	{0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0},
	{0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}, {0, 0}
};

static int Inside_ast = 0;
static int Alarm_runs = 0;
static int sigvec_done = 0;

#ifdef VxWorks
static timer_t Timer_id;
#endif

static time_t DIM_last_time = 0;
static int DIM_last_time_millies = 0;
static int DIM_next_time = 0;
static int DIM_time_left = 0;
static int Threads_off = 0;

/*
 * DTQ routines
 */


#ifndef WIN32

void dim_no_threads()
{
	extern void dic_no_threads();
	extern void dis_no_threads();
	
	DIM_Threads_OFF = 1;
	Threads_off = 1;
	dic_no_threads();
	dis_no_threads();
}

int dim_dtq_init(int thr_flag)
{
struct sigaction sig_info;
sigset_t set;
int ret = 0;

/*
	pid = getpid();
*/
	if( !sigvec_done) 
	{
	    Inside_ast = 0;
	    Alarm_runs = 0;
	    DIM_last_time = 0;
/*
	    for(i = 0; i < MAX_TIMER_QUEUES + 2; i++)
	    {
	        timer_queues[i].queue_head = 0;
			timer_queues[i].remove_entries = 0;
	    }
*/
		if( timer_queues[SPECIAL_QUEUE].queue_head == NULL ) {
			timer_queues[SPECIAL_QUEUE].queue_head = (TIMR_ENT *)malloc(sizeof(TIMR_ENT));
			memset(timer_queues[SPECIAL_QUEUE].queue_head, 0, sizeof(TIMR_ENT));
			dll_init( (DLL *)timer_queues[SPECIAL_QUEUE].queue_head);
		}
		if( timer_queues[WRITE_QUEUE].queue_head == NULL ) {
			timer_queues[WRITE_QUEUE].queue_head = (TIMR_ENT *)malloc(sizeof(TIMR_ENT));
			memset(timer_queues[WRITE_QUEUE].queue_head, 0, sizeof(TIMR_ENT));
			dll_init( (DLL *)timer_queues[WRITE_QUEUE].queue_head);
		}
	    if(!thr_flag)
	    {
	        Threads_off = 1;
	    }
		sigemptyset(&set);
	  
		sigaddset(&set,SIGIO);
		
		if(thr_flag)
			sig_info.sa_handler = dummy_alrm_sig_handler;
		else
			sig_info.sa_handler = alrm_sig_handler;
		sig_info.sa_mask = set;
#ifndef LYNXOS
		sig_info.sa_flags = SA_RESTART;
#else
		sig_info.sa_flags = 0;
#endif
		if( sigaction(SIGALRM, &sig_info, 0) < 0 ) {
			perror( "sigaction(SIGALRM)" );
			exit(1);
		}
	    
	    sigvec_done = 1;
	    ret = 1;
	}
	return(ret);
}

void dummy_alrm_sig_handler( int num )
{
	if(num){}
}

#else

int dim_dtq_init(int thr_flag)
{
	int tid = 1;
	void create_alrm_thread(void);

	if( !sigvec_done ) {
		Inside_ast = 0;
	    Alarm_runs = 0;
	    DIM_last_time = 0;
/*
	    for(i = 0; i < MAX_TIMER_QUEUES + 2; i++)
	    {
	        timer_queues[i].queue_head = 0;
			timer_queues[i].remove_entries = 0;
	    }
*/
		if( timer_queues[SPECIAL_QUEUE].queue_head == NULL ) {
			timer_queues[SPECIAL_QUEUE].queue_head = (TIMR_ENT *)malloc(sizeof(TIMR_ENT));
			memset(timer_queues[SPECIAL_QUEUE].queue_head, 0, sizeof(TIMR_ENT));
			dll_init( (DLL *)timer_queues[SPECIAL_QUEUE].queue_head);
		}
		if( timer_queues[WRITE_QUEUE].queue_head == NULL ) {
			timer_queues[WRITE_QUEUE].queue_head = (TIMR_ENT *)malloc(sizeof(TIMR_ENT));
			memset(timer_queues[WRITE_QUEUE].queue_head, 0, sizeof(TIMR_ENT));
			dll_init( (DLL *)timer_queues[WRITE_QUEUE].queue_head);
		}
/*
#ifndef STDCALL
		tid = _beginthread((void *)(void *)dtq_task,0,NULL);
#else
		tid = _beginthreadex(NULL, NULL,
			dtq_task,0,0,NULL);
#endif
*/
		create_alrm_thread();
		sigvec_done = 1;
	}
	return(tid);
}

#endif

void dim_dtq_stop()
{
/*
	int i;
	for(i = 0; i < MAX_TIMER_QUEUES + 2; i++)
	{
		if( timer_queues[i].queue_head != NULL)
		{
			dtq_delete(i);
			free((TIMR_ENT *)timer_queues[i].queue_head);
			timer_queues[i].queue_head = 0;
		}
	}
*/
	scan_it();
	if( timer_queues[WRITE_QUEUE].queue_head != NULL)
	{
		dtq_delete(WRITE_QUEUE);
		free((TIMR_ENT *)timer_queues[WRITE_QUEUE].queue_head);
		timer_queues[WRITE_QUEUE].queue_head = 0;
	}
	sigvec_done = 0;
}

static int get_current_time(int *millies)
{
	int secs;
#ifdef WIN32
	struct timeb timebuf;
#else
	struct timeval tv;
	struct timezone *tz;
#endif

#ifdef WIN32
	ftime(&timebuf);
	secs = (int)timebuf.time;
	*millies = timebuf.millitm;
#else
	tz = 0;
	gettimeofday(&tv, tz);
	secs = (int)tv.tv_sec;
	*millies = (int)tv.tv_usec / 1000;
#endif
	return secs;
}

static int get_elapsed_time()
{
	int millies, deltat;
	int now;

	now = get_current_time(&millies);
	deltat = now - (int)DIM_last_time;
	if((millies + 50) < DIM_last_time_millies)
	{
		deltat --;
	}
	return deltat;
}

static int my_alarm(int secs)
{
	int ret;

	DIM_next_time = secs;
#ifndef WIN32
	if(Threads_off)
	{
		if( secs < 0)
		{
			kill(getpid(),SIGALRM);
			return(0);
		}
		else
		{
			return((int)alarm((unsigned int)secs));
		}
	}
	else
	{
#endif

		ret = DIM_time_left;

		if(secs == 0)
			DIM_next_time = -1;
		return(ret);
#ifndef WIN32
	}
#endif
}

void dim_usleep(int usecs)
{

#ifndef WIN32
	struct timeval timeout;

	timeout.tv_sec = 0;
	timeout.tv_usec = usecs;
	select(FD_SETSIZE, NULL, NULL, NULL, &timeout);
#else
	usleep(usecs);
#endif
}

int dtq_task(void *dummy)
{
int deltat;
static int to_go;

	if(dummy){}
	while(1)
	{
		if(DIM_next_time)
		{
			DISABLE_AST
			DIM_time_left = DIM_next_time;
			if(DIM_time_left == -1)
				DIM_time_left = 0;
			to_go = DIM_next_time;
			DIM_next_time = 0;
			ENABLE_AST
		}
		if(DIM_time_left < 0)
		{
			DIM_time_left = 0;
			alrm_sig_handler(2);
#ifndef WIN32
			return(1);
#endif
		}
		else if(DIM_time_left > 0)
		{
			dim_usleep(100000);
			deltat = get_elapsed_time();
			DIM_time_left = to_go - deltat;
			if(DIM_time_left <= 0)
			{
				alrm_sig_handler(2);
#ifndef WIN32
				return(1);
#endif
			}
		}
		else
		{
			dim_usleep(1000);
		}
	}
}

int dtq_create()
{
	int i;
	extern void dim_init_threads(void);

	if(!Threads_off)
	{
		dim_init_threads();
	}
	dim_dtq_init(0);
	for( i = 1; i < MAX_TIMER_QUEUES; i++ )
		if( timer_queues[i].queue_head == 0 )
			break;

	if( i == MAX_TIMER_QUEUES )
		return(0);

	timer_queues[i].queue_head = (TIMR_ENT *)malloc( sizeof(TIMR_ENT) );
	memset( timer_queues[i].queue_head, 0, sizeof(TIMR_ENT) );
	dll_init( (DLL *)timer_queues[i].queue_head);

	return(i);
}


int dtq_delete(int queue_id)
{
	TIMR_ENT *queue_head, *entry;

	DISABLE_AST
	queue_head = timer_queues[queue_id].queue_head;
	if(queue_head)
	{
		while(!dll_empty((DLL *)queue_head))
		{
			entry = queue_head->next;
			dll_remove(entry);
			free(entry);
		}
		free(queue_head);
		timer_queues[queue_id].queue_head = 0;
	}
	ENABLE_AST
	return(1);			
}
	
TIMR_ENT *dtq_add_entry(int queue_id, int time, void (*user_routine)(), dim_long tag)
{
	TIMR_ENT *new_entry, *queue_head, *auxp, *prevp;
	int next_time, min_time = 100000;
	int time_left, deltat = 0;

	DISABLE_AST 

	next_time = time;
	if(!next_time)
		next_time = -10;
	if(Alarm_runs)
	{
		time_left = DIM_time_left;
		if(!time_left)
			time_left = DIM_next_time;
		if((time_left > next_time) || (queue_id == SPECIAL_QUEUE))
	    {
			if(next_time != -10)
			{
				min_time = stop_it();
				if((next_time > min_time) && (min_time != 0))
					next_time = min_time;
			}
			else
				my_alarm(next_time);
	    }
		else
		{
		    deltat = get_elapsed_time();
		}
	}
	new_entry = (TIMR_ENT *)malloc( sizeof(TIMR_ENT) );
	new_entry->time = time;
    if( user_routine )
   	   	new_entry->user_routine = user_routine;
	else
       	new_entry->user_routine = Std_timer_handler;
	new_entry->tag = tag;
	new_entry->time_left = time + deltat;

	queue_head = timer_queues[queue_id].queue_head;
	if(!time)
	{
		dll_insert_after((DLL *)queue_head->prev, (DLL *)new_entry);
	}
	else
	{
		if(queue_head)
		{
			auxp = queue_head;
			prevp = auxp;
			while((auxp = (TIMR_ENT *)dll_get_prev((DLL *)queue_head, (DLL *)auxp)))
			{
				if(time >= auxp->time)
				{
					break;
				}
				prevp = auxp;
			}
/*
			if(auxp)
			{
				if(queue_id != SPECIAL_QUEUE)
				{
					if(auxp->time_left > 0)
					{
						if(auxp->time == time)
							new_entry->time_left = auxp->time_left;
					}
				}
				prevp = auxp;
			}
*/
			dll_insert_after((DLL *)prevp, (DLL *)new_entry);
		}
	}
	if(!Alarm_runs)
	{
		if((next_time != -10) && (min_time == 100000))
		{
			min_time = get_minimum(0);
			if(next_time > min_time)
				next_time = min_time;
		}
		start_it(next_time);
	}
	ENABLE_AST
	return(new_entry); 
}

int dtq_clear_entry(TIMR_ENT *entry)
{
	int time_left, deltat = 0;

	DISABLE_AST
	deltat = get_elapsed_time();
	time_left = entry->time_left - deltat;
	entry->time_left = entry->time + deltat;
	ENABLE_AST
	return(time_left);
}


int dtq_rem_entry(int queue_id, TIMR_ENT *entry)
{
	int time_left, deltat = 0;

	DISABLE_AST
	deltat = get_elapsed_time();
	time_left = entry->time_left - deltat;
	if( Inside_ast ) 
	{
		timer_queues[queue_id].remove_entries++;
		entry->time = -1;
		ENABLE_AST
		return(time_left);
	}
	dll_remove(entry);
	free(entry);

	ENABLE_AST
	return(time_left);
}

static int rem_deleted_entries(int queue_id)
{
	TIMR_ENT *auxp, *prevp, *queue_head;
	int n;

	DISABLE_AST
	queue_head = timer_queues[queue_id].queue_head;
	n = timer_queues[queue_id].remove_entries;
	if(queue_head)
	{
		auxp = queue_head;
		prevp = auxp;
		while( (auxp = (TIMR_ENT *)dll_get_next((DLL *)queue_head, (DLL *)auxp)) )
		{
			if(auxp->time == -1)
			{
				dll_remove(auxp);
				free(auxp);
				auxp = prevp;
				n--;
				if(!n)
					break;
			}
			else
				prevp = auxp;
		}
	}
	ENABLE_AST;
	return(1);
}

static int get_minimum(int deltat)
{
	TIMR_ENT *auxp, *queue_head;
	int queue_id;
	int min_time = 100000;

	queue_head = timer_queues[WRITE_QUEUE].queue_head;
	if( dll_get_next((DLL *)queue_head,(DLL *)queue_head))
		min_time = -10;
	if((min_time != -10) || deltat)
	{
		if( (queue_head = timer_queues[SPECIAL_QUEUE].queue_head) != NULL)
		{
			auxp = queue_head;
			while( (auxp = (TIMR_ENT *)dll_get_next((DLL *)queue_head,(DLL *)auxp)) )
			{
				auxp->time_left -= deltat;
				if(auxp->time_left > 0)
				{
					if(auxp->time_left < min_time)
					{
						min_time = auxp->time_left;
					}
				}
			}
		}
		for( queue_id = 0; queue_id < MAX_TIMER_QUEUES; queue_id++ ) 
		{
			if( (queue_head = timer_queues[queue_id].queue_head) == NULL )
				continue;
			auxp = queue_head;
			while( (auxp = (TIMR_ENT *)dll_get_next((DLL *)queue_head,(DLL *)auxp)) )
			{
				auxp->time_left -= deltat;
				if(auxp->time_left > 0)
				{
					if(auxp->time_left < min_time)
					{
						min_time = auxp->time_left;
					}
				}
				else
				{
					if(auxp->time < min_time)
					{
						min_time = auxp->time;
					}
				}
				if((!deltat) && (min_time <= 1))
					break;
			}
		}
	}
	if(min_time == 100000)
		min_time = 0;
	return min_time;
}

static int stop_it()
{
	int min_time;
    int deltat = 0;

	DISABLE_AST
	if(Alarm_runs)
	{
		my_alarm(0);
        deltat = get_elapsed_time();
		if(deltat != 0)
			DIM_last_time = get_current_time(&DIM_last_time_millies);
		Alarm_runs = 0;
	}
	min_time = get_minimum(deltat);
	ENABLE_AST
	return(min_time);
}

static int start_it(int new_time)
{
	int next_time;
	TIMR_ENT *queue_head;

	DISABLE_AST
	next_time = new_time;
	if(next_time > 0)
	{
		queue_head = timer_queues[WRITE_QUEUE].queue_head;
		if( dll_get_next((DLL *)queue_head,(DLL *)queue_head))
		{
			next_time = -10;
		}
	}
	if(next_time)
	{
		my_alarm(next_time);
		Alarm_runs = 1;
		if(!DIM_last_time)
			DIM_last_time = get_current_time(&DIM_last_time_millies);
	}
	else
		DIM_last_time = 0;

	ENABLE_AST
	return(1);
}

static int scan_it()
{
	int queue_id, i, n = 0;
	static int curr_queue_id = 0;
	static TIMR_ENT *curr_entry = 0;
	TIMR_ENT *auxp, *prevp, *queue_head;
	TIMR_ENT *done[1024];

	DISABLE_AST
	queue_head = timer_queues[WRITE_QUEUE].queue_head;
	if(!queue_head)
	{
		ENABLE_AST
		return(0);
	}
	auxp = queue_head;
	while( (auxp = (TIMR_ENT *)dll_get_next((DLL *)queue_head,(DLL *)auxp)) )
	{	
		done[n++] = auxp;
		if(n == 1000)
			break;
	}
	ENABLE_AST
	for(i = 0; i < n; i++)
	{
		auxp = done[i];
		auxp->user_routine( auxp->tag );
	}
	{
		DISABLE_AST
		for(i = 0; i < n; i++)
		{
			auxp = done[i];
			dll_remove(auxp);
			free(auxp);
		}
		if(n == 1000)
		{
			ENABLE_AST
			return(1);
		}
		ENABLE_AST
	}
	{
	DISABLE_AST
	queue_head = timer_queues[SPECIAL_QUEUE].queue_head;
	auxp = queue_head;
	prevp = auxp;
	while( (auxp = (TIMR_ENT *)dll_get_next((DLL *)queue_head,(DLL *)auxp)) )
	{	
		if(auxp->time_left <= 0)
		{
			dll_remove(auxp);
			auxp->user_routine( auxp->tag );
			free(auxp);
			auxp = prevp;
			n++;
			if(n == 100)
			{
				ENABLE_AST
				return(1);
			}
		}
		else
			prevp = auxp;
	}
	for( queue_id = curr_queue_id; queue_id < MAX_TIMER_QUEUES; queue_id++ ) 
	{
		if( (queue_head = timer_queues[queue_id].queue_head) == NULL )
			continue;
		Inside_ast = 1;
		if((curr_entry) && (queue_id == curr_queue_id))
			auxp = curr_entry;
		else
			auxp = queue_head;
		while( (auxp = (TIMR_ENT *)dll_get_next((DLL *)queue_head,(DLL *)auxp)) )
		{	
			if(auxp->time_left <= 0)
			{
				auxp->user_routine( auxp->tag );
				auxp->time_left = auxp->time; /*restart clock*/
				n++;
				if(n == 100)
				{
					curr_queue_id = queue_id;
					curr_entry = auxp;
					ENABLE_AST
					return(1);
				}
			}
		}
		Inside_ast = 0;
		if( timer_queues[queue_id].remove_entries ) {
			rem_deleted_entries( queue_id );
			timer_queues[queue_id].remove_entries = 0;
		}
	}
	curr_queue_id = 0;
	curr_entry = 0;
	ENABLE_AST
	}
	return(0);
}

static void alrm_sig_handler( int num)
{
	int next_time;

	if(num){}
	next_time = stop_it();
	if(Threads_off)
	{
		if(scan_it())
			next_time = -10;
	}
	else
	{
		while(scan_it());
	}
	if(!Alarm_runs)
	{
		start_it(next_time);
	}
}

static void Std_timer_handler()
{
}

void dtq_start_timer(int time, void (*user_routine)(), dim_long tag)
{
	extern void dim_init_threads();

	if(!Threads_off)
	{
		dim_init_threads();
	}
	dim_dtq_init(0);
	if(time != 0)
		dtq_add_entry(SPECIAL_QUEUE, time, user_routine, tag);
	else
		dtq_add_entry(WRITE_QUEUE, time, user_routine, tag);
}


int dtq_stop_timer(dim_long tag)
{
	TIMR_ENT *entry, *queue_head;
	int time_left = -1;

	queue_head = timer_queues[SPECIAL_QUEUE].queue_head;
	entry = queue_head;
	while( (entry = (TIMR_ENT *)dll_get_next((DLL *)queue_head,(DLL *)entry)) )
	{
		if( entry->tag == tag ) 
		{
			time_left = dtq_rem_entry( SPECIAL_QUEUE, entry );
			break;
		}
	}
	return(time_left);
}

static int Dtq_sleeping = 0;

void dtq_sleep_rout(dim_long tag)
{
	if(tag){}
	Dtq_sleeping = 0;
#ifdef WIN32
	wake_up();
#endif
}

#ifndef WIN32

unsigned int dtq_sleep(int secs)
{

#ifndef NOTHREADS
	int i;
	for(i = 0; i < secs*2; i++)
    {
		dim_usleep(500000);
    }
	return(0);
#else
	sigset_t set, oset;

	sigemptyset(&set);
	sigaddset(&set,SIGALRM);
	sigprocmask(SIG_UNBLOCK, &set, &oset);
	Dtq_sleeping = 1;
	dtq_start_timer(secs, dtq_sleep_rout, (dim_long)123);
    do{
		pause();
	}while(Dtq_sleeping);
    sigprocmask(SIG_SETMASK,&oset,0);
	return(0);
#endif
}

#else

unsigned int dtq_sleep(int secs)
{
	Dtq_sleeping = 1;
	dtq_start_timer(secs, dtq_sleep_rout, 1);
	do{
		dim_wait();
	}while(Dtq_sleeping);
	return(0);
}

#endif
