from django.shortcuts import render
from wikispy.models import get_edits, Wiki
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.translation import ugettext as _
import itertools

def index(request):

    template_params = {}
    rdns = request.POST.get('rdns', None)
    wiki = request.POST.get('wiki', None)
    startip = request.POST.get('startip', None)
    endip = request.POST.get('endip', None)

    if rdns and wiki:
        return HttpResponseRedirect('/by_rdns/%s/%s' % (wiki, rdns))
    if startip and endip and wiki:
        return HttpResponseRedirect('/by_ip/%s/%s/%s' % (wiki,
                                    startip, endip))
    else:
        if request.POST:
            template_params['error'] = _(
                '''Please fill out the required fields
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

    try:
        edits = get_edits(wiki_name, offset, pagesize, rdns=rdns)
    except ValueError:
        return error(request, _("The query is too big."))

    # Let's see if it has any items...
    try:
        first = next(edits)
    except StopIteration:
        return error(request, _("No results were found."))

    edits_with_first_iter = itertools.chain([first], edits)

    return render(request, 'display_edits.html', {
        'edits': edits_with_first_iter,
        'wiki_name': wiki_name,
        'rdns': rdns,
        'offset': offset,
        'pagesize': pagesize,
        'skip_labels': pagesize == 0,
        'baseurl' : '/by_rdns/' + wiki_name + '/' + rdns,
        'baserandomurl' : '/by_rdns_random/' + wiki_name + '/' + rdns,
    })

def by_ip(request, wiki_name, startip, endip, offset, pagesize):

    if pagesize is None:
        pagesize = 50
    if offset is None:
        offset = 0
    offset, pagesize = int(offset), int(pagesize)

    edits = get_edits(wiki_name, offset, pagesize, startip=startip,
                      endip=endip)

    # Let's see if it has any items...
    try:
        first = next(edits)
    except StopIteration:
        return error(request, _("No results were found."))

    edits_with_first_iter = itertools.chain([first], edits)

    return render(request, 'display_edits.html', {
        'edits': edits_with_first_iter,
        'wiki_name': wiki_name,
        'startip': startip,
        'endip': endip,
        'offset': offset,
        'pagesize': pagesize,
        'baseurl' : '/by_ip/' + wiki_name + '/' + startip + '/' + endip,
        'skip_labels': pagesize == 0,
    })

def error(request, error_str):
    return render(request, 'error.html', {'error': error_str})


def rules(request):
    return render(request, 'rules.html', {})


def privacy(request):
    return render(request, 'privacy.html', {})

def info(request):
    return render(request, 'info.html', {})

def view_edit(request, wiki_name, edit_number):
    wiki = Wiki.objects.filter(name=wiki_name)[0]
    url = "https://"
    if wiki.language:
        url += "%s." % wiki.language
    url += "%s/wiki/Special:MobileDiff/%s" % (wiki.domain, edit_number)
    return HttpResponseRedirect(url)


def by_rdns_random(request, wiki_name, rdns):

    if not rdns.startswith('.'):
        rdns = '.' + rdns

    if '%' in rdns:
        return error(request, _("rDNS cannot contain %s sign." % '%'))

    edits = list(get_edits(wiki_name, random=True, rdns=rdns))
    if len(edits) == 0:
        return error(request, _("No edits found."))
    edit = edits[0]
    language = edit['language'] + '.' if edit['language'] else ''
    url = "https://%s%s/w/index.php?diff=prev&oldid=%s" % (language,
        edit['domain'], edit['wikipedia_edit_id'])
    return render(request, 'by_rdns_random.html', {
        'edit': edit,
        'url': url,
        'rdns': rdns,
        'wiki_name': wiki_name,
        'wikipedia_edit_id': edit['wikipedia_edit_id'],
    })

def by_rdns_single(request, wiki_name, wikipedia_edit_id):

    edits = list(get_edits(wiki_name, random=True,
                           wikipedia_edit_id=wikipedia_edit_id))
    if len(edits) == 0:
        return error(request, _("No edits found."))
    edit = edits[0]
    language = edit['language'] + '.' if edit['language'] else ''
    url = "https://%s%s/w/index.php?diff=prev&oldid=%s" % (language,
        edit['domain'], edit['wikipedia_edit_id'])
    return render(request, 'by_rdns_random.html', {
        'edit': edit,
        'url': url,
        'wiki_name': wiki_name,
        'wikipedia_edit_id': edit['wikipedia_edit_id'],
    })
