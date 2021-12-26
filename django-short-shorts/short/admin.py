from django.contrib import admin

# Register your models here.
from .models import grab_models

def register_models(models, ignore=None):
    return admin.site.register(grab_models(models, ignore=ignore))
