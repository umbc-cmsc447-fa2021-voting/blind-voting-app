from django.shortcuts import render

def password_reset(request):
    return render(request, 'password_reset.html')