from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import QueryDict, HttpResponse

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


### 

def map_download_georef(request, pk):
    import subprocess
    import codecs
    import io
    import json

    # find map
    mapp = Map.objects.get(pk=pk)

    # set args
    args = ["C:\Python27-64\python.exe", # python version
            r"C:\Users\kimok\OneDrive\Documents\GitHub\mapsearch_site\mapsearch\warp server.py", # georef program
            mapp.url, # georef url
            mapp.transform] # transform
    #print(args)
    p = subprocess.run(args,
                       capture_output=True,
                       )
    print('returncode')
    print(repr(p.returncode))
    #print('raw errors', p.stderr)
    raw = p.stdout
    #print('raw out', p.stdout)
    res = json.loads(raw)
    res['warping']['image'] = base64.b64decode(res['warping']['image'])
    #fobj = io.BytesIO()
    #fobj.write(res['warping']['image'])
    #res['warping']['image'] = Image.open(fobj)
    #print('as json', res)
    #res['warping']['image'].show()

    # return
    resp = HttpResponse(res['warping']['image'], content_type='image/png') 
    resp['Content-Disposition'] = 'attachment; filename=warped.png'
    return resp

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
    if res.get('segmentation'):
        mapp.layout = json.dumps(res.get('segmentation'))
    if res.get('gcps_final'):
        mapp.gcps = json.dumps(res.get('gcps_final'))
    if res.get('transform_estimation'):
        mapp.transform = json.dumps(res.get('transform_estimation'))

    # calc footprint
    # ... 

    # save
    mapp.save()

    # redirect
    return redirect('map_view', mapp.pk, 'georef')


