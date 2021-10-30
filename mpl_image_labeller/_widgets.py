import contextlib

import numpy as np
from matplotlib.patches import Rectangle

from ._util import add_text_to_rect, deactivatable_CallbackRegistry


class _array_button(Rectangle):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        active_color="green",
        inactive_color="tab:red",
        **rect_kwargs
    ):
        self._state = False
        self.active_color = active_color
        self.inactive_color = inactive_color

        super().__init__(
            (x, y), width, height, facecolor=inactive_color, picker=True, **rect_kwargs
        )

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        if not isinstance(value, (bool, np.bool_)):
            raise TypeError("Button state must be a bool")
        self._state = value
        self._update_color()

    def _update_color(self):
        col = self.active_color if self.state else self.inactive_color
        self.set_facecolor(col)
        self.set_edgecolor(col)
        self.stale = True


class button_array:
    def __init__(self, options, ax, active_color="green", inactive_color="tab:red"):
        self._ax = ax
        self._fig = ax.figure
        ax.axis("off")
        # if len(options) <= 3:
        #     nrow = 1
        ncol = 4
        len(options)

        gap = 0.05
        width = (1 - (ncol - 1) * gap) / ncol
        height = width
        self._buttons = []
        self._active_color = active_color
        self._inactive_color = inactive_color
        nrow = np.ceil(len(options) / ncol)
        total_height = nrow * height
        top = 0.5 + (total_height / 2)
        for i, o in enumerate(options):
            vert_pos = top - ((i // ncol) * (height + gap)) - height
            horiz_pos = (i % ncol) * (width + gap)
            button = _array_button(
                horiz_pos, vert_pos, width, height, active_color, inactive_color
            )
            self._ax.add_artist(button)
            add_text_to_rect(str(o), button)
            self._buttons.append(button)
        self._ax.figure.canvas.mpl_connect("pick_event", self._on_pick)
        # self._ax.figure.canvas.mpl_connect("key_press_event", self._on_pick)
        self.draw_on = True
        self._observers = deactivatable_CallbackRegistry()

    def on_state_change(self, func):
        """
        Connect *func* to be called the state of the checked buttons changes.
        *func* will receive the updated state and the old state

        Maybe todo: also send the diff of the state.
        """
        self._observers.connect(
            "state-changed", lambda new_state, old_state: func(new_state, old_state)
        )

    def _on_pick(self, event):
        if event.artist in self._buttons:
            old_state = self.get_states()
            event.artist.state = not event.artist.state
            self._observers.process("state-changed", self.get_states(), old_state)
            # TODO: consider whether to draw here?
            # maybe make it toggleable a la draw_on
            self._fig.canvas.draw()

    def activate_all(self):
        for b in self._buttons:
            b.state = True
        if self.draw_on:
            self._fig.canvas.draw()

    def set_states(self, states):
        """
        Update the "buttons" to
        Parameters
        ----------
        toggled : dict or list
            mapping i -> True/False. Does need to include states for every button.
        """
        if isinstance(states, dict):
            enum = states.items()
        else:
            enum = enumerate(states)
        for i, s in enum:
            self._buttons[i].state = s

    def get_states(self):
        """
        Get the states of all buttons as a list
        """
        states = []
        for button in self._buttons:
            states.append(button.state)
        return states

    @contextlib.contextmanager
    def no_callbacks(self):
        with self._observers.deactivate():
            yield
