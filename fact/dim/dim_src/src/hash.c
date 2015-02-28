#define DIMLIB
#include <dim.h>

/*
 * Hash function
 */

/*
int HashFunction(name, max)
char	*name;
int	max;
{
    register int code = 0;

	while(*name)
	{
		code += *name++;
	}
	return (code % max);
}
*/
int HashFunction(char *name, int max)
{
   unsigned int b    = 378551;
   unsigned int a    = 63689;
   unsigned int hash = 0;
   int i    = 0;
   int len;

   len = (int)strlen(name);

   for(i = 0; i < len; name++, i++)
   {
      hash = hash*a+(unsigned)(*name);
      a = a*b;
   }

   return ((int)(hash % (unsigned)max));
}
