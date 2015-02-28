#ifndef __DLLHHDEFS
#define __DLLHHDEFS

class DllExp DLLItem {
	friend class DLList ;
	DLLItem *next;
	DLLItem *prev;
public:
	DLLItem(){
		next = 0;
		prev = 0;
	};
};

class DllExp DLList {
	DLLItem *head;
	DLLItem *curr;
public:
	DLList (){
		DISABLE_AST
		head = new DLLItem();
		head->next = head;
		head->prev = head;
		curr = head;
		ENABLE_AST
	}
	~DLList()
	{
		DISABLE_AST
		delete head;
		ENABLE_AST
	}
    void add(DLLItem *item)
	{
		DLLItem *prevp;
		DISABLE_AST
		item->next = head;
		prevp = head->prev;
		item->prev = prevp;
		prevp->next = item;
		head->prev = item;
		ENABLE_AST
	}
	DLLItem *getHead()
	{
		DISABLE_AST
		if(head->next == head)
		{
			ENABLE_AST
			return((DLLItem *)0);
		}
		curr = head->next;
		ENABLE_AST
		return( head->next );
	}
	DLLItem *getLast()
	{
		DISABLE_AST
		if(head->prev == head)
		{
			ENABLE_AST
			return((DLLItem *)0);
		}
		curr = head->prev;
		ENABLE_AST
		return( head->prev );
	}
	DLLItem *getNext()
	{
		DISABLE_AST
		curr = curr->next;
		if(curr == head)
		{
			ENABLE_AST
			return((DLLItem *)0);
		}
		ENABLE_AST
		return( curr );
	}
	DLLItem *removeHead()
	{
		DLLItem *item;
		DISABLE_AST
		item = head->next;
		if(item == head)
		{
			ENABLE_AST
			return((DLLItem *)0);
		}
		remove(item);
		ENABLE_AST
		return(item);
	}
	void remove(DLLItem *item)
	{
		DLLItem *prevp, *nextp;
		DISABLE_AST
		prevp = item->prev;
		nextp = item->next;
		prevp->next = item->next;
		nextp->prev = prevp;
		ENABLE_AST
	}
};
#endif
