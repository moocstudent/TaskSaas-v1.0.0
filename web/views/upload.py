from django.http import HttpResponse
from rest_framework import views
from rest_framework.parsers import FileUploadParser


class FileUploadView(views.APIView):
    parser_classes = [FileUploadParser]

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        # ...
        # do some stuff with uploaded file
        # ...
        return HttpResponse(status=204)
