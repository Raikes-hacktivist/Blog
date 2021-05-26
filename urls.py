from django.urls import path
from . import views
from .feeds import LatestPostsFeed


app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail, 
         name='post_detail'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    path('confirm/', views.confirm, name='confirm'),
    path('delete/', views.delete, name='delete'),
    path('search/', views.post_search, name='post_search'),
    path('self/', views.self, name='self'),
    



]
