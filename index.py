import random
import string
from PIL import Image
from claptcha.claptcha import Claptcha


def randomString():
    rdLetters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(rdLetters)


c = Claptcha(randomString, "./data/DroidSansMono.ttf", (150, 60),
             resample=Image.BICUBIC, noise=0.5)

text, _ = c.write("./output/captcha1.png")
print(text)

text, _ = c.write("./output/captcha2.png")
print(text)

c.size = (150, 90)
c.margin = (25, 25)

text, _ = c.write("./output/captcha3.png")
print(text)
