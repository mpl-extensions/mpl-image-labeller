from typing import List, Union

from matplotlib.backend_bases import key_press_handler

# if TYPE_CHECKING:
from matplotlib.figure import Figure


def gen_key_press_handler(skip_keys):
    def handler(event, canvas=None, toolbar=None):
        if event.key in skip_keys:
            return
        key_press_handler(event, canvas, toolbar)

    return handler


class image_labeller:
    def __init__(
        self,
        images,
        classes,
        init_labels=None,
        label_keymap: Union[List[str], str] = "1234",
        labelling_advances_image: bool = True,
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
            in order to the classes. WARNING: These keys will be removed from the
            default keymap for that figure. So if *s* is included then *s* will no
            longer perform savefig.
        labelling_advances_image : bool, default: True
            Whether labelling an image should advance to the next image.
        fig : Figure
            An empty figure to build the UI in. Use this to embed image_labeller into
            a gui framework.
        """
        self._images = images
        self._label_advances = labelling_advances_image
        if init_labels is None:
            self._labels = [None] * len(images)
        elif len(init_labels) != len(images):
            raise ValueError("init_labels must have the same length as images")

        if label_keymap == "1234":
            if len(classes) > 10:
                raise ValueError(
                    "More classes than numbers on the keyboard,"
                    "please provide a custom keymap"
                )
            self._label_keymap = {f"{(i+1)%10}": i for i in range(len(classes))}
        elif label_keymap == "qwerty":
            if len(classes) > len("qwertyuiop"):
                raise ValueError(
                    "More classes than length of qwertyuiop,"
                    "please provide a custom keymap"
                )
            self._label_keymap = {"qwertyuiop"[c]: c for c in range(len(classes))}
        else:
            self._label_keymap = {label_keymap[i]: i for i in range(len(label_keymap))}

        self._classes = classes

        if fig is None:
            import matplotlib.pyplot as plt

            self._fig = plt.figure(constrained_layout=True)
        else:
            self._fig = fig

        # "remove" keys from the default keymap by overwriting the key handler method
        # see https://gitter.im/matplotlib/matplotlib?at=617988daee6c260cf743e9cb
        self._fig.canvas.mpl_disconnect(self._fig.canvas.manager.key_press_handler_id)

        self._fig.canvas.manager.key_press_handler_id = self._fig.canvas.mpl_connect(
            "key_press_event", gen_key_press_handler(list(self._label_keymap.keys()))
        )

        self._image_index = 0
        self._ax = self._fig.add_subplot(111)
        self._im = self._ax.imshow(images[0])

        # shift axis to make room for list of keybindings
        box = self._ax.get_position()
        box.x0 = box.x0 - 0.20
        box.x1 = box.x1 - 0.20
        self._ax.set_position(box)
        self._update_title()

        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

        textstr = """Keybindings
        <- : Previous Image
        -> : Next Image"""

        self._ax.text(
            1.05,
            0.95,
            textstr,
            transform=self._ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props,
            horizontalalignment="left",
        )

        textstr = """Class Keybindings:\n"""
        for k, v in self._label_keymap.items():
            textstr += f"{k} : {self._classes[v]}\n"

        self._ax.text(
            1.05,
            0.55,
            textstr,
            transform=self._ax.transAxes,
            fontsize=14,
            verticalalignment="top",
            bbox=props,
        )

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

    def _update_title(self):
        self._ax.set_title(
            f"Image {self._image_index}\nLabel: {self._labels[self._image_index]}"
        )

    def _update_displayed(self):
        self._im.set_data(self._images[self._image_index])
        self._update_title()
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
            if self._label_advances:
                if self.image_index == len(self._images) - 1:
                    # make sure we update the title we are on the last image
                    self._update_title()
                    self._fig.canvas.draw_idle()
                else:
                    self.image_index += 1
            else:
                # only updating the text
                self._update_title()
                # TODO: blit just the text here
                self._fig.canvas.draw_idle()
