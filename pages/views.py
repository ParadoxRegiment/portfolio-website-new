from django.shortcuts import render
from django.db.models import Count, Q

from projects.models import Category, Project

def home(request):
    featured = (
        Project.objects.published()
        .filter(featured=True)
        .select_related("category")
        .prefetch_related("tags")[:3]
    )
    categories = Category.objects.annotate(
        num_projects=Count("projects", filter=Q(projects__is_published=True))
    ).filter(num_projects__gt=0)
    
    return render(
        request,
        "pages/home.html",
        {"featured": featured, "categories": categories},
    )

def contact(request):
    return render(request, "pages/contact.html")
