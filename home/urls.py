from django.urls import path
from . import views
from .views import ResetPasswordView


urlpatterns = [
    path('', views.index, name='home.index'),
    path('about/', views.about, name='home.about'),
    path('my-pokemon/', views.my_pokemon, name='home.my_pokemon'),
    path('marketplace/', views.marketplace, name='home.marketplace'),
    path('signup/', views.signup, name='home.signup'),
    path('login/', views.login, name='home.login'),
    path('logout/', views.logout, name='home.logout'),
    path('get-starters/', views.get_starter_pokemon, name='get_starter_pokemon'),
    path('my-pokemon/<str:name>/', views.pokemon_detail, name='pokemon_detail'),
    path('sell/<str:name>/', views.list_pokemon_for_sale, name='list_pokemon_for_sale'),
    path('login/password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('login/resetpass.html/', views.resetpass, name='accounts.resetpass'),
    path('add-to-cart/<int:pokemon_id>/', views.add_to_cart, name='add_to_cart'),
    path("cart/", views.cart_view, name="cart"),
    path('purchase/', views.purchase, name='purchase'),
    path('marketplace/<str:name>/', views.marketplace_pokemon_detail, name='marketplace_pokemon_detail'),
    path('purchase-pokemon/<int:pokemon_id>/', views.purchase_pokemon, name='purchase_pokemon'),
    path('remove-from-cart/<int:pokemon_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('manage-listed/<int:pokemon_id>/', views.manage_listed_pokemon, name='manage_listed_pokemon'),
    path('notifications/', views.notification_view, name='home.notifications'),
    path('chat/', views.chat_room, name='chat_room'),
]