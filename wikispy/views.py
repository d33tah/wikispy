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
        return error(request, _("rDNS cannot contain %s sign." % '%'))
    edits = get_edits_by_rdns(rdns, wiki_name)
    # Let's see if it has any items...
    try:
        first = next(edits)
    except StopIteration:
        return error(request, _("No results were found."))
    edits_with_first_iter = itertools.chain([first], edits)
    return render(request, 'by_rdns.html', {'edits': edits_with_first_iter})


def error(request, error_str):
    return render(request, 'error.html', {'error': error_str})


def rules(request):
    return render(request, 'rules.html', {})


def privacy(request):
    return render(request, 'privacy.html', {})
