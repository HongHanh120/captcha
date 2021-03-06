import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import PIL.Image
import IPython.display as display
import time
import os
import random
from datetime import datetime
from tensorflow.keras.applications import vgg19

gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.5)
config = tf.compat.v1.ConfigProto(gpu_options=gpu_options)
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)

gpus = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(gpus[0], True)

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


style_dir = './images/style/'
style_paths = []
for file in os.listdir(style_dir):
    image_path = os.path.join(style_dir, file)
    if file.endswith(".jpg"):
        style_paths.append(image_path)
    else:
        if file.endswith(".png"):
            style_paths.append(image_path)

content_path = './images/content/703876203_640.jpg'
style_path = random.choice(style_paths)
# print(style_path)


def load_img(path_to_img):
    max_dim = 512
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

# plt.subplot(1, 2, 1)
# imshow(content_image, 'Content Image')
#
# plt.subplot(1, 2, 2)
# imshow(style_image, 'Style Image')

# plt.show()

# x = vgg19.preprocess_input(content_image * 255)
# x = tf.image.resize(x, (224, 224))
# vgg = vgg19.VGG19(include_top=True, weights='imagenet')
# prediction_probabilities = vgg(x)
# prediction_probabilities.shape


# print()
# for layer in vgg.layers:
#     print(layer.name)

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


# for name, normal in zip(style_layers, style_outputs):
#     print(name)
#     print(" shape: ", normal.numpy().shape)
#     print(" min: ", normal.numpy().min())
#     print(" max: ", normal.numpy().max())
#     print(" mean: ", normal.numpy().mean())
#     print()


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
        "Expects float input in [0,1]"
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

# print('Styles:')
# for name, normal in sorted(results['style'].items()):
#   print("  ", name)
#   print("    shape: ", normal.numpy().shape)
#   print("    min: ", normal.numpy().min())
#   print("    max: ", normal.numpy().max())
#   print("    mean: ", normal.numpy().mean())
#   print()
#
# print("Contents:")
# for name, normal in sorted(results['content'].items()):
#   print("  ", name)
#   print("    shape: ", normal.numpy().shape)
#   print("    min: ", normal.numpy().min())
#   print("    max: ", normal.numpy().max())
#   print("    mean: ", normal.numpy().mean())

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
epochs = 1
steps_per_epoch = 100

step = 0

for n in range(epochs):
    for m in range(steps_per_epoch):
        step += 1
        train_step(image)
        print('.', end='')
    display.clear_output(wait=True)
    display.display(tensor_to_image(image))
    # print("Train step: {}".format(step))


end = time.time()
print("Total time: {:.1f}".format(end-start))


def high_pass_x_y(image):
    x_var = image[:, :, 1:, :] - image[:, :, :-1, :]
    y_var = image[:, 1:, :, :] - image[:, :-1, :, :]
    return x_var, y_var


x_deltas, y_deltas = high_pass_x_y(content_image)

plt.figure(figsize=(14, 10))


# plt.subplot(2, 2, 1)
# imshow(clip_0_1(2 * y_deltas + 0.5), 'Horizontal Deltas: Original')
#
# plt.subplot(2, 2, 2)
# imshow(clip_0_1(2 * x_deltas + 0.5), 'Vertical Deltas: Original')
#
# x_deltas, y_deltas = high_pass_x_y(image)
#
# plt.subplot(2, 2, 3)
# imshow(clip_0_1(2 * y_deltas + 0.5), 'Horizontal Deltas: Styled')
#
# plt.subplot(2, 2, 4)
# imshow(clip_0_1(2 * x_deltas + 0.5), 'Vertical Deltas: Styled')

# sobel = tf.image.sobel_edges(content_image)
# plt.subplot(1, 2, 1)
# imshow(clip_0_1(sobel[..., 0] / 4 + 0.5), 'Horizontal Sobel-edges')
#
# plt.subplot(1, 2, 2)
# imshow(clip_0_1(sobel[..., 1] / 4 + 0.5), 'Vertical Sobel-edges')
#
# plt.show()


def total_variation_loss(image):
    x_deltas, y_deltas = high_pass_x_y(image)
    return tf.reduce_sum(tf.abs(x_deltas)) + tf.reduce_sum(tf.abs(y_deltas))

# print(total_variation_loss(image).numpy())
# print(tf.image.total_variation(image).numpy())


createdDate = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
convertedDate = int(datetime.strptime(createdDate, "%d/%m/%Y %H:%M:%S").timestamp())
imageName = 'stylizedImage' + str(convertedDate)
file_name = './images/normal/' + imageName + '.png'
tensor_to_image(image).save(file_name)
