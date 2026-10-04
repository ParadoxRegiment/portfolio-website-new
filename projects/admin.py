from django.contrib import admin

from .models import Category, Project, Tag, ScriptDemo

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "order"]
    list_editable = ["order"]
    prepopulated_fields = {"slug": ["name"]}
    
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}
    
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "featured", "is_published", "order"]
    list_editable = ["featured", "is_published", "order"]
    list_filter = ["category", "tags", "featured", "is_published"]
    search_fields = ["title", "summary", "description"]
    prepopulated_fields = {"slug": ["title"]}
    filter_horizontal = ["tags"]
    
class ScriptDemoInline(admin.StackedInline):
    model = ScriptDemo
    extra = 0