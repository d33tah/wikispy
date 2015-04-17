from django.shortcuts import render
from wikispy.models import get_edits_by_rdns
from django.http import HttpResponseRedirect, HttpResponse


def index(request):
    return HttpResponseRedirect('/by_rdns/plwiki/.gov.pl')


def by_rdns(request, wiki_name, rdns):
    if not rdns.startswith('.'):
        rdns = '.' + rdns
    if '%' in rdns:
        return error(request, "rDNS cannot contain % sign.")
    edits = get_edits_by_rdns(rdns, wiki_name)
    return render(request, 'index.html', {'edits': edits})


def error(request, error_str):
    return HttpResponse(error_str)


def rules(request):
    return render(request, 'rules.html', {})


def privacy(request):
    return render(request, 'privacy.html', {})
