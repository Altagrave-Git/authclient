from django.contrib import admin
from django.urls import path
from users import views
from django.shortcuts import render

'''
We'll define basic views here to act as client application pages.
Thesse will retrieve data only through FetchAPI requests
which is why we're keeping it seperate from the server's API views.
'''

def home_view(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Client views
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    # API views
    path('authorize/', views.authorize, name='authorize'),
]