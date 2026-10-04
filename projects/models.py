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
    
    