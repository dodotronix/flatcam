from PyQt6 import QtWidgets

from appGUI.GUIElements import RadioSet, FCDoubleSpinner, FCCheckBox, NumericalEvalTupleEntry, FCLabel, FCGridLayout
from appGUI.preferences.OptionsGroupUI import OptionsGroupUI

import gettext
import appTranslation as fcTranslate
import builtins

fcTranslate.apply_language('strings')
if '_' not in builtins.__dict__:
    _ = gettext.gettext


class Tools2CalPrefGroupUI(OptionsGroupUI):
    def __init__(self, defaults, decimals=4, parent=None):

        super(Tools2CalPrefGroupUI, self).__init__(self, parent=parent)

        self.setTitle(str(_("Calibration Plugin")))
        self.decimals = decimals
        self.defaults = defaults

        # ## Grid Layout
        grid_lay = FCGridLayout(v_spacing=5, h_spacing=3)
        self.layout.addLayout(grid_lay)

        self.param_label = FCLabel('<b>%s:</b>' % _('Parameters'))
        self.param_label.setToolTip(
            _("Parameters used for this tool.")
        )
        grid_lay.addWidget(self.param_label, 0, 0, 1, 2)

        # Calibration source
        self.cal_source_lbl = FCLabel("<b>%s:</b>" % _("Source Type"))
        self.cal_source_lbl.setToolTip(_("The source of calibration points.\n"
                                         "It can be:\n"
                                         "- Object -> click a hole geo for Excellon or a pad for Gerber\n"
                                         "- Free -> click freely on canvas to acquire the calibration points"))
        self.cal_source_radio = RadioSet([{'label': _('Object'), 'value': 'object'},
                                          {'label': _('Free'), 'value': 'free'}],
                                         compact=True)

        grid_lay.addWidget(self.cal_source_lbl, 1, 0)
        grid_lay.addWidget(self.cal_source_radio, 1, 1, 1, 2)

        separator_line = QtWidgets.QFrame()
        separator_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        grid_lay.addWidget(separator_line, 2, 0, 1, 2)

        # Travel Z entry
        travelz_lbl = FCLabel('%s:' % _("Travel Z"))
        travelz_lbl.setToolTip(
            _("Height (Z) for travelling between the points.")
        )

        self.travelz_entry = FCDoubleSpinner()
        self.travelz_entry.set_range(-10000.0000, 10000.0000)
        self.travelz_entry.set_precision(self.decimals)
        self.travelz_entry.setSingleStep(0.1)

        grid_lay.addWidget(travelz_lbl, 3, 0)
        grid_lay.addWidget(self.travelz_entry, 3, 1, 1, 2)

        # Verification Z entry
        verz_lbl = FCLabel('%s:' % _("Verification Z"))
        verz_lbl.setToolTip(
            _("Height (Z) for checking the point.")
        )

        self.verz_entry = FCDoubleSpinner()
        self.verz_entry.set_range(-10000.0000, 10000.0000)
        self.verz_entry.set_precision(self.decimals)
        self.verz_entry.setSingleStep(0.1)

        grid_lay.addWidget(verz_lbl, 4, 0)
        grid_lay.addWidget(self.verz_entry, 4, 1, 1, 2)

        # Zero the Z of the verification tool
        self.zeroz_cb = FCCheckBox('%s' % _("Zero Z tool"))
        self.zeroz_cb.setToolTip(
            _("Include a sequence to zero the height (Z)\n"
              "of the verification tool.")
        )

        grid_lay.addWidget(self.zeroz_cb, 5, 0, 1, 3)

        # Toochange Z entry
        toolchangez_lbl = FCLabel('%s:' % _("Toolchange Z"))
        toolchangez_lbl.setToolTip(
            _("Height (Z) for mounting the verification probe.")
        )

        self.toolchangez_entry = FCDoubleSpinner()
        self.toolchangez_entry.set_range(0.0000, 10000.0000)
        self.toolchangez_entry.set_precision(self.decimals)
        self.toolchangez_entry.setSingleStep(0.1)

        grid_lay.addWidget(toolchangez_lbl, 6, 0)
        grid_lay.addWidget(self.toolchangez_entry, 6, 1, 1, 2)

        # Toolchange X-Y entry
        toolchangexy_lbl = FCLabel('%s:' % _('Toolchange X-Y'))
        toolchangexy_lbl.setToolTip(
            _("Toolchange X,Y position.\n"
              "If no value is entered then the current\n"
              "(x, y) point will be used,")
        )

        self.toolchange_xy_entry = NumericalEvalTupleEntry(border_color='#0069A9')

        grid_lay.addWidget(toolchangexy_lbl, 7, 0)
        grid_lay.addWidget(self.toolchange_xy_entry, 7, 1, 1, 2)

        # Second point choice
        second_point_lbl = FCLabel('%s:' % _("Second point"))
        second_point_lbl.setToolTip(
            _("Second point in the Gcode verification can be:\n"
              "- top-left -> the user will align the PCB vertically\n"
              "- bottom-right -> the user will align the PCB horizontally")
        )
        self.second_point_radio = RadioSet([{'label': _('Top Left'), 'value': 'tl'},
                                            {'label': _('Bottom Right'), 'value': 'br'}],
                                           orientation='vertical')

        grid_lay.addWidget(second_point_lbl, 8, 0)
        grid_lay.addWidget(self.second_point_radio, 8, 1, 1, 2)

        self.layout.addStretch()
