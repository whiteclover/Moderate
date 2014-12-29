try:
    import simplejson as json
except ImportError:
    import json


pack = json.dumps
unpack = json.loads