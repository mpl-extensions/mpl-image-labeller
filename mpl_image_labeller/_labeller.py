from typing import List, Union

import numpy as np
from matplotlib.backend_bases import key_press_handler
from matplotlib.cbook import CallbackRegistry
from matplotlib.figure import Figure

from ._util import ConflictingArgumentsError, list_to_onehot, onehot_to_list
from ._widgets import button_array


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
        multiclass=False,
        label_keymap: Union[List[str], str] = "1234",
        title=None,
        init_labels=None,
        init_labels_onehot=None,
        labelling_advances_image: bool = True,
        N_images=None,
        fig: Figure = None,
        **imshow_kwargs,
    ):
        """
        Parameters
        ----------
        images : (N, Y, X) ArrayLike
        classes : (N,) ArrayLike
            The available classes for the images.
        multiclass : bool, default: False
            Whether to allow for an image to have multiple classes or just one.
        label_keymap : list of str, or str
            If a str must be one of the predefined values *1234* (1, 2, 3,..),
            *qwerty* (q, w, e, r, t, y). If an iterable then the items will be assigned
            in order to the classes. WARNING: These keys will be removed from the
            default keymap for that figure. So if *s* is included then *s* will no
            longer perform savefig.
        title : str or Callable, optional
            A {} style format string for the title of images or a function that
            returns a title string given the image index. If a format string
            then it will be used with ``title.format(image_index=...)``. If *None*
            then the default str of 'Image Index: {image_index}' will be used.
        init_labels: list of list or list of str, optional
            The initial labels for the images. If given it must be the same length as
            *images* and each entry should be either a single class or an iterable of
            classes. Incompatible with *init_labels_onehot*.
        init_labels_onehot: 2D ArrayLike, optional
            The initial labels for the images as a onehot encoding. If given it must
            have shape (N_images, N_classes) and be castable to a boolean array.
            Incompatible with *init_labels*.
        labelling_advances_image : bool, default: True
            Whether labelling an image should advance to the next image.
            Ignored if *multiclass* is True.
        N_images : int or None
            The number of images. Required if passing a Callable for images, otherwise
            ignored.
        fig : Figure
            An empty figure to build the UI in. Use this to embed image_labeller into
            a gui framework.
        **imshow_kwargs :
            kwargs to be passed to the imshow function that displays the images.
        """
        self._multi = multiclass
        self._images = images
        if title is None:
            title = "Image Index: {image_index}"
        if isinstance(title, str):

            def _title(image_index):
                return title.format(image_index=image_index)

            self._title = _title
        elif callable(title):
            self._title = title
        else:
            raise TypeError("Title must be a str or a Callable")

        if callable(images):
            if not isinstance(N_images, int):
                raise TypeError(
                    "If images is a callable then N_images must be provided"
                )
            self._N_images = N_images

            def _get_image(i):
                return self._images(i)

        else:
            self._N_images = len(images)

            def _get_image(i):
                return self._images[i]

        self._get_image = _get_image

        self._label_advances = labelling_advances_image

        # TODO: sync this up with labels
        # TODO: make sure init_labels does something here
        self._onehot = np.zeros((self._N_images, len(classes)), dtype=bool)

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
        elif len(label_keymap) != len(classes):
            raise ValueError("label_keymap must have the same length as classes")
        else:
            self._label_keymap = {label_keymap[i]: i for i in range(len(label_keymap))}

        # make array for easy indexing
        self._classes = np.asarray(classes)

        if init_labels is not None and init_labels_onehot is not None:
            raise ConflictingArgumentsError(
                "init_labels and init_labels_onehot cannot both be *None*"
            )

        if init_labels is not None:
            # length errors are handled in the setter
            self.labels = init_labels
        elif init_labels_onehot is not None:
            self.labels_onehot = init_labels_onehot
        else:
            if self._multi:
                self.labels = [[]] * self._N_images
            else:
                self.labels = [None] * self._N_images

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
        if self._multi:
            self._image_ax, self._info_ax = self._fig.subplots(1, 2)
        else:
            gs = self._fig.add_gridspec(1, 5)
            self._image_ax = self._fig.add_subplot(gs[:, :-1])
            self._info_ax = self._fig.add_subplot(gs[:, -1])

        self._info_ax.axis("off")
        aspect = imshow_kwargs.pop("aspect", "equal")
        self._im = self._image_ax.imshow(
            self._get_image(0), aspect=aspect, **imshow_kwargs
        )

        if self._multi:

            def on_state_change(new_state, old_state):
                self._onehot[self._image_index] = new_state
                # self.labels[self._image_index] = self._classes[new_state]

            texts = []
            for key, klass in zip(self._label_keymap.keys(), classes):
                texts.append(f"[{key}]\n{str(klass)}")
            self._buttons = button_array(texts, self._info_ax)
            self._buttons.on_state_change(on_state_change)
        else:
            # shift axis to make room for list of keybindings
            # box = self._image_ax.get_position()
            # box.x0 = box.x0 - 0.20
            # box.x1 = box.x1 - 0.20
            # self._image_ax.set_position(box)

            # these are matplotlib.patch.Patch properties
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)

            textstr = """Keybindings
            <- : Previous Image
            -> : Next Image"""
            horiz_pos = 0.575

            self._info_ax.text(
                horiz_pos,
                0.75,
                textstr,
                # transform=self._fig.transFigure,
                fontsize=14,
                verticalalignment="top",
                bbox=props,
                horizontalalignment="left",
            )

            textstr = """Class Keybindings:\n"""
            for k, v in self._label_keymap.items():
                textstr += f"{k} : {self._classes[v]}\n"

            self._info_ax.text(
                horiz_pos,
                0.55,
                textstr,
                # transform=self._fig.transFigure,
                fontsize=14,
                verticalalignment="top",
                bbox=props,
            )

            textstr = f"Current Class:\n{str(self._labels[0])}"
            self._class_display = self._info_ax.text(
                horiz_pos,
                0.25,
                textstr,
                # transform=self._fig.transFigure,
                fontsize=14,
                verticalalignment="top",
                bbox=props,
            )

        self._update_title()

        self._fig.canvas.mpl_connect("key_press_event", self._key_press)
        self._observers = CallbackRegistry()

    @property
    def ax(self):
        """
        **readonly** - The `~matplotlib.axes.Axes` object the image's are displayed on.
        """
        return self._image_ax

    @property
    def labels(self):
        """
        The current labels as a list of lists or a list of strings.
        """
        if self._multi:
            return onehot_to_list(self._onehot, self._classes)
        else:
            return self._labels

    @labels.setter
    def labels(self, value):
        if len(value) != self._N_images:
            raise ValueError(
                "Length of labels must be the same as the number of images"
            )
        if self._multi:
            self._onehot = list_to_onehot(value, self._classes)
        else:
            self._labels = value

    @property
    def labels_onehot(self):
        """
        The current labels as a one hot encoding.
        """
        if self._multi:
            return self._onehot
        else:
            return list_to_onehot(self._labels, self._classes)

    @labels_onehot.setter
    def labels_onehot(self, value):
        value = np.asanyarray(value)
        expected_shape = (self._N_images, len(self._classes))
        if value.shape != expected_shape:
            raise ValueError(
                "One hot labels must have shape (N images, num classes."
                f"Expected shape {expected_shape} but got {value.shape}"
            )
        if self._multi:
            self._onehot = value
        else:
            self._labels = onehot_to_list(value)

    @property
    def image_index(self):
        """
        **int** the index of the currently displayed image.
        """
        return self._image_index

    @image_index.setter
    def image_index(self, value):
        if value == self._image_index:
            # quick return to avoid unnecessary draw
            return
        elif value >= self._N_images:
            if self._image_index == self._N_images - 1:
                # quick return to avoid unnecessary draw
                return
            self._image_index = self._N_images - 1
        elif value < 0:
            if self._image_index == 0:
                # quick return to avoid unnecessary draw
                return
            self._image_index = 0
        else:
            self._image_index = value
        self._update_displayed()

    def _update_title(self):
        text = self._title(self._image_index)
        self._image_ax.set_title(text)

    def _update_displayed(self):
        image = np.asarray(self._get_image(self._image_index))
        # for some reason this keeps getting turned off by something
        self._image_ax.set_autoscale_on(True)
        self._im.set_data(image)
        self._im.set_extent((-0.5, image.shape[1] - 0.5, image.shape[0] - 0.5, -0.5))
        self._update_title()
        self._observers.process("image-changed", self._image_index, image)
        if self._multi:
            with self._buttons.no_callbacks():
                # TODO: check that this no_callbacks actually works....
                new_state = self._onehot[self._image_index]
                self._buttons.set_states(new_state)
        else:
            textstr = f"Current Class:\n{str(self._labels[self._image_index])}"
            self._class_display.set_text(textstr)
        self._fig.canvas.draw_idle()

    def _key_press(self, event):
        if event.key == "left":
            self.image_index -= 1
        elif event.key == "right":
            self.image_index += 1
        elif event.key in self._label_keymap:
            which_label = self._label_keymap[event.key]
            klass = self._classes[which_label]
            if self._multi:
                img_labels = self._onehot[self._image_index]
                img_labels[which_label] = not img_labels[which_label]
                self._buttons.set_states(img_labels)
            else:
                self._labels[self._image_index] = klass
            self._observers.process("label-assigned", self._image_index, klass)
            if self._label_advances and not self._multi:
                if self.image_index == self._N_images - 1:
                    # make sure we update the title we are on the last image
                    self._update_title()
                    textstr = f"Current Class:\n{str(self._labels[self._image_index])}"
                    self._class_display.set_text(textstr)
                    self._fig.canvas.draw_idle()
                else:
                    self.image_index += 1
            else:
                # only updating the text
                self._update_title()
                # TODO: blit just the text here
                self._fig.canvas.draw_idle()

    def on_label_assigned(self, func):
        """
        Connect *func* as a callback function for when a label is assigned
        to an image. *func* will receive the index of the image and the
        new class.

        Parameters
        ----------
        func : callable
            Function to call when a point is added.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*).
        """
        return self._observers.connect("label-assigned", lambda *args: func(*args))

    def on_image_changed(self, func):
        """
        Connect *func* as a callback function for when the displayed image
        is changed. *func* will receive the index of the new image and the
        image. `fig.canvas.draw_idle` will be called after the callback is
        executed so if you are modifying the figure then you do not need to
        explicitly call *draw* yourself.

        Parameters
        ----------
        func : callable
            Function to call when a point is added.

        Returns
        -------
        int
            Connection id (which can be used to disconnect *func*).
        """
        return self._observers.connect("image-changed", lambda *args: func(*args))
