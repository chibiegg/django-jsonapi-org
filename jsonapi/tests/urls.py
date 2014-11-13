from django.conf.urls import patterns, include, url
from jsonapi.tests.views import prefectures, model_prefectures


urlpatterns = patterns('',
    (r'^prefectures/', include(prefectures.urls)),
    (r'^models/prefectures/', include(model_prefectures.urls)),
)
