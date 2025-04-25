from django.contrib import admin
from .models import OwnedPokemon, ListedPokemon

admin.site.register(OwnedPokemon)
admin.site.register(ListedPokemon)