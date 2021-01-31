# import math
# from turtle import Turtle, Screen
# from itertools import cycle
#
# color_list = ['red', 'blue', 'green', 'purple', 'pink']
#
#
# def createTurtles(count):
#     turtles = []
#     colors = cycle(color_list)
#
#     for _ in range(count):
#         turtle = Turtle('turtle')
#         turtle.color(next(colors))
#         turtle.speed('fastest')
#         turtle.width(3)
#
#         turtles.append(turtle)
#
#     return turtles
#
#
# def wave(count):
#     for n in range(count):
#         amp = amp_list[n]
#         freq = freq_list[n]
#         turtle = turtles_list[n]
#         turtle.penup()
#
#         for x in range(361):
#             y_val = amp * math.sin(math.radians(x * freq))
#             turtle.goto(x, y_val)
#             turtle.pendown()
#
#
# num_waves = int(input('How many sine waves do you want to create? '))
#
# amp_list = []
# freq_list = []
# counter = 1
#
# for x in range(num_waves):
#     print('\nSine Wave #', counter)
#     amp = int(input('Enter the amplitude of the sine wave: '))
#     freq = float(input('Enter the frequency of the sine wave: '))
#     amp_list.append(amp)
#     freq_list.append(freq)
#     counter += 1
#
# amp_screen = max(amp_list) + 1
#
# screen = Screen()
# screen.bgcolor('lightyellow')
# screen.setworldcoordinates(0, -amp_screen, 400, amp_screen)
#
# turtles_list = createTurtles(num_waves)
#
# wave(counter - 1)
#
# screen.exitonclick()

# import matplotlib.pyplot as plt
# from matplotlib.path import Path
# import matplotlib.patches as patches
# import numpy as np
#
# n_teams = 4
# n_weeks = 4
# t = np.array([[1, 2, 4, 3],
#               [4, 3, 3, 2],
#               [3, 4, 1, 4],
#               [2, 1, 2, 1]])
# fig, ax = plt.subplots(figsize=(10, 4), facecolor='#1b1b1b')
# ax.set_facecolor('#1b1b1b')
#
# indent = 0.8
# for tj in t:
#     ax.scatter(np.arange(len(tj)), tj, marker='o', color='#4F535C', s=100, zorder=3)
#     # create bezier curves
#     verts = [(i + d, tij) for i, tij in enumerate(tj) for d in (-indent, 0, indent)][1:-1]
#     codes = [Path.MOVETO] + [Path.CURVE4] * (len(verts) - 1)
#     path = Path(verts, codes)
#     patch = patches.PathPatch(path, facecolor='none', lw=2, edgecolor='#4F535C')
#     ax.add_patch(patch)
# ax.set_xticks([])
# ax.set_yticks([])
# ax.autoscale() # sets the xlim and ylim for the added patches
# plt.show()


# import cv2 as cv
# import math
# import numpy as np
# import scipy.interpolate as si
# import matplotlib.pyplot as plt
#
# image_path = './images/normal/captcha_1610007581.png'
# im = cv.imread(image_path)
#
# # x = np.arange(0.1, 4 * np.pi, 0.1)  # start,stop,step
# points = np.array([[0.0, 0.0]])
# for x in np.arange(3, 200, 5):
#     y = np.sin(x)
#     y = 10 + 10 * np.sin(2 * .1 * np.pi * x)
#     points = np.append(points, [[x, y]], axis=0)
#
# print(points)
#
# degree = 3
# points_t = points + points[0:degree + 1]
# points_t = np.array(points)
# n_points = len(points_t)
# x = points_t[:, 0]
# y = points_t[:, 1]
#
# t = range(len(x))
# ipl_t = np.linspace(1.0, len(points_t) - degree, 10)
# x_tup = si.splrep(t, x, k=degree, per=1)
# y_tup = si.splrep(t, y, k=degree, per=1)
#
# x_list = list(x_tup)
# xl = x.tolist()
# x_list[1] = [0.0] + xl + [0.0, 0.0, 0.0, 0.0]
#
# y_list = list(y_tup)
# yl = y.tolist()
# y_list[1] = [0.0] + yl + [0.0, 0.0, 0.0, 0.0]
#
# x_i = si.splev(ipl_t, x_list)
# y_i = si.splev(ipl_t, y_list)
#
# fig = plt.figure()
#
# ax = fig.add_subplot(231)
# plt.plot(t, x, '-og')
# plt.plot(ipl_t, x_i, 'r')
# plt.xlim([0.0, max(t)])
# plt.title('Splined x(t)')
# plt.show()
#
# cv.polylines(im, np.int32([points]), 0, (255, 0, 0), 2, 4, 0)
# image_name = 'curve.png'
#
# cv.imwrite(image_name, im)

# import numpy as np
# import cv2
#
# # Read the main image
#
# inputImage = cv2.imread("input.png")
#
# # Convert it to grayscale
#
# inputImageGray = cv2.cvtColor(inputImage, cv2.COLOR_BGR2GRAY)
#
# # Line Detection
#
# edges = cv2.Canny(inputImageGray,100,200,apertureSize = 3)
#
# minLineLength = 500
# maxLineGap = 5
#
# lines = cv2.HoughLinesP(edges,1,np.pi/180,90,minLineLength,maxLineGap)
#
# for x in range(0, len(lines)):
#    for x1,y1,x2,y2 in lines[x]:
#        cv2.line(inputImage,(x1,y1),(x2,y2),(0,128,0),2)
#
# cv2.putText(inputImage,"Tracks Detected", (500,250), font, 0.5, 255)
#
# # Show result
#
# cv2.imshow("Trolley_Problem_Result", inputImage)


import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

# x = [0, 1, 1, 0, 0]
# y = [0, 0, 1, 1, 0]
points = np.array([[0.0, 0.0]])
for x in np.arange(3, 200, 5):
    y = np.sin(x)
    y = 10 + 10 * np.sin(2 * .1 * np.pi * x)
    points = np.append(points, [[x, y]], axis=0)

n = len(points)
x = points[:, 0]
y = points[:, 1]

# Pad the x and y series so it "wraps around".
# Note that if x and y are numpy arrays, you'll need to
# use np.r_ or np.concatenate instead of addition!
orig_len = len(x)
# x = x[-3:-1] + x + x[1:3]
# y = y[-3:-1] + y + y[1:3]

t = np.arange(len(x))
ti = np.linspace(2, orig_len + 1, 10 * orig_len)

xi = interp1d(t, x, kind='cubic')(ti)
yi = interp1d(t, y, kind='cubic')(ti)

fig, ax = plt.subplots()
ax.plot(xi, yi)
ax.plot(x, y)
ax.margins(0.05)
plt.show()