from django.shortcuts import render

def chat(request):
    return render(request, 'web/chat/index.html')