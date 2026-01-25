from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Topics)
admin.site.register(models.Entry)
