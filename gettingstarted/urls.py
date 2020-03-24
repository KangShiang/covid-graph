from django.urls import path, include

from django.contrib import admin
from django.conf.urls.static import static
import gettingstarted.settings as settings

admin.autodiscover()

import hello.views
import covidstats.views

# To add a new path, first import the app:
# import blog
#
# Then add the new path:
# path('blog/', blog.urls, name="blog")
#
# Learn more here: https://docs.djangoproject.com/en/2.1/topics/http/urls/

urlpatterns = [
    path("", hello.views.index, name="index"),
    path("db/", hello.views.db, name="db"),
    path("stats/", covidstats.views.get2, name="covdistats"),
    path("stats", covidstats.views.get2, name="covdistats"),
    path("demo/", covidstats.views.demo, name="demo"),
    path("admin/", admin.site.urls),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
