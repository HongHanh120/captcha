import os
import sys
import random
import string
import getopt
from normal_captcha import ImageCaptcha
from datetime import datetime

arguments = len(sys.argv)
print("Total arguments passed: ", arguments)
print("Name of Python script: ", sys.argv[0])

inputs = sys.argv[1].split()
print(inputs)
inputs_length = len(inputs)
optlist, args = getopt.getopt(inputs, '', ['text=', 'noise-dots=', 'noise-curve='])
print(optlist)
# print(args)


def random_string():
    random_letters = (random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return "".join(random_letters)


text = ''
is_noise_dots = ''
is_noise_curve = ''

for opt, arg in optlist:
    if opt == '--text':
        text = arg
    if opt == '--noise-dots':
        is_noise_dots = arg
        if is_noise_dots == '' or is_noise_dots == '0' \
                or is_noise_dots == 'F' or is_noise_dots == 'false':
            is_noise_dots = 0
        if is_noise_dots == '1' or is_noise_dots == 'T' or is_noise_dots == 'true':
            is_noise_dots = 1

    if opt == '--noise-curve':
        is_noise_curve = arg
        if is_noise_curve == '' or is_noise_curve == '0' \
                or is_noise_curve == 'F' or is_noise_curve == 'false':
            is_noise_curve = 0
        if is_noise_curve == '1' or is_noise_curve == 'T' or is_noise_curve == 'true':
            is_noise_curve = 1

text_length = len(text)

if text_length:
    captcha = text
else:
    captcha = random_string()


# print(captcha)
# print(is_noise_dots)
# print(is_noise_curve)

image = ImageCaptcha(fonts=['./data/DroidSansMono.ttf'])

created_date = datetime.now().strftime("%c")
converted_date = int(datetime.strptime(created_date, "%c").timestamp())
image_name = 'captcha_' + str(converted_date)
image_dir = 'images/normal/'
abs_image_path = os.path.join(image_dir, image_name + ".png")

image.write(captcha.upper(), abs_image_path, is_noise_dots, is_noise_curve)
