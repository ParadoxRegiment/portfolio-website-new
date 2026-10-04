from django.shortcuts import render, get_object_or_404
from django.views.decorators.vary import vary_on_headers

from .models import Project
from .filters import ProjectFilter

def published_projects():
    return (
        Project.objects.published()
        .select_related("category")
        .prefetch_related("tags")
    )

@vary_on_headers("HX-Request")
def project_list(request):
    filterset = ProjectFilter(request.GET, queryset=published_projects())
    context = {"filterset": filterset, "projects": filterset.qs}
    
    template = "projects/project_list.html"
    if request.htmx and not request.htmx.history_restore_request:
        template += "#results"
    
    return render(request, template, context)
    
def project_detail(request, slug):
    project = get_object_or_404(published_projects(), slug=slug)
    return render(request, "projects/project_detail.html", {"project": project})