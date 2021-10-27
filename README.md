# mpl-image-labeller

[![License](https://img.shields.io/pypi/l/mpl-image-labeller.svg?color=green)](https://github.com/ianhi/mpl-image-labeller/raw/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/mpl-image-labeller.svg?color=green)](https://pypi.org/project/mpl-image-labeller)
[![Python Version](https://img.shields.io/pypi/pyversions/mpl-image-labeller.svg?color=green)](https://python.org)

Use Matplotlib to label images for classification. Works anywhere Matplotlib does - from the notebook to a standalone gui!

## Install

```bash
pip install mpl-image-labeller
```
## Key features
- Simple interface
- Uses keys instead of mouse
- Only depends on Matplotlib
    - Works anywhere - from inside Jupyter to any supported GUI framework
- Displays images with correct aspect ratio
- Easily configurable keymap
- Smart interactions with default Matplotlib keymap

![gif of usage for labelling images of cats and dogs](example.gif)

## Usage

```python
import matplotlib.pyplot as plt
import numpy as np

from mpl_image_labeller import image_labeller

images = np.random.randn(5, 10, 10)
labeller = image_labeller(
    images, classes=["good", "bad", "meh"], label_keymap=["a", "s", "d"]
)
plt.show()
```

**accessing the axis**
You can further modify the image (e.g. add masks over them) by using the plotting methods on
axis object accessible by `labeller.ax`.

**Lazy Loading Images**
If you want to lazy load your images you can provide a function to give the images. This function should take
the integer `idx` as an argument and return the image that corresponds to that index. If you do this then you
must also provide `N_images` in the constructor to let the object know how many images it should expect. See `examples/lazy_loading.py` for an example.

### Controls

- `<-` move one image back
- `->` move one image forward

To label images use the keys defined in the `label_keymap` argument - default 0, 1, 2...


Get the labels by accessing the `labels` property.

### Overwriting default keymap
Matplotlib has default keybindings that it applied to all figures via `rcparams.keymap` that allow for actions such as `s` to save or `q` to quit. If you inlcude one of these keys as a shortcut for labelling as a class then that default keymap will be disabled for that figure.


## Related Projects

This is not the first project to implement easy image labelling but seems to be the first to do so entirely in Matplotlib. The below
projects implement varying degrees of complexity and/or additional features in different frameworks.

- https://github.com/wbwvos/pidgey
- https://github.com/agermanidis/pigeon
- https://github.com/Serhiy-Shekhovtsov/tkteach
- https://github.com/robertbrada/PyQt-image-annotation-tool
- https://github.com/Cartucho/OpenLabeling
