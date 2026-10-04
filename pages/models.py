from django.db import models

class SocialLink(models.Model):
    
    platform = models.CharField(max_length=40)
    label = models.CharField(max_length=80)
    url = models.CharField(max_length=200, help_text="https://... or mailto:...")
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ["order", "platform"]
        
    def __str__(self) -> str:
        return self.platform
    
    @property
    def is_external(self) -> bool:
        return self.url.startswith("http")