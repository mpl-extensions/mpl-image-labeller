# You can lazy load images by providing a function instead of a list for *images*
# if you do this then you must also provide *N_images* in the labeller constructor


import matplotlib.pyplot as plt
from numpy.random import default_rng

from mpl_image_labeller import image_labeller


def lazy_image_generator(idx):
    rng = default_rng(idx)
    return rng.random((10, 10))


labeller = image_labeller(
    lazy_image_generator, classes=["cool", "rad", "lame"], N_images=57
)
plt.show()
