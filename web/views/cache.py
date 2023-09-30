from django.core.cache import cache
from django.http import JsonResponse


def cache_set(request):
    trigger = request.POST.get("trigger")
    cache.set('mytaskTrigger', trigger, timeout=None)
    print(cache.get('mytaskTrigger'))
    return JsonResponse({'code':1})

def day_cache_set(request):
    trigger = request.POST.get("trigger")
    cache.set('mydayTrigger', trigger, timeout=None)
    print(cache.get('mydayTrigger'))
    return JsonResponse({'code':1})

def echart_legend_cache_set(request):
    trigger = request.POST.get("trigger")
    cache.set('myechartlegendTrigger', trigger, timeout=None)
    print(cache.get('myechartlegendTrigger'))
    return JsonResponse({'code':1})