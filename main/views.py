import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Pet, AdoptionRequest
from django.db.models import Q
from .models import Pet, AdoptionRequest, Notification,ContactMessage
from django.contrib import messages



# ---------- Contact(user send message) ----------
@login_required(login_url='login')  # Redirects to login if not logged in
def contact(request):
    if request.method == "POST":
        ContactMessage.objects.create(
            user=request.user,
            name=request.user.username,
            email=request.user.email,
            message=request.POST['message']
        )
        # Notify user that message sent
        messages.success(request, "Your message has been sent to the admin ✅")
        return redirect('home')

    return render(request, 'contact.html')


# ---------- Helper ----------
def is_admin(user):
    return user.is_staff


# ---------- Admin reply to contact message ----------
@login_required
@user_passes_test(lambda u: u.is_staff)
def reply_message(request, msg_id):
    msg = get_object_or_404(ContactMessage, id=msg_id)
    
    if request.method == "POST":
        reply_text = request.POST.get('reply')
        if reply_text:
            msg.reply = reply_text
            msg.save()

            # Send notification to user
            Notification.objects.create(
                user=msg.user,
                message=f"Admin replied to your message: {reply_text[:50]}..."
            )
            messages.success(request, "Reply sent successfully ✅")
        return redirect('admin_dashboard')

    

# ---------- Signup (Updated with strict validation) ----------
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        # Updated names to match HTML
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Unique Username Check
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        # 2. Strict Gmail Validation
        if not re.match(r"^[a-zA-Z0-9._%+-]+@gmail\.com$", email):
            return render(request, 'signup.html', {'error': 'Invalid Email! Use a @gmail.com address.'})

        # 3. Match Check: Password and Confirm Password
        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        # 4. Complexity Check: 8 chars, Upper, Lower, Number
        if len(password) < 8:
            return render(request, 'signup.html', {'error': 'Password must be at least 8 digits'})
        
        if not any(x.isupper() for x in password) or \
           not any(x.islower() for x in password) or \
           not any(x.isdigit() for x in password):
            return render(request, 'signup.html', {'error': 'Password needs 1 uppercase, 1 lowercase, and 1 number'})

        # SUCCESS: Save the user
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('home')

    return render(request, 'signup.html')


# ---------- Login ----------
def user_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard' if request.user.is_staff else 'home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('admin_dashboard' if user.is_staff else 'home')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


# ---------- Logout ----------
def user_logout(request):
    logout(request)
    return redirect('login')

# ---------- Home ----------
@login_required
def home(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    # 1. Start with the base QuerySet
    pets = Pet.objects.all()   

    # 2. Apply Filters first (Category & Search)
    if category:
        pets = pets.filter(category=category)

    if query:
        pets = pets.filter(
            Q(name__icontains=query) |
            Q(breed__icontains=query)
        )

    # 3. APPLY THE ALGORITHM (Weighted Scoring)
    # Convert QuerySet to a list so we can sort using our custom Python method
    pets_list = list(pets)
    
    # Sort the list based on the score returned by the model method
    # Higher scores move to the top (reverse=True)
    # This sorts by Score FIRST (highest first)
    pets_list.sort(
    key=lambda x: (x.get_priority_score(), x.created_at.timestamp()),
    reverse=True
)

    # 4. Handle Notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    return render(request, 'home.html', {
        'pets': pets_list,  # Note: we are passing the sorted list here
        'query': query,
        'notifications': notifications,
        'unread_count': unread_count
    })


# ---------- Adopt Pet (with mobile validation) ----------
@login_required
def adopt_pet(request, pet_id):
    pet = get_object_or_404(Pet, id=pet_id)

    if request.method == 'POST':
        # 1. Capture ALL form data from POST
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        age = request.POST.get('age')
        occupation = request.POST.get('occupation')
        
        # --- MISSING FIELDS ADDED HERE ---
        housing_type = request.POST.get('housing_type')
        own_or_rent = request.POST.get('own_or_rent')
        landlord_permission = request.POST.get('landlord_permission')
        previous_pet = request.POST.get('previous_pet')
        current_pet = request.POST.get('current_pet')
        experience = request.POST.get('experience')
        reason = request.POST.get('reason')

        # 2. Capture Files
        photo_id = request.FILES.get('photo_id')
        legal_doc = request.FILES.get('legal_doc')
        selfie_with_pet = request.FILES.get('selfie_with_pet')

        # 3. Create the object with EVERY field
        AdoptionRequest.objects.create(
            user=request.user,
            pet=pet,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            age=age,
            occupation=occupation,
            # Save the new fields
            housing_type=housing_type,
            own_or_rent=own_or_rent,
            landlord_permission=landlord_permission,
            previous_pet=previous_pet,
            current_pet=current_pet,
            experience=experience,
            reason=reason,
            # Files
            photo_id=photo_id,
            legal_doc=legal_doc,
            selfie_with_pet=selfie_with_pet
        )

        Notification.objects.create(
            user=request.user,
            message=f"Your adoption request for {pet.name} has been submitted!"
        )

        return redirect('home')

    return render(request, 'adopt_pet.html', {'pet': pet})

# ---------- Admin Dashboard ----------

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    pets = Pet.objects.all()
    adoption_requests = AdoptionRequest.objects.all()
    messages = ContactMessage.objects.all().order_by('-created_at')

    return render(request, 'admin_dashboard.html', {
        'pets': pets,
        'adoption_requests': adoption_requests,
        'messages': messages
    })

#  deletet_adoptiion req.
@login_required
@user_passes_test(is_admin)
def delete_adoption_request(request, req_id):
    req = get_object_or_404(AdoptionRequest, id=req_id)
    req.delete()
    messages.success(request, "Adoption request deleted successfully ✅")
    return redirect('admin_dashboard')



# Admin check
def is_admin(user):
    return user.is_superuser  # or your custom check

# Approve Request
@login_required
@user_passes_test(is_admin)
def approve_request(request, req_id):
    req = get_object_or_404(AdoptionRequest, id=req_id)
    req.status = 'Approved'
    req.pet.available = False
    req.pet.save()
    req.save()

    Notification.objects.create(
        user=req.user,
        message=f"Your adoption request for {req.pet.name} has been APPROVED 🎉"
    )
    return redirect('admin_dashboard')

# Reject Request
@login_required
@user_passes_test(is_admin)
def reject_request(request, req_id):
    req = get_object_or_404(AdoptionRequest, id=req_id)
    
    if request.method == "POST":
        # Get the reason from the custom dashboard form
        reason = request.POST.get('rejection_reason', "No specific reason provided.")
        
        # 1. Update the AdoptionRequest record
        req.status = 'Rejected'
        req.rejection_reason = reason
        req.save()

        # 2. Create the Notification for the user including the reason
        Notification.objects.create(
            user=req.user,
            message=f"Your adoption request for {req.pet.name} has been REJECTED. Reason: {reason}"
        )
        
        messages.error(request, f"Request for {req.pet.name} rejected with reason.")
        return redirect('admin_dashboard')
    
    # If someone tries to access via GET, just redirect back
    return redirect('admin_dashboard')

# Delete Contact Message
@login_required
@user_passes_test(is_admin)
def delete_contact_message(request, msg_id):  # matches URL param
    msg = get_object_or_404(ContactMessage, id=msg_id)
    msg.delete()
    messages.success(request, "Message deleted successfully ✅")
    return redirect('admin_dashboard')


# ---------- Static Pages ----------
def about(request):
    return render(request, 'about.html')

    
# ---------------- Mark Notification as Read -------------

@login_required
def view_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    # Mark it as read
    if not notif.is_read:
        notif.is_read = True
        notif.save()
    return render(request, 'view_notification.html', {'notif': notif})

@login_required
def delete_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, user=request.user)
    notif.delete()
    messages.success(request, "Notification deleted ✅")
    return redirect('home')  # Or a dedicated notifications page


#adoption request status
@login_required
def my_adoption_requests(request):
    adoption_requests = AdoptionRequest.objects.filter(user=request.user)
    return render(request, 'my_adoption_requests.html', {
        'adoption_requests': adoption_requests
    })

#clear notification
@login_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return redirect(request.META.get('HTTP_REFERER', 'home')) # Redirects back to the same page