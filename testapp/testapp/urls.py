from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    # url(r'^$', 'testapp.views.home', name='home'),
    # url(r'^testapp/', include('testapp.foo.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
