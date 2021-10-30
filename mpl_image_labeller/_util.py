import contextlib
from collections.abc import Iterable

import numpy as np
from matplotlib.cbook import CallbackRegistry

__all__ = [
    "deactivatable_CallbackRegistry",
    "add_text_to_rect",
    "list_to_onehot",
    "onehot_to_list",
    "ConflictingArgumentsError",
]


class deactivatable_CallbackRegistry(CallbackRegistry):
    def __init__(self, exception_handler=None):
        if exception_handler is not None:
            super().__init__(exception_handler)
        else:
            super().__init__()
        self._active = True

    def process(self, s, *args, **kwargs):
        """
        Process signal *s*.

        All of the functions registered to receive callbacks on *s* will be
        called with ``*args`` and ``**kwargs``.
        """
        if self._active:
            super().process(s, *args, **kwargs)

    @contextlib.contextmanager
    def deactivate(self):
        self._active = False
        yield
        self._active = True


def add_text_to_rect(text, rect, **text_kwargs):
    rx, ry = rect.get_xy()
    cx = rx + rect.get_width() / 2.0
    cy = ry + rect.get_height() / 2.0
    ha = text_kwargs.pop("ha", "center")
    va = text_kwargs.pop("va", "center")
    rect.axes.annotate(text, (cx, cy), ha=ha, va=va, **text_kwargs)


def list_to_onehot(labels, classes):
    lookup = {c: i for i, c in enumerate(classes)}
    arr = np.zeros((len(labels), len(classes)), dtype=bool)
    for i, l in enumerate(labels):

        if isinstance(l, str) or not isinstance(l, Iterable):
            # str, or number, or something like that
            arr[i, lookup[l]] = True
        else:
            for j in l:
                arr[i, lookup[j]] = True
    return arr


def onehot_to_list(onehot, classes):
    c_arr = np.asarray(classes)
    labels = []
    for row in onehot:
        labels.append(list(c_arr[row]))
    return labels


class ConflictingArgumentsError(ValueError):
    pass
