import os
import time
import random
import string
import PIL.Image
import numpy as np
import tensorflow as tf
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import IPython.display as display
from datetime import datetime
from normal_captcha import ImageCaptcha
from tensorflow.keras.applications import vgg19

# image = ImageCaptcha(fonts=['./data/DroidSansMono.ttf'])
from claptcha.claptcha import Claptcha


def random_string():
    random_letters = (random.choice(string.ascii_uppercase) for _ in range(6))
    return "".join(random_letters)


text = random_string()

c = Claptcha(text, './data/DroidSansMono.ttf')
text, image = c.image
print(text)

created_date = datetime.now().strftime("%c")
converted_date = int(datetime.strptime(created_date, "%c").timestamp())
image_name = 'captcha_' + str(converted_date)
image_dir = 'images/normal/'
abs_image_path = os.path.join(image_dir, image_name + ".png")

text, file = c.write(abs_image_path)

# img = mpimg.imread(abs_image_path)
# imgplot = plt.imshow(img)
# plt.show()

gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.5)
config = tf.compat.v1.ConfigProto(gpu_options=gpu_options)
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)

batch_sizes = tf.data.Dataset.range(8)

mpl.rcParams['figure.figsize'] = (12, 12)
mpl.rcParams['axes.grid'] = False


def tensor_to_image(tensor):
    tensor = tensor * 255
    tensor = np.array(tensor, dtype=np.uint8)
    if np.ndim(tensor) > 3:
        assert tensor.shape[0] == 1
        tensor = tensor[0]
    return PIL.Image.fromarray(tensor)


style_dir = "./images/style/"
style_paths = []
for file in os.listdir(style_dir):
    style_image_path = os.path.join(style_dir, file)
    if file.endswith('.jpg'):
        style_paths.append(style_image_path)
    if file.endswith('.png'):
        style_paths.append(style_image_path)

content_path = abs_image_path
style_path = random.choice(style_paths)
print(style_path)


def load_img(path_to_img):
    max_dim = 160
    img = tf.io.read_file(path_to_img)
    img = tf.image.decode_image(img, channels=3)
    img = tf.image.convert_image_dtype(img, tf.float32)

    shape = tf.cast(tf.shape(img)[:-1], tf.float32)
    long_dim = max(shape)
    scale = max_dim / long_dim

    new_shape = tf.cast(shape * scale, tf.int32)

    img = tf.image.resize(img, new_shape)
    img = img[tf.newaxis, :]
    return img


def imshow(image, title=None):
    if len(image.shape) > 3:
        image = tf.squeeze(image, axis=0)

    plt.imshow(image)
    if title:
        plt.title(title)


content_image = load_img(content_path)
style_image = load_img(style_path)

content_layers = ['block5_conv2']

style_layers = ['block1_conv1',
                'block2_conv1',
                'block3_conv1',
                'block4_conv1',
                'block5_conv1']

num_content_layers = len(content_layers)
num_style_layers = len(style_layers)


def vgg_layers(layer_names):
    vgg = vgg19.VGG19(include_top=False, weights='imagenet')
    vgg.trainable = False

    outputs = [vgg.get_layer(name).output for name in layer_names]

    model = tf.keras.Model([vgg.input], outputs)
    return model


style_extractor = vgg_layers(style_layers)
style_outputs = style_extractor(style_image * 255)


def gram_matrix(input_tensor):
    result = tf.linalg.einsum('bijc,bijd->bcd', input_tensor, input_tensor)
    input_shape = tf.shape(input_tensor)
    num_locations = tf.cast(input_shape[1] * input_shape[2], tf.float32)
    return result / num_locations


class StyleContentModel(tf.keras.models.Model):
    def __init__(self, style_layer, content_layer):
        super(StyleContentModel, self).__init__()
        self.vgg = vgg_layers(style_layer + content_layer)
        self.style_layers = style_layer
        self.content_layers = content_layer
        self.num_style_layers = len(style_layer)
        self.vgg.trainable = False

    def call(self, inputs):
        inputs = inputs * 255.0
        preprocessed_input = tf.keras.applications.vgg19.preprocess_input(inputs)
        outputs = self.vgg(preprocessed_input)
        style_outputs, content_outputs = (outputs[:self.num_style_layers],
                                          outputs[self.num_style_layers:])

        style_outputs = [gram_matrix(style_output)
                         for style_output in style_outputs]

        content_dict = {content_name: value
                        for content_name, value
                        in zip(self.content_layers, content_outputs)}

        style_dict = {style_name: value
                      for style_name, value
                      in zip(self.style_layers, style_outputs)}

        return {'content': content_dict, 'style': style_dict}


extractor = StyleContentModel(style_layers, content_layers)

results = extractor(tf.constant(content_image))

style_targets = extractor(style_image)['style']
content_targets = extractor(content_image)['content']

image = tf.Variable(content_image)


def clip_0_1(image):
    return tf.clip_by_value(image, clip_value_min=0.0, clip_value_max=1.0)


opt = tf.optimizers.Adam(learning_rate=0.02, beta_1=0.99, epsilon=1e-1)

style_weight = 1e-2
content_weight = 1e4


def style_content_loss(outputs):
    style_outputs = outputs['style']
    content_outputs = outputs['content']
    style_loss = tf.add_n([tf.reduce_mean((style_outputs[name] - style_targets[name]) ** 2)
                           for name in style_outputs.keys()])
    style_loss *= style_weight / num_style_layers

    content_loss = tf.add_n([tf.reduce_mean((content_outputs[name] - content_targets[name]) ** 2)
                             for name in content_outputs.keys()])
    content_loss *= content_weight / num_content_layers
    loss = style_loss + content_loss
    return loss


total_variation_weight = 30


@tf.function()
def train_step(image):
    with tf.GradientTape() as tape:
        outputs = extractor(image)
        loss = style_content_loss(outputs)
        loss += total_variation_weight * tf.image.total_variation(image)

    grad = tape.gradient(loss, image)
    opt.apply_gradients([(grad, image)])
    image.assign(clip_0_1(image))


image = tf.Variable(content_image)

start = time.time()
epochs = 10
steps_per_epoch = 100

step = 0

for n in range(epochs):
    for m in range(steps_per_epoch):
        step += 1
        train_step(image)
        print('.', end='')

    display.clear_output(wait=True)
    display.display(tensor_to_image(image))

end = time.time()
print('Total time: {:.1f}'.format(end - start))


def high_pass_x_y(image):
    x_var = image[:, :, 1:, :] - image[:, :, :-1, :]
    y_var = image[:, 1:, :, :] - image[:, :-1, :, :]
    return x_var, y_var


x_deltas, y_deltas = high_pass_x_y(content_image)

plt.figure(figsize=(14, 10))


def total_variation_loss(image):
    x_deltas, y_deltas = high_pass_x_y(image)
    return tf.reduce_sum(tf.abs(x_deltas)) + tf.reduce_sum(tf.abs(y_deltas))


created_output_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
converted_output_date = int(datetime.strptime(created_output_date, "%d/%m/%Y %H:%M:%S").timestamp())
output_image_name = 'styled_captcha_' + str(converted_output_date)
file_name = './images/neural-style/' + output_image_name + '.png'
tensor_to_image(image).save(file_name)
