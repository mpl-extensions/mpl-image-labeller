import numpy as np

from mpl_image_labeller import image_labeller

N = 5
M = 3
im1 = np.ones([N, M])
im1[0, 0] = 0
im2 = np.ones([M, N]) * 5
im2[0, 0] = 0.5
ims = [im1, im2]


# norm and extent
def test_norm_and_extent_updates():
    labeller = image_labeller(ims, ["good", "bad"])
    assert labeller._im.norm.vmin == 0
    assert labeller._im.norm.vmax == 1
    assert labeller._im.get_extent() == (-0.5, M - 0.5, N - 0.5, -0.5)
    assert labeller._image_ax.get_xlim() == (-0.5, M - 0.5)
    assert labeller._image_ax.get_ylim() == (N - 0.5, -0.5)

    labeller.image_index += 1
    assert labeller._im.norm.vmin == 0.5
    assert labeller._im.norm.vmax == 5
    assert labeller._im.get_extent() == (-0.5, N - 0.5, M - 0.5, -0.5)
    assert labeller._image_ax.get_xlim() == (-0.5, N - 0.5)
    assert labeller._image_ax.get_ylim() == (M - 0.5, -0.5)


def test_norm_with_explict_vmin_vmax():
    labeller = image_labeller(ims, ["good", "bad"], vmin=0.3, vmax=4)
    assert labeller._im.norm.vmin == 0.3
    assert labeller._im.norm.vmax == 4
    labeller.image_index += 1
    assert labeller._im.norm.vmin == 0.3
    assert labeller._im.norm.vmax == 4

    labeller = image_labeller(ims, ["good", "bad"], vmin=0.3)
    assert labeller._im.norm.vmin == 0.3
    assert labeller._im.norm.vmax == im1.max()
    labeller.image_index += 1
    assert labeller._im.norm.vmin == 0.3
    assert labeller._im.norm.vmax == im2.max()

    labeller = image_labeller(ims, ["good", "bad"], vmax=4)
    assert labeller._im.norm.vmin == im1.min()
    assert labeller._im.norm.vmax == 4
    labeller.image_index += 1
    assert labeller._im.norm.vmin == im2.min()
    assert labeller._im.norm.vmax == 4
