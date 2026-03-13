from django.shortcuts import render


def cro_b1(request):
    return render(request, 'compliance/cro_b1.html')


def ct1(request):
    return render(request, 'compliance/ct1.html')


def vat(request):
    return render(request, 'compliance/vat.html')


def rbo(request):
    return render(request, 'compliance/rbo.html')


def paye(request):
    return render(request, 'compliance/paye.html')


def calendar(request):
    return render(request, 'compliance/calendar.html')


def history(request):
    return render(request, 'compliance/history.html')
