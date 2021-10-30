
# mpl-image-labeller's Documentation

Use Matplotlib to label images for classification. Works anywhere Matplotlib does - from the notebook to a standalone gui!


## Key features
- Single or Multiclass interfaces!
- Supports lists of classes or onehot encodings
- Uses keys instead of mouse
- Only depends on Matplotlib
    - Works anywhere - from inside Jupyter to any supported GUI framework
- Displays images with correct aspect ratio
- Easily configurable keymap
- Smart interactions with default Matplotlib keymap
- Callback System (see `examples/callbacks.py`)

## Install
```bash
pip install mpl-image-labeller
```

## Example GIFs
```{table}
:align: center

| Single Class Interface | Multiclass Interface |
| ----------------------- | --------------------|
|![alt](_static/single_class.gif) | ![alt](_static/multi_class.gif)|
```

## Getting help
Please ask usage questions on https://discourse.matplotlib.org/c/3rdparty/18. When you do so feel free
to use `@ianhi` to ping me.

## Reporting Issues
Please report any issues on github at https://github.com/ianhi/mpl-image-labeller/issues/new/choose





```{toctree}
:maxdepth: 2

API <api/mpl_image_labeller>
contributing
```

```{toctree}
:caption: Examples
:maxdepth: 1

examples/single-class.ipynb
examples/multi-class.ipynb
examples/lazy-loading.ipynb
examples/callbacks.ipynb
```
