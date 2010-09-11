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
TAG_MAP = yaml.load(file(options.mapfile))
TASKS = []
print TAG_MAP

def getTasks():
    r = urllib2.Request("http://www.toggl.com/api/v3/tasks.json")
    #TODO: do the auth dance.
    f = urllib2.urlopen(r)
    TASKS = (json.load(f))['data']
    print TASKS

def updateToggl(task_name, duration):
    """update the supplied task on toggl.com.
    """
    pass
    # map needs to map to a task id.
    # when we get input, fetch the task associated with the tag, increment the duration, and post it.

while True:
    s = stdin.readline()
    if not s:
        break
    (key, duration) = s.split() 
    print "key: %s" % key
    if(TAG_MAP.has_key(key)):
        print TAG_MAP[key]
    else:
        print "unknown tag: %s" % key
