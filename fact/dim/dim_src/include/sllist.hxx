#ifndef __SLLHHDEFS
#define __SLLHHDEFS

class DllExp SLLItem {
	friend class SLList ;
	SLLItem *next;
public:
	SLLItem(){
		next = 0;
	};
};

class DllExp SLList {
	SLLItem *head;
	SLLItem *curr;
public:
	SLList (){
		DISABLE_AST
		head = new SLLItem();
		curr = head;
		ENABLE_AST
	}
	~SLList()
	{
		DISABLE_AST
		delete head;
		ENABLE_AST
	}
    void add(SLLItem *itemptr)
	{
		DISABLE_AST
		SLLItem *ptr = head;
		while(ptr->next)
		{
			ptr = ptr->next;
		}
		ptr->next = itemptr;
		ENABLE_AST
	}
	SLLItem *getHead()
	{
		curr = head->next;
		return( head->next );
	}
	SLLItem *getNext()
	{
		DISABLE_AST
		if(!curr)
			curr = head;
		curr = curr->next;
		ENABLE_AST
		return( curr );
	}
	SLLItem *removeHead()
	{
		SLLItem *ptr;

		DISABLE_AST
		ptr = head->next;
		if(ptr)
		{
			head->next = ptr->next;
			curr = head->next;
		}
		ENABLE_AST
		return( ptr);
	}
	void remove(SLLItem *itemptr)
	{
		SLLItem *ptr = head, *prev;
		DISABLE_AST
		while(ptr->next)
		{
			prev = ptr;
			ptr = ptr->next;
			if( itemptr == ptr )
			{
				prev->next = ptr->next;
			}
		}
		ENABLE_AST
	}
};
#endif
