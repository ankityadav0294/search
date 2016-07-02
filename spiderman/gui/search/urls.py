# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')


from django.conf.urls import url
from views import searchview, autocomplete

app_name = 'search'

urlpatterns = [
    url(r'^$', searchview, name="search"),
    url(r'^getcustomer/$', autocomplete, name="autocomplete"),
]