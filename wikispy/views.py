from django.shortcuts import render
from wikispy.models import Edit

def index(request):
    edits = Edit.objects.filter(wikipedia_id='16702065')
    return render(request, 'index.html', {'edits': edits})
