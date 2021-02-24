import os
import math
import random
import string
from PIL import Image, ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from io import BytesIO
from datetime import datetime

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]
FONT_SIZE = 70

table = []
for i in range(256):
    table.append(i)


class Captcha(object):
    def generate(self, chars, format='png'):
        im = self.generate_image(chars)
        out = BytesIO()
        im.save(out, format=format)
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        im = self.generate_image(chars)
        return im.save(output, format=format)


class ImageCaptcha(Captcha):
    def __init__(self, width=270, height=100, fonts=None, font_sizes=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS
        self._font_sizes = font_sizes or FONT_SIZE
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, FONT_SIZE)
            for n in self._fonts
        ])
        return self._truefonts

    @staticmethod
    def create_noise_chars_using_mask(image, char, number):
        width, height = image.size
        font = truetype('../data/DroidSansMono.ttf', 30)
        draw = Draw(image)
        w, h = draw.textsize(char, font=font)

        x = random.randint(0, int(8 * width / 9))
        y = random.randint(0, int(7 * height / 10))

        while number:
            im = Image.new('RGBA', (w, h))

            color = random_color(10, 200, random.randint(220, 255))

            dx = 0
            dy = 0

            Draw(im).text((dx, dy), char, font=font, fill=color)
            Draw(im).text((dx + 1, dy + 1), char, font=font, fill=color)
            Draw(im).text((dx - 1, dy - 1), char, font=font, fill=color)

            im = im.rotate(random.uniform(-45, 45), Image.BILINEAR, expand=1)
            im = im.crop(im.getbbox())

            mask = im.convert('L').point(table)

            image.paste(im, (x, y), mask=mask)
            number -= 1

        return image

    @staticmethod
    def create_noise_chars_without_mask(image, char, number):
        w, h = image.size
        font = truetype('../data/DroidSansMono.ttf', 30)
        draw = Draw(image)

        while number:
            x = random.randint(0, int(8 * w / 9))
            y = random.randint(0, int(7 * h / 10))

            color = random_color(10, 200, random.randint(220, 225))

            draw.text((x, y), char, fill=color, font=font)
            draw.text((x + 1, y + 1), char, fill=color, font=font)
            draw.text((x - 1, y - 1), char, fill=color, font=font)
            number -= 1

        return image

    def create_captcha_image(self, chars, background):
        image = Image.new('RGB', (self._width, self._height), background)
        draw = Draw(image)

        def draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)
            color = random_color(10, 200, random.randint(220, 225))
            bold_width = 3

            dx = 0
            dy = 0

            im = Image.new('RGBA', (w + bold_width, h + bold_width))

            Draw(im).text((dx, dy), c, font=font, fill=color)
            Draw(im).text((dx + 1, dy + 1), c, font=font, fill=color)
            Draw(im).text((dx - 1, dy - 1), c, font=font, fill=color)

            im = im.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)
            im = im.crop(im.getbbox())

            alpha = im.convert('RGBA').split()[-1]
            bg = Image.new('RGBA', im.size, background + (255,))
            self.create_noise_chars_using_mask(bg, random.choice(chars), 1)
            bg.paste(im, mask=alpha)

            im = bg

            # wrap
            x = int(dx)
            y = int(dy)
            w2 = w + abs(x)
            h2 = h + abs(y)

            data = (x, y,
                    -x, h2 - y,
                    w2 + x, h2 + y,
                    w2 - x, -y)

            im = im.resize((w2, h2))
            im = im.transform((w, h), Image.QUAD, data)
            return im

        images = []
        for c in chars:
            images.append(draw_character(c))

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        offset = int(average * 0.1)

        for im in images:
            w, h = im.size
            image.paste(im, (offset, int((self._height - h) / 2)), mask=None)
            offset += w

        if width > self._width:
            image = image.resize((self._width, self._height))

        return image

    def generate_image(self, chars):
        background = (255, 255, 255)
        # text_color = (0, 0, 0)
        im = self.create_captcha_image(chars, background)
        for c in chars:
            self.create_noise_chars_using_mask(im, c, 1)
            self.create_noise_chars_without_mask(im, c, 1)
        im = im.filter(ImageFilter.SMOOTH)
        return im


def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return red, green, blue
    return red, green, blue, opacity


def random_string():
    random_letter = (random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return ''.join(random_letter)


captcha = random_string()
print(captcha)

img = ImageCaptcha(fonts=['../data/DroidSansMono.ttf'])

created_date = datetime.now().strftime("%c")
converted_date = int(datetime.strptime(created_date, "%c").timestamp())
image_name = "mass_captcha_" + str(converted_date) + ".png"
image_dir = '../images/mass'
abs_image_path = os.path.join(image_dir, image_name)
img.write(captcha, abs_image_path)
