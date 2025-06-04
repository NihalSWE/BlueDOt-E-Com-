from django.contrib import admin
from django.utils.html import format_html
from .models import *

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

@admin.register(MaterialInventoryDetail)
class MaterialInventoryDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'mid_material', 'mid_invoice_id', 'mid_entry_by', 'order_id', 'mid_deal_type', 'mid_entry_date']
    list_filter = ['mid_deal_type', 'mid_entry_date']
    search_fields = ['mid_invoice_id', 'mid_material__mr_material_name']
# admin.site.register(Material)
# admin.site.register(ProductMaterial)