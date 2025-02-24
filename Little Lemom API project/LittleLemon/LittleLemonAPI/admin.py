from django.contrib import admin

# Register your models here.
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug')  # Display these columns in admin
    search_fields = ('title',)  # Make title searchable
    prepopulated_fields = {"slug": ("title",)}  # Automatically generate the slug from the title