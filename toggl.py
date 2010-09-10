#!/usr/bin/python
#
# read rfid tags, translate to tasks, and send task updates to toggl.com 
#
# input: <rfid tag number> <seconds>\n

from optparse import OptionParser
from sys import stdin
import urllib2
import yaml

parser = OptionParser()
parser.add_option("-k", "--toggl_key", dest='apikey', help="Toggl api key")
parser.add_option("-m", "--tagmap", dest='mapfile',
                  help="yaml file containing tag id -> task mapping")
(options, args) = parser.parse_args()

# dictionary of tag number -> string
TAG_MAP = yaml.load(options.mapfile)

while True:
    s = stdin.readline()
    if not s:
        break
    (key, duration) = s.split(maxsplit=1) 
    if(TAG_MAP.has_key(key)):
        print TAG_MAP[key]
    else:
        print "unknown tag: %s" % key
