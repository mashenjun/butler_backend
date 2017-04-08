import requests
import os

img_dir = []

dir_name = './Kaufland'
print(sorted(os.listdir(os.path.join(dir_name,'1'))))

for fn in os.listdir(dir_name):
        print(fn)
        if os.path.isdir(fn):
            print (fn)
# superMarket = data.get('superMarket')
# img = data.get('picFile')
# picFile = (img.name, img, img.content_type)
# files = {'picFile': picFile}
# response = requests.post(OCR_HOST, data=[('key', OCR_KEY), ('superMarket', superMarket)], files=files)


print('Hello, world!')




