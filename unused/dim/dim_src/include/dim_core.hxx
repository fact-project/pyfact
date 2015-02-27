#ifndef DIM_CORE
#define DIM_CORE

   #if defined __cplusplus
         /* If the functions in this header have C linkage, this
           * will specify linkage for all C++ language compilers.
           */
         extern "C" {
   #endif

   # if defined __DECC || defined __DECCXX
         /* If you are using pragmas that are only defined
           * with DEC C and DEC C++, this line is necessary
           * for both C and C++ compilers.   A common error
           * is to only have #ifdef __DECC, which causes
           * the compiler to skip the conditionalized
           * code.
           */
   #    pragma __extern_model __save
   #    pragma __extern_model __strict_refdef
         extern const char some_definition [];
   #    pragma __extern_model __restore
   # endif

    /* ...some data and function definitions go here... */

#include "dis.h"
#include "dic.h"

   #if defined __cplusplus
         }    /* matches the linkage specification at the beginning. */
   #endif

#endif
