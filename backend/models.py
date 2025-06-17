from django.db import models
from PIL import Image
import os
# Create your models here.


from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from backend.utils.slug_utils import generate_unique_slug
from django.utils import timezone
from django.core.files.storage import default_storage
from io import BytesIO
from django.core.files.base import ContentFile
from decimal import Decimal




def banner_image_upload_path(instance, filename):
    # Extract file extension
    ext = os.path.splitext(filename)[-1]  # includes the dot (e.g., .jpg)
    name_slug = slugify(instance.name)

    # Build base name
    base_filename = f"{name_slug}-banner_image"

    # Check if it's a new instance or an update
    if instance.pk and instance.banner_image:
        # If updating, retain the same number part but update the extension
        current_name = os.path.basename(instance.banner_image.name)
        number_part = '01'  # default
        parts = current_name.replace(f"{base_filename}-", '').split('.')
        if parts and parts[0].isdigit():
            number_part = parts[0]

        filename = f"{base_filename}-{number_part}{ext}"
    else:
        # New upload, determine number based on existing files
        directory = "category_images/"
        existing_files = default_storage.listdir(directory)[1]  # Get files list
        count = len([f for f in existing_files if f.startswith(f"{base_filename}-")])
        number_part = str(count + 1).zfill(2)
        filename = f"{base_filename}-{number_part}{ext}"

    return os.path.join("category_images", filename)



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
            user_id=user_id or '445900',
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
    name = models.CharField(max_length=250, blank=True, null=True)

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



class Category(models.Model):
    STATUS_CHOICES = (
        ('1', 'Active'),
        ('0', 'Inactive'),
    )

    name = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    meta_keys = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    codes = models.CharField(max_length=50, unique=True, help_text="Unique identifier for the category")
    position = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    banner_image = models.ImageField(upload_to=banner_image_upload_path, blank=True, null=True)
    parent_category = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="If this is a subcategory, select the parent category"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def generate_unique_slug(instance, model_class, slug_field_name='slug'):
        """
        Generate a unique slug for an instance based on its name.
        """
        base_slug = slugify(instance.name)
        slug = base_slug
        index = 1

        # Get field to check uniqueness on
        slug_field = model_class._meta.get_field(slug_field_name).attname

        # Check for uniqueness
        while model_class.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{index}"
            index += 1

        return slug

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)  # Save to get pk first if new

        if not self.slug:
            self.slug = generate_unique_slug(self, Category)
        
        if is_new or not self.codes:
            if self.parent_category:
                self.codes = f"{self.parent_category.codes}{str(self.pk).zfill(2)}"
            else:
                self.codes = str(self.pk).zfill(2)
        
        # Resize image if exists
        if self.image:
            try:
                img = Image.open(self.image.path)
                img = img.convert('RGB')
                img = img.resize((300, 300), Image.LANCZOS)  # Resize to 300x300
                img.save(self.image.path)
            except Exception as e:
                print(f"Image resizing failed: {e}")       
        
        super().save(update_fields=['slug', 'codes'])
        

    def __str__(self):
        return self.name



class Brand(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    name = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    image = models.ImageField(upload_to='brands/', null=True, blank=True)  # <-- changed here
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.name or "Unnamed Brand"
    
    
class Product(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ('flat', 'Flat'),
        ('percent', 'Percentage'),
    )
    name = models.CharField(max_length=255)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='products')
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, related_name='products')
    slug = models.SlugField(unique=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_material_quantity = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, help_text="Rough estimate of total material required"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Required thumbnail image
    thumbnail = models.ImageField(upload_to='product_thumbnails/', help_text="Main thumbnail image (required)")
    # Many-to-Many for materials
    materials = models.ManyToManyField('Material', through='ProductMaterial')
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    class Meta:
        verbose_name = "Inv Product"
        verbose_name_plural = "Inv Products"
        
    @property
    def active_discount(self):
        return self.discounts.filter(
            status=1,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
        
    @property
    def best_active_discount(self):
        now = timezone.now()
        # Filter discounts linked to this product with active category and status
        active_discounts = self.discounts.filter(
            status=1,
            category__status=1,
            category__start_date__lte=now,
            category__end_date__gte=now
        )
        if not active_discounts.exists():
            return None
        
        # Find the discount with max monetary value for this product
        best_discount = None
        max_discount_amount = Decimal('0')
        for discount in active_discounts:
            if discount.discount_type == 'flat':
                amount = discount.discount_value
            elif discount.discount_type == 'percent':
                amount = (discount.discount_value / 100) * self.base_price
            else:
                amount = Decimal('0')

            if amount > max_discount_amount:
                max_discount_amount = amount
                best_discount = discount

        return best_discount

    @property
    def final_price(self):
        # Priority 1: apply best active discount from Discount model if any
        best_discount = self.best_active_discount
        if best_discount:
            if best_discount.discount_type == 'flat':
                return max(self.base_price - best_discount.discount_value, 0)
            elif best_discount.discount_type == 'percent':
                discount_amount = (best_discount.discount_value / 100) * self.base_price
                return max(self.base_price - discount_amount, 0)

        # Priority 2: fallback to product-level discount
        if self.discount_type == 'flat' and self.discount_value:
            return max(self.base_price - self.discount_value, 0)
        elif self.discount_type == 'percent' and self.discount_value:
            discount_amount = (self.discount_value / 100) * self.base_price
            return max(self.base_price - discount_amount, 0)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug(Product)
        super().save(*args, **kwargs)
        
    def generate_unique_slug(self, model_class, slug_field_name='slug'):
        from django.utils.text import slugify
        base_slug = slugify(self.name)
        slug = base_slug
        index = 1
        slug_field = model_class._meta.get_field(slug_field_name).attname
        while model_class.objects.filter(**{slug_field: slug}).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{index}"
            index += 1
        return slug
    
    
    
    
    
class DiscountCategory(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)  # optional description
    image = models.ImageField(upload_to='discount_categories/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)  # 1 = Active, 0 = Inactive
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name
    def is_active(self):
        now = timezone.now()
        return (
            self.status == 1 and
            self.start_date <= now <= self.end_date
        )
class Discount(models.Model):
    STATUS_CHOICES = (
        (1, 'Active'),
        (0, 'Inactive'),
    )
    products = models.ManyToManyField('Product', related_name='discounts')
    category = models.ForeignKey(DiscountCategory, on_delete=models.CASCADE, related_name='discounts')
    discount_type = models.CharField(max_length=10, choices=(('flat', 'Flat'), ('percent', 'Percentage')))
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=1)  # 1 = Active, 0 = Inactive
    def __str__(self):
        return f"{self.category.name} - {self.discount_value} {self.get_discount_type_display()}" 
    
    

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        verbose_name = "Inv Product Image"
        verbose_name_plural = "Inv Products Images"

    def __str__(self):
        return f"Image for {self.product.name}"
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                img_path = self.image.path
                with Image.open(img_path) as img:
                    # Resize image to 800x600
                    img = img.resize((800, 600), Image.LANCZOS)

                    # Handle transparency if present
                    if img.mode in ('RGBA', 'LA'):
                        img.save(img_path, format='PNG')
                    else:
                        img = img.convert('RGB')
                        img.save(img_path, format='JPEG')

            except Exception as e:
                print(f"Error resizing product image: {e}")
        
    
    
    
    
class MeasurementType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g. Length, Weight, Quantity
    
    class Meta:
        verbose_name = "Inv Measurement Type"
        verbose_name_plural = "Inv Measurement Types"

    def __str__(self):
        return self.name
    
    

class MeasurementUnit(models.Model):
    unit = models.CharField(max_length=50)  # e.g. Centimeter
    symbol = models.CharField(max_length=10)  # e.g. cm
    measurement_type = models.ForeignKey(MeasurementType, on_delete=models.CASCADE)
    conversion_factor_to_base = models.FloatField(
        help_text="Conversion factor to the base unit of the type (e.g., cm → 0.01 for meter)"
    )
    
    class Meta:
        verbose_name = "Inv Measurement Unit"
        verbose_name_plural = "Inv Measurement Units"

    def __str__(self):
        return f"{self.abbreviation} ({self.measurement_type.name})"
    

class Material(models.Model):
    name = models.CharField(max_length=255)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.CASCADE)
    quantity_in_stock = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Inv Material"
        verbose_name_plural = "Inv Materials"

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
        verbose_name = "Inv Product Material"
        verbose_name_plural = "Inv Product Materials"

    def __str__(self):
        return f"{self.material.name} for {self.product.name}"
    
    


class Order(models.Model):
    STATUS_CHOICES = [
        (0, 'Pending'),
        (1, 'Approved'),
        (2, 'Processing'),
        (3, 'Completed'),
        (4, 'Cancelled'),
        (5, 'Not Viewed'),
    ]
    SHIPPING_TYPE_CHOICES = [
        ('flat_rate', 'Flat Rate (৳100)'),
        ('free_shipping', 'Free Shipping'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    customer = models.ForeignKey('CustomerInfo', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending',null=True,blank=True)
    order_date = models.DateField(null=True, blank=True)  # NEW FIELD
    notes = models.TextField(blank=True, null=True)  # ← Add this line
    invoice_id = models.CharField(max_length=20,unique=True, blank=True, null=True)
    
    # Order Financial Information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPE_CHOICES, default='flat_rate',null=True,blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=100.00,null=True,blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_invoice_id(self):
        import random
        import string
        while True:
            invoice_id = 'ORD' + ''.join(random.choices(string.digits, k=8))
            if not Order.objects.filter(invoice_id=invoice_id).exists():
                return invoice_id

    def save(self, *args, **kwargs):
        if not self.invoice_id:
            self.invoice_id = self.generate_invoice_id()
        super().save(*args, **kwargs)
        
    

    def __str__(self):
        return f"Order #{self.invoice_id} - {self.customer.CustomerName}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    product_name = models.CharField(max_length=200,null=True,blank=True)
   
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)

   
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.product.final_price or self.product.base_price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.invoice_id})"
    

class OrderSpecification(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    measurement = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Estimated weight of final product")
    custom_description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Inv Order Specification"
        verbose_name_plural = "Inv Order Specifications"

    def __str__(self):
        return f"Specs for Order #{self.order.id}"
    
    

class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Kilogram, Meter, Litre
    symbol = models.CharField(max_length=10, unique=True)  # e.g., kg, m, L, pcs
    
    class Meta:
        verbose_name = "Inv Unit"
        verbose_name_plural = "Inv Units"

    def __str__(self):
        return f"{self.name} ({self.symbol})"
    
    

class InventoryLog(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    change_type = models.CharField(max_length=20, choices=[('in', 'Stock In'), ('out', 'Stock Out')])
    quantity_changed = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inv Log"
        verbose_name_plural = "Inv Logs"

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
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                img_path = self.image.path
                with Image.open(img_path) as img:
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")

                    img = img.resize((730, 410), Image.LANCZOS)
                    img.save(img_path, format='PNG')
            except Exception as e:
                print(f"Error resizing image: {e}")
    
    
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


from urllib.parse import urlparse, parse_qs
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
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.video_thumbnail:
            try:
                img = Image.open(self.video_thumbnail.path)
                img = img.convert("RGB")
                img = img.resize((570, 298), Image.LANCZOS)
                img.save(self.video_thumbnail.path)
            except Exception as e:
                print(f"Error resizing image: {e}")
    def get_embed_video_url(self):
        """Return embed-friendly video URL for YouTube"""
        try:
            parsed = urlparse(self.video_url)
            if 'youtube.com' in parsed.netloc:
                video_id = parse_qs(parsed.query).get('v', [None])[0]
                if video_id:
                    return f'https://www.youtube.com/embed/{video_id}'
            elif 'youtu.be' in parsed.netloc:
                video_id = parsed.path.lstrip('/')
                return f'https://www.youtube.com/embed/{video_id}'
        except:
            pass
        return ''
    def __str__(self):
        return f"FAQ Section - {self.section_title or 'Untitled'}"
    
    
    
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
    

class PracticeArea(models.Model):
    heading = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.heading
    

# Our Faq
class OurfaqBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    background_image = models.ImageField(upload_to='Ourfaq_banner/')

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
                
# Our Faq faq's              
class FAQ(models.Model):
    # FAQ item fields
    question = models.CharField(max_length=500, help_text="FAQ Question")
    answer = models.TextField(help_text="FAQ Answer")
    is_active = models.BooleanField(default=True, help_text="Display this FAQ on frontend")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    
    # Left-side visual content
    image = models.ImageField(
        upload_to='faq/section/',
        blank=True,
        null=True,
        help_text="Background/side image (will be resized to 400x218)"
    )
    section_title = models.CharField(
        max_length=255,
        default="Presvila Your Printing Company",
        help_text="Section heading text"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question[:50] + "..." if len(self.question) > 50 else self.question

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Resize image if it exists
        if self.image:
            try:
                img_path = self.image.path
                with Image.open(img_path) as img:
                    img = img.convert("RGB")
                    img = img.resize((400, 218), Image.LANCZOS)
                    img.save(img_path)
            except Exception as e:
                print(f"Error resizing image: {e}")
                
                
#Home page 1st 2 cards
class CenterCard(models.Model):
    subtitle = models.CharField(max_length=100, default="LATEST DESIGN")
    title = models.CharField(max_length=200)
    button_text = models.CharField(max_length=100, default="Shop Now")
    button_link = models.URLField(default="#")
    image = models.ImageField(upload_to='center_cards/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                img_path = self.image.path
                with Image.open(img_path) as img:
                    # Resize image keeping mode and transparency
                    img = img.resize((433, 363), Image.LANCZOS)

                    # Save as PNG (preserving transparency)
                    img.save(img_path, format='PNG')
            except Exception as e:
                print(f"Error resizing image: {e}")



class PartyRegSupplier(models.Model):
    prs_slid = models.CharField(max_length=15, primary_key=True)
    prs_name = models.CharField(max_length=50)
    prs_address = models.CharField(max_length=50)
    prs_person = models.CharField(max_length=50)
    prs_mobile = models.CharField(max_length=50)
    prs_phone = models.CharField(max_length=50, null=True, blank=True)
    prs_email = models.CharField(max_length=50, null=True, blank=True)
    prs_website = models.CharField(max_length=50, null=True, blank=True)
    prs_complain_number = models.CharField(max_length=20, null=True, blank=True)

    prs_reg_date = models.CharField(max_length=10, null=True, blank=True)
    loginidno = models.CharField(max_length=25, null=True, blank=True)
    open_sdue = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.prs_name
    



class MaterialType(models.Model):
    TypeName = models.CharField(max_length=255)
    adminid = models.IntegerField(null=True, blank=True)  # nullable integer field
    
    class Meta:
        verbose_name = "Inv Material Type"
        verbose_name_plural = "Inv Material Types"

    def __str__(self):
        return self.TypeName
    


class Measurement(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., Weight, Length, Volume, Count
    product_id = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    
    class Meta:
        verbose_name = "Inv Measurement"
        verbose_name_plural = "Inv Measurements"

    def __str__(self):
        return self.name

    
    

class MaterialRegistration(models.Model):
    mr_supplier = models.ForeignKey(
        'PartyRegSupplier', 
        null=True, 
        on_delete=models.CASCADE, 
        db_column='mr_supplier_id'
    )
    mr_type = models.ForeignKey(
        'MaterialType', 
        on_delete=models.SET_NULL, 
        null=True, 
        db_column='mr_type'
    )
    mr_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)
    mr_material_name = models.CharField(max_length=255)
    mr_material_details = models.TextField(null=True, blank=True)
    mr_buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    mr_sell_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    adminid = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Inv Material Registration "
        verbose_name_plural = "Inv Material Registration"

    def __str__(self):
        return self.mr_material_name


class MaterialInventoryDetail(models.Model):
    mid_party = models.ForeignKey('PartyRegSupplier', on_delete=models.CASCADE, related_name='inventory_details')  # Supplier or customer
    mid_entry_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='entered_inventory')
    mid_material = models.ForeignKey('MaterialRegistration', on_delete=models.CASCADE, related_name='inventory_entries')
    mid_invoice_id = models.CharField(max_length=100)
    
    order_id = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)

    mid_buy_quentity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mid_buy_prices = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mid_buy_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    mid_sell_quentity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mid_sell_prices = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mid_sell_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    mid_exp_date = models.DateField(null=True, blank=True)
    mid_entry_date = models.DateTimeField(default=timezone.now,null=True)

    mid_deal_type = models.CharField(max_length=10, choices=[('buy', 'Buy'), ('sell', 'Sell')])

    adminid = models.IntegerField(null=True, blank=True)  # if using custom tracking dsfsd

    due_discount = models.DecimalField(max_digits=10,  decimal_places=2, default=0)
    
    id_debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    mid_credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = "Inv Material Details "
        verbose_name_plural = "Inv Material Details"

    def __str__(self):
        return f"Inventory #{self.id} - Material: {self.mid_material.mr_material_name}"
    


class InvWarehouse(models.Model):
    invw_id = models.AutoField(primary_key=True)
    invw_name = models.CharField(max_length=255)
    invw_code = models.CharField(max_length=100, unique=True)
    invw_address = models.TextField(blank=True, null=True)
    invw_city = models.CharField(max_length=100, blank=True, null=True)
    invw_state = models.CharField(max_length=100, blank=True, null=True)
    invw_postal_code = models.CharField(max_length=20, blank=True, null=True)
    invw_country = models.CharField(max_length=100, blank=True, null=True)

    invw_contact_person = models.CharField(max_length=100, blank=True, null=True)
    invw_contact_phone = models.CharField(max_length=20, blank=True, null=True)
    invw_contact_email = models.EmailField(max_length=255, blank=True, null=True)

    invw_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_warehouses')
    invw_status = models.IntegerField(choices=[(0, 'Inactive'), (1, 'Active')], default=1)

    invw_created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='warehouses_created')
    invw_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='warehouses_updated')

    invw_created_at = models.DateTimeField(auto_now_add=True)
    invw_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'inv_warehouse'
        verbose_name = "Inv Warehouse"
        verbose_name_plural = "Inv Warehouse"

    def __str__(self):
        return f"{self.invw_name} ({self.invw_code})"
    
    

class MaterialUsage(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        related_name='material_usages',
        null=True, blank=True
    )
    material = models.ForeignKey(MaterialRegistration, on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT)  # NEW FIELD
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'material')
        verbose_name = "Inv Material Usage "
        verbose_name_plural = "Inv Material Usage"

    def __str__(self):
        return f"{self.quantity_used} of {self.material.mr_material_name} for Order #{self.order.id}"
    
    
class CustomerInfo(models.Model):
    CustomerID = models.CharField(max_length=50)
    CustomerName = models.CharField(max_length=50)
    CustomerAddress = models.CharField(max_length=250)
    CustomerEmail = models.CharField(max_length=25,null=True)
    CustomerContact = models.CharField(max_length=25)
    
    district_id = models.CharField(max_length=10, blank=True, null=True)
    district_name = models.CharField(max_length=100, blank=True)
    thana_id = models.CharField(max_length=10, blank=True, null=True)
    thana_name = models.CharField(max_length=100, blank=True)
    
    RegDate = models.DateField()
    dabite = models.CharField(max_length=100,null=True)
    cradit = models.CharField(max_length=100,null=True)
    adminid = models.IntegerField(null=True)
    type = models.CharField(max_length=25,null=True)
    open_due = models.CharField(max_length=100,null=True)  # Assuming it's varchar like the others

    def __str__(self):
        return self.CustomerName

    class Meta:
        db_table = 'customer_info'
        
        
        
        
class HomeCTA(models.Model):
    sub_title = models.CharField(max_length=255, default='BEST SELLER PRODUCTS')
    title = models.CharField(max_length=255, default='Discover Our Best Selling Product You Need')
    button_text = models.CharField(max_length=100, default='Make an Order')
    button_link = models.CharField(max_length=100,default='#')
    image = models.ImageField(upload_to='home/cta/', blank=True, null=True)

    def __str__(self):
        return "Home CTA Section"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            try:
                img_path = self.image.path
                with Image.open(img_path) as img:
                    # Convert mode if needed (to ensure transparency support)
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")

                    # Resize to 692 x 500
                    img = img.resize((692, 500), Image.LANCZOS)

                    # Save as PNG to preserve transparency
                    img.save(img_path, format='PNG')
            except Exception as e:
                print(f"Error resizing image: {e}")
    
 
class PricingCard(models.Model):
    sub_title = models.CharField(max_length=255, default="GET 30% OFF TODAY")
    title = models.CharField(max_length=255, default="Nice Colorful Bag Printing")
    price_text = models.CharField(max_length=255, default="Start selling")
    price_value = models.CharField(max_length=100, default="$235.00")
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_link = models.CharField(max_length=255, default="#")  # using CharField instead of URLField
    image = models.ImageField(upload_to='pricing_card/')

    def save(self, *args, **kwargs):
        # Resize image to 556x540 using LANCZOS
        if self.image:
            img = Image.open(self.image)
            img = img.convert("RGB")
            img = img.resize((570, 448), Image.LANCZOS)

            buffer = BytesIO()
            img.save(fp=buffer, format='JPEG')
            self.image.save(self.image.name, ContentFile(buffer.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title 
    
# Contact Page banner
class CartBanner(models.Model):
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
                resized_img = img.resize((1920, 300), Image.LANCZOS)
                resized_img.save(image_path, quality=90, optimize=True)
    
    
class BlogBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    background_image = models.ImageField(upload_to='Blog_banner/')
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
                
                
                
class ProductBanner(models.Model):
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
                
                

# models.py

from django.utils.text import slugify
from ckeditor.fields import RichTextField
from django.utils import timezone

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField(
    max_length=5000,
    blank=True,
    help_text="Blog content with rich text editor")

    image = models.ImageField(upload_to='blog/', help_text="Blog thumbnail image")
    category = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='blog_posts', help_text="Select product category")
    author = models.CharField(max_length=100, default="Admin")
    date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = self.generate_unique_slug()
        

        # Resize image if provided
        if self.image and hasattr(self.image, 'file'):
            try:
                img = Image.open(self.image)
                img = img.convert('RGB')
                img = img.resize((730, 410), Image.LANCZOS)
                buffer = BytesIO()
                img.save(fp=buffer, format='JPEG', quality=85)
                self.image.save(self.image.name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                print(f"Error resizing image: {e}")
        
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        index = 1
        
        while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{index}"
            index += 1
        return slug

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('blog_details', kwargs={'slug': self.slug})

    def get_category_name(self):
        return self.category.name if self.category else "General"

    def get_short_description(self):
        """Return first 150 characters of description without HTML tags"""
        from django.utils.html import strip_tags
        clean_text = strip_tags(self.description)
        return clean_text[:150] + "..." if len(clean_text) > 120 else clean_text      
       
       
#Blogpost Coments
class BlogComment(models.Model):
    blog = models.ForeignKey('BlogPost', on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    number = models.CharField(max_length=20, blank=True, null=True, help_text="Optional phone number")
    website = models.URLField(blank=True, null=True)
    message = models.TextField(default="No message",max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.name} on {self.blog}'
    
    
from django.core.validators import MinValueValidator, MaxValueValidator
class ProductReview(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comment = models.TextField()
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Review by {self.name} - {self.product.name}"
    


class Visitor(models.Model):
    DEVICE_CHOICES = [
        ('mobile', 'Mobile'),
        ('desktop', 'Desktop'),
    ]
    
    ip_address = models.GenericIPAddressField()
    device_type = models.CharField(max_length=10, choices=DEVICE_CHOICES)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_type} - {self.ip_address}"
    

from decimal import Decimal
class AddCart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart item: {self.product.name} (Qty: {self.quantity})"

    @property
    def final_price(self):
    # Ensure safe decimal fallback
        price = getattr(self.product, 'final_price', None)
        if price is None:
            price = getattr(self.product, 'base_price', 0)
        return price or Decimal('0.00')
        
        
        
        
        


       
#checkout page-----
#Banner-----------    
class CheckoutBanner(models.Model):
    title = models.CharField(max_length=255)
    subtitle = models.TextField(blank=True, null=True)
    background_image = models.ImageField(upload_to='checkout_banner/')
    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # First save to get the file on disk
        if self.background_image:
            image_path = self.background_image.path
            with Image.open(image_path) as img:
                # Force resize to 1920x570 (may distort if original ratio differs)
                resized_img = img.resize((1920, 300), Image.LANCZOS)
                resized_img.save(image_path, quality=90, optimize=True)
                
                
#Order summary through checkout page


import uuid
class OrderSummary(models.Model):
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    SHIPPING_TYPE_CHOICES = [
        ('flat_rate', 'Flat Rate (৳100)'),
        ('free_shipping', 'Free Shipping'),
    ]
    
    # Order identification
    order_id = models.CharField(max_length=20, unique=True, editable=False)
    
    # Billing Information
    phone = models.CharField(max_length=20)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    
    # Address Information
    district_id = models.CharField(max_length=10, blank=True, null=True)
    district_name = models.CharField(max_length=100, blank=True)
    thana_id = models.CharField(max_length=10, blank=True, null=True)
    thana_name = models.CharField(max_length=100, blank=True)
    address = models.TextField(max_length=500)
    order_notes = models.TextField(max_length=500, blank=True, null=True)

    
    # Order Financial Information
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPE_CHOICES, default='flat_rate')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Order Status
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            # Generate unique order ID
            self.order_id = self.generate_order_id()
        super().save(*args, **kwargs)
    
    def generate_order_id(self):
        """Generate unique order ID"""
        import random
        import string
        while True:
            order_id = 'ORD' + ''.join(random.choices(string.digits, k=8))
            if not OrderSummary.objects.filter(order_id=order_id).exists():
                return order_id

    
    def __str__(self):
        return f"Order #{self.order_id} - {self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_address(self):
        return f"{self.address}, {self.thana_name}, {self.district_name}"
    
    
    
class OrderItemSummary(models.Model):
    order = models.ForeignKey(OrderSummary, related_name='items', on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    product_id = models.IntegerField()  # Store original product ID
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Optional: Store product image URL or path
    product_image = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
    
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
        
        
        
        
        
        
        
        
        