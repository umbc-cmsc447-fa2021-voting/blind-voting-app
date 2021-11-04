from django.contrib import admin
from .models import Ballot, Question, Choice

# Register your models here.

admin.site.site_header = "Ballot Creation Admin"
admin.site.site_title = "Admin Area"
admin.site.index_title = "Welcome Admin Area"

class BallotsAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['ballot_title', 'ballot_description']}),
                 ('Date Information', {'fields': ['pub_date', 'due_date']}),
                 (None, {'fields': ['district']}), (None, {'fields': ['slug']})]

admin.site.register(Choice)
admin.site.register(Question)
admin.site.register(Ballot, BallotsAdmin)