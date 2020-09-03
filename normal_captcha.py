import os
import random
from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
from io import BytesIO  # for Python3

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]

table = []
for i in range(256):
    table.append(i)


class Captcha(object):
    def generate(self, chars, format='png'):
        """generate an images captcha of given characters"""
        """chars: text to be generated
            format: images file format"""
        im = self.generate_image(chars)
        """create BytesIO like file object"""
        out = BytesIO()
        im.save(out, format=format)
        """return back to the start"""
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        """Generate and write an images CAPTCHA data to the normal
            chars: text to be generated
            normal: normal destination
            format: images file format
        """
        im = self.generate_image(chars)
        return im.save(output, format=format)


class ImageCaptcha(Captcha):
    """ create an images captcha """

    def __init__(self, width=160, height=60, fonts=None, font_sizes=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS
        self._font_sizes = font_sizes or (42, 50, 56)
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        """truetype returns a font object"""
        return self._truefonts

    @staticmethod
    def create_noise_curve(image, color):
        w, h = image.size
        x1 = random.randint(0, int(w / 5))
        x2 = random.randint(w - int(w / 5), w)
        y1 = random.randint(int(h / 5), h - int(h / 5))
        y2 = random.randint(y1, h - int(h / 5))
        """points to define the bounding box"""
        points = [x1, y1, x2, y2]
        """ending angle (degrees)"""
        end = random.randint(160, 200)
        """starting angle (degrees)"""
        start = random.randint(0, 20)
        """draws an arc"""
        Draw(image).arc(points, start, end, fill=color)
        return image

    @staticmethod
    def create_noise_dots(image, color, width=2, number=35):
        w, h = image.size
        while number:
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            x2 = x1 + 1
            y2 = y1 + 1
            points = [x1, y1, x2, y2]
            Draw(image).line(points, fill=color, width=width)
            number -= 1
        return image

    def create_captcha_image(self, chars, color, background):
        image = Image.new('RGB', (self._width, self._height), background)
        """mode RGB 3x8-bit pixels, true color
            size 2 tuple, containing (width, height) in pixels
            color = background"""
        draw = Draw(image)

        def draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)

            dx = random.randint(0, 4)
            dy = random.randint(0, 6)
            """RGBA 4x8-bit pixels, true color with transparency mask"""
            im = Image.new('RGBA', (w + dx, h + dy))
            Draw(im).text((dx, dy), c, font=font, fill=color)

            # rotate
            im = im.crop(im.getbbox())
            """getbbox calculates the bounding box of the images"""
            im = im.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)
            """random.uniform returns a random floating point number
                BILINEAR linear interpolation"""

            # wrap
            dx = w * random.uniform(0.1, 0.3)
            dy = h * random.uniform(0.2, 0.3)
            x1 = int(random.uniform(-dx, dx))
            y1 = int(random.uniform(-dy, dy))
            x2 = int(random.uniform(-dx, dx))
            y2 = int(random.uniform(-dy, dy))
            w2 = w + abs(x1) + abs(x2)
            h2 = h + abs(y1) + abs(y2)

            data = (x1, y1,
                    -x1, h2 - y2,
                    w2 + x2, h2 + y2,
                    w2 - x2, -y1)
            im = im.resize((w2, h2))
            im = im.transform((w, h), Image.QUAD, data)
            """(w, h) the normal size
                Image.QUAD the transformation method -> data"""
            return im

        images = []
        for c in chars:
            if random.random() > 0.5:
                images.append(draw_character(" "))
            images.append(draw_character(c))

        text_width = sum([im.size[0] for im in images])

        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        average = int(text_width / len(chars))
        rand = int(0.25 * average)
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
            offset = offset + w + random.randint(-rand, 0)

        if width > self._width:
            image = image.resize((self._width, self._height))

        return image

    def generate_image(self, chars):
        background = random_color(238, 255)
        color = random_color(10, 200, random.randint(220, 255))
        im = self.create_captcha_image(chars, color, background)
        self.create_noise_dots(im, color)
        self.create_noise_curve(im, color)
        im = im.filter(ImageFilter.SMOOTH)
        return im


def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return (red, green, blue)
    return (red, green, blue, opacity)
