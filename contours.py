import cv2 as cv
from datetime import datetime
import os

# Image path
image_path = './images/normal/captcha_1611806085.png'

# Using cv.imread() method to read the image
im = cv.imread(image_path)
gray = cv.cvtColor(im, cv.COLOR_BGR2GRAY)

# Find Canny edges
edged = cv.Canny(gray, 100, 200, apertureSize=7, L2gradient=True)

# Finding Contours
# Use a copy of the image e.g. edged.copy()
# since findContours alters the image
contours, hierarchy = cv.findContours(edged,
                                      cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

print("Number of Contours found = " + str(len(contours)))

# Draw all contours
# -1 signifies drawing all contours
# cv.drawContours(im, contours, -1, (255, 0, 0), 3)
cv.drawContours(im, contours, -1, 3)

# Image name
created_date = datetime.now().strftime("%c")
converted_date = int(datetime.strptime(created_date, "%c").timestamp())
image_name = 'contour_' + str(converted_date) + '.png'

# Image directory
image_dir = 'images/contours/'
# Change the current directory to specified dictionary
os.chdir(image_dir)

# Using cv2.imwrite() method saving the image
cv.imwrite(image_name, im)
