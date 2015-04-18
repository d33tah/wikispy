from django.shortcuts import render
from wikispy.models import get_edits_by_rdns
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
import itertools

def index(request):
    return HttpResponseRedirect('/by_rdns/plwiki/.gov.pl')


def by_rdns(request, wiki_name, rdns):
    if not rdns.startswith('.'):
        rdns = '.' + rdns
    if '%' in rdns:
        return error(request, _("rDNS cannot contain % sign."))
    edits = get_edits_by_rdns(rdns, wiki_name)
    # Let's see if it has any items...
    try:
        first = next(edits)
    except StopIteration:
        return error(request, _("No results were found."))
    return render(request, 'by_rdns.html',
                  {'edits': itertools.chain([first], edits)})


def error(request, error_str):
    return render(request, 'error.html', {'error': error_str})


def rules(request):
    return render(request, 'rules.html', {})


def privacy(request):
    return render(request, 'privacy.html', {})
