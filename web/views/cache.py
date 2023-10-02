import json

from django.core.cache import cache
from django.http import JsonResponse


def cache_set(request):
    trigger = request.POST.get("trigger")
    cache.set(str(request.web.user.id)+'mytaskTrigger', trigger, timeout=None)
    print(cache.get(str(request.web.user.id)+'mytaskTrigger'))
    return JsonResponse({'code':1})

def day_cache_set(request):
    trigger = request.POST.get("trigger")
    cache.set(str(request.web.user.id)+'mydayTrigger', trigger, timeout=None)
    print(cache.get(str(request.web.user.id)+'mydayTrigger'))
    return JsonResponse({'code':1})

def echart_legend_cache_set(request):
    print('id>>>',request.web.user.id)
    trigger = request.POST.get("trigger")
    print(trigger)
    cache.set(str(request.web.user.id)+'myechartlegendTrigger', trigger, timeout=None)
    print(cache.get(str(request.web.user.id)+'myechartlegendTrigger'))
    return JsonResponse({'code':1})


#因为是打开新页面，所以这个可没有
# def issues_status_cache_set(request):
#     print('id>>>',request.web.user.id)
#     trigger = request.POST.get("trigger")
#     print(trigger)
#     cache.set(str(request.web.user.id)+'myissuesStatusTrigger', trigger, timeout=None)
#     print(cache.get(str(request.web.user.id)+'myissuesStatusTrigger'))
#     return JsonResponse({'code':1})