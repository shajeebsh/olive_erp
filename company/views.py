from django.shortcuts import render


def profile(request):
    return render(request, 'company/profile.html')
