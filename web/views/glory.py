from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView

from web.forms.glory import GloryModelForm
from web.models import Glory


def glory_detail(request,glory_id):
    if (glory_id):
        glory = Glory.objects.filter(id=glory_id).first()
        return render(request, 'web/glory_detail.html', {'glory': glory})
    raise Exception("can not get id")

class GloryAPI(APIView):
    def get(self,request,format=None):

        glorys =  Glory.objects.all()
        # context = {
        #     'glory_names':glory_names
        # }
        form = GloryModelForm(request, data=request.POST,user=request.web.user)
        return render(request, 'web/glory_list.html', {'form': form, 'glorys': glorys})

    def get_object(self,request):
        glory_id = request.GET.get('glory_id')
        print('glory_id ',glory_id)
        return JsonResponse({'status':1})

    def post(self,request):
        form = GloryModelForm(request, data=request.POST,user=request.web.user)
        if form.is_valid():
            instance = form.save()
            return JsonResponse({'status': True, })
        return JsonResponse({'status': False, 'error': form.errors})

    # def get
