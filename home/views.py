from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from .models import OwnedPokemon
import requests
import random


def index(request):
    template_data = {}
    template_data['title'] = 'PokeTrade'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})

def marketplace(request):
    template_data = {}
    template_data['title'] = 'Marketplace'
    return render(request, 'home/marketplace.html', {'template_data': template_data})

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
def buy_pokemon(request, pokemon_name):
    OwnedPokemon.objects.create(user=request.user, name=pokemon_name.lower())
    return redirect('home.my_pokemon')

@login_required
def sell_pokemon(request, pokemon_name):
    OwnedPokemon.objects.filter(user=request.user, name=pokemon_name.lower()).delete()
    return redirect('home.my_pokemon')


def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = UserCreationForm()
        return render(request, 'home/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = UserCreationForm(request.POST)
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