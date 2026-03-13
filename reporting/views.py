from django.shortcuts import render


def index(request):
    return render(request, "reporting/index.html")


def builder(request):
    return render(request, "reporting/builder.html")


def saved(request):
    return render(request, "reporting/saved.html")


def scheduled(request):
    return render(request, "reporting/scheduled.html")


def datasources(request):
    return render(request, "reporting/datasources.html")
