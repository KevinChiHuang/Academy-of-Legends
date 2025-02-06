from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient('mongodb+srv://User:snoopy123@aol.5fchw.mongodb.net/?retryWrites=true&w=majority')
db = client['Capstone']
users_collection = db['users']

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if username already exists
            if users_collection.find_one({'username': username}):
                return render(request, 'accounts/register.html', {'form': form, 'error': 'Username already exists.'})

            # Create a new user document and insert it into the database
            user_data = {
                'username': username,
                'password': password, 
                'is_admin': False,
            }
            result = users_collection.insert_one(user_data)  
            user_id = result.inserted_id  

            request.session['user_id'] = str(user_id)

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Check if the user exists in the database
            user = users_collection.find_one({'username': username})
            if user:
                if user['password'] == password:  
                    request.session['user_id'] = str(user['_id']) 
                    return redirect('home')
                else:
                    return render(request, 'accounts/login.html', {'form': form, 'error': 'Incorrect password.'})
            else:
                return render(request, 'accounts/login.html', {'form': form, 'error': 'User does not exist.'})
    else:
        form = LoginForm() 

    return render(request, 'accounts/login.html', {'form': form})

def home(request):
    if 'user_id' not in request.session:
        return redirect('login') 

    # Fetch the user's details from the database
    user_id = request.session['user_id']  
    user = users_collection.find_one({'_id': ObjectId(user_id)})  

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    # Pass the username to the template
    return render(request, 'home.html', {
        'username': user['username'],
        'is_admin': user.get('is_admin', False) 
    })

def admin(request):
    if 'user_id' not in request.session:
        return redirect('login')  # Redirect to login if not logged in

    # Fetch user details from the database
    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')  # Redirect to login if user not found

    # Check if the user is an admin
    if user.get('is_admin', False):
        return render(request, 'admin.html', {'username': user['username']})  # Render the admin page
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')  # Redirect to home if not an admin 

def logout(request):
    # Clear the session to log out the user
    request.session.flush()
    messages.success(request, 'You have logged out successfully!')
    return redirect('login')  