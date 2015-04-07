#__author__ = 'WeiFu'
from skimage import data, io, segmentation, color
from skimage.future import graph
from matplotlib import pyplot as plt
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from skimage.morphology import watershed, disk
from skimage import data
from skimage.filters import rank
from skimage.util import img_as_ubyte
import pdb
from libtiff import TIFF

 # img = data.coffee()
img = mpimg.imread('ilk-3b-1024.tif')
labels1 = segmentation.slic(img, compactness=20, n_segments=400)
out1 = color.label2rgb(labels1, img, kind='avg')
tif = TIFF.open('A.tif', mode='w')
tif.write_image(out1)
# pdb.set_trace()
g = graph.rag_mean_color(img, labels1, mode='similarity')
labels2 = graph.cut_normalized(labels1, g)
out2 = color.label2rgb(labels2, img, kind='avg')

plt.figure()
io.imshow(out1)
plt.figure()
io.imshow(out2)
io.show()