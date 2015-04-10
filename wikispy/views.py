from django.shortcuts import render
from wikispy.models import Edit

def index(request):
    edits = Edit.objects.all()[:10]
    return render(request, 'index.html', {'edits': edits})
