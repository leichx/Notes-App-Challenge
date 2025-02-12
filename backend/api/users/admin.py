from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Profile
from api.users.models import Category


class ProfileInline(admin.StackedInline):
    """
    Profile inline for UserAdmin
    """
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    """
    User admin
    """
    inlines = (ProfileInline,)
    list_display = ('email', 'first_name', 'last_name', 'is_staff')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    list_filter = ()
    search_fields = ('name',)
    ordering = ('name',)