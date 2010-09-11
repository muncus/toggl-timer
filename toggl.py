#!/usr/bin/python
#
# read rfid tags, translate to tasks, and send task updates to toggl.com 
#
# input: <rfid tag number> <seconds>\n

from optparse import OptionParser
from sys import stdin
import base64
import urllib2
import yaml
import json

#TODO: remove the need for a yaml map of rfid->task
#TODO: turn the yaml map into a json map, so i dont need both formats.

parser = OptionParser()
parser.add_option("-k", "--toggl_key", dest='apikey', help="Toggl api key")
parser.add_option("-m", "--tagmap", dest='mapfile',
                  help="yaml file containing tag id -> task mapping")
(options, args) = parser.parse_args()

# dictionary of tag number -> string
TAG_MAP = yaml.load(file(options.mapfile))
TASKS = []
print TAG_MAP

def updateTask(taskid, duration):
    """ add duration to the duration of the task with the supplied id.
    """
    TASKS = getTasks() # refresh our task list.
    print TASKS
    task = None
    taskid = taskid
    for t in TASKS:
        if t['id'] == taskid:
            task = t
            break
    task['duration'] += int(duration)

    # now send up the new task.
    posturl = "http://www.toggl.com/api/v3/tasks/%d.json" % task['id']
    r = urllib2.Request(posturl, data="{\"task\": %s }" % str(task))
    r = addAuthHeader(r, options.apikey)
    r.add_header("Content-type", "application/json")
    r.method = 'PUT'
    f = urllib2.urlopen(r)
    print f


def addAuthHeader(request, apikey):
    """ This is needed because the toggl servers dont do standard http basic auth.
    """
    base64string = base64.encodestring('%s:%s' % (apikey, 'api_token')).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    return request

def getTasks():
    r = urllib2.Request("http://www.toggl.com/api/v3/tasks.json")
    r = addAuthHeader(r, options.apikey)

    f = urllib2.urlopen(r)
    TASKS = (json.load(f))['data']
    return TASKS
    #print TASKS

def updateToggl(task_name, duration):
    """update the supplied task on toggl.com.
    """
    pass
    # map needs to map to a task id.
    # when we get input, fetch the task associated with the tag, increment the duration, and post it.

getTasks()
while True:
    s = stdin.readline()
    if not s:
        break
    (key, duration) = s.split() 
    print "key: %s" % key
    if(TAG_MAP.has_key(key)):
        print TAG_MAP[key]
        updateTask(TAG_MAP[key], duration)
    else:
        print "unknown tag: %s" % key
