import random
import string
from normal_captcha import ImageCaptcha
from datetime import datetime

image = ImageCaptcha(fonts=['./data/DroidSansMono.ttf'])


def randomString():
    rdLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(rdLetters)


text = randomString()
print(text)
createdDate = datetime.now().strftime("%c")
convertedDate = int(datetime.strptime(createdDate, "%c").timestamp())
imageName = 'captcha' + str(convertedDate)
image.write(text, './output/' + imageName + '.png')
