import os
import random
import string
from split_captcha import ImageCaptcha


def random_string():
    random_letter = (random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return ''.join(random_letter)


captcha = random_string()
print(captcha)

img = ImageCaptcha(fonts=['../data/DroidSansMono.ttf'])
image_name = 'split_captcha_test.png'
image_dir = '../images/split'
abs_image_path = os.path.join(image_dir, image_name)
img.write(captcha, abs_image_path)
