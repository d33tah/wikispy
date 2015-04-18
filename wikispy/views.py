from django.shortcuts import render
from wikispy.models import get_edits_by_rdns
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
import itertools

def index(request):
    return render(request, 'index.html', {})


def by_rdns(request, wiki_name, rdns, offset, pagesize):

    if pagesize is None:
        pagesize = 50
    if offset is None:
        offset = 0
    offset, pagesize = int(offset), int(pagesize)

    if not rdns.startswith('.'):
        rdns = '.' + rdns

    if '%' in rdns:
        return error(request, _("rDNS cannot contain %s sign." % '%'))

    edits = get_edits_by_rdns(rdns, wiki_name, offset, pagesize)

    # Let's see if it has any items...
    try:
        first = next(edits)
    except StopIteration:
        return error(request, _("No results were found."))

    edits_with_first_iter = itertools.chain([first], edits)

    return render(request, 'by_rdns.html', {
        'edits': edits_with_first_iter,
        'wiki_name': wiki_name,
        'rdns': rdns,
        'offset': offset,
        'skip_labels': pagesize == 0,
    })


def error(request, error_str):
    return render(request, 'error.html', {'error': error_str})


def rules(request):
    return render(request, 'rules.html', {})


def privacy(request):
    return render(request, 'privacy.html', {})
