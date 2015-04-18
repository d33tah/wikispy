from django.shortcuts import render
from wikispy.models import get_edits_by_rdns, Wiki
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
import itertools

def index(request):
    rdns = request.POST.get('rdns', None)
    wiki = request.POST.get('wiki', None)
    template_params = {}
    if rdns and wiki:
        return HttpResponseRedirect('/by_rdns/%s/%s' % (wiki, rdns))
    elif request.POST:
        template_params['error'] = _(
            '''Please enter rDNS and Wiki
               or click the "Sample query" link below.'''
        )
    wikis = list(Wiki.objects.all())
    template_params['wikis'] = wikis
    return render(request, 'index.html', template_params)


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
