#include <jni.h>
/* Header for class dim_Native */

#ifndef _Included_dim_Native
#define _Included_dim_Native
#ifdef __cplusplus
extern "C" {
#endif
#undef dim_Native_ONCE_ONLY
#define dim_Native_ONCE_ONLY 0x1L
#undef dim_Native_TIMED
#define dim_Native_TIMED 0x2L
#undef dim_Native_MONITORED
#define dim_Native_MONITORED 0x4L
#undef dim_Native_MONIT_ONLY
#define dim_Native_MONIT_ONLY 0x20L
#undef dim_Native_UPDATE
#define dim_Native_UPDATE 0x40L
#undef dim_Native_TIMED_ONLY
#define dim_Native_TIMED_ONLY	0x80L
#undef dim_Native_MONIT_FIRST
#define dim_Native_MONIT_FIRST 0x100L
#undef dim_Native_F_STAMPED
#define dim_Native_F_STAMPED /*4096L*/ 0x1000L
#undef dim_Native_F_WAIT
#define dim_Native_F_WAIT /*-2147483648L*/ 0x10000000L


#undef dim_Dbg_MODULE
#define dim_Dbg_MODULE 1L
#undef dim_Dbg_TRANSACTIONS
#define dim_Dbg_TRANSACTIONS 2L
#undef dim_Dbg_SEND_CALLBACK
#define dim_Dbg_SEND_CALLBACK 4L
#undef dim_Dbg_SEND_NATIVE
#define dim_Dbg_SEND_NATIVE 8L
#undef dim_Dbg_INFO_CALLBACK
#define dim_Dbg_INFO_CALLBACK 16L
#undef dim_Dbg_INFO_SERVICE
#define dim_Dbg_INFO_SERVICE 32L
#undef dim_Dbg_SERVER
#define dim_Dbg_SERVER 256L
#undef dim_Dbg_SERVICE_CALLBACK
#define dim_Dbg_SERVICE_CALLBACK 512L
#undef dim_Dbg_ADD_SERVICE
#define dim_Dbg_ADD_SERVICE 1024L
#undef dim_Dbg_RELEASE_SERVICE
#define dim_Dbg_RELEASE_SERVICE 2048L
#undef dim_Dbg_CMND_CALLBACK
#define dim_Dbg_CMND_CALLBACK 4096L
#undef dim_Dbg_ADD_CMND
#define dim_Dbg_ADD_CMND 8192L
#undef dim_Dbg_UPDATE_SERVICE
#define dim_Dbg_UPDATE_SERVICE 16384L
#undef dim_Dbg_GETCLIENT
#define dim_Dbg_GETCLIENT 32768L
#undef dim_Dbg_SERIALIZER
#define dim_Dbg_SERIALIZER 65536L
#undef dim_Dbg_DESCRIPTORS
#define dim_Dbg_DESCRIPTORS 131072L
#undef dim_Dbg_FULL
#define dim_Dbg_FULL -1L

/* Inaccessible static: dim_version */
/* Inaccessible static: dll_locations */

#ifdef __cplusplus
}
#endif
#endif
