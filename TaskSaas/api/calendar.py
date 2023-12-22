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
    # 创建居中对齐格式
    alignment = xlwt.Alignment()
    alignment.horz = 0x02
    alignment.vert = 0x01
    alignment.wrap = 0x01

    alignment_right = xlwt.Alignment()
    alignment_right.horz = 0x03
    alignment_right.vert = 0x01

    # 初始化样式
    style0 = xlwt.XFStyle()
    style0.alignment = alignment
    # 首行加粗、字体放大
    font = xlwt.Font()
    font.height = 20 * 12  # 12为字号，20为衡量单位
    font.bold = True
    style1 = xlwt.XFStyle()
    style1.font = font
    style1.alignment = alignment

    font_title = xlwt.Font()
    font_title.height = 20 * 18
    font_title.bold = True

    style_title = xlwt.XFStyle()
    style_title.font = font_title
    style_title.alignment = alignment

    pattern0 = xlwt.Pattern()  #
    pattern0.pattern = xlwt.Pattern.SOLID_PATTERN  #
    pattern0.pattern_fore_colour = 5  #

    pattern1 = xlwt.Pattern()  #
    pattern1.pattern = xlwt.Pattern.SOLID_PATTERN  #
    pattern1.pattern_fore_colour = 2  #

    pattern2 = xlwt.Pattern()  #
    pattern2.pattern = xlwt.Pattern.SOLID_PATTERN  #
    pattern2.pattern_fore_colour = 1  #

    style_right = xlwt.XFStyle()
    style_right.alignment = alignment_right
    style_right.pattern=pattern2

    # style_color = xlwt.XFStyle()  # Create the Pattern
    # style_color.pattern = pattern

    # 添加工作表
    sheet = wb.add_sheet('工作记录表',cell_overwrite_ok=True)
    sheet.write_merge(0, 0, 0, 1, '工作周记录 '+ begin_time + ' 起',style=style_title)
    # 查询所有老师的信息
    queryset = WorkRecord.objects.filter(Q(calendar_day_date__range=(start_date,end_date)),
                                    Q(user=request.web.user),
                                    Q(project=request.web.project)).order_by('calendar_day_date')
    # 向Excel表单中写入表头
    colnames = ('日期','内容')
    for index, name in enumerate(colnames):
        if index==0:
            style1.pattern = pattern0
        else:
            style1.pattern = pattern1
        sheet.write(1, index, name,style=style1)
    sheet.col(0).width = 256 * 20
    sheet.col(1).width = 512 * 40

    # 向单元格中写入老师的数据
    props = ('calendar_day','content')
    row_end = 0
    for row, record in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(record, prop, '')
            the_row = row+2
            row_end = the_row
            sheet.write(the_row, col, value,style=style0)
    print('row_end:',row_end)
    sheet.write_merge(row_end+3, row_end+3, 0, 1, '本记录使用TaskSaas生成导出',style=style_right)

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

