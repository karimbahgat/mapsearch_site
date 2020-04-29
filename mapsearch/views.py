from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import QueryDict

from .models import Map
from .forms import MapForm

import urllib
import io
import base64
from PIL import Image

# Create your views here.

def search(request):
    if request.GET:
        # get search results
        dct = request.GET.dict()
        
        if dct['search'].startswith('http'):
            # searching map url
            # check if already exists in db
            matches = Map.objects.filter(url=dct['search'])
            mapp = matches[0] if matches else None
            if mapp is None:
                request.GET = QueryDict(mutable=True)
                request.GET['url'] = dct['search']
                return map_add(request)
                
            # link to the map view
            return redirect('map_view', mapp.pk)
        
        else:
            # search text of existing maps
            # ...
            return render(request, 'templates/search.html', {})
    else:
        # front page search screen
        recent_maps = []
        for m in Map.objects.order_by('-created'): # limit somehow...
            if m.thumbnail:
                print(repr(m.thumbnail))
                thumb = 'data:image/png;base64,' + str(m.thumbnail, 'ascii')
                print(repr(thumb))
            else:
                thumb = None
            recent_maps.append({'obj':m, 'thumb':thumb})
        return render(request, 'templates/search.html', {'recent_maps':recent_maps})

# MAP

def map_add(request):
    dct = request.GET.dict()
    
    # download image
    fobj = io.BytesIO(urllib.request.urlopen(dct['url']).read())
    img = Image.open(fobj)
    print(img)
    
    # add to db
    mapp = Map.objects.create(url=dct['url'])

    # create thumbnail
    max_size = 150
    longest = max(img.size)
    scale = max_size / float(longest)
    size = img.size[0] * scale, img.size[1] * scale
    img.thumbnail(size)
    print(img)

    fobj = io.BytesIO()
    img.save(fobj, "PNG")
    raw = base64.b64encode(fobj.getvalue())
    mapp.thumbnail = raw
    
    # process map in background? 
    # ...

    # save
    mapp.save()

    # redirect to map view
    return redirect('map_view', mapp.pk)

def map_update_about(request, pk):
    # add to db
    mapp = Map.objects.get(pk=pk)

    # download image
    fobj = io.BytesIO(urllib.request.urlopen(mapp.url).read())
    img = Image.open(fobj)
    print(img)

    # create thumbnail
    max_size = 150
    longest = max(img.size)
    scale = max_size / float(longest)
    size = img.size[0] * scale, img.size[1] * scale
    img.thumbnail(size)
    print(img)

    fobj = io.BytesIO()
    img.save(fobj, "PNG")
    raw = base64.b64encode(fobj.getvalue())
    mapp.thumbnail = raw

    # save
    mapp.save()

    # redirect to map view
    return redirect('map_view', mapp.pk)

def map_view(request, pk, tab=None):
    mapp = Map.objects.get(pk=pk)
    mappform = MapForm(instance=mapp)
    tab = tab or 'about'
    return render(request, 'templates/map_view_{}.html'.format(tab), {'map':mapp, 'form':mappform, 'tab':tab})


def map_auto_georef(request, pk):
    import subprocess
    import codecs
    import io
    import json

    # find map
    mapp = Map.objects.get(pk=pk)

    # set args
    args = ["C:\Python27-64\python.exe", # python version
            r"C:\Users\kimok\OneDrive\Documents\GitHub\mapsearch_site\mapsearch\taag server.py", # georef program
            mapp.url] # georef url
    #results = codecs.getwriter('utf8')(io.BytesIO()) #io.BytesIO()
    #errors = codecs.getwriter('utf8')(io.BytesIO())
    p = subprocess.run(args,
                       capture_output=True,
                       #stdout=results, # capture final json output bytes
                       #stderr=errors) # ignore warnings+errors
                       )
    print('returncode')
    print(repr(p.returncode))
    print('raw errors', p.stderr)
    raw = p.stdout
    print('raw result string', raw)
    res = json.loads(raw)
    print('as json', res)

    # set results of map instance
    mapp.georeferenced = timezone.now()
    mapp.layout = res.get('segmentation', None)
    mapp.gcps = res.get('gcps_final', None)
    mapp.transform = res.get('transform_estimation', None)

    # calc footprint
    # ... 

    # save
    mapp.save()

    # redirect
    return redirect('map_view', mapp.pk, 'georef')


