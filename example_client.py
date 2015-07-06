#!/usr/bin/env python
import argparse
import os
import requests

parser = argparse.ArgumentParser(
  description='Send a request to the Dreaming as a Service server.')
parser.add_argument('input_file_name', type=str)
parser.add_argument('output_file_name', type=str)
parser.add_argument('--server', type=str, default='52.7.11.64:5000', help='''
  IP Address (and optionally the port) of the server to connect to.''')
parser.add_argument('--params', type=str, default='', help='''
  List of parameters to pass the server. i.e.: --params=x=123,y=hello''')
args = parser.parse_args()


print "Weirdifying %s -> %s..." % (args.input_file_name, args.output_file_name)

input_file = open(args.input_file_name, 'rb')
files={args.input_file_name: input_file}

params = {}
for assignment in args.params.split(","):
  if assignment != '':
    pieces = assignment.split("=")
    if len(pieces) != 2:
      print "%s ought to contain one equal sign" % assignment
      sys.exit(1)
    params[pieces[0]] = pieces[1]

url = "http://%s/" % args.server
response = requests.post(url, params=params, files=files)
if response.status_code == 200:
  image_content = response.content

  output_file = open(args.output_file_name, 'wb')
  output_file.write(image_content)
  output_file.close()
  print "Done."
else:
  print "Error %d." % response.status_code

