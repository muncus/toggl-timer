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
import datetime

USERAGENT = "toggl.py/punchclock"

class MethodRequest(urllib2.Request):
    ''' Used to create HEAD/PUT/DELETE/... requests with urllib2 '''
    def __init__(self, url, data=None, headers={}, method="GET"):
        urllib2.Request.__init__(self, url, data, headers)
        self.set_method(method)
    def set_method(self, method):
        self.method = method.upper()
    def get_method(self):
        return getattr(self, 'method', urllib2.Request.get_method(self))


#TODO: remove the need for a yaml map of rfid->task
#TODO: turn the yaml map into a json map, so i dont need both formats.


# dictionary of tag number -> string
TAG_MAP = {}
TASKS = []

def updateTask(taskid, duration):
    """ add duration to the duration of the task with the supplied id.
    """
    TASKS = getTasks() # refresh our task list.
    task = None
    taskid = taskid
    for t in TASKS:
        if t['id'] == taskid:
            task = t
            break
    task['duration'] += int(duration)

    # now send up the new task.
    posturl = "http://www.toggl.com/api/v3/tasks/%d.json" % task['id']
    r = MethodRequest(posturl, data="{\"task\": %s }" % json.dumps(task), method="PUT")
    r = addAuthHeader(r, options.apikey)
    r.add_header("Content-type", "application/json")
    print r.get_data()
    print r.get_full_url()
    f = urllib2.urlopen(r)
    print f.read()

def createTask(taskobj):
    """ creates a new task in Toggl with the specified contents."""
    # now send up the new task.
    posturl = "http://www.toggl.com/api/v3/tasks.json"
    r = MethodRequest(posturl, data=json.dumps(taskobj), method="POST")
    r = addAuthHeader(r, options.apikey)
    r.add_header("Content-type", "application/json")
    print r.get_data()
    print r.get_full_url()
    f = urllib2.urlopen(r)
    print f.read()

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

def getTaskJsonObject(cpn, duration):
    """Creates a Toggl task api object, using a JsonObject."""
    starttime = datetime.datetime.utcnow() - datetime.timedelta(seconds=duration)
    endtime = datetime.datetime.utcnow()
    baseobj = {
        'duration': duration,
        'billable': True,
        'start': starttime.isoformat(),
        'end': endtime.isoformat(),
        'project' : {'client_project_name': cpn},
        'created_with': USERAGENT,
    }
    return {'task': baseobj}

def getTask(cpn, duration):
    """creates a new toggl task, with the specified client_project_name."""
    #TODO: consider implementing this with JSONObject instead
    task_template = """{
    "task" : {
      "duration": %(duration)s,
      "billable": true,
      "start": "%(timestamp)s",
      "project" : {
      "client_project_name": "%(cpn)s"
      },
      "created_with": "%(useragent)s"
    }}"""
    #TODO: implement timezone
    return task_template % {
        'duration': duration,
        'cpn' : cpn,
        'useragent': "toggl.py",
        'timestamp': datetime.datetime.utcnow().isoformat(),
    }

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-k", "--toggl_key", dest='apikey', help="Toggl api key")
    parser.add_option("-t", "--tagmap", dest='mapfile',
                      help="yaml file containing tag id -> task mapping")
    parser.add_option("-i", "--input", dest='input', default=None,
                      help="read input from the specified file/device")
    parser.add_option("-m", "--min_time", dest='min_time', default=10,
                      help="events shorter than this will not be reported")
    (options, args) = parser.parse_args()
    if not options.apikey:
      parser.error("--toggl_key is a required argument")
    if not options.mapfile:
      parser.error("--tagmap is a required argument")

    TAG_MAP = yaml.load(file(options.mapfile))

    if options.input:
      # input specified, read it.
      inputfh = open(options.input)
    else:
      inputfh = stdin

    while True:
        s = inputfh.readline()
        if not s or s[0] == '#':
            continue
        (key, duration) = s.split() 
        #print "key: %s" % key
        if(TAG_MAP.has_key(key)):
            print TAG_MAP[key]
            if(duration < options.min_time):
              print "%s : event too short" % key
            createTask(getTaskJsonObject(TAG_MAP[key], int(duration)))
        else:
            print "unknown tag: %s" % key
