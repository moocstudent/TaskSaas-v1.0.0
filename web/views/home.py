from django.shortcuts import render


def index(request):
    return render(request, 'web/index.html')

def help(request):
    return render(request, 'web/help.html')
