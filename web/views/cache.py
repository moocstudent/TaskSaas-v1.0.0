from django.core.cache import cache
from django.http import JsonResponse


def cache_set(request):
    trigger = request.POST.get("trigger")
    cache.set('mytaskTrigger', trigger, timeout=None)
    print(cache.get('mytaskTrigger'))
    return JsonResponse({'code':1})
