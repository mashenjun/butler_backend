
import requests
import base64
from rest_framework.validators import UniqueValidator

from rest_framework import generics,views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FileUploadParser,MultiPartParser
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import status
from rest_framework.exceptions import ValidationError
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
    FAKE_IMG_URL,
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

        try:
            serializer.is_valid(raise_exception=True)
            superMarket = serializer.validated_data.get('superMarket')
            img = serializer.validated_data.get('picFile')
            picFile = (img.name, img, img.content_type)
            files = {'picFile': picFile}
            response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', superMarket)], files=files)
            result = {
                "pic_url":FAKE_IMG_URL,
                "result":response.json()
            }
            return Response(result, status=response.status_code)


        except ValidationError as e:
            # for key in serializer.errors:
            #     print("key: %s , value: %s" % (key, serializer.errors[key][0]))
            errorsmessage = {k:serializer.errors[k][0] for k in serializer.errors}
            response_data_fail = {
                'errormessage': errorsmessage
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



