#-*- coding: UTF-8 -*-
import requests
import os

from backend.config import (
    OCR_HOST,
    OCR_KEY,
    DEBUG_URL,
    FAKE_IMG_URL,
    BUCKET_NAME,
)

img_dirs = list(map(str,list(range(1,2))))
dir_name = 'Kaufland'

# for dir in img_dirs:
#     img_names = sorted(os.listdir(os.path.join('.',dir_name,dir)))
#     for idx,file in enumerate(img_names):
#         img_name = os.path.join('.',dir_name,dir,file)
#         record_name = '{}_{}_{}'.format(dir_name,dir,idx)
#         print(img_name)
#         with open(img_name,'rb') as f:
#             img = (file, f, 'image/jpeg')
#             print(file)
#             files = {'picFile': img}
#             response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', dir_name)], files=files)
#             print(response.text)

with open('./Kaufland/1/新文档 2017-03-12 20.50.36_1.jpg', 'rb') as f:
    img = (f.name, f, 'image/jpeg')
    files = {'picFile': img}
    response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', 'Kaufland')], files=files)
    print(response.text)
    print(response.encoding)

print('END')




