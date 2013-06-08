__author__ = "Jonas Geduldig"
__date__ = "June 7, 2013"
__license__ = "MIT"

# unicode printing for Windows 
import sys, codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

import argparse
import constants
import pprint
from TwitterOauth import TwitterOauth
from TwitterAPI import TwitterAPI


def find_field(name, obj):
	"""Breadth-first search of the JSON result fields."""
	q = []
	q.append(obj)
	while q:
		obj = q.pop(0)
		if hasattr(obj, '__iter__'):
			isdict = type(obj) is dict
			if isdict and name in obj:
				return obj[name]
			for k in obj:
				q.append(obj[k] if isdict else k)
	else:
		return None


def to_dict(param_list):
	"""Convert a list of key=value to dict[key]=value"""			
	if param_list is not None:
		return {name: value for (name, value) in [param.split('=') for param in param_list]}
	else:
		return None


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Request any Twitter Streaming or REST API endpoint')
	parser.add_argument('-oauth', metavar='FILENAME', type=str, help='file containing OAuth credentials')
	parser.add_argument('-endpoint', metavar='ENDPOINT', type=str, help='Twitter endpoint', required=True)
	parser.add_argument('-parameters', metavar='NAME_VALUE', type=str, help='parameter NAME=VALUE', nargs='+')
	parser.add_argument('-fields', metavar='FIELD', type=str, help='print a top-level field in the json response', nargs='+')
	args = parser.parse_args()	

	try:
		params = to_dict(args.parameters)
		oauth = TwitterOauth.read_file(args.oauth)

		api = TwitterAPI(oauth.consumer_key, oauth.consumer_secret, oauth.access_token_key, oauth.access_token_secret)
		api.request(args.endpoint, params)
		iter = api.get_iterator()
		
		pp = pprint.PrettyPrinter()
		for item in iter:
			if 'message' in item:
				print 'ERROR:', item['message']
			elif args.fields is None:
				pp.pprint(item)
			else:
				for name in args.fields:
					value = find_field(name, item)
					if value is not None:
						print '%s: %s' % (name, value)
						
	except KeyboardInterrupt:
		print>>sys.stderr, '\nTerminated by user'
		
	except Exception, e:
		print>>sys.stderr, '*** STOPPED', e