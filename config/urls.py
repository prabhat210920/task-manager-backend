urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
