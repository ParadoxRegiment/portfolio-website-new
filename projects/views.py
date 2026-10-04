from django.shortcuts import render, get_object_or_404
from .models import Project

def published_projects():
    return (
        Project.objects.published()
        .select_related("category")
        .prefetch_related("tags")
    )

def project_list(request):
    return render(
        request,
        "projects/project_list.html",
        {"projects": published_projects()},
        )
    
def project_detail(request, slug):
    project = get_object_or_404(published_projects(), slug=slug)
    return render(request, "projects/project_detail.html", {"project": project})