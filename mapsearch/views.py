from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import QueryDict, HttpResponse

from .models import Map, Text
from .forms import MapForm

import os
import urllib
import io
import base64
from PIL import Image

# Create your views here.

######################
# GENERAL VIEWS

def search(request):
    if request.GET:
        # get search results
        dct = request.GET.dict()
        
        if dct['search'].startswith('http'):
            # searching url
            if dct['search'].endswith(('.jpg','.png','.gif','.tif')):
                # searching specific map
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
                # searching website
                request.GET = QueryDict(mutable=True)
                request.GET['url'] = dct['search']
                return scrape(request)
        
        else:
            # search text of existing maps
            return search_text(request)
    else:
        # front page search screen
        recent_maps = []
        for m in Map.objects.order_by('-created'): # limit somehow...
            if m.thumbnail:
                thumb = 'data:image/png;base64,' + str(m.thumbnail, 'ascii')
            else:
                thumb = None
            recent_maps.append({'obj':m, 'thumb':thumb})
        return render(request, 'templates/search.html', {'recent_maps':recent_maps})

def search_text(request):
    if request.GET:
        dct = request.GET.dict()
        # text search results screen
        maps = []
        for m in Map.objects.filter(texts__text__contains=dct['search']): # limit somehow...
            if m.thumbnail:
                thumb = 'data:image/png;base64,' + str(m.thumbnail, 'ascii')
            else:
                thumb = None
            maps.append({'obj':m, 'thumb':thumb})
        return render(request, 'templates/search_text.html', {'maps':maps})

def scrape(request):
    if request.GET:
        # landing page for deciding+defining a url scrape
        dct = request.GET.dict()
        root_url = dct['url']
        root_url_dir = os.path.split(root_url)[0]

        # parse website html
        raw = urllib.request.urlopen(root_url).read()
        raw = str(raw)
        elems = raw.replace('>', '<').split('<')

        # loop and identify image links
        urls = []
        for elem in elems:
            if elem.startswith('a href='):
                url = elem.replace('a href=', '').strip('"')

                if url.endswith(('.png','.jpg','.gif','.tif')):
                    # make relative links to absolute
                    if not url.startswith('http'):
                        url = root_url_dir.strip('/') + '/' + url.strip('/')

                    print(url)

                    # skip if already exists
                    #matches = Map.objects.filter(url=url)
                    #if matches
                    #    continue

                    # get filename
                    filename = os.path.split(url)[-1]
                    urls.append((filename,url))

        # send to template for displaying
        return render(request, 'templates/scrape.html', {'urls':urls})

    elif request.POST:
        for url in request.POST.getlist('images'):
            print(url)
            matches = Map.objects.filter(url=url)
            mapp = matches[0] if matches else None
            
            if mapp:
                # update existing
                if request.POST.get('update'):
                    print('updating')
                    map_update_about(request, mapp.pk)
                    map_update_georef(request, mapp.pk)
                
            else:
                # add new
                print('adding') 
                request.GET = QueryDict(mutable=True)
                request.GET['url'] = url
                map_add(request)
                
        return redirect('home')

#############################
# MAP OBJECT

# ADD

def map_add(request):
    dct = request.GET.dict()
    
    # download image
    fobj = io.BytesIO(urllib.request.urlopen(dct['url']).read())
    img = Image.open(fobj)
    print(img)

    # check that doesn't already exist
    matches = Map.objects.filter(url=dct['url'])
    mapp = matches[0] if matches else None
    if mapp:
        # already exists, redirect to map view
        # MAYBE UPDATE INSTEAD? 
        return redirect('map_view', mapp.pk)
    
    # add to db
    w,h = img.size
    mapp = Map.objects.create(url=dct['url'], width=w, height=h)

    # create thumbnail
    max_size = 150
    longest = max(img.size)
    scale = max_size / float(longest)
    size = img.size[0] * scale, img.size[1] * scale
    img.thumbnail(size)
    print(img)
    # encode to png bytestring
    fobj = io.BytesIO()
    img.save(fobj, "PNG")
    raw = base64.b64encode(fobj.getvalue())
    mapp.thumbnail = raw

    # save
    mapp.save()

    # georeference map? 
    map_update_georef(request, mapp.pk)

    # redirect to map view
    return redirect('map_view', mapp.pk)

# UPDATE

def map_update_about(request, pk):
    # add to db
    mapp = Map.objects.get(pk=pk)

    # download image
    fobj = io.BytesIO(urllib.request.urlopen(mapp.url).read())
    img = Image.open(fobj)
    print(img)

    # edit
    w,h = img.size
    mapp.width = w
    mapp.height = h

    # create thumbnail
    max_size = 150
    longest = max(img.size)
    scale = max_size / float(longest)
    size = img.size[0] * scale, img.size[1] * scale
    img.thumbnail(size)
    print(img)
    # encode to png bytestring
    fobj = io.BytesIO()
    img.save(fobj, "PNG")
    raw = base64.b64encode(fobj.getvalue())
    mapp.thumbnail = raw

    # save
    mapp.save()

    # redirect to map view
    return redirect('map_view', mapp.pk)

def map_update_georef(request, pk):
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
        x1,y1,x2,y2 = res['bbox']
        mapp.xmin = min(x1,x2)
        mapp.ymin = min(y1,y2)
        mapp.xmax = max(x1,x2)
        mapp.ymax = max(y1,y2)

    # calc footprint
    # ...

    # save map
    mapp.save()

    # then texts

    # delete previous texts
    for text in mapp.texts.all():
        text.delete()

    # add new texts
    if res.get('text_recognition'):
        for feat in res.get('text_recognition')['features']:
            props = feat['properties']
            vals = {'map':mapp,
                    'text':props['text_clean'],
                    'color':json.dumps(list(map(int, props['color']))),
                    'fontheight':props['fontheight'],
                    'geom':json.dumps(feat['geometry']),
                    }
            text = Text(**vals)
            text.save()

    # redirect
    return redirect('map_view', mapp.pk, 'georef')

# VIEW

def map_view(request, pk, tab=None):
    mapp = Map.objects.get(pk=pk)
    mappform = MapForm(instance=mapp)
    for t in mapp.texts.all():
        print(t.text)
    tab = tab or 'about'
    return render(request, 'templates/map_view_{}.html'.format(tab), {'map':mapp, 'form':mappform, 'tab':tab})

# DOWNLOAD

def map_download_georef(request, pk):
    import subprocess
    import codecs
    import io
    import json

    # find map
    mapp = Map.objects.get(pk=pk)

    # set args
    print(request.GET.dict())
    args = ["C:\Python27-64\python.exe", # python version
            r"C:\Users\kimok\OneDrive\Documents\GitHub\mapsearch_site\mapsearch\warp server.py", # georef program
            mapp.url, # georef url
            mapp.transform] # transform
    if request.GET.get('maxdim'):
        args.append(request.GET.get('maxdim'))
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

def map_download_thumb(request, pk):
    import subprocess
    import codecs
    import io
    import json

    # find map
    mapp = Map.objects.get(pk=pk)

    # get thumbnail
    thumb = base64.b64decode(mapp.thumbnail)

    # return
    resp = HttpResponse(thumb, content_type='image/png') 
    resp['Content-Disposition'] = 'attachment; filename=thumbnail.png'
    return resp



