import os
import random
import string
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from normal_captcha import ImageCaptcha
from datetime import datetime

image = ImageCaptcha(fonts=['./data/DroidSansMono.ttf'])


def randomString():
    rdLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(rdLetters)


text = randomString()
createdDate = datetime.now().strftime("%c")
convertedDate = int(datetime.strptime(createdDate, "%c").timestamp())
imageName = 'captcha' + str(convertedDate)
image_dir = './output/'
abs_image_path = os.path.join(image_dir, imageName + ".png")
image.write(text, abs_image_path)


img = mpimg.imread(abs_image_path)
imgplot = plt.imshow(img)
plt.show()