from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import *




@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    # Fields to display in list view
    list_display = ('user_id', 'email', 'name', 'user_type', 'user_status', 'is_staff')
    list_filter = ('user_type', 'user_status', 'is_staff')

    # Fields for search bar
    search_fields = ('email', 'user_id', 'name', 'phone_number')
    ordering = ('email',)

    # Fields visible in the user form (admin detail/edit page)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('user_id', 'username', 'name', 'phone_number', 'address')}),
        ('Permissions', {'fields': ('user_type', 'user_status', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    # Fields for the add user form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'user_id', 'username', 'name', 'phone_number', 'user_type', 'user_status', 'password1', 'password2'),
        }),
    )
    
    
# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'base_price', 'thumbnail_preview', 'created_at')
    list_filter = ('category', 'brand', 'created_at')
    search_fields = ('name', 'description', 'slug')
    readonly_fields = ('thumbnail_preview',)
    prepopulated_fields = {'slug': ('name',)}  # Optional, in case you want to fill it automatically

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="60" height="60" style="object-fit: contain;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = "Thumbnail"

admin.site.register(Product, ProductAdmin)
admin.site.register(Brand)
admin.site.register(Category)


# Inline for Order Items
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

# Inline for Material Usage
class MaterialUsageInline(admin.TabularInline):
    model = MaterialUsage
    extra = 0

# Inline for OrderSpecification
class OrderSpecificationInline(admin.StackedInline):
    model = OrderSpecification
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__name']
    inlines = [OrderItemInline, MaterialUsageInline, OrderSpecificationInline]
    ordering = ['-created_at']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
    search_fields = ['order__id', 'product__name']
    list_filter = ['product']

@admin.register(OrderSpecification)
class OrderSpecificationAdmin(admin.ModelAdmin):
    list_display = ['order', 'measurement', 'weight']
    search_fields = ['order__id', 'measurement']

@admin.register(MaterialUsage)
class MaterialUsageAdmin(admin.ModelAdmin):
    list_display = ['order', 'material', 'quantity_used']
    search_fields = ['order__id', 'material__mr_material_name']
    list_filter = ['material']

@admin.register(ProductMaterial)
class ProductMaterialAdmin(admin.ModelAdmin):
    list_display = ['product', 'material', 'quantity']
    search_fields = ['product__name', 'material__mr_material_name']

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ['material', 'change_type', 'quantity_changed', 'reference', 'created_at']
    search_fields = ['material__mr_material_name', 'reference']
    list_filter = ['change_type', 'created_at']

@admin.register(MaterialRegistration)
class MaterialRegistrationAdmin(admin.ModelAdmin):
    list_display = ['mr_material_name', 'mr_type', 'mr_supplier', 'mr_quantity', 'mr_buy_price', 'unit']
    search_fields = ['mr_material_name']
    list_filter = ['mr_type', 'unit']

admin.site.register(MaterialInventoryDetail)
admin.site.register(PartyRegSupplier)
# admin.site.register(Material)
# admin.site.register(ProductMaterial)