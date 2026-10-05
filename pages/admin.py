from django.contrib import admin

from .models import SocialLink

@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ["platform", "icon", "label", "url", "order"]
    list_editable = ["icon", "order"]