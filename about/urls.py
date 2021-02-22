from django.urls import path

from . import views

app_name = 'about'

urlpatterns = [
    path("author/", views.StaticPageAuthor.as_view(), name='author'),
    path("tech/", views.StaticPageTech.as_view(), name='tech'),
]
