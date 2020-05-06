import numpy as np
import numpy.testing as npt
import pytest
from matplotlib.figure import Figure
from matplotlib.axes import Subplot

from pulse2percept.implants import ArgusII, DiskElectrode
from pulse2percept.models import AxonMapSpatial
from pulse2percept.viz import plot_axon_map, plot_implant_on_axon_map


def test_plot_axon_map():
    fig, ax = plot_axon_map()
    npt.assert_equal(isinstance(fig, Figure), True)
    npt.assert_equal(isinstance(ax, Subplot), True)

    # Check axis limits:
    for xlim, ylim in zip([None, (-2000, 1500)], [(-3000, 1300), None]):
        _, ax = plot_axon_map(xlim=xlim, ylim=ylim)
        if xlim is None:
            xlim = (-5000, 5000)
        if ylim is None:
            ylim = (-4000, 4000)
        npt.assert_almost_equal(ax.get_xlim(), xlim)
        npt.assert_almost_equal(ax.get_ylim(), ylim)

    # Check optic disc center in both eyes:
    model = AxonMapSpatial()
    for eye in ['RE', 'LE']:
        for loc_od in [(15.5, 1.5), (17.9, -0.01)]:
            od = (-loc_od[0], loc_od[1]) if eye == 'LE' else loc_od
            _, ax = plot_axon_map(eye=eye, loc_od=od)
            npt.assert_equal(len(ax.patches), 1)
            npt.assert_almost_equal(
                ax.patches[0].center, model.dva2ret(od))

    # Electrodes and quadrants can be annotated:
    for ann_q, n_q in [(True, 4), (False, 0)]:
        _, ax = plot_axon_map(annotate_quadrants=ann_q)
        npt.assert_equal(len(ax.texts), n_q)

    # Setting upside_down flips y axis:
    _, ax = plot_axon_map(upside_down=True)
    npt.assert_equal(ax.get_xlim(), (-5000, 5000))
    npt.assert_equal(ax.get_ylim(), (4000, -4000))

    with pytest.raises(ValueError):
        plot_axon_map(loc_od=[3])
    with pytest.raises(ValueError):
        plot_axon_map(eye='foo')
    with pytest.raises(ValueError):
        plot_axon_map(n_bundles=0)


def test_plot_implant_on_axon_map():
    fig, ax = plot_implant_on_axon_map(ArgusII())
    npt.assert_equal(isinstance(fig, Figure), True)
    npt.assert_equal(isinstance(ax, Subplot), True)

    # Check axis limits:
    for xlim, ylim in zip([None, (-2000, 1500)], [(-3000, 1300), None]):
        _, ax = plot_implant_on_axon_map(ArgusII(), xlim=xlim, ylim=ylim)
        if xlim is None:
            xlim = (-4000, 4500)
        if ylim is None:
            ylim = (-2500, 3000)
        npt.assert_almost_equal(ax.get_xlim(), xlim)
        npt.assert_almost_equal(ax.get_ylim(), ylim)

    # Check optic disc center in both eyes:
    model = AxonMapSpatial()
    for eye in ['RE', 'LE']:
        for loc_od in [(15.5, 1.5), (17.9, -0.01)]:
            od = (-loc_od[0], loc_od[1]) if eye == 'LE' else loc_od
            _, ax = plot_implant_on_axon_map(ArgusII(eye=eye), loc_od=od)
            npt.assert_equal(len(ax.patches), 1)
            npt.assert_almost_equal(ax.patches[0].center, model.dva2ret(od))

    # Electrodes and quadrants can be annotated:
    for ann_el, n_el in [(True, 60), (False, 0)]:
        for ann_q, n_q in [(True, 4), (False, 0)]:
            _, ax = plot_implant_on_axon_map(ArgusII(),
                                             annotate_implant=ann_el,
                                             annotate_quadrants=ann_q)
            npt.assert_equal(len(ax.texts), n_el + n_q)
            npt.assert_equal(len(ax.collections[0]._paths), 60)

    # Stimulating electrodes are marked:
    fig, ax = plot_implant_on_axon_map(ArgusII(stim=np.ones(60)))

    # Setting upside_down flips y axis:
    _, ax = plot_implant_on_axon_map(ArgusII(), upside_down=True)
    npt.assert_almost_equal(ax.get_xlim(), (-4000, 4500))
    npt.assert_almost_equal(ax.get_ylim(), (3000, -2500))

    with pytest.raises(TypeError):
        plot_implant_on_axon_map(DiskElectrode(0, 0, 0, 100))
    with pytest.raises(ValueError):
        plot_implant_on_axon_map(ArgusII(), n_bundles=0)
