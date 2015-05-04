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

def peek_results(edits, pagesize):
    """Check if "edits" actually contains any results. Returns "edits" after
       iterating over it (the original might have some elements removed) and
       a boolean value telling whether we should display a link to the new
       page."""
    taken = []
    try:
        taken += [next(edits)]
    except StopIteration:
        return None, False
    if pagesize != 0:
        has_next_page = True
        i = 0
        while True:
            try:
                taken += [next(edits)]
            except StopIteration:
                has_next_page = False
                break
            i += 1
            if i >= pagesize:
                break
    else:
        has_next_page = False
    iterator = itertools.islice(itertools.chain(taken, edits), 0, pagesize)
    return iterator, has_next_page


def validate_pagesize_and_offset(f):
    """A function decorator that sanitizes the pagesize and offset view
       variables."""
    def new_f(*args, **kwargs):
        if kwargs.get('pagesize') is None:
            kwargs['pagesize'] = 50
        else:
            kwargs['pagesize'] = int(kwargs['pagesize'])
        if kwargs.get('offset') is None:
            kwargs['offset'] = 0
        else:
            kwargs['offset'] = int(kwargs['offset'])
        return f(*args, **kwargs)
    return new_f

def validate_rdns(f):
    """A function decorator that sanitizes the rDNS string."""
    def new_f(*args, **kwargs):
        rdns = kwargs['rdns']
        if not rdns.startswith('.'):
            kwargs['rdns'] = '.' + rdns

        if '%' in rdns:
            return error(request, _("rDNS cannot contain %s sign." % '%'))

        return f(*args, **kwargs)
    return new_f

@validate_rdns
@validate_pagesize_and_offset
def by_rdns(request, wiki_name, rdns, offset, pagesize):

    try:
        edits = get_edits(wiki_name, offset, pagesize + 1, rdns=rdns)
    except ValueError:
        return error(request, _("The query is too big."))

    edits_checked, has_next_page = peek_results(edits, pagesize)
    if edits_checked is None:
        return error(request, _("No results were found."))

    return render(request, 'display_edits.html', {
        'has_next_page': has_next_page,
        'edits': edits_checked,
        'wiki_name': wiki_name,
        'rdns': rdns,
        'offset': offset,
        'pagesize': pagesize,
        'skip_labels': pagesize == 0,
        'baseurl' : '/by_rdns/' + wiki_name + '/' + rdns,
        'baserandomurl' : '/by_rdns_random/' + wiki_name + '/' + rdns,
    })

@validate_pagesize_and_offset
def by_ip(request, wiki_name, startip, endip, offset, pagesize):

    edits = get_edits(wiki_name, offset, pagesize + 1, startip=startip,
                      endip=endip)

    edits_checked, has_next_page = peek_results(edits, pagesize)
    if edits_checked is None:
        return error(request, _("No results were found."))

    return render(request, 'display_edits.html', {
        'has_next_page': has_next_page,
        'edits': edits_checked,
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


@validate_rdns
def by_rdns_random(request, wiki_name, rdns):

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
