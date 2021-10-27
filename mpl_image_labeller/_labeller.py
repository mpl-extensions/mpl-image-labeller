from typing import TYPE_CHECKING, List, Union


# if TYPE_CHECKING:
from matplotlib.figure import Figure
from numpy.typing import ArrayLike


class image_labeller:
    def __init__(
        self,
        images: ArrayLike,
        classes: ArrayLike,
        init_labels: ArrayLike = None,
        label_keymap: Union[List[str], str] = "1234",
        fig: Figure = None,
    ):
        """
        Parameters
        ----------
        images : (N, Y, X) ArrayLike
        classes : (N,) ArrayLike
            The available classes for the images.
        init_labels: 1D ArrayLike, optional
            The initial labels for the images. If given it must be the same length as
            *images*
        label_keymap : list of str, or str
            If a str must be one of the predefined values *1234* (1, 2, 3,..),
            *qwerty* (q, w, e, r, t, y). If an iterable then the items will be assigned
            in order to the classes.
        fig : Figure
            An empty figure to build the UI in. Use this to embed image_labeller into
            a gui framework.
        """
        self._images = images
        if init_labels is None:
            self._labels = [None] * len(images)
        elif len(init_labels) != len(images):
            raise ValueError("init_labels must have the same length as images")

        if label_keymap == "1234":
            if len(classes) > 10:
                raise ValueError(
                    "More classes than numbers on the keyboard, please provide a custom keymap"
                )
            self._label_keymap = {f"{(i+1)%10}": i for i in range(len(classes))}
        elif label_keymap == "qwerty":
            if len(classes) > len("qwertyuiop"):
                raise ValueError(
                    "More classes than length of qwertyuiop, please provide a custom keymap"
                )
            self._label_keymap = {c: c for c in "qwertyuiop"[: len(classes)]}
        else:
            self._label_keymap = {label_keymap[i]: i for i in range(len(label_keymap))}

        self._classes = classes

        if fig is None:
            import matplotlib.pyplot as plt

            self._fig = plt.figure()
        else:
            self._fig = fig

        self._image_index = 0
        self._ax = self._fig.add_subplot(111)
        self._im = self._ax.imshow(images[0])

        self._fig.canvas.mpl_connect("key_press_event", self._key_press)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        if len(value) != len(self._images):
            raise ValueError(
                "Length of labels must be the same as the number of images"
            )
        self._labels = value

    @property
    def image_index(self):
        return self._image_index

    @image_index.setter
    def image_index(self, value):
        N = len(self._images)
        if value == self._image_index:
            # quick return to avoid unnecessary draw
            return
        elif value >= N:
            if self._image_index == N - 1:
                # quick return to avoid unnecessary draw
                return
            self._image_index = N - 1
        elif value < 0:
            if self._image_index == 0:
                # quick return to avoid unnecessary draw
                return
            self._image_index = 0
        else:
            self._image_index = value
        self._update_displayed()

    def _update_displayed(self):
        self._im.set_data(self._images[self._image_index])
        self._ax.set_title(
            f"Image {self._image_index} - Label: {self._labels[self._image_index]}"
        )
        self._fig.canvas.draw_idle()

    def _key_press(self, event):
        if event.key == "left":
            self.image_index -= 1
        elif event.key == "right":
            self.image_index += 1
        elif event.key in self._label_keymap:
            self._labels[self._image_index] = self._classes[
                self._label_keymap[event.key]
            ]
            self._ax.set_title(
                f"Image {self._image_index} - Label: {self._labels[self._image_index]}"
            )
            # TODO: blit just the text here
            self._fig.canvas.draw_idle()
