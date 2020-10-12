import os
import sys
import random
import string
from normal_captcha import ImageCaptcha
from datetime import datetime

arguments = len(sys.argv)
print("Total arguments passed: ", arguments)
print("Name of Python script: ", sys.argv[0])

inputs = sys.argv[1].split(",")
inputs_length = len(inputs)
print(inputs)


def random_string():
    random_letters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(random_letters)


text_length = len(inputs[0])

if text_length:
    text = inputs[0]
else:
    text = random_string()
print(text)

options = []
for i in range(1, inputs_length):
    if inputs[i] == '':
        inputs[i] = '0'

    option = int(inputs[i])
    options.append(option)

is_noise_dots = options[0]
is_noise_curve = options[1]
print(options)

image = ImageCaptcha(fonts=['./data/DroidSansMono.ttf'])

created_date = datetime.now().strftime("%c")
converted_date = int(datetime.strptime(created_date, "%c").timestamp())
image_name = 'captcha_' + str(converted_date)
image_dir = 'images/normal/'
abs_image_path = os.path.join(image_dir, image_name + ".png")

image.write(text.upper(), abs_image_path, is_noise_dots, is_noise_curve)
