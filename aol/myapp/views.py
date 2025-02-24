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
                'gold': 0,
                'exp': 0,
                'hp': 0
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
        'exp': user['exp'],
        'gold': user['gold'],
        'hp': user['hp'],
        'is_admin': user.get('is_admin', False) 
    })

def admin(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    if user.get('is_admin', False):
        students = list(users_collection.find({}, {"password": 0}))  # Exclude passwords
        return render(request, 'admin.html', {'username': user['username'], 'students': students})
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

def logout(request):
    # Clear the session to log out the user
    request.session.flush()
    messages.success(request, 'You have logged out successfully!')
    return redirect('login')  

def shop(request):
    if 'user_id' not in request.session:
        return redirect('login') 

    # Fetch the user's details from the database
    user_id = request.session['user_id']  
    user = users_collection.find_one({'_id': ObjectId(user_id)})  

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    # Pass the username to the template
    return render(request, 'shop.html', {
        'username': user['username'],
        'is_admin': user.get('is_admin', False) 
    })


def board(request):
    if 'user_id' not in request.session:
        return redirect('login') 

    # Fetch the current user's details
    user_id = request.session['user_id']  
    user = users_collection.find_one({'_id': ObjectId(user_id)})  

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    # Fetch all students, excluding passwords, sorted by exp in descending order
    students = list(
        users_collection.find({}, {"password": 0}).sort("exp", -1)
    )
    
    return render(request, 'board.html', {
        'username': user['username'],
        'is_admin': user.get('is_admin', False),
        'students': students,
    })

def add(request):
    if 'user_id' not in request.session:
        return redirect('login') 

    # Fetch the user's details from the database
    user_id = request.session['user_id']  
    user = users_collection.find_one({'_id': ObjectId(user_id)})  

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    # Pass the username to the template
    return render(request, 'add.html', {
        'username': user['username'],
        'is_admin': user.get('is_admin', False) 
    })

def settings(request):
    # if 'user_id' not in request.session:
    #     return redirect('login') 

    # # Fetch the user's details from the database
    # user_id = request.session['user_id']  
    # user = users_collection.find_one({'_id': ObjectId(user_id)})  

    # if not user:
    #     messages.error(request, "User not found. Please log in again.")
    #     return redirect('login')

    # Pass the username to the template
    return render(request, 'settings.html', {
        # 'username': user['username'],
        # 'is_admin': user.get('is_admin', False) 
    })


def student_list(request):
    students = list(users_collection.find({}, {"password": 0}))  # Exclude passwords for security
    return render(request, 'admin.html','board.html', {'students': students})
    

def update_student(request):
    """Handles updating gold and hearts."""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        field = request.POST.get("field")  # 'gold' or 'hp'
        action = request.POST.get("action")  # 'add' or 'minus'

        user = users_collection.find_one({"_id": ObjectId(user_id)})

        if user:
            new_value = user[field] + 1 if action == "add" else max(0, user[field] - 1)
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {field: new_value}})
            return JsonResponse({"success": True, field: new_value})

    return JsonResponse({"success": False})

def delete_student(request):
    """Handles deleting a user."""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        users_collection.delete_one({"_id": ObjectId(user_id)})
        return JsonResponse({"success": True})

    return JsonResponse({"success": False})