from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    fieldsets = [(None, {'fields': ['middle_name', 'ssn', 'district', 'birth_date', 'sign']})]
    verbose_name = 'profile'
    verbose_name_plural = 'profiles'

class UserAdmin(DjangoUserAdmin):
    inlines = [ProfileInline]
    add_fieldsets = DjangoUserAdmin.add_fieldsets + ((None, {'fields': ['email']}),)
    list_display = ('username', 'email', 'last_name', 'first_name', 'middle_name', 'ssn', 'district', 'is_staff')

    def middle_name(self, obj):
        return Profile.objects.get(user=obj).middle_name

    def district(self, obj):
        return Profile.objects.get(user=obj).district

    def ssn(self, obj):
        return Profile.objects.get(user=obj).ssn

admin.site.unregister(User)
admin.site.register(User, UserAdmin)