/*
 * DNA (Delphi Network Access) implements the network layer for the DIM
 * (Delphi Information Managment) System.
 *
 * Started date   : 10-11-91
 * Written by     : C. Gaspar
 * UNIX adjustment: G.C. Ballintijn
 *
 */

/* This module can only handle one type of array, and DIC or DNS.
 * It cannot handle both simultaniously. It handles at same time
 * the NET and DNA array's. Although these have to be explicitly
 * created.
 */

#define DIMLIB
#include <dim.h>

static SRC_TYPES My_type;		/* Var. indicating type DIC or DIS */

#ifdef VMS
DIM_NOSHARE DNS_CONNECTION *Dns_conns;
DIM_NOSHARE DIC_CONNECTION *Dic_conns;
DIM_NOSHARE DNA_CONNECTION *Dna_conns;
DIM_NOSHARE NET_CONNECTION *Net_conns;
DIM_NOSHARE int Curr_N_Conns;
#else
DllExp DIM_NOSHARE DNS_CONNECTION *Dns_conns = 0;
DIM_NOSHARE DIC_CONNECTION *Dic_conns = 0;
DllExp DIM_NOSHARE DNA_CONNECTION *Dna_conns = 0;
DllExp DIM_NOSHARE NET_CONNECTION *Net_conns = 0;
DllExp DIM_NOSHARE int Curr_N_Conns = 0;
#endif

typedef struct id_item
{
	void *ptr;
	SRC_TYPES type;
}ID_ITEM;

static ID_ITEM *Id_arr;
/*
static void **Id_arr;
*/
static int Curr_N_Ids = 0;
static int Curr_id = 1;

void conn_arr_create(SRC_TYPES type)
{

	if( Curr_N_Conns == 0 )
		Curr_N_Conns = CONN_BLOCK;

	switch(type)
	{
	case SRC_DIC :
		Dic_conns = (DIC_CONNECTION *)
				calloc( (size_t)Curr_N_Conns, sizeof(DIC_CONNECTION) );
		My_type = type;
		break;
	case SRC_DNS :
		Dns_conns = (DNS_CONNECTION *)
				calloc( (size_t)Curr_N_Conns, sizeof(DNS_CONNECTION) );
		My_type = type;
		break;
	case SRC_DNA :
		Dna_conns = (DNA_CONNECTION *)
				calloc( (size_t)Curr_N_Conns, sizeof(DNA_CONNECTION) );
		Net_conns = (NET_CONNECTION *)
				calloc( (size_t)Curr_N_Conns, sizeof(NET_CONNECTION) );
		break;
	default:
		break;
	}
}


int conn_get()
{
	register DNA_CONNECTION *dna_connp;
	int i, n_conns, conn_id;

	DISABLE_AST
	for( i = 1, dna_connp = &Dna_conns[1]; i < Curr_N_Conns; i++, dna_connp++ )
	{
		if( !dna_connp->busy )
		{
			dna_connp->busy = TRUE;
			ENABLE_AST
			return(i);
		}
	}
	n_conns = Curr_N_Conns + CONN_BLOCK;
	Dna_conns = arr_increase( Dna_conns, sizeof(DNA_CONNECTION), n_conns );
	Net_conns = arr_increase( Net_conns, sizeof(NET_CONNECTION), n_conns );
	switch(My_type)
	{
	case SRC_DIC :
		Dic_conns = arr_increase( Dic_conns, sizeof(DIC_CONNECTION),
					  n_conns );
		break;
	case SRC_DNS :
		Dns_conns = arr_increase( Dns_conns, sizeof(DNS_CONNECTION),
					  n_conns );
		break;
	default:
		break;
	}
	conn_id = Curr_N_Conns;
	Curr_N_Conns = n_conns;
	Dna_conns[conn_id].busy = TRUE;
	ENABLE_AST
	return(conn_id);
}


void conn_free(int conn_id)
{
	DISABLE_AST
	Dna_conns[conn_id].busy = FALSE;
	ENABLE_AST
}


void *arr_increase(void *conn_ptr, int conn_size, int n_conns)
{
	register char *new_ptr;

	new_ptr = realloc( conn_ptr, (size_t)(conn_size * n_conns) );
	memset( new_ptr + conn_size * Curr_N_Conns, 0, (size_t)(conn_size * CONN_BLOCK) );
	return(new_ptr);
}

void id_arr_create()
{

	Curr_N_Ids = ID_BLOCK;
	Id_arr = (void *) calloc( (size_t)Curr_N_Ids, sizeof(ID_ITEM));
}


void *id_arr_increase(void *id_ptr, int id_size, int n_ids)
{
	register char *new_ptr;

	new_ptr = realloc( id_ptr, (size_t)(id_size * n_ids) );
	memset( new_ptr + id_size * Curr_N_Ids, 0, (size_t)(id_size * ID_BLOCK) );
	return(new_ptr);
}

int id_get(void *ptr, SRC_TYPES type)
{
	register int i, id;
	register ID_ITEM *idp;

	DISABLE_AST
	if(!Curr_N_Ids)
	{
		id_arr_create();
	}
	for( i = Curr_id, idp = &Id_arr[Curr_id]; i < Curr_N_Ids; i++, idp++ )
	{
		if( !idp->type )
		{
			idp->ptr = ptr;
			idp->type = type;
			Curr_id = i;
			ENABLE_AST
			return(i);
		}
	}
	Id_arr = id_arr_increase( Id_arr, sizeof(ID_ITEM), Curr_N_Ids + ID_BLOCK );
	id = Curr_N_Ids;
	idp = &Id_arr[id];
	idp->ptr = ptr;
	idp->type = type;
	Curr_N_Ids += ID_BLOCK;
	Curr_id = id;
	ENABLE_AST
	return(id);
}

void *id_get_ptr(int id, SRC_TYPES type)
{
	ID_ITEM *idp;
	void *ptr;
	DISABLE_AST

	if((id >= Curr_N_Ids) || (id <= 0))
	{
		ENABLE_AST
		return(0);
	}
	idp = &Id_arr[id];
	if(idp->type == type)
	{
		ptr = idp->ptr;
		ENABLE_AST
		return(ptr);
	}
	ENABLE_AST
	return(0);
}

void id_free(int id, SRC_TYPES type)
{
	ID_ITEM *idp;
	DISABLE_AST

	idp = &Id_arr[id];
	if(idp->type == type)
	{
		idp->type = 0;
		idp->ptr = 0;
	}
	Curr_id = 1;
	ENABLE_AST
}
