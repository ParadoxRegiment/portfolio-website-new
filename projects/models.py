from __future__ import annotations

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.templatetags.static import static

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
    
    objects: ProjectQuerySet = ProjectQuerySet.as_manager() # type: ignore[assignment]
    
    class Meta:
        ordering = ["order", "-created"]
        
    def __str__(self) -> str:
        return self.title
    
    def get_absolute_url(self):
        return reverse("projects:detail", kwargs={"slug": self.slug})

class ScriptDemo(models.Model):
    """In-browser console for script projects via Pyodide
    """
    
    project = models.OneToOneField(
        Project, on_delete=models.CASCADE, related_name="demo"
    )
    source_zip = models.FileField(
        upload_to="demos/",
        validators=[FileExtensionValidator(["zip"])],
        help_text="Zip of the script's source files. All files are public",
    )
    entry_point = models.CharField(
        max_length=200,
        help_text="Script to run, relative to the zip root (e.g. 'pipeline.py'), "
        "or a module name to run like 'python -m' (e.g. 'etl.pipeline').",
    )
    command = models.SlugField(
        max_length=40, help_text="What visitors type to run it, e.g. 'donki'."
    )
    packages = models.CharField(
        max_length=300,
        blank=True,
        help_text="Comma-separated packages to install, e.g. pandas, request, matplotlib",
    )
    intro = models.TextField(blank=True, help_text="Option note shown above the console.")
    examples = models.TextField(
        blank=True, help_text="One example command per line, show as clickable buttons."
    )
    
    def __str__(self) -> str:
        return f"Console for {self.project}"
    
    @property
    def package_list(self) -> list[str]:
        return [name.strip() for name in self.packages.split(",") if name.strip()]
    
    @property
    def example_list(self) -> list[str]:
        return [line.strip() for line in self.examples.splitlines() if line.strip()]
    
    def as_console_config(self) -> dict:
        return {
            "indexUrl": settings.PYODIDE_INDEX_URL,
            "workerUrl": static("js/console-worker.js"),
            "runtimeUrl": static("js/console_runtime.py"),
            "sourceUrl": self.source_zip.url,
            "command": self.command,
            "entryPoint": self.entry_point,
            "packages": self.package_list,
        }