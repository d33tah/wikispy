from django.shortcuts import render
from wikispy.models import Edit, query_scans_table
from django.http import HttpResponseRedirect, HttpResponse


def index(request):
    return HttpResponseRedirect('/by_rdns/plwiki/.gov.pl')

def by_rdns(request, wiki_name, rdns):
    if not rdns.startswith('.'):
        rdns = '.' + rdns
    if '%' in rdns:
        return error(request, "rDNS cannot contain % sign.")
    edits = Edit.objects.select_related()
    edits = edits.filter(rdns__rdns__rightanchored='%' + rdns)
    if query_scans_table(edits.query, 'wikispy_edit'):
        return error(request, "The query is too big.")
    return render(request, 'index.html', {'edits': edits})

def error(request, error_str):
    return HttpResponse(error_str)

def rules(request):
    return render(request, 'rules.html', {})

def privacy(request):
    return render(request, 'privacy.html', {})
