import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User



# ------------------ Notification ------------------
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"


# ------------------ Pet ------------------
class Pet(models.Model):
    CATEGORY_CHOICES = (
        ('Dog', 'Dog'),
        ('Cat', 'Cat'),
    )

    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    description = models.TextField()

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Dog')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')

    image = models.ImageField(
        upload_to='pet_images/',
        height_field='image_height',
        width_field='image_width',
        null=True,
        blank=True
    )

    image_height = models.IntegerField(null=True, blank=True)
    image_width = models.IntegerField(null=True, blank=True)

    available = models.BooleanField(default=True)


    def __str__(self):
        return self.name

    # NEW FIELDS FOR THE ALGORITHM
    is_special_needs = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now) # Tracks how long they've stayed
    
    # THE ALGORITHM METHOD
    def get_priority_score(self):
        score = 0

        # CRITICAL FACTOR (Weight: 100)
        if self.is_special_needs:
            score += 100
            
        # URGENT FACTOR (Weight: 50)
        days_in_shelter = (timezone.now() - self.created_at).days
        if days_in_shelter > 30:
            score += 50
            
        # IMPORTANT FACTOR (Weight: 30)
        if self.age >= 8:
            score += 30
            
        return score # This must be inside the function
       
 

# ------------------ Adoption Request ------------------
class AdoptionRequest(models.Model):
    # Status choices for better Admin control
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pet = models.ForeignKey('Pet', on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    age = models.IntegerField()
    occupation = models.CharField(max_length=200)

    housing_type = models.CharField(max_length=50)
    own_or_rent = models.CharField(max_length=50)
    landlord_permission = models.CharField(max_length=10, blank=True)

    previous_pet = models.CharField(max_length=10)
    current_pet = models.CharField(max_length=10, blank=True)
    experience = models.CharField(max_length=50)
    reason = models.TextField()

    # File uploads
    photo_id = models.FileField(upload_to='adoption_docs/')
    legal_doc = models.FileField(upload_to='adoption_docs/')
    selfie_with_pet = models.FileField(upload_to='adoption_docs/', blank=True, null=True)

    # --- UPDATED FIELDS ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    
    # This is where the Admin will type the reason for rejection
    rejection_reason = models.TextField(blank=True, null=True, help_text="Explain why the request was rejected.")
    # ----------------------

    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.pet.name} ({self.status})"


# ------------------ Contact Message ------------------
class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    replied = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name}"
