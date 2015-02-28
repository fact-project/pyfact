#ifndef __DICHHDEFS
#define __DICHHDEFS
#include <assert.h>
#include <stdlib.h>
#include <string.h>
#ifndef WIN32
#include <unistd.h>
#endif
#ifdef __VMS
#include <starlet.h>
#endif
#include "dim_core.hxx"
#include "dim.hxx"
#include "tokenstring.hxx"

enum DimServiceType {DimSERVICE=1, DimCOMMAND, DimRPC};

class DimClient;
class DimInfo;
class DimCurrentInfo;
class DimRpcInfo;

class DllExp DimInfoHandler{
public:
	DimInfo *itsService;
    DimInfo *getInfo() { return itsService; }; 
	virtual void infoHandler() = 0;
	virtual ~DimInfoHandler() {};
};

class DllExp DimInfo : public DimInfoHandler, public DimTimer{

public :
	DimInfoHandler *itsHandler;

	DimInfo()
		{ subscribe((char *)0, 0, (void *)0, 0, 0); };
	DimInfo(const char *name, int nolink) 
		{ subscribe((char *)name, 0, &nolink, sizeof(int), 0); };
	DimInfo(const char *name, int time, int nolink) 
		{ subscribe((char *)name, time, &nolink, sizeof(int), 0); };
	DimInfo(const char *name, float nolink) 
		{ subscribe((char *)name, 0, &nolink, sizeof(float), 0); };
	DimInfo(const char *name, int time, float nolink) 
		{ subscribe((char *)name, time, &nolink, sizeof(float), 0); };
	DimInfo(const char *name, double nolink) 
		{ subscribe((char *)name, 0, &nolink, sizeof(double), 0); };
	DimInfo(const char *name, int time, double nolink) 
		{ subscribe((char *)name, time, &nolink, sizeof(double), 0); };
	DimInfo(const char *name, longlong nolink) 
		{ subscribe((char *)name, 0, &nolink, sizeof(longlong), 0); };
	DimInfo(const char *name, int time, longlong nolink) 
		{ subscribe((char *)name, time, &nolink, sizeof(longlong), 0); };
	DimInfo(const char *name, short nolink) 
		{ subscribe((char *)name, 0, &nolink, sizeof(short), 0); };
	DimInfo(const char *name, int time, short nolink) 
		{ subscribe((char *)name, time, &nolink, sizeof(short), 0); };
	DimInfo(const char *name, char *nolink) 
		{ subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1, 0); };
	DimInfo(const char *name, int time, char *nolink) 
		{ subscribe((char *)name, time, nolink, (int)strlen(nolink)+1, 0); };
	DimInfo(const char *name, void *nolink, int nolinksize) 
		{ subscribe((char *)name, 0, nolink, nolinksize, 0); };
	DimInfo(const char *name, int time, void *nolink, int nolinksize) 
		{ subscribe((char *)name, time, nolink, nolinksize, 0); };

	DimInfo(const char *name, int nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, &nolink, sizeof(int), handler); };
	DimInfo(const char *name, int time, int nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, &nolink, sizeof(int), handler); };
	DimInfo(const char *name, float nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, &nolink, sizeof(float), handler); };
	DimInfo(const char *name, int time, float nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, &nolink, sizeof(float), handler); };
	DimInfo(const char *name, double nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, &nolink, sizeof(double), handler); };
	DimInfo(const char *name, int time, double nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, &nolink, sizeof(double), handler); };
	DimInfo(const char *name, longlong nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, &nolink, sizeof(longlong), handler); };
	DimInfo(const char *name, int time, longlong nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, &nolink, sizeof(longlong), handler); };
	DimInfo(const char *name, short nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, &nolink, sizeof(short), handler); };
	DimInfo(const char *name, int time, short nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, &nolink, sizeof(short), handler); };
	DimInfo(const char *name, char *nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1, handler); };
	DimInfo(const char *name, int time, char *nolink, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, nolink, (int)strlen(nolink)+1, handler); };
	DimInfo(const char *name, void *nolink, int nolinksize, DimInfoHandler *handler) 
		{ subscribe((char *)name, 0, nolink, nolinksize, handler); };
	DimInfo(const char *name, int time, void *nolink, int nolinksize, DimInfoHandler *handler) 
		{ subscribe((char *)name, time, nolink, nolinksize, handler); };

	virtual ~DimInfo();
	void *itsData;
	int itsDataSize;
	int itsSize;
	int getSize() {return itsSize; };
	char *getName()  { return itsName; } ;
	void *getData();
	int getInt() { return *(int *)getData(); } ;
	float getFloat() { return *(float *)getData(); } ;
	double getDouble() { return *(double *)getData(); } ;
	longlong getLonglong() { return *(longlong *)getData(); } ;
	short getShort() { return *(short *)getData(); } ;
	char *getString()  { return (char *)getData(); } ;

	virtual void infoHandler();
	void timerHandler();
	virtual void subscribe(char *name, int time, void *nolink, int nolinksize,
		DimInfoHandler *handler);
	virtual void doIt();
	int getQuality();
	int getTimestamp();
	int getTimestampMillisecs();
	char *getFormat();
	void subscribe(char *name, void *nolink, int nolinksize, int time, 
		DimInfoHandler *handler) 
		{ subscribe((char *)name, time, nolink, nolinksize, handler); };

protected :
	char *itsName;
	int itsId;
	int itsTime;
	int itsType;
//	int itsTagId;
	char *itsFormat;
	void *itsNolinkBuf;
	int itsNolinkSize;
	int secs, millisecs;
};

class DllExp DimStampedInfo : public DimInfo{

public :
	DimStampedInfo(){};
	DimStampedInfo(const char *name, int nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(int), 0); };
	DimStampedInfo(const char *name, int time, int nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(int), 0); };
	DimStampedInfo(const char *name, float nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(float), 0); };
	DimStampedInfo(const char *name, int time, float nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(float), 0); };
	DimStampedInfo(const char *name, double nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(double), 0); };
	DimStampedInfo(const char *name, int time, double nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(double), 0); };
	DimStampedInfo(const char *name, longlong nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(longlong), 0); };
	DimStampedInfo(const char *name, int time, longlong nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(longlong), 0); };
	DimStampedInfo(const char *name, short nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(short), 0); };
	DimStampedInfo(const char *name, int time, short nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(short), 0); };
	DimStampedInfo(const char *name, char *nolink) 
	{ subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1, 0); };
	DimStampedInfo(const char *name, int time, char *nolink) 
	{ subscribe((char *)name, time, nolink, (int)strlen(nolink)+1, 0); };
	DimStampedInfo(const char *name, void *nolink, int nolinksize) 
	{ subscribe((char *)name, 0, nolink, nolinksize, 0); };
	DimStampedInfo(const char *name, int time, void *nolink, int nolinksize) 
	{ subscribe((char *)name, time, nolink, nolinksize, 0); };

	DimStampedInfo(const char *name, int nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(int), handler); };
	DimStampedInfo(const char *name, int time, int nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(int), handler); };
	DimStampedInfo(const char *name, float nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(float), handler); };
	DimStampedInfo(const char *name, int time, float nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(float), handler); };
	DimStampedInfo(const char *name, double nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(double), handler); };
	DimStampedInfo(const char *name, int time, double nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(double), handler); };
	DimStampedInfo(const char *name, longlong nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(longlong), handler); };
	DimStampedInfo(const char *name, int time, longlong nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(longlong), handler); };
	DimStampedInfo(const char *name, short nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(short), handler); };
	DimStampedInfo(const char *name, int time, short nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(short), handler); };
		DimStampedInfo(const char *name, char *nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1, handler); };
	DimStampedInfo(const char *name, int time, char *nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, nolink, (int)strlen(nolink)+1, handler); };
	DimStampedInfo(const char *name, void *nolink, int nolinksize, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, nolink, nolinksize, handler); };
	DimStampedInfo(const char *name, int time, void *nolink, int nolinksize, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, nolink, nolinksize, handler); };

	virtual ~DimStampedInfo();
	void subscribe(char *name, void *nolink, int nolinksize, int time, 
		DimInfoHandler *handler) 
		{ subscribe((char *)name, time, nolink, nolinksize, handler); };
private :
	void doIt();
	void subscribe(char *name, int time, void *nolink, int nolinksize,
		DimInfoHandler *handler);
};

class DllExp DimUpdatedInfo : public DimInfo{

public :
	DimUpdatedInfo(){};
	DimUpdatedInfo(const char *name, int nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(int), 0); };
	DimUpdatedInfo(const char *name, int time, int nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(int), 0); };
	DimUpdatedInfo(const char *name, float nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(float), 0); };
	DimUpdatedInfo(const char *name, int time, float nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(float), 0); };
	DimUpdatedInfo(const char *name, double nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(double), 0); };
	DimUpdatedInfo(const char *name, int time, double nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(double), 0); };
	DimUpdatedInfo(const char *name, longlong nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(longlong), 0); };
	DimUpdatedInfo(const char *name, int time, longlong nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(longlong), 0); };
	DimUpdatedInfo(const char *name, short nolink) 
	{ subscribe((char *)name, 0, &nolink, sizeof(short), 0); };
	DimUpdatedInfo(const char *name, int time, short nolink) 
	{ subscribe((char *)name, time, &nolink, sizeof(short), 0); };
	DimUpdatedInfo(const char *name, char *nolink) 
	{ subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1, 0); };
	DimUpdatedInfo(const char *name, int time, char *nolink) 
	{ subscribe((char *)name, time, nolink, (int)strlen(nolink)+1, 0); };
	DimUpdatedInfo(const char *name, void *nolink, int nolinksize) 
	{ subscribe((char *)name, 0, nolink, nolinksize, 0); };
	DimUpdatedInfo(const char *name, int time, void *nolink, int nolinksize) 
	{ subscribe((char *)name, time, nolink, nolinksize, 0); };

	DimUpdatedInfo(const char *name, int nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(int), handler); };
	DimUpdatedInfo(const char *name, int time, int nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(int), handler); };
	DimUpdatedInfo(const char *name, float nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(float), handler); };
	DimUpdatedInfo(const char *name, int time, float nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(float), handler); };
	DimUpdatedInfo(const char *name, double nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(double), handler); };
	DimUpdatedInfo(const char *name, int time, double nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(double), handler); };
	DimUpdatedInfo(const char *name, longlong nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(longlong), handler); };
	DimUpdatedInfo(const char *name, int time, longlong nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(longlong), handler); };
	DimUpdatedInfo(const char *name, short nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, &nolink, sizeof(short), handler); };
	DimUpdatedInfo(const char *name, int time, short nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, &nolink, sizeof(short), handler); };
	DimUpdatedInfo(const char *name, char *nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1, handler); };
	DimUpdatedInfo(const char *name, int time, char *nolink, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, nolink, (int)strlen(nolink)+1, handler); };
	DimUpdatedInfo(const char *name, void *nolink, int nolinksize, DimInfoHandler *handler) 
	{ subscribe((char *)name, 0, nolink, nolinksize, handler); };
	DimUpdatedInfo(const char *name, int time, void *nolink, int nolinksize, DimInfoHandler *handler) 
	{ subscribe((char *)name, time, nolink, nolinksize, handler); };

	virtual ~DimUpdatedInfo();
	void subscribe(char *name, void *nolink, int nolinksize, int time, 
		DimInfoHandler *handler) 
		{ subscribe((char *)name, time, nolink, nolinksize, handler); };

private :
	void doIt();
	void subscribe(char *name, int time, void *nolink, int nolinksize,
		DimInfoHandler *handler);
};

class DllExp DimCmnd {
public :

	int wakeUp;
	int result;
	int send(char *name, void *data, int datasize);
	void sendNB(char *name, void *data, int datasize);
  DimCmnd(){};
};

class DllExp DimCurrentInfo {

public :
	void *itsData;
	int itsDataSize;
	int itsSize;
//	int itsTagId;
	int wakeUp;

	DimCurrentInfo(){
		subscribe((char *)0, 0, (void *)0, 0); };
	DimCurrentInfo(const char *name, int nolink) { 
		subscribe((char *)name, 0, &nolink, sizeof(int)); };
	DimCurrentInfo(const char *name, float nolink) { 
		subscribe((char *)name, 0, &nolink, sizeof(float)); };
	DimCurrentInfo(const char *name, double nolink) { 
		subscribe((char *)name, 0, &nolink, sizeof(double)); };
	DimCurrentInfo(const char *name, longlong nolink) { 
		subscribe((char *)name, 0, &nolink, sizeof(longlong)); };
	DimCurrentInfo(const char *name, short nolink) { 
		subscribe((char *)name, 0, &nolink, sizeof(short)); };
	DimCurrentInfo(const char *name, char *nolink) { 
		subscribe((char *)name, 0, nolink, (int)strlen(nolink)+1); };
	DimCurrentInfo(const char *name, void *nolink, int nolinksize) { 
		subscribe((char *)name, 0, nolink, nolinksize); };
	DimCurrentInfo(const char *name, int time, int nolink) { 
		subscribe((char *)name, time, &nolink, sizeof(int)); };
	DimCurrentInfo(const char *name, int time, float nolink) { 
		subscribe((char *)name, time, &nolink, sizeof(float)); };
	DimCurrentInfo(const char *name, int time, double nolink) { 
		subscribe((char *)name, time, &nolink, sizeof(double)); };
	DimCurrentInfo(const char *name, int time, longlong nolink) { 
		subscribe((char *)name, time, &nolink, sizeof(longlong)); };
	DimCurrentInfo(const char *name, int time, short nolink) { 
		subscribe((char *)name, time, &nolink, sizeof(short)); };
	DimCurrentInfo(const char *name, int time, char *nolink) { 
		subscribe((char *)name, time, nolink, (int)strlen(nolink)+1); };
	DimCurrentInfo(const char *name, int time, void *nolink, int nolinksize) { 
		subscribe((char *)name, time, nolink, nolinksize); };


	virtual ~DimCurrentInfo();
	char *getName()  { return itsName; } ;
	void *getData();
	int getInt() { return *(int *)getData(); } ;
	float getFloat() { return *(float *)getData(); } ;
	double getDouble() { return *(double *)getData(); } ;
	longlong getLonglong() { return *(longlong *)getData(); } ;
	short getShort() { return *(short *)getData(); } ;
	char *getString()  { return (char *)getData(); } ;
	int getSize()  { getData(); return itsSize; } ;
	void subscribe(char *name, void *nolink, int nolinksize, int time) 
		{ subscribe((char *)name, time, nolink, nolinksize); };

private :
	char *itsName;
	void *itsNolinkBuf;
	int itsNolinkSize;
	void subscribe(char *name, int time, void *nolink, int nolinksize);
};

class DllExp DimRpcInfo : public DimTimer {
public :
	int itsId;
//	int itsTagId;
	int itsInit;
	void *itsData;
	int itsDataSize;
	void *itsDataOut;
	int itsDataOutSize;
	int itsSize;
	int wakeUp;
	int itsWaiting;
	int itsConnected;
	void *itsNolinkBuf;
	int itsNolinkSize;
	DimRpcInfo *itsHandler;

	DimRpcInfo(const char *name, int nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(int), 0); };
	DimRpcInfo(const char *name, float nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(float), 0); };
	DimRpcInfo(const char *name, double nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(double), 0); };
	DimRpcInfo(const char *name, longlong nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(longlong), 0); };
	DimRpcInfo(const char *name, short nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(short), 0); };
	DimRpcInfo(const char *name, char *nolink) { 
		subscribe((char *)name, 0, 0, nolink, (int)strlen(nolink)+1, 0); };
	DimRpcInfo(const char *name, void *nolink, int nolinksize) { 
		subscribe((char *)name, 0, 0, nolink, nolinksize, 0); };

	DimRpcInfo(const char *name, int time, int nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(int), time); };
	DimRpcInfo(const char *name, int time, float nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(float), time); };
	DimRpcInfo(const char *name, int time, double nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(double), time); };
	DimRpcInfo(const char *name, int time, longlong nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(longlong), time); };
	DimRpcInfo(const char *name, int time, short nolink) { 
		subscribe((char *)name, 0, 0, &nolink, sizeof(short), time); };
	DimRpcInfo(const char *name, int time, char *nolink) { 
		subscribe((char *)name, 0, 0, nolink, (int)strlen(nolink)+1, time); };
	DimRpcInfo(const char *name, int time, void *nolink, int nolinksize) { 
		subscribe((char *)name, 0, 0, nolink, nolinksize, time); };
	
	virtual void rpcInfoHandler();

	virtual ~DimRpcInfo();
	int getId() {return itsId;};
	void keepWaiting() {itsWaiting = 2;};
	char *getName()  { return itsName; } ;
	void *getData();
	int getInt() { return *(int *)getData(); } ;
	float getFloat() { return *(float *)getData(); } ;
	double getDouble() { return *(double *)getData(); } ;
	longlong getLonglong() { return *(longlong *)getData(); } ;
	short getShort() { return *(short *)getData(); } ;
	char *getString()  { return (char *)getData(); } ;
	int getSize()  { getData(); return itsSize; } ;

	void setData(void *data, int size) { doIt(data, size); };
	void setData(int &data) { doIt(&data, sizeof(int)); } ;
	void setData(float &data) { doIt(&data, sizeof(float)); } ;
	void setData(double &data) { doIt(&data, sizeof(double)); } ;
	void setData(longlong &data) { doIt(&data, sizeof(longlong)); } ;
	void setData(short &data) { doIt(&data, sizeof(short)); } ;
	void setData(char *data)  { doIt(data, (int)strlen(data)+1); } ;

private :
	char *itsName;
	char *itsNameIn;
	char *itsNameOut;
	int itsTimeout;
	void subscribe(char *name, void *data, int size, 
		void *nolink, int nolinksize, int timeout);
	void doIt(void *data, int size);
	void timerHandler();
};

class DllExp DimClient : public DimInfoHandler, public DimErrorHandler
{
public:

	static char *dimDnsNode;
	static DimErrorHandler *itsCltError;

	DimClient();
	virtual ~DimClient();
	static int sendCommand(const char *name, int data);
	static int sendCommand(const char *name, float data);
	static int sendCommand(const char *name, double data);
	static int sendCommand(const char *name, longlong data);
	static int sendCommand(const char *name, short data);
	static int sendCommand(const char *name, const char *data);
	static int sendCommand(const char *name, void *data, int datasize);
	static void sendCommandNB(const char *name, int data);
	static void sendCommandNB(const char *name, float data);
	static void sendCommandNB(const char *name, double data);
	static void sendCommandNB(const char *name, longlong data);
	static void sendCommandNB(const char *name, short data);
	static void sendCommandNB(const char *name, char *data);
	static void sendCommandNB(const char *name, void *data, int datasize);
	static int setExitHandler(const char *serverName);
	static int killServer(const char *serverName);
	static int setDnsNode(const char *node);
	static int setDnsNode(const char *node, int port);
	static char *getDnsNode();
	static int getDnsPort();
	static void addErrorHandler(DimErrorHandler *handler);
	void addErrorHandler();
	virtual void errorHandler(int /* severity */, int /* code */, char* /* msg */) {};
	static char *serverName;
	// Get Current Server Identifier	
	static int getServerId();
	// Get Current Server Process Identifier	
	static int getServerPid();
	// Get Current Server Name	
	static char *getServerName();
	static char **getServerServices();
//	static char *getServerServices(int serverId);

	virtual void infoHandler() {};

	static int dicNoCopy;
	static void setNoDataCopy();
	static int getNoDataCopy();
	static int inCallback();
};

class DllExp DimBrowser
{
public :

	DimBrowser();

	~DimBrowser();

	int getServices(const char *serviceName);
	int getServers();
	int getServerServices(const char *serverName);
	int getServerClients(const char *serverName);
	int getServices(const char *serviceName, int timeout);
	int getServers(int timeout);
	int getServerServices(const char *serverName, int timeout);
	int getServerClients(const char *serverName, int timeout);
	int getNextService(char *&service, char *&format);
	int getNextServer(char *&server, char *&node);
	int getNextServer(char *&server, char *&node, int &pid);
	int getNextServerService(char *&service, char *&format);
	int getNextServerClient(char *&client, char *&node);

private:

	TokenString *itsData[5];
	int currIndex; 
	char *currToken;
	char none;
	DimRpcInfo *browserRpc;
};

#endif
