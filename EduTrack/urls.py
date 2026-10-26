from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Administrator/', include('Administrator.urls')),
    path('', include('Guest.urls')),
    path('Student/', include('Student.urls')),
    path('Faculty/', include('Faculty.urls')),
    path('Company/', include('Company.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
