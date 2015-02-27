#ifndef __DISHHDEFS
#define __DISHHDEFS
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
/*
#define DimSHORT	"S"
#define DimINT		"I"
#define DimLONG		"L"
#define DimFLOAT	"F"
#define DimDOUBLE	"D"
#define DimSTRING	"C"
#define DimXLONG	"X"
*/
enum DisTYPE {
	DisPOINTER, DisSHORT, DisINT, DisFLOAT, DisDOUBLE, DisSTRING, DisXLONG, DisCOMMAND
};

class DimService;
class DimCommand;

class DllExp DimServiceHandler{
public:
	DimService *itsService;
	DimService *getService() { return itsService; } ;
	virtual void serviceHandler() = 0;
	virtual ~DimServiceHandler() {};
};

class DllExp DimCommandHandler{
public:
	DimCommand *itsCommand;
	DimCommand *getCommand() { return itsCommand; } ;
	virtual void commandHandler() = 0;
	virtual ~DimCommandHandler() {};
};

class DllExp DimClientExitHandler{
public:
	virtual void clientExitHandler() = 0;
	virtual ~DimClientExitHandler() {};
};

class DllExp DimExitHandler{
public:
	virtual void exitHandler(int code) = 0;
	virtual ~DimExitHandler() {};
};

class DllExp DimServerDns
{
public:
	DimServerDns(const char *node);
	DimServerDns(const char *node, int port);
	DimServerDns(const char *node, int port, char *name);
	~DimServerDns();
	void init(const char *node, int port);
	dim_long getDnsId();
	void setName(const char *name);
	char *getName();
	void clearName();
	void autoStartOn();
	void autoStartOff();
	int isAutoStart();
	void addServiceId(int id);
	int *getServiceIdList();
private:
	char *itsNode;
	int itsPort;
	dim_long itsDnsId;
	char *itsName;
	int autoStart;
	int *itsServiceIdList;
	int itsServiceIdListSize;
	int itsNServiceIds;
//	int itsNServices;
};

class DllExp DimServer : public DimServiceHandler, public DimCommandHandler,
	public DimClientExitHandler, public DimExitHandler, public DimErrorHandler
{
public:
	static char *clientName;
	static char *itsName;
	static char *dimDnsNode;
	static int autoStart;
	static DimClientExitHandler *itsClientExit;
	static DimExitHandler *itsExit;
	static DimErrorHandler *itsSrvError;
//	static int itsNServices;
	DimServer();
	virtual ~DimServer();
	static void start(const char *name);
	static void start(DimServerDns *dns, const char *name);
	static void start();
	static void start(DimServerDns *dns);
	static void stop();
	static void stop(DimServerDns *dns);
	static void autoStartOn();
	static void autoStartOff();
	// Get Current Client Identifier	
	static int getClientId();
	// Get Current Client Name	
	static char *getClientName();
	static void setClientExitHandler(int clientId);
	static void clearClientExitHandler(int clientId);
	static void addClientExitHandler(DimClientExitHandler *handler);
	void addClientExitHandler();
	static void addExitHandler(DimExitHandler *handler);
	static void addErrorHandler(DimErrorHandler *handler);
	static int setDnsNode(const char *node);
	static int setDnsNode(const char *node, int port);
	static dim_long addDns(const char *node, int port);
	static void stopDns(dim_long dnsid);
	static char *getDnsNode();
	static int getDnsPort();
	static void setWriteTimeout(int secs);
	static int getWriteTimeout();
	void addExitHandler();
	void addErrorHandler();
	virtual void clientExitHandler() {};
	virtual void exitHandler(int /* code */) {};
	virtual void errorHandler(int /* severity */, int /* code */, char* /* msg */) {};
//	static char *getClientServices();
//	static char *getClientServices(int clientId);
	static char **getClientServices();

	virtual void serviceHandler() {};
	virtual void commandHandler() {};
	static int inCallback();
};

class DllExp DimService : public DimServiceHandler {

public :
	DimServiceHandler *itsServiceHandler;

	// The object contains the value to be published. Service to be updated with an argument of same type;
	DimService();

	DimService(const char *name, int &value);
	DimService(const char *name, float &value);
	DimService(const char *name, double &value);
	DimService(const char *name, longlong &value);
	DimService(const char *name, short &value);
	DimService(const char *name, char *string);

	DimService(const char *name, char *format, void *structure, int size);

	DimService(const char *name, char *format, DimServiceHandler *handler);

	DimService(const char *name, const char *format, void *structure, int size);

	DimService(const char *name, const char *format, DimServiceHandler *handler);

	DimService(DimServerDns *dns, const char *name, int &value);
	DimService(DimServerDns *dns, const char *name, float &value);
	DimService(DimServerDns *dns, const char *name, double &value);
	DimService(DimServerDns *dns, const char *name, longlong &value);
	DimService(DimServerDns *dns, const char *name, short &value);
	DimService(DimServerDns *dns, const char *name, char *string);

	DimService(DimServerDns *dns, const char *name, char *format, void *structure, int size);

	DimService(DimServerDns *dns, const char *name, char *format, DimServiceHandler *handler);

	DimService(DimServerDns *dns, const char *name, const char *format, void *structure, int size);

	DimService(DimServerDns *dns, const char *name, const char *format, DimServiceHandler *handler);

	virtual ~DimService();

	// Update methods
	int updateService();
	// Update the value as well...
	int updateService( int &value );
	int updateService( float &value );
	int updateService( double &value ) ;
	int updateService( longlong &value );
	int updateService( short &value );
	int updateService( char *string );
	
	int updateService( void *structure, int size );
	
	// Selective Update methods
	int selectiveUpdateService(int *cids);
	// Update the value as well...
	int selectiveUpdateService( int &value, int *cids);
	int selectiveUpdateService( float &value, int *cids );
	int selectiveUpdateService( double &value, int *cids );
	int selectiveUpdateService( longlong &value, int *cids );
	int selectiveUpdateService( short &value, int *cids );
	int selectiveUpdateService( char *string, int *cids );
	
	int selectiveUpdateService( void *structure, int size, int *cids );
	
	void setQuality(int quality);
	void setTimestamp(int secs, int millisecs);

	void *itsData;
	int itsDataSize;
	int itsSize;
	DisTYPE itsType;
	void setData(void *data, int size);
	void setData(int &data);
	void setData(float &data);
	void setData(double &data);
	void setData(longlong &data);
	void setData(short &data);
	void setData(char *data);

	virtual void serviceHandler() {};
	// Accessors
	char *getName();
	int getTimeout(int clientId);
	int getNClients();

private :
	char *itsName;
	int itsId;
	int itsTagId;
	void declareIt(char *name, char *format, DimServiceHandler *handler, DimServerDns *dns);
	void storeIt(void *data, int size);
	DimServerDns *itsDns;
};

class DllExp CmndInfo : public SLLItem {
	friend class DimCommand;
	void *itsData;
	int itsDataSize;
	int secs, millisecs;
public:
	CmndInfo(void *data, int datasize, int tsecs, int tmillisecs);
	~CmndInfo();
};

class DllExp DimCommand : public DimCommandHandler {

public :
	DimCommandHandler *itsCommandHandler;

	DimCommand(const char *name, char *format);

	DimCommand(const char *name, char *format, DimCommandHandler *handler);

	DimCommand(DimServerDns *dns, const char *name, char *format);

	DimCommand(DimServerDns *dns, const char *name, char *format, DimCommandHandler *handler);

	DimCommand(const char *name, const char *format);

	DimCommand(const char *name, const char *format, DimCommandHandler *handler);

	DimCommand(DimServerDns *dns, const char *name, const char *format);

	DimCommand(DimServerDns *dns, const char *name, const char *format, DimCommandHandler *handler);

	int getNext();
	int hasNext();
	void *itsData;
	int itsSize;
	void *getData();
	int getInt();
	float getFloat();
	double getDouble();
	longlong getLonglong();
	short getShort();
	char *getString();
	int getSize();
	char *getFormat();
	int getTimestamp();
	int getTimestampMillisecs();

	virtual void commandHandler();

	// Accessors
	char *getName();
	virtual ~DimCommand();

private :
	char *itsName;
	int itsId;
	int itsTagId;
	char *itsFormat;
	void declareIt(char *name, char *format, DimCommandHandler *handler, DimServerDns *dns);
	CmndInfo *currCmnd;
	SLList itsCmndList;
	DimServerDns *itsDns;
public:
	int secs, millisecs;
};

class DllExp DimRpc
{
public :

	// The object contains the value to be published. Service to be updated with an argument of same type;
	DimRpc();

	DimRpc(const char *name, const char *formatin, const char *formatout);

	DimRpc(DimServerDns *dns, const char *name, const char *formatin, const char *formatout);

	// Desctructor
	virtual ~DimRpc();

	void *itsDataIn;
	int itsSizeIn;
	void *getData();
	int getInt();
	float getFloat();
	double getDouble();
	longlong getLonglong();
	short getShort();
	char *getString();
	int getSize();

	void *itsDataOut;
	int itsDataOutSize;
	int itsSizeOut;

	void setData(void *data, int size);
	void setData(int &data);
	void setData(float &data);
	void setData(double &data);
	void setData(longlong &data);
	void setData(short &data);
	void setData(char *data);

	virtual void rpcHandler() = 0;
	// Accessors
	char *getName();
	int itsIdIn;
	int itsIdOut;
private :
	int itsTagId;
	char *itsName;
	char *itsNameIn;
	char *itsNameOut;
	void declareIt(char *name, char *formatin, char *formatout, DimServerDns *dns);
	void storeIt(void *data, int size);
	void timerHandler();
	DimServerDns *itsDns;
public:
	int itsKilled;
	int itsTimeout;
};


#endif

