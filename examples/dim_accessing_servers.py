from __future__ import print_function
import fact.dim

def main():

	print("""
		Welcome to the first fact.dim example --- accessing servers

		fact.dim tries to give you a somewhat easy access to FACTs
		DIM servers. In addition it aims to make writing of such 
		DIM servers easier for you.

		http://dim.web.cern.ch/dim/

		Unfortunately fact.dim does not yet bring a DIM DNS server.
		So you can't explore the features of fact.dim on the privacy
		of your personal computer, instead you will need to 
		connect to any already exisiting DIM DNS server.

		There is one running on 'newdaq', so if you happen
		to be connected to the FACT VPN, you can start right away.

		If you want to proceed, please enter now the hostname
		of your DIM DNS server. Otherwise type 'q'
		""")

	dim_dns_hostname = raw_input("DIM_DNS_HOST [default:newdaq]")
	if not dim_dns_hostname.split():
		dim_dns_hostname = 'newdaq'
	elif dim_dns_hostname.split()[0].lower() == 'q':
		return
	
	dns = fact.dim.Dns(dim_dns_hostname)

	print("Requesting dict of DIM servers, which are currently online ...")
	online_servers = dns.servers()
	print(online_servers.keys())

	raw_input("\n -- press any key to go on --")
	
	print("We are going to talk to CHAT as an example \n     chat = online_servers['CHAT']")
	chat = online_servers['CHAT']
	raw_input("\n -- press any key to go on --")
	print ("Let's see what services this server provides:")
	print(chat.services.keys())
	raw_input("\n -- press any key to go on --")

	print("""All (UPPERCASE) services of a server are provided to you as (lowercase) methods.

		So, in order to send a chat message to the CHAT server, 
		feel free to call it's msg() method.

		Unfortunately, you'll need to wrap the parameters into a tuple at the moment,
		so in order to send "Hello World"
		You'll need to type:

		chat.msg( ("Hello World",) )

		We are working on that ;-)

		In order to check, if your message was actually recieved by the server, look here:
		http://fact-project.org/smartfact/index.html?sound#chat

		Congrat's you just send your first DIM command using fact.dim.

		-----------------------------------------

		In order to get the last message anybody ever sent to the chat server, you'll
		need to request a DIM servers SERIVCE. There is a complicated (but correct) way
		to listen to a servers services, which involves writing a 'call-back' function, 
		that will be called whenever a servers services are updated. That call-back function
		then needs to be hooked into the DIM system.

		However, we want to make this easier for you. So in order to request the 'current'
		services value, just call the method named after the service and you're done.

		chat.message() 

		As you see, the result is a string, that is still contained in a tuple. 
		We're also working on that ;-)
		""")

	return chat
	
if __name__ == '__main__':
	chat = main()