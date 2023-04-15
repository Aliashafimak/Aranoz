from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account,Address


# Register your models here.

class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'username', 'last_login', 'date_joined', 'is_active')
    list_display_links = ('email', 'first_name', 'last_name')#to go inside when we click on name
    readonly_fields = ('last_login', 'date_joined')#search
    ordering = ('-date_joined',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
admin.site.register(Account, AccountAdmin)    



admin.site.register(Address)
class Address(admin.ModelAdmin):     
    list_display: tuple(('user','city','district','state','country'))
    
from .models import Account, UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    # def thumbnail(self, object):
    #     return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    # thumbnail.short_description = 'Profile Picture'
    list_display = ( 'user', 'city', 'state', 'country')


admin.site.register(UserProfile, UserProfileAdmin)