from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('ea.views',
    url(r'^$', 'index'),
    url(r'^record$', 'record'),
    url(r'^demosurvey$', 'demosurvey'),
    url(r'^control/(tut)$', 'control'),
    url(r'^control()$', 'control'),
    url(r'^adaptive/(tut)$', 'adaptive'),
    url(r'^adaptive()$', 'adaptive'),
    url(r'^survey_(\w+)$', 'survey'),
    url(r'^finalsurvey$', 'finalsurvey'),
    url(r'^done$', 'done'),
)
