import matplotlib.pyplot as plt

from mpl_image_labeller import image_labeller

# from PIL import imread
im1 = plt.imread("im1.jpg")
im2 = plt.imread("im2.jpg")
im3 = plt.imread("im3.jpg")
ims = [im1, im2, im3]
labeller = image_labeller(
    ims,
    classes=["doggo", "cat", "car", "sofa"],
    # classes=["doggo", "cat", "other"],
    label_keymap=["a", "s", "d", "f"],
    multiclass=True,
)
plt.show()
print(labeller.labels)
