from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home.index'),
    path('about/', views.about, name='home.about'),
    path('my-pokemon/', views.my_pokemon, name='home.my_pokemon'),
    path('marketplace/', views.marketplace, name='home.marketplace'),
    path('signup/', views.signup, name='home.signup'),
    path('login/', views.login, name='home.login'),
    path('logout/', views.logout, name='home.logout'),
]