import os
import random
from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from io import BytesIO  # for Python3

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]
FONT_SIZE = 45

table = []
for i in range(256):
    table.append(i)


class Captcha(object):
    def generate(self, chars, is_rotate, format='png'):
        """generate an images captcha of given characters"""
        """chars: text to be generated
            format: images file format"""
        im = self.generate_image(chars, is_rotate)
        """create BytesIO like file object"""
        out = BytesIO()
        im.save(out, format=format)
        """return back to the start"""
        out.seek(0)
        return out

    def write(self, chars, output, is_rotate, format='png'):
        im = self.generate_image(chars, is_rotate)
        return im.save(output, format=format)


def create_rotate_character(image):
    image.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)
    return image


class ImageCaptcha(Captcha):
    """ create an images captcha """

    def __init__(self, width=160, height=60, fonts=None, font_sizes=None):
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
        """truetype returns a font object"""
        return self._truefonts

    def create_captcha_image(self, chars, color, background, is_rotate):
        image = Image.new('RGB', (self._width, self._height), background)
        """mode RGB 3x8-bit pixels, true color
            size 2 tuple, containing (width, height) in pixels
            color = background"""
        draw = Draw(image)

        def draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)

            # dx = random.randint(0, 4)
            # dy = random.randint(0, 6)
            dx = 0
            dy = 0
            """RGBA 4x8-bit pixels, true color with transparency mask"""
            im = Image.new('RGBA', (w + dx, h + dy))
            Draw(im).text((dx, dy), c, font=font, fill=color)

            # rotate
            im = im.crop(im.getbbox())
            if is_rotate == 1:
                create_rotate_character(im)
            """getbbox calculates the bounding box of the images"""

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
            """(w, h) the normal size
                Image.QUAD the transformation method -> data"""
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
            mask = im.convert('L').point(table)
            """
            convert im to table with mode L 
            and maps this images through a lookup table
            mode L 8 pixels, black and white """
            image.paste(im, (offset, int((self._height - h) / 2)), mask)
            """paste another images into an images
                offset = x coordinate in upper left
                int((self._height - h) / 2)) = y coordinate in upper left
                box = (x, y)"""
            offset = offset + w

        if width > self._width:
            image = image.resize((self._width, self._height))

        return image

    def generate_image(self, chars, is_rotate):
        background = (255, 255, 255, 0)
        color = random_color(10, 200, random.randint(220, 255))
        im = self.create_captcha_image(chars, color, background, is_rotate)
        im = im.filter(ImageFilter.SMOOTH)
        return im


def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return red, green, blue
    return red, green, blue, opacity
