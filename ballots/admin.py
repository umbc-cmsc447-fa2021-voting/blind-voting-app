from django.contrib import admin
from .models import Ballot, Question, Choice

# Register your models here.

admin.site.site_header = "Ballot Creation Admin"
admin.site.site_title = "Admin Area"
admin.site.index_title = "Welcome Admin Area"

class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionInLine(admin.TabularInline):
    model = Question
    extra = 1

class BallotsAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['ballot_title']}), ('Date Information', {'fields': ['pub_date']}), ]
    inlines = [QuestionInLine, ChoiceInLine]

admin.site.register(Ballot, BallotsAdmin)