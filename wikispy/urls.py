from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'wikispy.views.index', name='home'),
    url(r'^by_rdns/(?P<wiki_name>[^/]*)/(?P<rdns>[^/]*)(?:/(?P<offset>[0-9]+))?$',
        'wikispy.views.by_rdns', name='home'),
    url(r'^rules$', 'wikispy.views.rules', name='home'),
    url(r'^privacy$', 'wikispy.views.privacy', name='home'),
)
