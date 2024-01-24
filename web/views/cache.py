from django.core.cache import cache
from django.http import JsonResponse


def cache_set(request,project_id):
    trigger = request.POST.get("trigger")
    cache.set('mytaskTrigger'+str(request.web.user.id)+'_'+str(project_id), trigger, timeout=None)
    return JsonResponse({'code':1})

def attention_cache_set(request,project_id):
    trigger = request.POST.get("trigger")
    cache.set('myAttentionTrigger'+str(request.web.user.id)+'_'+str(project_id), trigger, timeout=None)
    return JsonResponse({'code':1})

def day_cache_set(request,project_id):
    trigger = request.POST.get("trigger")
    print('day_cache_set pid ',project_id)
    print("'mydayTrigger'+str(request.web.user.id)+'_'+str(project_id)>",'mydayTrigger'+str(request.web.user.id)+'_'+str(project_id))
    print('trigger>',trigger)
    cache.set('mydayTrigger'+str(request.web.user.id)+'_'+str(project_id), trigger, timeout=None)
    print(cache.get('mydayTrigger' + str(request.web.user.id) + '_' + str(project_id)))
    return JsonResponse({'code':1})

def main_echart_legend_cache_set(request,project_id):
    trigger = request.POST.get("trigger")
    cache.set('mainLegendTrigger'+str(request.web.user.id)+'_'+str(project_id), trigger, timeout=None)
    return JsonResponse({'code':1})
def echart_legend_cache_set(request,project_id):
    trigger = request.POST.get("trigger")
    cache.set('myechartlegendTrigger'+str(request.web.user.id)+'_'+str(project_id), trigger, timeout=None)
    return JsonResponse({'code':1})


#因为是打开新页面，所以这个可没有
# def issues_status_cache_set(request):
#     print('id>>>',request.web.user.id)
#     trigger = request.POST.get("trigger")
#     print(trigger)
#     cache.set(str(request.web.user.id)+'myissuesStatusTrigger', trigger, timeout=None)
#     print(cache.get(str(request.web.user.id)+'myissuesStatusTrigger'))
#     return JsonResponse({'code':1})