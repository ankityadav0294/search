# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')


from django.conf.urls import url
from . import views

app_name = 'search'

urlpatterns = [
    url(r'', views.searchview, name="search")
]