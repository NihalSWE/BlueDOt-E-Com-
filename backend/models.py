from django.db import models
from PIL import Image
import os
# Create your models here.


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserManager(BaseUserManager):
    def create_user(self, email, user_id=None, username=None, phone_number=None, password=None, user_type=3, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        user = self.model(
            user_id=user_id,
            username=username,
            email=email,
            phone_number=phone_number,
            user_type=user_type,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, user_id=None, username=None, phone_number=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 0)

        return self.create_user(
            email=email,
            user_id=user_id or 'admin001',
            username=username or 'admin',
            phone_number=phone_number,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        (0, 'Admin'),
        (1, 'Warehouse'),
        (2, 'Staff'),
    )

    STATUS_CHOICES = (
        (0, 'Inactive'),
        (1, 'Active'),
        (2, 'Suspended'),
    )

    user_id = models.CharField(unique=True, max_length=15, blank=True, null=True)
    username = models.CharField(unique=True, max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True, max_length=100)
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=2)
    user_status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['user_id', 'username', 'phone_number']

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(null=True, blank=True)
    job_title = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    biography = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()

    def __str__(self):
        return self.name
    


class Product(models.Model):
    name = models.CharField(max_length=255)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_material_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Rough estimate of total material required"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # M2M through table
    materials = models.ManyToManyField('Material', through='ProductMaterial')

    def __str__(self):
        return self.name
    
    
class MeasurementType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. Length, Weight, Quantity

    def __str__(self):
        return self.name
    
    

class MeasurementUnit(models.Model):
    unit = models.CharField(max_length=50)  # e.g. Centimeter
    symbol = models.CharField(max_length=10)  # e.g. cm
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)
    conversion_factor_to_base = models.FloatField(
        help_text="Conversion factor to the base unit of the type (e.g., cm → 0.01 for meter)"
    )

    def __str__(self):
        return f"{self.abbreviation} ({self.measurement_type.name})"
    

class Material(models.Model):
    name = models.CharField(max_length=255)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.CASCADE)
    quantity_in_stock = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.measurement_unit.abbreviation})"

    @property
    def measurement_type(self):
        return self.measurement_unit.measurement_type.name
    
    

class ProductMaterial(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('product', 'material')

    def __str__(self):
        return f"{self.material.name} for {self.product.name}"
    
    


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"
    

class OrderSpecification(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    measurement = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Estimated weight of final product")
    custom_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Specs for Order #{self.order.id}"
    
    
class MaterialUsage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'material')

    def __str__(self):
        return f"{self.quantity_used} of {self.material.name} for Order #{self.order.id}"
    

class InventoryLog(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=[('in', 'Stock In'), ('out', 'Stock Out')])
    quantity_changed = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.change_type} - {self.material.name} ({self.quantity_changed})"


class AboutUs(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    image = models.ImageField(upload_to='about/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
    
class WhoWeAre(models.Model):
    heading = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='who_we_are/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.heading
    
    
class OurService(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=100, help_text="FontAwesome or custom icon class", blank=True)
    short_description = models.CharField(max_length=255)
    detailed_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class Portfolio(models.Model):
    title = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255, blank=True)
    project_type = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='portfolio/')
    project_url = models.URLField(blank=True, null=True)
    date_completed = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=100)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date', '-created_at']

    def __str__(self):
        return self.title
    

class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    author = models.CharField(max_length=100)
    excerpt = models.CharField(max_length=300, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date', '-created_at']

    def __str__(self):
        return self.title
    
    
class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.name} on {self.blog.title}"
    
    
# -----------------------
# Home Banner Slider
class HomeSlider(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='slider/')
    button_text = models.CharField(max_length=50, default="Start Your Projects")
    button_link = models.CharField(max_length=200, default="#")
    created_at = models.DateTimeField(auto_now_add=True)  # track creation time

    class Meta:
        ordering = ['-created_at'] 
        
    def __str__(self):
        return self.title
    
    
# Contact Page banner   
class ContactUsBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    background_image = models.ImageField(upload_to='contact_banner/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # First save to get the file on disk

        if self.background_image:
            image_path = self.background_image.path
            with Image.open(image_path) as img:
                # Force resize to 1920x570 (may distort if original ratio differs)
                resized_img = img.resize((1920, 570), Image.LANCZOS)
                resized_img.save(image_path, quality=90, optimize=True)
                
                
# Conatct page branch locations
class ContactLocation(models.Model):
    city = models.CharField(max_length=100)
    address = models.TextField()
    image = models.ImageField(upload_to='contact_locations/', null=True, blank=True)

    def __str__(self):
        return self.city

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            img = Image.open(self.image.path)
            img = img.convert('RGB')  # Ensure it's in a valid format
            img = img.resize((160, 108), Image.LANCZOS)
            img.save(self.image.path)
            
            
# COntact Msg
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    number = models.CharField(max_length=20)  # Mandatory
    website = models.URLField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.email}"
    
    
#About Us page 
#banner 
# models.py

class AboutUsBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    background_image = models.ImageField(upload_to='about_banner/')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.background_image:
            from PIL import Image
            image_path = self.background_image.path
            with Image.open(image_path) as img:
                resized_img = img.resize((1920, 570), Image.LANCZOS)
                resized_img.save(image_path, quality=90, optimize=True)


#ABout area
class AboutUs_AboutArea(models.Model):
    sub_title = models.CharField(max_length=255)
    main_title = models.CharField(max_length=255)
    description = models.TextField()

    quality_title = models.CharField(max_length=255)
    quality_description = models.TextField()

    automation_title = models.CharField(max_length=255)
    automation_description = models.TextField()

    center_title = models.CharField(max_length=255)
    
    button_text = models.CharField(max_length=50, default="Discover More")
    button_url = models.CharField(max_length=255, blank=True)

    call_text = models.CharField(max_length=255)
    call_number = models.CharField(max_length=50)

    bg_image = models.ImageField(upload_to='about/')
    man_image = models.ImageField(upload_to='about/')
    shape1 = models.ImageField(upload_to='about/')
    shape2 = models.ImageField(upload_to='about/')
    call_image = models.ImageField(upload_to='about/')

    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Section"

    def __str__(self):
        return f"About Area Content"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to ensure image files exist

        def resize_image(field_name, size):
            image_field = getattr(self, field_name)
            if image_field:
                img_path = image_field.path
                img = Image.open(img_path)
                if img.size != size:
                    img = img.convert('RGB')  # Convert to RGB to avoid mode issues
                    img = img.resize(size, Image.LANCZOS)
                    img.save(img_path, quality=90)

        resize_image('bg_image', (643, 557))
        resize_image('man_image', (353, 634))
        resize_image('shape1', (98, 103))
        resize_image('shape2', (240, 300))
        resize_image('call_image', (60, 60))
        
        
class CallToAction(models.Model):
    sub_title = models.CharField(max_length=255)
    main_title = models.CharField(max_length=255)
    button_text = models.CharField(max_length=50, default="Contact Us")
    button_link = models.CharField(max_length=255, blank=True)
    shape1 = models.ImageField(upload_to='cta/', blank=True, null=True)

    def __str__(self):
        return f"CTA: {self.main_title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save first to get access to file

        if self.shape1:
            img_path = self.shape1.path
            img = Image.open(img_path)

            # Resize to 1920x615
            output_size = (1920, 615)
            img = img.resize(output_size, Image.LANCZOS)

            # Save resized image back to same path
            img.save(img_path)
            
            
class ChooseUsSection(models.Model):
    thumb_image = models.ImageField(upload_to='choose_us/')
    shape_3 = models.ImageField(upload_to='choose_us/', blank=True, null=True)
    shape_4 = models.ImageField(upload_to='choose_us/', blank=True, null=True)

    def __str__(self):
        return f"Choose Us Section {self.id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        def resize_image(field_name, size):
            image_field = getattr(self, field_name)
            if image_field:
                img = Image.open(image_field.path)
                if img.size != size:
                    img = img.convert('RGB')
                    img = img.resize(size, Image.LANCZOS)
                    img.save(image_field.path, quality=90)

        resize_image('thumb_image', (570, 580))
        resize_image('shape_3', (177, 260))
        resize_image('shape_4', (225, 170))
        
        

class ChooseUsItem(models.Model):
    section = models.ForeignKey(
        ChooseUsSection,
        related_name='items',
        on_delete=models.CASCADE
    )
    icon_image = models.ImageField(
        upload_to='choose_us/icons/',
        help_text="Upload icon image (60x60 recommended)"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            if self.icon_image:
                img = Image.open(self.icon_image.path)
                if img.size != (60, 60):
                    img = img.convert('RGBA')
                    img = img.resize((60, 60), Image.LANCZOS)
                    img.save(self.icon_image.path, quality=90)
        except Exception as e:
            print(f"Error resizing icon image: {e}")


class FAQSection(models.Model):
    # Left side video and skills
    video_url = models.URLField(
        max_length=255,
        help_text="YouTube or video link for popup video"
    )
    video_thumbnail = models.ImageField(
        upload_to='faq/thumbnails/',
        help_text="Upload video thumbnail image (recommended size: 570x298)"
    )
    # Skills with progress percentage (e.g. T-Shirt Printing, Branding)
    skill1_name = models.CharField(max_length=100, default="T-Shirt Printing")
    skill1_progress = models.PositiveIntegerField(
        default=75,
        help_text="Progress in percentage (0-100)"
    )
    skill2_name = models.CharField(max_length=100, default="Branding")
    skill2_progress = models.PositiveIntegerField(
        default=85,
        help_text="Progress in percentage (0-100)"
    )
    # Statistic on left side below skills
    stat_icon_class = models.CharField(
        max_length=50,
        default="flaticon-roll",
        help_text="Icon CSS class for stat"
    )
    stat_title = models.CharField(max_length=100, default="Smooth Automation")
    stat_count = models.PositiveIntegerField(default=428)
    stat_description = models.CharField(max_length=150, default="Printing Specialist")

    # Right side section title and subtitle
    section_subtitle = models.CharField(
        max_length=255,
        default="FREQUENTLY ASKED QUESTION",
        blank=True,
        null=True
    )
    section_title = models.CharField(
        max_length=255,
        default="What Our Clients Ask About Presvila",
        blank=True,
        null=True
    )

    def __str__(self):
        return f"FAQ Section - {self.section_title}"


class FAQItem(models.Model):
    faq_section = models.ForeignKey(
        FAQSection, 
        related_name='faq_items', 
        on_delete=models.CASCADE
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()
    # Track whether FAQ is open by default
    is_expanded = models.BooleanField(default=False)

    def __str__(self):
        return self.question