from django.shortcuts import render, redirect

from .models import Map

# Create your views here.

def search(request):
    if request.GET:
        dct = request.GET.dict()
        
        if dct['search'].startswith('http'):
            # searching map url
            # check if already exists in db
            matches = Map.objects.filter(url=dct['search'])
            mapp = matches[0] if matches else None
            if 1:#mapp is None:
                # download image
                # ...

                # create thumbnail
                # ...
                
                # add to db
                #mapp = Map.objects.create(url=dct['search'])
                
                # process map in background
                import subprocess
                import codecs
                import io
                import json
                args = ["C:\Python27-64\python.exe", # python version
                        r"C:\Users\kimok\OneDrive\Documents\GitHub\mapsearch_site\mapsearch\taag server.py", # georef program
                        dct['search']] # georef url
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
                js = json.loads(raw)
                print('as json', js)
                
            # link to the map view
            return redirect('map_view', mapp.pk)
        
        else:
            # search text of existing maps
            # ...
            return render(request, 'templates/search.html', {})
    else:
        return render(request, 'templates/search.html', {})

def map_view(request, pk):
    mapp = Map.objects.get(pk=pk)
    return render(request, 'templates/map_view.html', {'map':mapp})




