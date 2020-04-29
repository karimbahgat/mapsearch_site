from django.shortcuts import render, redirect
from django.utils import timezone

from .models import Map
from .forms import MapForm

# Create your views here.

def search(request):
    if request.GET:
        dct = request.GET.dict()
        
        if dct['search'].startswith('http'):
            # searching map url
            # check if already exists in db
            matches = Map.objects.filter(url=dct['search'])
            mapp = matches[0] if matches else None
            if mapp is None:
                # download image
                # ...

                # create thumbnail
                # ...
                
                # add to db
                mapp = Map.objects.create(url=dct['search'])
                
                # process map in background
                # ...
                
            # link to the map view
            return redirect('map_view', mapp.pk)
        
        else:
            # search text of existing maps
            # ...
            return render(request, 'templates/search.html', {})
    else:
        return render(request, 'templates/search.html', {})

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


