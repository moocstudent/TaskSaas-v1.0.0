from datetime import datetime
from io import BytesIO

from django.db.models import Q
from django.http import JsonResponse, HttpResponse

from web.models import WorkRecord
import xlwt
import urllib.parse

# def calendar_time_range_export_works(request,project_id):
#     time_range = request.POST.get('time_range')
#     # 导出对应时间区间的（工作）数据
#
#     return JsonResponse({'status':1})

def calendar_time_range_export_works(request,project_id):
    print('calendar_time_range_export_works')
    begin_time = request.GET.get("begin_time")
    end_time = request.GET.get("end_time")
    start_date = datetime.strptime(begin_time, '%Y-%m-%d')
    end_date = datetime.strptime(end_time, '%Y-%m-%d')
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('工作记录表')
    # 查询所有老师的信息
    queryset = WorkRecord.objects.filter(Q(calendar_day_date__range=(start_date,end_date)),Q(user=request.web.user),Q(project=request.web.project))
    # 向Excel表单中写入表头
    colnames = ('日期','内容')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    # 向单元格中写入老师的数据
    props = ('calendar_day','content')
    for row, record in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(record, prop, '')
            sheet.write(row + 1, col, value)
    # 保存Excel
    buffer = BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    # 中文文件名需要处理成百分号编码
    filename = urllib.parse.quote('工作内容'+begin_time+'-'+end_time+'.xls')
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
    print('resp:',resp)
    return resp


def calendar_time_range_export_tasks(request, project_id):
    time_range = request.POST.get('time_range')
    # 导出对应时间区间的（工作）数据

    return JsonResponse({'status': 1})

