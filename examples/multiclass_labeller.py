import matplotlib.pyplot as plt
import numpy as np

from mpl_image_labeller import image_labeller

images = np.random.randn(5, 10, 10)
labeller = image_labeller(
    images,
    classes=["good", "bad", "meh"],
    label_keymap=["a", "s", "d"],
    multiclass=True,
)
plt.show()
print(labeller.labels)
print(labeller.labels_onehot)
