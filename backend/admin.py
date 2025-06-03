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
# admin.site.register(Material)
# admin.site.register(ProductMaterial)