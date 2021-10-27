import matplotlib.pyplot as plt
import numpy as np

from mpl_image_labeller import image_labeller

images = np.random.randn(5, 10, 10)
labeller = image_labeller(images, classes=["good", "bad", "blarg"])


def image_changed_callback(index, image):
    print(index)
    print(image.sum())


def label_assigned(index, label):
    print(f"label {label} assigned to image {index}")


labeller.on_image_changed(image_changed_callback)
labeller.on_label_assigned(image_changed_callback)
plt.show()
