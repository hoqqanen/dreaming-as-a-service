#!/usr/bin/env python
import argparse
import os
import requests

parser = argparse.ArgumentParser(
  description='Send a request to the Dreaming as a Service server.')
parser.add_argument('input_file_name', type=str)
parser.add_argument('output_file_name', type=str)
parser.add_argument('--server', type=str, default='52.7.11.64:5000')
args = parser.parse_args()

print "Weirdifying %s -> %s..." % (args.input_file_name, args.output_file_name)

input_file = open(args.input_file_name, 'rb')
files={args.input_file_name: input_file}

url = "http://%s/" % args.server
response = requests.post(url, files=files)
image_content = response.content

output_file = open(args.output_file_name, 'wb')
output_file.write(image_content)
output_file.close()

print "Done."
