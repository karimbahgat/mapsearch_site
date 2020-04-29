# the functions to be exposed as a web service

import automap as mapfit
from PIL import Image

import sys, io, codecs
import urllib
import json

def warp_map(kwargs):
    '''A simple automap function that takes an input url,
    warps the image using a precalculated transform,
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
    params = kwargs
    params.update(dict(warp=True)) # override with hardcoded defaults
    
    # run result
    #result = mapfit.automap(img, **params)
    result = {'warping': mapfit.main.warp_image(img, params['priors']['transinfo']) }
    return result

if __name__ == '__main__':
    # redirect all prints
    sys.stdout = codecs.getwriter('utf8')(io.BytesIO()) #io.TextIOWrapper(io.BytesIO(), encoding='utf8', errors='ignore')
    sys.stderr = codecs.getwriter('utf8')(io.BytesIO())

    # parse args
    print(sys.argv)
    url,trans = sys.argv[1],sys.argv[2]
    print(url, trans)
    trans = json.loads(trans)
    kwargs = {'url':url,
              'priors':{'transinfo':trans},
              }
    print(kwargs)

    # run
    result = warp_map(kwargs)
    print(result)

    # get image file as bytes
    fobj = io.BytesIO()
    result['warping']['image'].save(fobj, "PNG")
    raw = fobj.getvalue().encode('base64')
    result['warping']['image'] = raw

    # TODO: should actually return as geotiff with affine and/or prj
    # ... 

    # return result json via normal stdout
    sys.__stdout__.write(json.dumps(result))
    


