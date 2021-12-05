from django.contrib import admin
from .models import Ballot, Question, Choice, VoteRecord

# Register your models here.

admin.site.site_header = "Ballot Creation Admin"
admin.site.site_title = "Admin Area"
admin.site.index_title = "Welcome Admin Area"


class BallotsAdmin(admin.ModelAdmin):
    fieldsets = [(None, {'fields': ['ballot_title', 'ballot_description']}),
                 ('Date Information', {'fields': ['pub_date', 'due_date']}),
                 (None, {'fields': ['district']})]


class QuestionAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["ballot", "question_text"]  # Once the ballot is chosen it cannot be change
        else:
            return []


class ChoiceAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["question", "choice_text", "votes"]  # Once the question is chosen it cannot change
        else:
            return ["votes"]  # Makes the vote field readonly. The admins can not edit it


admin.site.register(Choice, ChoiceAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Ballot, BallotsAdmin)