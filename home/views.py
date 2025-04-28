from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm  

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import OwnedPokemon, ListedPokemon
from .models import Notification
import requests
import random
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect
from .models import ListedPokemon
from .forms import ListPokemonForm

def index(request):
    template_data = {}
    template_data['title'] = 'PokeTrade'
    return render(request, 'home/index.html', {'template_data': template_data})

def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request, 'home/about.html', {'template_data': template_data})

def marketplace(request):
    query = request.GET.get('q')  # Get search input from URL if exists

    if query:
        listed = ListedPokemon.objects.filter(name__icontains=query)
    else:
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
            'pokemon': listed_data,
            'search_query': query or ''
        }
    })



@login_required(login_url='/login/')
def my_pokemon(request):
    owned = OwnedPokemon.objects.filter(user=request.user)
    listed = ListedPokemon.objects.filter(seller=request.user)

    owned_pokemon_data = []
    listed_pokemon_data = []

    # Owned Pokémon
    for poke in owned:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke.name.lower()}')
        if response.status_code == 200:
            data = response.json()
            owned_pokemon_data.append({
                'name': data['name'].capitalize(),
                'image': data['sprites']['other']['official-artwork']['front_default'],
                'types': [t['type']['name'] for t in data['types']],
            })

    # Listed Pokémon
    for poke in listed:
        response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke.name.lower()}')
        if response.status_code == 200:
            data = response.json()
            listed_pokemon_data.append({
                'id': poke.id,
                'name': data['name'].capitalize(),
                'image': data['sprites']['other']['official-artwork']['front_default'],
                'types': [t['type']['name'] for t in data['types']],
                'price': poke.price,
            })

    template_data = {
        'title': 'My PokeMon',
        'owned_pokemon': owned_pokemon_data,
        'listed_pokemon': listed_pokemon_data,
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

    if request.method == 'POST':
        price = request.POST.get('price')
        if price and price.isdigit():
            price = int(price)
            if price > 0:
                ListedPokemon.objects.create(name=owned.name, seller=request.user, price=price)

                notification_message = f'You have listed {name} for sell at price {price}!'
                Notification.objects.create(user=request.user, message=notification_message)
                
                owned.delete()
                return redirect('home.my_pokemon')
        # Optional: handle error if price is invalid (you could add a message)
    
    # If not POST or invalid POST, just redirect
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
        form = CustomUserCreationForm(request.POST)
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

@login_required
def add_to_cart(request, pokemon_id):
    cart = request.session.get('cart', [])

    # Find the Pokémon from ListedPokemon
    poke = get_object_or_404(ListedPokemon, id=pokemon_id)

    # Fetch the image from PokeAPI
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke.name.lower()}')
    if response.status_code == 200:
        data = response.json()
        image_url = data['sprites']['other']['official-artwork']['front_default']
    else:
        image_url = ''  # fallback in case PokeAPI fails

    # Store FULL Pokémon info
    poke_data = {
        'id': poke.id,
        'name': poke.name.capitalize(),
        'price': poke.price,
        'image': image_url,
    }

    # Avoid duplicate entries
    if poke_data not in cart:
        cart.append(poke_data)
        request.session['cart'] = cart

    return redirect('cart')

def cart_view(request):
    cart_pokemon = request.session.get('cart', [])
    return render(request, 'home/cart.html', {'cart_pokemon': cart_pokemon})

@login_required
def purchase_pokemon(request, pokemon_id):
    if request.method == 'POST':
        poke = get_object_or_404(ListedPokemon, id=pokemon_id)
        
        # Add to user's owned Pokémon
        OwnedPokemon.objects.create(user=request.user, name=poke.name)

        # Remove from marketplace
        poke.delete()

        # Remove from cart session
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['id'] != pokemon_id]
        request.session['cart'] = cart

        notification_message = f'You have successfully purchased {poke.name}!'
        Notification.objects.create(user=request.user, message=notification_message)

        return redirect('home.my_pokemon')

def purchase(request):
    request.session['cart'] = []
    return render(request, 'purchase_success.html')

@login_required
def remove_from_cart(request, pokemon_id):
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['id'] != pokemon_id]
        request.session['cart'] = cart

        return redirect('cart')

def marketplace_pokemon_detail(request, name):
    # Find the listed Pokémon
    poke = get_object_or_404(ListedPokemon, name=name.lower())

    # Fetch extra data from PokeAPI
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{name.lower()}')
    if response.status_code != 200:
        return redirect('home.marketplace')

    data = response.json()
    pokemon_info = {
        'id': poke.id,
        'name': data['name'].capitalize(),
        'image': data['sprites']['other']['official-artwork']['front_default'],
        'types': [t['type']['name'] for t in data['types']],
        'height': data['height'],
        'weight': data['weight'],
        'base_experience': data['base_experience'],
        'seller': poke.seller.username,
        'price': poke.price,
    }

    return render(request, 'home/marketplace_pokemon_detail.html', {'pokemon': pokemon_info})

@login_required
def manage_listed_pokemon(request, pokemon_id):
    poke = get_object_or_404(ListedPokemon, id=pokemon_id, seller=request.user)

    # Fetch full Pokémon details
    response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{poke.name.lower()}')
    if response.status_code == 200:
        data = response.json()
        pokemon_info = {
            'image': data['sprites']['other']['official-artwork']['front_default'],
            'types': [t['type']['name'] for t in data['types']],
            'height': data['height'],
            'weight': data['weight'],
            'base_experience': data['base_experience'],
        }
    else:
        pokemon_info = {
            'image': '',
            'types': [],
            'height': '',
            'weight': '',
            'base_experience': '',
        }

    if request.method == 'POST':
        if 'update_price' in request.POST:
            new_price = request.POST.get('price')
            if new_price and new_price.isdigit() and int(new_price) > 0:
                poke.price = int(new_price)
                poke.save()
                notification_message = f'You have updated the price of {poke.name}!'
                Notification.objects.create(user=request.user, message=notification_message)
                return redirect('home.my_pokemon')

        elif 'remove_listing' in request.POST:
            OwnedPokemon.objects.create(user=request.user, name=poke.name)
            notification_message = f'You have successfully purchased {poke.name}!'
            Notification.objects.create(user=request.user, message=notification_message)
            poke.delete()
            return redirect('home.my_pokemon')

    return render(request, 'home/manage_listed_pokemon.html', {'pokemon': poke, 'pokemon_info': pokemon_info})

def notification_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    return render(request, 'home/notifications.html', {'notifications': notifications})

from django.shortcuts import render
from .models import Notification

def home_index(request):
    notifications = []
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]

    return render(request, 'home/index.html', {
        'notifications': notifications,
        'user': request.user  # Pass the user explicitly to the template
    })

from django.shortcuts import render
from django.contrib.auth.models import User


def all_users(request):
    # Fetch all users except the currently logged-in user
    users = User.objects.exclude(id=request.user.id)

    # Fetch the form for the page
    form = CustomUserCreationForm()

    # Return the template with users and form data
    return render(request, 'home/pokemon_detail.html', {
        'users': users,
        'form': form
    })
from django.shortcuts import get_object_or_404, redirect
from .models import OwnedPokemon, User, Notification
from django.contrib.auth.decorators import login_required

@login_required
def transfer_pokemon(request):
    if request.method == 'POST':
        # Get the selected user and Pokémon to transfer
        selected_user_id = request.POST.get('user')  # User selected in the form
        pokemon_id = request.POST.get('pokemon_id')  # Pokémon being transferred

        # Fetch the selected user and the Pokémon to transfer
        selected_user = get_object_or_404(User, id=selected_user_id)
        pokemon_to_transfer = get_object_or_404(OwnedPokemon, id=pokemon_id, user=request.user)

        # Transfer the Pokémon
        pokemon_to_transfer.user = selected_user
        pokemon_to_transfer.save()

        # Notify both users about the transfer
        notification_message = f'{request.user.username} has transferred {pokemon_to_transfer.name} to you.'
        Notification.objects.create(user=selected_user, message=notification_message)

        # Send a notification to the sender as well
        notification_message = f'You have successfully transferred {pokemon_to_transfer.name} to {selected_user.username}.'
        Notification.objects.create(user=request.user, message=notification_message)

        return redirect('home.my_pokemon')  # Redirect back to the user's Pokémon page

    else:
        # If the request is not POST, simply show the transfer form
        users = User.objects.exclude(id=request.user.id)  # Fetch all users except the current one
        pokemon_to_transfer = OwnedPokemon.objects.filter(user=request.user)

        return render(request, 'home/transfer_pokemon.html', {
            'users': users,
            'pokemon_to_transfer': pokemon_to_transfer
        })
