from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .forms import RegisterForm, LoginForm
from django.contrib import messages
from pymongo import MongoClient
from django.contrib.auth.hashers import make_password, check_password
from bson.objectid import ObjectId
import gridfs
import json

client = MongoClient('mongodb+srv://User:snoopy123@aol.5fchw.mongodb.net/?retryWrites=true&w=majority')
db = client['Capstone']
users_collection = db['users']
rewards_collection = db['rewards']
fs = gridfs.GridFS(db) 

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data["confirm_password"]

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect("login")

            # Check if username already exists
            if users_collection.find_one({'username': username}):
                return render(request, 'accounts/login.html', {'form': form, 'error': 'Username already exists.'})

            # Hash the password before storing
            hashed_password = make_password(password)

            user_data = {
                'username': username,
                'password': hashed_password,  
                'is_admin': False,
                'gold': 0,
                'exp': 0,
                'hp': 0
            }
            result = users_collection.insert_one(user_data)
            user_id = result.inserted_id

            request.session['user_id'] = str(user_id)
            messages.success(request, "Registration successful! You can now log in.")

            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/login.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = users_collection.find_one({'username': username})

            if user and check_password(password, user['password']):  # Check hashed password
                request.session['user_id'] = str(user['_id'])
                request.session['is_admin'] = user.get('is_admin', False)  # Store admin status

                messages.success(request, f"Welcome, {username}!")

                if user.get('is_admin', False):  # If user is an admin, redirect to admin page
                    return redirect('admin')  # Make sure 'admin_page' is mapped to `admin.html`
                else:
                    return redirect('home')

            else:
                messages.error(request, "Invalid username or password.")

    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def home(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    inventory = user.get('inventory', [])
    
    students = list(users_collection.find({}).sort("exp", -1))
    ranking = {str(student['_id']): index + 1 for index, student in enumerate(students)}
    user_rank = ranking.get(str(user['_id']), "N/A")

    return render(request, 'home.html', {
        'username': user['username'],
        'is_admin': user.get('is_admin', False),
        'gold': user.get('gold', 0),
        'exp': user.get('exp', 0),
        'hp': user.get('hp', 0),
        'rank': user_rank,
        'inventory': inventory
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
        students = list(users_collection.find({}, {"password": 0}))
        # Convert ObjectId to string
        for student in students:
            student['id'] = str(student['_id'])
            del student['_id']
        return render(request, 'admin.html', {
            'username': user['username'],
            'students': students,
            'is_admin': True,
        })
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('home')

def logout(request):
    request.session.flush()
    messages.success(request, 'You have logged out successfully!')
    return redirect('login')  

def shop(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    rewards = list(rewards_collection.find({}))
    for reward in rewards:
        reward['id'] = str(reward['_id'])

    return render(request, 'shop.html', {
        'username': user['username'],
        'gold': user['gold'],
        'is_admin': user.get('is_admin', False),
        'rewards': rewards,
    })

def board(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    students = list(users_collection.find({}, {"password": 0}).sort("exp", -1))
    # Convert _id to string for each student
    for student in students:
        student['id'] = str(student.pop('_id'))
    
    return render(request, 'board.html', {
        'username': user['username'],
        'is_admin': user.get('is_admin', False),
        'students': students,
    })

def add(request):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    if not user.get('is_admin', False):  # Prevent non-admins from accessing
        messages.error(request, "You do not have permission to access this page.")
        return redirect('board')

    if request.method == "POST":
        item_name = request.POST.get("item")
        gold = request.POST.get("gold")
        description = request.POST.get("description")
        image_file = request.FILES.get("upload")

        image_id = None
        if image_file:
            image_id = fs.put(image_file.read(), filename=image_file.name, content_type=image_file.content_type)

        reward = {
            "item": item_name,
            "gold": gold,
            "description": description,
            "image_id": str(image_id) if image_id else None
        }
        db.rewards.insert_one(reward)

        return redirect("shop")

    return render(request, "add.html", {"is_admin": user.get("is_admin", False)})


def settings(request):
    return render(request, 'settings.html')

def student_list(request):
    students = list(users_collection.find({}, {"password": 0}))
    # Rename _id to id
    for student in students:
        student['id'] = str(student.pop('_id'))
    return render(request, 'admin.html', {'students': students})

def update_student(request):
    """Handles updating gold and hearts."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)
        
        user_id = data.get("user_id")
        field = data.get("field")  # 'gold' or 'hp'
        action = data.get("action")  # 'add' or 'minus'
        
        if not user_id or not field or not action:
            return JsonResponse({"success": False, "error": "Missing parameters."}, status=400)

        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            return JsonResponse({"success": False, "error": "Invalid user id."}, status=400)

        if user:
            current_value = user.get(field, 0)
            
            # Modified section for gold +25
            if field == 'gold' and action == 'add':
                new_value = current_value + 25
            else:
                # Original logic for other operations
                if action == "add":
                    new_value = current_value + 1
                else:
                    new_value = max(0, current_value - 1)
            
            users_collection.update_one(
                {"_id": ObjectId(user_id)}, 
                {"$set": {field: new_value}}
            )
            return JsonResponse({"success": True, field: new_value})
    
    return JsonResponse({"success": False})

# UPDATED: Process JSON from request.body for deletion too.
def delete_student(request):
    """Handles deleting a user."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)
        user_id = data.get("user_id")
        if user_id:
            try:
                users_collection.delete_one({"_id": ObjectId(user_id)})
            except Exception as e:
                return JsonResponse({"success": False, "error": "Invalid user id."}, status=400)
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        file_id = fs.put(image_file.read(), filename=image_file.name, content_type=image_file.content_type)
        return JsonResponse({"message": "File uploaded successfully", "file_id": str(file_id)})
    return JsonResponse({"error": "No file uploaded"}, status=400)

def get_image(request, image_id):
    try:
        file = fs.get(ObjectId(image_id))
        return HttpResponse(file.read(), content_type=file.content_type)
    except gridfs.errors.NoFile:
        return HttpResponse("File not found", status=404)

def buy_reward(request, reward_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user:
        messages.error(request, "User not found. Please log in again.")
        return redirect('login')

    reward = rewards_collection.find_one({'_id': ObjectId(reward_id)})

    if not reward:
        messages.error(request, "Reward not found.")
        return redirect('shop')

    user_gold = int(user['gold'])
    reward_price = int(reward['gold'])

    if user_gold < reward_price:
        messages.error(request, "Not enough gold!")
        return redirect('shop')

    new_gold = user_gold - reward_price
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$push': {'inventory': {
            'item_id': str(reward['_id']),  # Store reward ID
            'item': reward['item'],
            'description': reward.get('description', ''),
            'image_id': str(reward.get('image_id', ''))
        }}}
    )

    messages.success(request, f"You have successfully purchased {reward['item']}!")
    return redirect('home')

def remove_reward(request, reward_id):
    if 'user_id' not in request.session:
        return redirect('login')

    user_id = request.session['user_id']
    user = users_collection.find_one({'_id': ObjectId(user_id)})

    if not user or not user.get('is_admin', False):
        messages.error(request, "You don't have permission to delete items.")
        return redirect('shop')

    # Delete the reward from MongoDB
    result = rewards_collection.delete_one({'_id': ObjectId(reward_id)})

    if result.deleted_count > 0:
        messages.success(request, "Item removed successfully.")
    else:
        messages.error(request, "Item not found or could not be deleted.")

    return redirect('shop')

def edit_student(request, student_id):
    if not request.session.get('is_admin'):
        return redirect('login')
    
    try:
        # Get student document
        student = users_collection.find_one({'_id': ObjectId(student_id)})
        if not student:
            raise Exception("Student not found")

        # Convert MongoDB ObjectId to string
        student['id'] = str(student['_id'])
        
        # Handle inventory safely
        inventory = []
        for item in student.get('inventory', []):
            try:
                # First try to get item_id
                item_id_str = item.get('item_id')
                
                # Fallback for legacy items without item_id
                if not item_id_str and 'item' in item:
                    reward = rewards_collection.find_one({'item': item['item']})
                    if reward:
                        item_id_str = str(reward['_id'])
                
                if not item_id_str:
                    continue
                    
                item_id = ObjectId(item_id_str)
                reward = rewards_collection.find_one({'_id': item_id})
                
                if reward:
                    inventory.append({
                        'id': str(reward['_id']),
                        'name': reward.get('item', 'Unknown'),
                        'description': reward.get('description', ''),
                        'image_id': str(reward.get('image_id', ''))
                    })
            except Exception as e:
                print(f"Skipping invalid item: {str(e)}")
                continue

        # Prepare student data with safe defaults
        student_data = {
            'id': student['id'],
            'username': student.get('username', ''),
            'email': student.get('email', ''),
            'exp': student.get('exp', 0),
            'gold': student.get('gold', 0),
            'hp': student.get('hp', 0),
            'inventory': inventory
        }

        return render(request, 'settings.html', {
            'student': student_data,
            'is_admin': True
        })

    except Exception as e:
        print(f"Error in edit_student: {str(e)}")
        messages.error(request, "Error loading student details")
        return redirect('admin')



    
def update_student_details(request, student_id):
    if not request.session.get('is_admin'):
        return redirect('login')
    
    try:
        if request.method == "POST":
            # Validate data types
            update_data = {
                'username': request.POST.get('username'),
                'email': request.POST.get('email'),
                'exp': int(request.POST.get('exp', 0)),
                'gold': int(request.POST.get('gold', 0)),
                'hp': int(request.POST.get('hp', 0))
            }

            # Update database
            result = users_collection.update_one(
                {'_id': ObjectId(student_id)},
                {'$set': update_data}
            )

            if result.modified_count > 0:
                messages.success(request, "Student updated successfully!")
            else:
                messages.info(request, "No changes detected")

            return redirect('admin')

    except ValueError as e:
        messages.error(request, f"Invalid number format: {str(e)}")
    except Exception as e:
        messages.error(request, f"Error updating student: {str(e)}")
    
    return redirect('edit_student', student_id=student_id)

def delete_item(request, student_id, item_id):
    if not request.session.get('is_admin'):
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    
    try:
        # Direct string match without ObjectId conversion
        result = users_collection.update_one(
            {'_id': ObjectId(student_id)},
            {'$pull': {'inventory': {'item_id': item_id}}}
        )

        if result.modified_count > 0:
            return JsonResponse({"success": True})
        return JsonResponse({
            "success": False,
            "error": "Item not found in inventory"
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Server error: {str(e)}"
        }, status=500)
    

    
def final_migration(request):
    if not request.session.get('is_admin'):
        return HttpResponseForbidden()
    
    updated = 0
    students = users_collection.find({'inventory': {'$exists': True}})
    
    for student in students:
        new_inventory = []
        for item in student.get('inventory', []):
            # Force string format for item_id
            if 'item_id' not in item:
                reward = rewards_collection.find_one({'item': item.get('item')})
                if reward:
                    item['item_id'] = str(reward['_id'])
                    updated += 1
            # Ensure item_id is string
            elif isinstance(item['item_id'], ObjectId):
                item['item_id'] = str(item['item_id'])
                updated += 1
            new_inventory.append(item)
        
        users_collection.update_one(
            {'_id': student['_id']},
            {'$set': {'inventory': new_inventory}}
        )
    
    return HttpResponse(f"Final migration completed. Updated {updated} items.")