#ifndef __DICDEFS
#define __DICDEFS

#include "dim_common.h"

/* part for CFORTRAN */

#define dic_info_service dic_info_service_
#define dic_info_service_stamped dic_info_service_stamped_
#define dic_cmnd_service dic_cmnd_service_
#define dic_cmnd_callback dic_cmnd_callback_
#define dic_cmnd_service_stamped dic_cmnd_service_stamped_
#define dic_cmnd_callback_stamped dic_cmnd_callback_stamped_
#define dic_change_address dic_change_address_
#define dic_release_service dic_release_service_
#define dic_find_service dic_find_service_
#define dic_get_id dic_get_id_
#define dic_get_quality dic_get_quality_
#define dic_get_timestamp dic_get_timestamp_
#define dic_get_format dic_get_format_

/* Routine definition */
#ifdef __cplusplus
extern "C" {
#define __CXX_CONST const
#else
#define __CXX_CONST
#endif

_DIM_PROTOE( unsigned dic_info_service, (__CXX_CONST char *service_name, int req_type,
				    int req_timeout, void *service_address,
				    int service_size, void (*usr_routine)(void*, void*, int*),
				    dim_long tag, void *fill_addr, int fill_size) );
_DIM_PROTOE( unsigned dic_info_service_stamped, (__CXX_CONST char *service_name, int req_type,
				    int req_timeout, void *service_address,
				    int service_size, void (*usr_routine)(void*, void*, int*),
				    dim_long tag, void *fill_addr, int fill_size) );
_DIM_PROTOE( int dic_cmnd_callback,      (__CXX_CONST char *service_name, void *service_address,
				    int service_size, void (*usr_routine)(void*, int*),
				    dim_long tag) );
_DIM_PROTOE( int dic_cmnd_service,      (__CXX_CONST char *service_name, void *service_address,
				    int service_size) );
_DIM_PROTOE( void dic_change_address,  (unsigned service_id, void *service_address,
				    int service_size) );
_DIM_PROTOE( void dic_release_service,  (unsigned service_id) );
_DIM_PROTOE( int dic_find_service,      (__CXX_CONST char *service_name) );
_DIM_PROTOE( int dic_get_id,      		(__CXX_CONST char *name) );
_DIM_PROTOE( int dic_get_quality,  		(unsigned service_id) );
_DIM_PROTOE( int dic_get_timestamp,  (unsigned service_id, int *secs, int *milisecs) );
_DIM_PROTOE( char *dic_get_format,      		(unsigned service_id) );
_DIM_PROTOE( void dic_disable_padding,      		() );
_DIM_PROTOE( void dic_close_dns,      		() );
_DIM_PROTOE( void dic_add_error_handler,(void (*usr_routine)(int, int, char*)) );
_DIM_PROTOE( char *dic_get_error_services,	() );
_DIM_PROTOE( char *dic_get_server_services,	(int conn_id) );
_DIM_PROTOE( int dic_get_server,       (char *name ) );
_DIM_PROTOE( int dic_get_conn_id,      () );
_DIM_PROTOE( void dic_stop,      () );
_DIM_PROTOE( int dic_get_server_pid,       (int *pid ) );

#ifdef __cplusplus
#undef __CXX_CONST
}
#endif

#endif









