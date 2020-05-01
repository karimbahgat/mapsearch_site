# the functions to be exposed as a web service

import automap as mapfit
from PIL import Image

import sys, io, codecs
import urllib
import json

def georeference_map(kwargs):
    '''A simple automap function that takes an input url,
    processes the information needed to georeference,
    and returns as json to user. 
    '''
    
    # get main arg
    print kwargs
    url = kwargs.pop('url')
    
    # load img
    fobj = io.BytesIO(urllib.urlopen(url).read())
    img = Image.open(fobj)
    print img
  
    # set params
    params = dict(db=r"C:\Users\kimok\Desktop\BIGDATA\gazetteer data\optim\gazetteers.db", source='best')
    params.update(kwargs) # override with user input
    params.update(dict(warp=False)) # override with hardcoded defaults
    
    # run result
    result = mapfit.automap(img, **params)
    return result

if __name__ == '__main__':
    # redirect all prints
    sys.stdout = codecs.getwriter('utf8')(io.BytesIO()) #io.TextIOWrapper(io.BytesIO(), encoding='utf8', errors='ignore')
    sys.stderr = codecs.getwriter('utf8')(io.BytesIO())

    # parse args
    url = sys.argv[1]
    kwargs = {'url':url} #, 'textcolor':(0,0,0)}

    # run
    result = georeference_map(kwargs)

    # return result json via normal stdout
    sys.__stdout__.write(json.dumps(result))
    


