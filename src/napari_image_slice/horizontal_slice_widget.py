import napari
import numpy as np

from magicgui import magicgui
from napari_matplotlib.base import NapariMPLWidget
from qtpy import QtWidgets


class HorizontalSliceWidget(NapariMPLWidget):

    DEFAULT_X_AXIS_LABEL = "x"
    DEFAULT_Y_AXIS_LABEL = "z"

    def __init__(self, napari_viewer: napari.Viewer):
        super().__init__(napari_viewer)
        self.axes = self.canvas.figure.subplots()

        self._grid_layout = QtWidgets.QGridLayout()

        self.layer: napari.layers.Image = None
        self._layer_selection = magicgui(
            self._set_layer,
            call_button=False,
            auto_call=True,
        )
        self._grid_layout.addWidget(self._layer_selection.native, 0, 0)

        self._channel: int = 0
        self._channel_selection = magicgui(
            self._set_channel,
            call_button=False,
            auto_call=True,
            channel=dict(min=0, max=2, step=1),
        )
        self._grid_layout.addWidget(self._channel_selection.native, 1, 0)

        self.layout().insertLayout(0, self._grid_layout)

        self.viewer.cursor.events.position.connect(self._update)

        self.viewer.layers.events.inserted.connect(
            lambda *args: self._layer_selection.reset_choices()
        )
        self.viewer.layers.events.removed.connect(
            lambda *args: self._layer_selection.reset_choices()
        )

        self.setMinimumHeight(300)

    def _update(self, event):
        if self.layer is None:
            self.layer = self._layer_selection.layer.value

        if self.layer is None:
            return

        shape = self.layer.data.shape
        pos = [
            min(max(0, int(xx)), shape[ii] - 1)
            for ii, xx in enumerate(self.viewer.cursor.position)
        ]
        col = pos[-1]
        if self.layer.visible:
            self.axes.clear()
            col1, col2 = self.layer.corner_pixels[:, -1]
            pos[-1] = slice(col1, col2)
            data = self.layer.data[tuple(pos)].squeeze()
            # TODO make this RGB if the layer is RGB
            if data.ndim == 2:
                data = data[:, self._channel]

            data = np.asarray(data)
            cursor_value = data[col - col1]
            self.axes.plot(np.arange(col1, col2), data)
            vmin, vmax = data.min(), data.max()

            self.axes.vlines([col], vmin, vmax, color="r")
            self.axes.text(col, vmax, f"{cursor_value:.3f}")
            self.axes.set_ylabel(self.DEFAULT_Y_AXIS_LABEL)
            self.axes.set_xlabel(self.DEFAULT_X_AXIS_LABEL)
            self.canvas.draw()

    def _set_layer(self, layer: napari.layers.Image):
        self.layer = layer
        self._channel_selection.channel.max = layer.data.shape[-1] - 1
        self._update(None)

    def _set_channel(self, channel: int):
        self._channel = channel
        self._update(None)
