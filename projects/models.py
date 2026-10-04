from __future__ import annotations

from django.db import models
from django.urls import reverse

class Category(models.Model):
    """Generalized project types, e.g. 'Web Apps' or 'Data Tools'. Only one per project.
    """
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True)
    description = models.CharField(max_length=200, blank=True)
    order=models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "categories"
        
    def __str__(self) -> str:
        return self.name
    
class Tag(models.Model):
    """Skill and technical labels meant for more precise filtering. Projects can have multiple tags.
    """
    
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    
    class Meta:
        ordering = ["name"]
        
    def __str__(self) -> str:
        return self.name
    
class ProjectQuerySet(models.QuerySet):
    def published(self) -> ProjectQuerySet:
        return self.filter(is_published=True)
    
class Project(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110, unique=True)
    summary = models.CharField(max_length=200, help_text="One-liner shown on cards")
    description = models.TextField(help_text="Problem → approach → result.")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="projects"
    )
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)
    thumbnail = models.ImageField(upload_to="projects/", blank=True)
    repo_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False, help_text="Show on the home page.")
    is_published = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = ProjectQuerySet.as_manager()
    
    class Meta:
        ordering = ["order", "-created"]
        
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})
    