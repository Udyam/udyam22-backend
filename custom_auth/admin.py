from django.contrib import admin

# Register your models here.
from custom_auth.models import UserAccount, ProfileImages

admin.site.register(UserAccount)
admin.site.register(ProfileImages)
