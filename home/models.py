from django.db import models
from django.contrib.auth.models import User
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


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message[:30]  # Just show a short part of the message
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}..."