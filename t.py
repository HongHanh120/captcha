from scipy.interpolate import interp1d
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

image = Image.new("RGBA", (500, 500), color="white")
draw = ImageDraw.Draw(image)

x = np.linspace(0, 10, num=11, endpoint=True)
y = np.cos(-x**2/9.0) + 100
f = interp1d(x, y)
f2 = interp1d(x, y, kind='cubic')

xnew = np.linspace(0, 10, num=41, endpoint=True)
x_len = len(xnew)
points = [0.0, 0.0]
for x in xnew:
    points.append(x + 20)
    points.append(float(f2(x)))

print(points)
# points = [xnew, f2(xnew)]
draw.point(points, fill='blue')
draw.polygon(points, outline="black")
image.show()

# plt.plot(x, y, 'o', xnew, f(xnew), '-', xnew, f2(xnew), '--')
# plt.legend(['data', 'linear', 'cubic'], loc='best')
# plt.show()