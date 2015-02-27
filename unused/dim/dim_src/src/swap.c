/*
 *  (Delphi Network Access) implements the network layer for the DIM
 * (Delphi Information Managment) System.
 *
 * Started date   : 10-11-91
 * Written by     : C. Gaspar
 * UNIX adjustment: G.C. Ballintijn
 *
 */

double _swapd( double d )
{
	double	r[2];
	register char	*p, *q;
	register int 	n;

	p = (char *) &r[1];
	q = (char *) &d;
	for( n = sizeof(double)+1; --n; *--p = *q++) ;
	return r[0];
}

int _swapl( int l )
{
	int	r[2];
	register char	*p, *q;

	p = (char *) &r[1];
	q = (char *) &l;
	*--p = *q++;
	*--p = *q++;
	*--p = *q++;
	*--p = *q++;

	return r[0];
}

short _swaps( short s )
{
	short	r[2];
	register char	*p, *q;

	p = (char *) &r[1];
	q = (char *) &s;
	*--p = *q++;
	*--p = *q++;

	return r[0];
}

double _swapd_by_addr( double *d )
{
	double	r[2];
	register char	*p, *q;
	register int 	n;

	p = (char *) &r[1];
	q = (char *) d;
	for( n = sizeof(double)+1; --n; *--p = *q++) ;

	return r[0];
}

int _swapl_by_addr( int *l )
{
	int	r[2];
	register char	*p, *q;

	p = (char *) &r[1];
	q = (char *) l;
	*--p = *q++;
	*--p = *q++;
	*--p = *q++;
	*--p = *q++;

	return r[0];
}

short _swaps_by_addr( short *s )
{
	short	r[2];
	register char	*p, *q;

	p = (char *) &r[1];
	q = (char *) s;
	*--p = *q++;
	*--p = *q++;

	return r[0];
}

void _swaps_buffer( short *s2, short *s1, int n)
{
	register char *p, *q;
	short r[2];
	register short *s;

	p = (char *) s2;
	q = (char *) s1;
	if( p != q ) {
		p += sizeof(short);
		for( n++; --n; p += 2*sizeof(short)) {
			*--p = *q++;
			*--p = *q++;
		}
	} else {
		for( s = s2, n++; --n; *s++ = r[0]) {
			p = (char *) &r[1] ;
			*--p = *q++;
			*--p = *q++;
		}
	}
}

void _swapl_buffer( int *s2, int *s1, int n)
{
	register char *p, *q;
	int r[2];
	register int *l;

	p = (char *) s2;
	q = (char *) s1;
	if( p != q ) {
		p += sizeof(int);
		for( n++; --n; p += 2*sizeof(int)) {
			*--p = *q++;
			*--p = *q++;
			*--p = *q++;
			*--p = *q++;
		}
	} else {
		for( l = s2, n++; --n; *l++ = r[0]) {
			p = (char *) &r[1] ;
			*--p = *q++;
			*--p = *q++;
			*--p = *q++;
			*--p = *q++;
		}
	}
}


void _swapd_buffer( double *s2, double *s1, int n)
{
	register char *p, *q;
	double r[2];
	register double *d;
	register int m;

	p = (char *) s2;
	q = (char *) s1;
	if( p != q ) {
		p += sizeof(double);
		for( n++; --n; p += 2*sizeof(double)) {
			for( m = sizeof(double)+1; --m; *--p = *q++) ;
		}
	} else {
		for( d = s2, n++; --n; *d++ = r[0]) {
			p = (char *) &r[1] ;
			for( m = sizeof(double)+1; --m; *--p = *q++) ;
		}
	}
}


