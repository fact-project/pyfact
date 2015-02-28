#ifndef __DISDEFS
#define __DISDEFS

#include "dim_common.h"

/* CFORTRAN interface */

#define dis_start_serving dis_start_serving_
#define dis_stop_serving dis_stop_serving_
#define dis_get_next_cmnd dis_get_next_cmnd_
#define dis_get_client dis_get_client_
#define dis_add_service dis_add_service_
#define dis_add_cmnd dis_add_cmnd_
#define dis_add_client_exit_handler dis_add_client_exit_handler_
#define dis_add_exit_handler dis_add_exit_handler_
#define dis_set_client_exit_handler dis_set_client_exit_handler_
#define dis_report_service dis_report_service_
#define dis_update_service dis_update_service_
#define dis_remove_service dis_remove_service_
#define dis_send_service dis_send_service_
#define dis_convert_str dis_convert_str_
#define dis_set_quality dis_set_quality_
#define dis_set_timestamp dis_set_timestamp_
#define dis_selective_update_service dis_selective_update_service_
#define dis_get_timestamp dis_get_timestamp_

#ifdef __cplusplus
extern "C" {
#define __CXX_CONST const
#else
#define __CXX_CONST
#endif

_DIM_PROTOE( int dis_start_serving,    (__CXX_CONST char *task_name) );
_DIM_PROTOE( void dis_stop_serving,    () );
_DIM_PROTOE( int dis_get_next_cmnd,    (dim_long *tag, int *buffer, int *size ) );
_DIM_PROTOE( int dis_get_client,       (char *name ) );
_DIM_PROTOE( int dis_get_conn_id,      () );
_DIM_PROTOE( unsigned dis_add_service, (__CXX_CONST char *service_name, __CXX_CONST char *service_type,
				   void *service_address, int service_size,
				   void (*usr_routine)(void*,void**,int*,int*), dim_long tag) );
_DIM_PROTOE( unsigned dis_add_cmnd,        (__CXX_CONST char *service_name, __CXX_CONST char *service_type,
			           void (*usr_routine)(void*,void*,int*), dim_long tag) );
_DIM_PROTOE( void dis_add_client_exit_handler,(void (*usr_routine)(int*)) );
_DIM_PROTOE( void dis_set_client_exit_handler,(int conn_id, int tag) );
_DIM_PROTOE( void dis_add_exit_handler,(void (*usr_routine)(int*)) );
_DIM_PROTOE( void dis_add_error_handler,(void (*usr_routine)(int, int, char*)) );
_DIM_PROTOE( void dis_report_service,  (__CXX_CONST char *service_name) );
_DIM_PROTOE( int dis_update_service,   (unsigned service_id) );
_DIM_PROTOE( int dis_remove_service,   (unsigned service_id) );
_DIM_PROTOE( void dis_send_service,    (unsigned service_id, int *buffer,
				   int size) );
_DIM_PROTOE( int dis_set_buffer_size,  (int size) );
_DIM_PROTOE( void dis_set_quality,     (unsigned service_id, int quality) );
_DIM_PROTOE( int dis_set_timestamp,     (unsigned service_id, 
					int secs, int millisecs) );
_DIM_PROTOE( int dis_selective_update_service,   (unsigned service_id, 
					int *client_id_list) );
_DIM_PROTOE( void dis_disable_padding,      		() );
_DIM_PROTOE( int dis_get_timeout,      		(unsigned service_id, int client_id) );
_DIM_PROTOE( char *dis_get_error_services,	() );
_DIM_PROTOE( char *dis_get_client_services,	(int conn_id) );
_DIM_PROTOE( int dis_start_serving_dns,		(dim_long dns_id, __CXX_CONST char *task_name/*, int *id_list*/) );
_DIM_PROTOE( void dis_stop_serving_dns,		(dim_long dns_id) );
_DIM_PROTOE( unsigned dis_add_service_dns,	(dim_long dns_id, __CXX_CONST char *service_name, __CXX_CONST char *service_type,
				   void *service_address, int service_size,
				   void (*usr_routine)(void*,void**,int*,int*), dim_long tag) );
_DIM_PROTOE( unsigned dis_add_cmnd_dns,		(dim_long dns_id, __CXX_CONST char *service_name, __CXX_CONST char *service_type,
			       void (*usr_routine)(void*,void*,int*), dim_long tag) );
_DIM_PROTOE( int dis_get_n_clients,	(unsigned service_id) );
_DIM_PROTOE( int dis_get_timestamp,     (unsigned service_id, 
					int *secs, int *millisecs) );
#ifdef __cplusplus
#undef __CXX_CONST
}
#endif

#endif
