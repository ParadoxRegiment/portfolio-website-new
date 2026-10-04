import django_filters
from django import forms

from .models import Category, Project, Tag

class ProjectFilter(django_filters.FilterSet):
    category = django_filters.ModelMultipleChoiceFilter(
        field_name="category__slug",
        to_field_name="slug",
        queryset=Category.objects.filter(projects__is_published=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        label="Type",
    )
    
    tag = django_filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        to_field_name="slug",
        queryset=Tag.objects.filter(projects__is_published=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        conjoined=True,
        label="Tags",
    )
    
    class Meta:
        model = Project
        fields = ["category", "tag"]