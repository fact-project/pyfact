#define DIMLIB
#include <dim.h>
#include <dic.h>
#include <dis.h>

#ifdef VMS
#	include <cvtdef.h>
#endif

#if defined(WIN32) || defined(__unix__)
#define PADD64
#endif

#if defined(aix) || defined (LYNXOS)
#undef PADD64
#endif

#if defined(__linux__) && !defined (__LP64__)
#undef PADD64
#endif

static int Dic_padding = 1;
static int Dis_padding = 1;

void dic_disable_padding()
{
	Dic_padding = 0;
}

void dis_disable_padding()
{
	Dis_padding = 0;
}

static int get_curr_bytes(int items, int bytes_left, int item_size)
{
	int num;

	if(!(num = items))
	{
		num = bytes_left;
	} 
	else 
	{
		num *= item_size;
	}
	return num;
}

#ifdef vms
		
static int check_vms_out(flags, format, curr_par_num, buff_out)
short flags;
int format, curr_par_num;
void *buff_out;
{
	unsigned int input_code;
	int i;
	int num;
	
	if(	(flags & IT_IS_FLOAT) && ((format & 0xF0) == IEEE_FLOAT) )
	{
		switch(flags & 0x3)
		{
			case SWAPL :
				num = curr_par_num;
				(int *)buff_out -= num;
				for( i = 0; i < num; i++) 
				{
					cvt$convert_float((void *)buff_out, CVT$K_VAX_F, 
									(void *)buff_out, CVT$K_IEEE_S,
									0 );
					((int *)buff_out)++;
				}
				break;
			case SWAPD :
#ifdef __alpha
				input_code = CVT$K_VAX_G;
#else
				input_code = CVT$K_VAX_D;
#endif
				num = curr_par_num;
				(double *)buff_out -= num;
				for( i = 0; i < num; i++ )
				{
					cvt$convert_float((void *)buff_out, input_code,
									(void *)buff_out, CVT$K_IEEE_T,
									0 );
					((double *)buff_out)++;
				}
				break;
		}
	}
}



static int check_vms_in(flags, curr_par_num, curr_par_bytes, buff_out)
short flags;
int curr_par_num, curr_par_bytes;
void *buff_out;
{
	unsigned int input_code, output_code;
	int i;
	int num;
	
	if(flags & 0xF0)
	{
		switch(curr_par_bytes) 
		{
			case SIZEOF_FLOAT :
				if((flags & 0xF0) == IEEE_FLOAT)
				{
					num = curr_par_num;
					(int *)buff_out -= num;
					for( i = 0; i<num; i++)
					{
						cvt$convert_float((void *)buff_out, CVT$K_IEEE_S,
										  (void *)buff_out, CVT$K_VAX_F,
										  0 );
						((int *)buff_out)++;
					}
				}
				break;
			case SIZEOF_DOUBLE :
#ifdef __alpha
				output_code = CVT$K_VAX_G;
#else
				output_code = CVT$K_VAX_D;
#endif
				switch(flags & 0xF0)
				{
					case VAX_FLOAT:
						input_code = CVT$K_VAX_D;
						break;	
					case AXP_FLOAT:
						input_code = CVT$K_VAX_G;
						break;	
					case IEEE_FLOAT:
						input_code = CVT$K_IEEE_T;
						break;	
				}							
				num = curr_par_num;
				(double *)buff_out -= num;
				for( i = 0; i<num; i++)
				{
					cvt$convert_float((void *)buff_out, input_code,
									  (void *)buff_out, output_code,
									  0 );
					((double *)buff_out)++;
				}
				break;
		}
	}
}

#endif

static int check_padding(int curr_bytes, int item_size)
{
	int num;

	if( (num = curr_bytes % item_size))
	{
		num = item_size - num;
	}
	return num;
}

int copy_swap_buffer_out(int format, FORMAT_STR *format_data, void *buff_out, void *buff_in, int size)
{
	int num = 0, pad_num = 0, curr_size = 0, curr_out = 0;
	int next_par_bytes, curr_par_num;
	
	if(format){}
	if(!format_data->par_bytes) {
		if(buff_in != buff_out)
			memcpy( buff_out, buff_in, (size_t)size );
		return(size);
	}
	next_par_bytes = format_data->par_bytes;
	while(next_par_bytes)
	{
		curr_par_num = format_data->par_num;
		if((curr_size+(curr_par_num * format_data->par_bytes))
		   > size)
		{
			curr_par_num = (size - curr_size)/format_data->par_bytes;
			next_par_bytes = 0;
		}
		switch(format_data->flags & 0x3) 
		{
			case NOSWAP :

				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_CHAR);

				memcpy( buff_out, buff_in, (size_t)num);
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
			case SWAPS :
				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_SHORT);

				if(Dis_padding)
				{
					if( (pad_num = check_padding(curr_size, SIZEOF_SHORT)) )
					{
						inc_pter( buff_in, pad_num);
						curr_size += pad_num;
					}
				}
				memcpy( buff_out, buff_in, (size_t)num);
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
			case SWAPL :
				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_LONG);

				if(Dis_padding)
				{
					if( (pad_num = check_padding(curr_size, SIZEOF_LONG)) )
					{
						inc_pter( buff_in, pad_num);
						curr_size += pad_num;
					}
				}
				memcpy( buff_out, buff_in, (size_t)num);
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
			case SWAPD :
				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_DOUBLE);

				if(Dis_padding)
				{
#ifdef PADD64
					if( (pad_num = check_padding(curr_size, SIZEOF_DOUBLE)) )
#else
					if( (pad_num = check_padding(curr_size, SIZEOF_LONG)) )
#endif
					{
						inc_pter( buff_in, pad_num);
						curr_size += pad_num;
					}
				}
				memcpy( buff_out, buff_in, (size_t)num);
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
		}
#ifdef vms
		check_vms_out(format_data->flags, format, curr_par_num, buff_out);
#endif
		curr_size += num;
		format_data++;
		if(next_par_bytes)
			next_par_bytes = format_data->par_bytes;
	}
	return(curr_out);
}

int copy_swap_buffer_in(FORMAT_STR *format_data, void *buff_out, void *buff_in, int size)
{
	int num, pad_num, curr_size = 0, curr_out = 0;
	int next_par_bytes, curr_par_num, curr_par_bytes;
	
	num = 0;
	if(!format_data->par_bytes) {
		if(buff_in != buff_out)
			memcpy( buff_out, buff_in, (size_t)size );
		return(size);
	}
	next_par_bytes = format_data->par_bytes;
	while(next_par_bytes)
	{
		curr_par_num = format_data->par_num;
		curr_par_bytes = format_data->par_bytes;
		if((curr_size+(curr_par_num * curr_par_bytes))
		   > size)
		{
			curr_par_num = (size - curr_size)/curr_par_bytes;
			next_par_bytes = 0;
		}
		switch(format_data->flags & 0x3) 
		{
			case NOSWAP :

				num = get_curr_bytes(curr_par_num,
					size - curr_size, curr_par_bytes);

				if(Dic_padding)
				{
					if(curr_par_bytes == SIZEOF_DOUBLE)
					{
#ifdef PADD64
						if( (pad_num = check_padding(curr_out, SIZEOF_DOUBLE)) )
#else
						if( (pad_num = check_padding(curr_out, SIZEOF_LONG)) )
#endif
						{
							inc_pter( buff_out, pad_num);
							curr_out += pad_num;
						}
					}
					else
					{
						if( (pad_num = check_padding(curr_out, curr_par_bytes)) )
						{
							inc_pter( buff_out, pad_num);
							curr_out += pad_num;
						}
					}
				}

				if(buff_in != buff_out)
					memcpy( buff_out, buff_in, (size_t)num);
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
			case SWAPS :

				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_SHORT);

				if(Dic_padding)
				{
					if( (pad_num = check_padding(curr_out, SIZEOF_SHORT)) )
					{
						inc_pter( buff_out, pad_num);
						curr_out += pad_num;
					}
				}
				_swaps_buffer( (short *)buff_out, (short *)buff_in, num/SIZEOF_SHORT) ;
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
			case SWAPL :

				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_LONG);

				if(Dic_padding)
				{
					if( (pad_num = check_padding(curr_out, SIZEOF_LONG)) )
					{
						inc_pter( buff_out, pad_num);
						curr_out += pad_num;
					}
				}
				_swapl_buffer( (short *)buff_out, (short *)buff_in, num/SIZEOF_LONG) ;
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
			case SWAPD :

				num = get_curr_bytes(curr_par_num,
					size - curr_size, SIZEOF_DOUBLE);

				if(Dic_padding)
				{
#ifdef PADD64
					if( (pad_num = check_padding(curr_out, SIZEOF_DOUBLE)) )
#else
					if( (pad_num = check_padding(curr_out, SIZEOF_LONG)) )
#endif
					{
						inc_pter( buff_out, pad_num);
						curr_out += pad_num;
					}
				}
				_swapd_buffer( (short *)buff_out, (short *)buff_in, num/SIZEOF_DOUBLE) ;
				inc_pter( buff_in, num);
				inc_pter( buff_out, num);
				curr_out += num;
				break;
		}
#ifdef vms
		check_vms_in(format_data->flags, curr_par_num, curr_par_bytes, buff_out);
#endif
		curr_size += num;
		format_data++;
		if(next_par_bytes)
			next_par_bytes = format_data->par_bytes;
	}
	return(curr_out);
}













