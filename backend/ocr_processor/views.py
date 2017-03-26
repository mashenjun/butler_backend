
import requests
import base64
import mimetypes
import urllib.request
import urllib.parse
import urllib.error
import time

from rest_framework import generics,views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FileUploadParser,MultiPartParser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly
)

from backend.config import (
    OCR_HOST,
    OCR_KEY,
    DEBUG_URL,
)

from .serializers import receiptSerializer
from ocr_processor.utils import createLogger
# Create your views here.

logger = createLogger(__name__);



class receiptCreateView(generics.CreateAPIView):
    """
    Returns a list of all authors.
    """
    serializer_class = receiptSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,)
        logger.debug(request.data)
        try:
            serializer.is_valid()
            superMarket = serializer.validated_data.get('superMarket')
            img = serializer.validated_data.get('picFile')
            picFile = (img.name, img, 'image/jpeg')
            files = {'picFile': picFile}
            response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', superMarket)], files=files)
            return Response(response.text, status=response.status_code)
        except:
            pass
        errors = serializer.errors
        response_data_fail = {
            'errormessage': errors
        }
        return Response(response_data_fail, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def ocr_proxy(request):

    image_file = open("test_img2.jpg", "rb")
    # with open("test_img1.jpg", "rb") as image_file:
    encoded_img = base64.b64encode(image_file.read())
    encoded_file = b'data:image/jpg;base64,'+encoded_img
    # print("[DEBUG: {0}]".format(encoded_file))
    img = (image_file.name,image_file,'image/jpeg')
    key = (None, OCR_KEY)
    superMarket = (None, 'Kaufland')

    # payload = {'key': key,'superMarket':'Kaufland'}
    # response = requests.post(OCR_HOST, files={'key': key, 'superMarket': superMarket,'picFile':img} )
    # response = requests.post("https://www.google.nl/")
    with open('test_img2.jpg', 'rb') as f:
        img = (f.name, f, 'image/jpeg')
        files = {'picFile':img}
        response = requests.post(OCR_HOST, data=[('key',OCR_KEY),('superMarket','Kaufland')],files=files)
        # print("[DEBUG: {0}]".format(response.request.headers))
    return Response(response.text, status=response.status_code)



