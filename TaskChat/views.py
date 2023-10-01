from django.shortcuts import render


def index(request):
    return render(request, 'web/chat/index.html', {})


def room(request, room_name):
    return render(request, 'web/chat/room.html', {
        'room_name': room_name
    })
