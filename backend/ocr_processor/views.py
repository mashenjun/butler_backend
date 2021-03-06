import requests,base64,uuid,os,time
from multiprocessing.pool import ThreadPool


from rest_framework.validators import UniqueValidator
from rest_framework import generics,views
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import FileUploadParser,MultiPartParser,JSONParser
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


from django.db import connection
from django.core.files.base import ContentFile


import boto3
from botocore.config import Config
from PIL import Image

from .models import (
    Person,
    ProcessedReceipt,
)
from backend.config import (
    OCR_HOST,
    OCR_KEY,
    DEBUG_URL,
    FAKE_IMG_URL,
    BUCKET_NAME,
)
from .serializers import (
    receiptSerializer,
    PersonCreateSerializer,
    processedReceiptSerializer
)
from ocr_processor.utils import (
    createLogger,
    ocr_space_url,
    ocr_space_file,
)


import Levenshtein

# Create your views here.
logger = createLogger(__name__);


def sendtoOCR(superMarket,img):
    # the data is just a response data
    superMarket = superMarket
    # superMarket = data.get('superMarket')
    # img = data.get('picFile')
    picFile = (img.name, img, img.content_type)
    files = {'picFile': picFile}
    response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', superMarket)], files=files)
    return response


def sendtoS3(supermarket,img):
    superMarket = supermarket
    # s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    s3 = boto3.client('s3')
    s3_filename = os.path.join(superMarket, '{}_{}.{}'.format(uuid.uuid4().hex, '0', 'jpg'))
    # s3.upload_fileobj(img, BUCKET_NAME, s3_filename,
    #                   ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'})
    s3.put_object(ACL='public-read',Body = img,ContentType = "image/jpeg",Bucket = BUCKET_NAME,Key = s3_filename)
    bucket_location = s3.get_bucket_location(Bucket=BUCKET_NAME)
    url = "https://s3-{0}.amazonaws.com/{1}/{2}".format(
        bucket_location['LocationConstraint'],
        BUCKET_NAME,
        s3_filename)

    return url


class receiptCreateView(generics.CreateAPIView):
    """
    Returns a processed OCR result in json format for the given image.
    """
    serializer_class = receiptSerializer
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser,JSONParser)

    def post(self, request, *args, **kwargs):
        # s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        # bucket = s3.Bucket(BUCKET_NAME)
        serializer = self.get_serializer(data=request.data,)

        try:
            serializer.is_valid(raise_exception=True)
            superMarket = serializer.validated_data.get('superMarket').lower()
            img = serializer.validated_data.get('picFile')
            # img = ContentFile(serializer.validated_data.get('picFile').read())
            # picFile = (img.name, img, img.content_type)
            # files = {'picFile': picFile}
            # use thread to send to OCR
            # img.seek(0, os.SEEK_SET)
            start = time.time()
            url = sendtoS3(superMarket, img)
            end = time.time()
            elapsed = end - start
            print(elapsed)
            img.seek(0, os.SEEK_SET)
            # pool = ThreadPool(processes=1)
            # async_result = pool.apply_async(sendtoS3, args = (superMarket, img))

            # response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', superMarket)], files=files)
            # use thread to upload image to S3
            # s3_filename = os.path.join(superMarket, '{}_{}.{}'.format(uuid.uuid4().hex,'0','jpg'))
            # s3.upload_fileobj(img, BUCKET_NAME, s3_filename, ExtraArgs={'ACL':'public-read','ContentType':'image/jpeg'})
            # bucket.put_object(ACL='public-read',Body=img)
            # bucket.upload_fileobj(img, s3_filename, ExtraArgs={'ACL':'public-read','ContentType':'image/jpeg'})
            # bucket_location = s3.get_bucket_location(Bucket=BUCKET_NAME)
            start = time.time()
            processedResult = sendtoOCR(serializer.validated_data.get('superMarket'), img)
            end = time.time()
            elapsed = end - start
            print(elapsed)
            # url = async_result.get()
            if(len(processedResult.content)==0):
                processedResult_json = {}
            else:
                processedResult_json = processedResult.json()

            img.close()
            # TODO do correction

            with connection.cursor() as cursor:
                # cursor.execute("SELECT production FROM production WHERE store = %s", [superMarket])
                try:
                    query = "SELECT name FROM {0}".format(superMarket)
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    for item in processedResult_json.get('items'):
                        name = item.get('name')
                        corrected_name = name
                        temp_diff = 0.0
                        # logger.debug(name)
                        # diff_list = [Levenshtein.ratio(name.lower(),k[0].lower()) for k in rows]
                        # logger.debug(min(diff_list))
                        for prod in rows :
                            diff = Levenshtein.ratio(name.lower(),prod[0].lower())
                            if (diff>temp_diff):
                                temp_diff = diff
                                corrected_name = prod[0]
                        # logger.debug('{0},{1},{2}'.format(name, corrected_name, temp_diff))
                        item['name'] = corrected_name
                except:
                    pass

            result = {
                "pic_url":url,
                "result":processedResult_json
            }
            return Response(result,status = processedResult.status_code )

        except ValidationError as e:
            # for key in serializer.errors:
            #     print("key: %s , value: %s" % (key, serializer.errors[key][0]))
            errorsmessage = {k:serializer.errors[k][0] for k in serializer.errors}
            response_data_fail = {
                'errormessage': errorsmessage
            }
            return Response(response_data_fail, status=status.HTTP_400_BAD_REQUEST)

class PersonListCreateView(generics.ListCreateAPIView):
    serializer_class = PersonCreateSerializer
    permission_classes = [AllowAny]
    queryset = Person.objects.all()

class processedReceiptCreateView(generics.ListCreateAPIView):
    serializer_class = processedReceiptSerializer
    permission_classes = [AllowAny]
    queryset = ProcessedReceipt.objects.all()

    def post(self, request, *args, **kwargs):
        logger.debug(request.data)
        return self.create(request, *args, **kwargs)


@api_view(['GET','POST'])
@permission_classes([AllowAny])
def ocr_proxy(request):

    # image_file = open("test_img2.jpg", "rb")
    # # with open("test_img1.jpg", "rb") as image_file:
    # encoded_img = base64.b64encode(image_file.read())
    # encoded_file = b'data:image/jpg;base64,'+encoded_img
    # # print("[DEBUG: {0}]".format(encoded_file))
    # img = (image_file.name,image_file,'image/jpeg')
    # key = (None, OCR_KEY)
    # superMarket = (None, 'Kaufland')

    # payload = {'key': key,'superMarket':'Kaufland'}
    # response = requests.post(OCR_HOST, files={'key': key, 'superMarket': superMarket,'picFile':img} )
    # response = requests.post("https://www.google.nl/")
    with open('test.jpg', 'rb') as f:
        img = (f.name, f, 'image/jpeg')
        files = {'picFile':img}
        response = requests.post(OCR_HOST, data=[('key',OCR_KEY),('superMarket','Kaufland')],files=files)
        # print("[DEBUG: {0}]".format(response.request.headers))
    return Response(response.text, status=response.status_code)





