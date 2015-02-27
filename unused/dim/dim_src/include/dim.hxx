#ifndef DIM_HH
#define DIM_HH

#include "dim_common.h"
#include "sllist.hxx"
#include "dllist.hxx"

class DimCore
{
public:
	static int inCallback;
};

class DllExp DimErrorHandler{
public:
	virtual void errorHandler(int severity, int code, char *msg) = 0;
	virtual ~DimErrorHandler() {};
};

class DllExp DimTimer
{
public:
	int firedFlag;
	int runningFlag;
	DimTimer();
	DimTimer(int time);
	virtual ~DimTimer();
	int start(int time);
	int stop();
	int fired() { return firedFlag;}; 
	void clear() { firedFlag = 0;};
	virtual void timerHandler() { };
};

class DllExp DimThread
{
public:
	long itsId;
	DimThread();
	virtual ~DimThread();
	int start();
//	int stop();
//	void start(int time);
//	int stop();
//	int fired() { return firedFlag;}; 
//	void clear() { firedFlag = 0;};
	virtual void threadHandler() { };
};

class DllExp DimUtil
{
public:
	static char *getEnvVar(char *varName);
	DimUtil();
	~DimUtil();
	static char *itsBuffer;
	static int itsBufferSize;
};

#endif
