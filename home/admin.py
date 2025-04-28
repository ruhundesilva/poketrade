from django.contrib import admin
from .models import OwnedPokemon, ListedPokemon, Notification

admin.site.register(OwnedPokemon)
admin.site.register(ListedPokemon)
admin.site.register(Notification)