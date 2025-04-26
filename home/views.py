from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  # assuming your custom form is in forms.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import OwnedPokemon, ListedPokemon
import requests
import random
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


def index(request):
    template_data = {}
    template_data['title'] = 'PokeTrade'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})

def marketplace(request):
    listed = ListedPokemon.objects.all()
    listed_data = []

    for p in listed:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{p.name.lower()}')
        if response.status_code == 200:
            data = response.json()
            listed_data.append({
                'name': data['name'].capitalize(),
                'image': data['sprites']['other']['official-artwork']['front_default'],
                'types': [t['type']['name'] for t in data['types']],
                'seller': p.seller.username,
                'price': p.price
            })

    return render(request, 'home/marketplace.html', {
        'template_data': {
            'title': 'Marketplace',
            'pokemon': listed_data
        }
    })



@login_required(login_url='/login/')
def my_pokemon(request):
    owned = OwnedPokemon.objects.filter(user=request.user)
    pokemon_data = []

    for poke in owned:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke.name.lower()}')
        if response.status_code == 200:
            data = response.json()
            pokemon_data.append({
                'name': data['name'].capitalize(),
                'image': data['sprites']['other']['official-artwork']['front_default'],
                'types': [t['type']['name'] for t in data['types']],
            })

    template_data = {
        'title': 'My PokeMon',
        'pokemon': pokemon_data,
        'can_get_starters': owned.count() == 0
    }

    return render(request, 'home/my_pokemon.html', {'template_data': template_data})

@login_required
def get_starter_pokemon(request):
    if OwnedPokemon.objects.filter(user=request.user).exists():
        return redirect('home.my_pokemon')  # Already has Pokémon

    starter_ids = random.sample(range(1, 151), 3)  # Random IDs from Gen 1
    for poke_id in starter_ids:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke_id}')
        if response.status_code == 200:
            data = response.json()
            OwnedPokemon.objects.create(user=request.user, name=data['name'])

    return redirect('home.my_pokemon')

@login_required
def list_pokemon_for_sale(request, name):
    owned = get_object_or_404(OwnedPokemon, user=request.user, name=name.lower())

    # Optional check: prevent duplicate listings
    if not ListedPokemon.objects.filter(name=name.lower(), seller=request.user).exists():
        ListedPokemon.objects.create(name=owned.name, seller=request.user)

    # Remove from user's collection
    owned.delete()

    return redirect('home.my_pokemon')

@login_required
def pokemon_detail(request, name):
    # Ensure the user owns this Pokémon
    get_object_or_404(OwnedPokemon, user=request.user, name=name.lower())

    # Fetch data from PokeAPI
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{name.lower()}')
    if response.status_code != 200:
        return redirect('home.my_pokemon')

    data = response.json()
    pokemon_info = {
        'name': data['name'].capitalize(),
        'image': data['sprites']['other']['official-artwork']['front_default'],
        'types': [t['type']['name'] for t in data['types']],
        'height': data['height'],
        'weight': data['weight'],
        'base_experience': data['base_experience'],
    }

    return render(request, 'home/pokemon_detail.html', {
        'pokemon': pokemon_info
    })


def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'home/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm()(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home.index')
        else:
            template_data['form'] = form
            return render(request, 'home/signup.html',
                {'template_data': template_data})
        
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'home/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'home/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')
        
@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def resetpass(request):
    return render(request, 'home/accounts/resetpass.html')

class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'home/accounts/password_reset.html'
    email_template_name = 'home/accounts/password_reset_email.html'
    subject_template_name = 'home/accounts/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('accounts.login')