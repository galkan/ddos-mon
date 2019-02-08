#!/usr/bin/env python

try:
	import sys
	import time
	import signal
	import urllib3
	import argparse
	import requests
	import dns.resolver
	from fake_useragent import UserAgent
except ImportError, err:
	import sys
	print >> sys.stderr, err
	sys.exit(1)


urllib3.disable_warnings()



class AddressAction(argparse.Action):

    	def __call__(self, parser, args, values, option = None):
	
		if args.service == "dns" and getattr(args, 'domain') is None:
			parser.error('error: argument -d/--domain expected one argument')



class DdosRate(object):

	def __init__(self):

		signal.signal(signal.SIGINT, self.__signal_handler)

		description = "DDOS Rate ..."
                parser = argparse.ArgumentParser()

		parser.add_argument('--service', dest = 'service', action = 'store', choices=('http', 'https', 'dns'), help = 'Service', required = True)
		parser.add_argument('--target', dest = 'target', action = 'store', help = 'Target to check', required = True)
		parser.add_argument('--port', dest = 'port', action = 'store', help = 'Port Number', required = True)
		parser.add_argument('--duration', dest = 'duration', action = 'store', type = int, help = 'Duration time', required = True)
		parser.add_argument('--domain', dest = 'domain', action = 'store',  help = 'Domain Name to lookup')
		parser.add_argument('options', nargs = '*', action = AddressAction)

		args = parser.parse_args()

		self.__port = args.port
		self.__target = args.target
		self.__domain = args.domain
		self.__service = args.service	
		self.__duration = args.duration

		self.__resolver = None

		useragent = UserAgent()
		self.__headers = { "User-Agent":useragent.random}

		self.__sum = []
		self.__timeout = 10

		self.__action = { "http":self.__http, "https":self.__http, "dns":self.__dns }
		

	def __print_summary(self):

		try:
			return sum(self.__sum)/len(self.__sum)
		except:
			return 0

	
	def __signal_handler(self, signal, frame):	

		print "SUM: {0}".format(self.__print_summary())
        	sys.exit(0)


	def __dns(self):
	
		if not self.__resolver:
			self.__resolver = dns.resolver.Resolver()
			self.__resolver.timeout = self.__timeout
			self.__resolver.lifetime = self.__timeout
			self.__resolver.namerservers =  [self.__target]		
		
		try:
			start = time.time()
			res =  self.__resolver.query(self.__domain, 'A')
			stop = time.time()

			result = float(stop - start)
                        self.__sum.append(result)

			time.sleep(0.5)
		except Exception, err:
			print err


	def __http(self):

		url = "{0}://{1}:{2}/".format(self.__service, self.__target, self.__port)

		try:	
			start = time.time()
			req = requests.get(url, headers=self.__headers, timeout=self.__timeout,  verify=False, allow_redirects=True)
			stop = time.time()

			result = float(stop - start)
			self.__sum.append(result)
		except requests.exceptions.Timeout, err:
			print "Timeout. Taking ScreenShoot : {0}".format(float(stop - start))
		except Exception, err:
			print err
			sys.exit(1)
		

	def _run(self):

		start = int(time.time())

		while True:
			check = int(time.time())
			if int(check - start) >= self.__duration * 60:
				print "SUM: {0}".format(self.__print_summary())
				break
			else:
				self.__action[self.__service]()

##
### Main
##

if __name__ == "__main__":
	
	ddos_date = DdosRate()
	ddos_date._run()

