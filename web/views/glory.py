from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import APIView

from web.forms.glory import GloryModelForm
from web.models import Glory


class GloryAPI(APIView):
    def get(self,request,format=None):
        glorys =  Glory.objects.all()
        # context = {
        #     'glory_names':glory_names
        # }
        form = GloryModelForm(request, data=request.POST,user=request.web.user)
        return render(request, 'web/glory_list.html', {'form': form, 'glorys': glorys})

    def post(self,request):
        form = GloryModelForm(request, data=request.POST,user=request.web.user)
        if form.is_valid():
            instance = form.save()
            return JsonResponse({'status': True, })
        return JsonResponse({'status': False, 'error': form.errors})
