import napari
import numpy as np

from napari_image_slice.horizontal_slice_widget import HorizontalSliceWidget


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_hozitontal_slice_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))
    my_widget = HorizontalSliceWidget(viewer)
    assert True
