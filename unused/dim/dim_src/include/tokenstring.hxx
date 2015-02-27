#ifndef __TOKENSTRINGDEFS
#define __TOKENSTRINGDEFS
#include <string.h>
#include "dim_core.hxx"

class DllExp TokenString
{
public:

	TokenString(char *str);
	TokenString(char *str, char *seps);
	~TokenString();
	int getToken(char *&token);
	void pushToken();
	void popToken();
	int cmpToken(char *str);
	int firstToken();
	int getNTokens();
	int getNTokens(char *str);

private:
	void store_str(char *str);
	char *token_buff;
	char *token_ptr;
	char *curr_token_ptr;
	char *push_token_ptr;
	char *token_seps;
	int n_tokens;
};

#endif
