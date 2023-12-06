from django.http import JsonResponse


def calendar_time_range_export_works(request,project_id):
    time_range = request.POST.get('time_range')
    # 导出对应时间区间的（工作）数据

    return JsonResponse({'status':1})


def calendar_time_range_export_tasks(request, project_id):
    time_range = request.POST.get('time_range')
    # 导出对应时间区间的（工作）数据

    return JsonResponse({'status': 1})