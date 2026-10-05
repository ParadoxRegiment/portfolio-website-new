from django.db import models

class SocialLink(models.Model):
    
    class Icon(models.TextChoices):
        GITHUB = "github", "GitHub"
        LINKEDIN = "linkedin", "LinkedIn"
        EMAIL = "envelope", "Email"
        X = "twitter-x", "X / Twitter"
        MASTODON = "mastodon", "Mastodon"
        DISCORD = "discord", "Discord"
        YOUTUBE = "youtube", "YouTube"
        WEBSITE = "globe", "Website / other"
    
    platform = models.CharField(max_length=40)
    label = models.CharField(max_length=80)
    url = models.CharField(max_length=200, help_text="https://... or mailto:...")
    icon = models.CharField(max_length=20, choices=Icon.choices, default=Icon.WEBSITE)
    order = models.PositiveSmallIntegerField(default=0)
    
    class Meta:
        ordering = ["order", "platform"]
        
    def __str__(self) -> str:
        return self.platform
    
    @property
    def is_external(self) -> bool:
        return self.url.startswith("http")
    
    @property
    def icon_template(self) -> str:
        return f"icons/{self.icon}.svg"