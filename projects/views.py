from django.shortcuts import render


def active(request):
    return render(request, 'projects/active.html')


def tasks(request):
    return render(request, 'projects/tasks.html')


def timeline(request):
    return render(request, 'projects/timeline.html')


def resources(request):
    return render(request, 'projects/resources.html')
