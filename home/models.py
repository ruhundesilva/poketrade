from django.db import models
from django.contrib.auth.models import User

class OwnedPokemon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Store the Pokémon name, e.g. "pikachu"

    def __str__(self):
        return f"{self.user.username} owns {self.name}"


class ListedPokemon(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.PositiveIntegerField(default=100)  # Example price field

    def __str__(self):
        return f"{self.name} listed by {self.seller.username}"