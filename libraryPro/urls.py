from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'), 
    path('', include('user_management.urls')),
    path('', include('book_catalog.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
