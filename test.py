import os
import sys
import random
import string
import getopt
from test_captcha import ImageCaptcha
from datetime import datetime

arguments = len(sys.argv)
print("Total arguments passed: ", arguments)
print("Name of Python script: ", sys.argv[0])

inputs = sys.argv[1].split()
print(inputs)
inputs_length = len(inputs)
optlist, args = getopt.getopt(inputs, '', ['text=', 'rotate='])
print(optlist)


def random_string():
    random_letters = (random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return "".join(random_letters)


text = ''
is_rotate = ''

for opt, arg in optlist:
    if opt == '--text':
        text = arg
    if opt == '--rotate':
        is_rotate = arg
        if is_rotate == '' or is_rotate == '0' \
                or is_rotate == 'F' or is_rotate == 'false':
            is_rotate = 0
        if is_rotate == '1' or is_rotate == 'T' or is_rotate == 'true':
            is_rotate = 1

text_length = len(text)
if text_length:
    captcha = text
else:
    captcha = random_string()

print(captcha)
# print(type(is_rotate))

image = ImageCaptcha(fonts=['./data/DroidSansMono.ttf'])

created_date = datetime.now().strftime("%c")
converted_date = int(datetime.strptime(created_date, "%c").timestamp())
image_name = 'captcha_' + str(converted_date)
image_dir = 'images/normal/'
abs_image_path = os.path.join(image_dir, image_name + ".png")

image.write(captcha.upper(), abs_image_path, is_rotate)
