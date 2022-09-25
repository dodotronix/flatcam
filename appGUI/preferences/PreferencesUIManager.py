import os
from PyQt6 import QtGui, QtCore, QtWidgets
from PyQt6.QtCore import QSettings
from defaults import AppDefaults

from appGUI.GUIElements import FCMessageBox

import gettext
import appTranslation as fcTranslate
import builtins

fcTranslate.apply_language('strings')
if '_' not in builtins.__dict__:
    _ = gettext.gettext


class PreferencesUIManager(QtCore.QObject):

    def __init__(self, defaults: AppDefaults, data_path: str, ui, inform, options):
        """
        Class that control the Preferences Tab

        :param defaults:    a dictionary storage where all the application settings are stored
        :param data_path:   a path to the file where all the preferences are stored for persistence
        :param ui:          reference to the MainGUI class which constructs the UI
        :param inform:      a pyqtSignal used to display information's in the StatusBar of the GUI
        :param options:     a dict holding the current defaults loaded in the application
        """
        super(PreferencesUIManager, self).__init__()

        self.general_displayed = False
        self.gerber_displayed = False
        self.excellon_displayed = False
        self.geometry_displayed = False
        self.cnc_displayed = False
        self.engrave_displayed = False
        self.plugins_displayed = False
        self.plugins2_displayed = False
        self.util_displayed = False

        self.defaults = defaults
        self.data_path = data_path
        self.ui = ui
        self.inform = inform
        self.ignore_tab_close_event = False

        # if Preferences are changed in the Edit -> Preferences tab the value will be set to True
        self.preferences_changed_flag = False

        self.old_color = QtGui.QColor('black')

        # when adding entries here read the comments in the  method found below named:
        # def app_obj.new_object(self, kind, name, initialize, active=True, fit=True, plot=True)
        self.defaults_form_fields = {
            # General App
            "decimals_inch": self.ui.general_pref_form.general_app_group.precision_inch_entry,
            "decimals_metric": self.ui.general_pref_form.general_app_group.precision_metric_entry,
            "units": self.ui.general_pref_form.general_app_group.units_radio,
            "global_graphic_engine": self.ui.general_pref_form.general_app_group.ge_radio,
            "global_graphic_engine_3d_no_mp": self.ui.general_pref_form.general_app_group.ge_comp_cb,
            "global_app_level": self.ui.general_pref_form.general_app_group.app_level_radio,
            "global_log_verbose": self.ui.general_pref_form.general_app_group.verbose_combo,
            "global_portable": self.ui.general_pref_form.general_app_group.portability_cb,

            "global_language_current": self.ui.general_pref_form.general_app_group.language_combo,

            "global_systray_icon": self.ui.general_pref_form.general_app_group.systray_cb,
            "global_shell_at_startup": self.ui.general_pref_form.general_app_group.shell_startup_cb,
            "global_project_at_startup": self.ui.general_pref_form.general_app_group.project_startup_cb,
            "global_version_check": self.ui.general_pref_form.general_app_group.version_check_cb,
            "global_send_stats": self.ui.general_pref_form.general_app_group.send_stats_cb,

            "global_worker_number": self.ui.general_pref_form.general_app_group.worker_number_sb,
            "global_tolerance": self.ui.general_pref_form.general_app_group.tol_entry,

            "global_compression_level": self.ui.general_pref_form.general_app_group.compress_spinner,
            "global_save_compressed": self.ui.general_pref_form.general_app_group.save_type_cb,
            "global_autosave": self.ui.general_pref_form.general_app_group.autosave_cb,
            "global_autosave_timeout": self.ui.general_pref_form.general_app_group.autosave_entry,

            "global_tpdf_tmargin": self.ui.general_pref_form.general_app_group.tmargin_entry,
            "global_tpdf_bmargin": self.ui.general_pref_form.general_app_group.bmargin_entry,
            "global_tpdf_lmargin": self.ui.general_pref_form.general_app_group.lmargin_entry,
            "global_tpdf_rmargin": self.ui.general_pref_form.general_app_group.rmargin_entry,

            # General GUI Preferences
            "global_appearance": self.ui.general_pref_form.general_gui_group.appearance_radio,
            "global_dark_canvas": self.ui.general_pref_form.general_gui_group.dark_canvas_cb,
            "global_layout": self.ui.general_pref_form.general_gui_group.layout_combo,
            "global_hover_shape": self.ui.general_pref_form.general_gui_group.hover_cb,
            "global_selection_shape": self.ui.general_pref_form.general_gui_group.selection_cb,
            "global_selection_shape_as_line": self.ui.general_pref_form.general_gui_group.selection_outline_cb,

            "global_gui_layout": self.ui.general_pref_form.general_gui_group.gui_lay_combo,

            "global_sel_fill": self.ui.general_pref_form.general_gui_group.sf_color_entry,
            "global_sel_line": self.ui.general_pref_form.general_gui_group.sl_color_entry,
            "global_alt_sel_fill": self.ui.general_pref_form.general_gui_group.alt_sf_color_entry,
            "global_alt_sel_line": self.ui.general_pref_form.general_gui_group.alt_sl_color_entry,
            "global_draw_color": self.ui.general_pref_form.general_gui_group.draw_color_entry,
            "global_sel_draw_color": self.ui.general_pref_form.general_gui_group.sel_draw_color_entry,

            "global_proj_item_color_light": self.ui.general_pref_form.general_gui_group.proj_color_light_entry,
            "global_proj_item_dis_color_light": self.ui.general_pref_form.general_gui_group.proj_color_dis_light_entry,
            "global_proj_item_color_dark": self.ui.general_pref_form.general_gui_group.proj_color_dark_entry,
            "global_proj_item_dis_color_dark": self.ui.general_pref_form.general_gui_group.proj_color_dis_dark_entry,

            "global_project_autohide": self.ui.general_pref_form.general_gui_group.project_autohide_cb,

            # General APP Settings
            "global_gridx": self.ui.general_pref_form.general_app_set_group.gridx_entry,
            "global_gridy": self.ui.general_pref_form.general_app_set_group.gridy_entry,
            "global_snap_max": self.ui.general_pref_form.general_app_set_group.snap_max_dist_entry,
            "global_workspace": self.ui.general_pref_form.general_app_set_group.workspace_cb,
            "global_workspaceT": self.ui.general_pref_form.general_app_set_group.wk_cb,
            "global_workspace_orientation": self.ui.general_pref_form.general_app_set_group.wk_orientation_radio,

            "global_axis_color": self.ui.general_pref_form.general_app_set_group.axis_color_entry,

            "global_cursor_type": self.ui.general_pref_form.general_app_set_group.cursor_radio,
            "global_cursor_size": self.ui.general_pref_form.general_app_set_group.cursor_size_entry,
            "global_cursor_width": self.ui.general_pref_form.general_app_set_group.cursor_width_entry,
            "global_cursor_color_enabled": self.ui.general_pref_form.general_app_set_group.mouse_cursor_color_cb,
            "global_cursor_color": self.ui.general_pref_form.general_app_set_group.mouse_cursor_entry,
            "global_pan_button": self.ui.general_pref_form.general_app_set_group.pan_button_radio,
            "global_mselect_key": self.ui.general_pref_form.general_app_set_group.mselect_radio,
            "global_delete_confirmation": self.ui.general_pref_form.general_app_set_group.delete_conf_cb,
            "global_allow_edit_in_project_tab": self.ui.general_pref_form.general_app_set_group.allow_edit_cb,
            "global_open_style": self.ui.general_pref_form.general_app_set_group.open_style_cb,
            "global_toggle_tooltips": self.ui.general_pref_form.general_app_set_group.toggle_tooltips_cb,

            "global_bookmarks_limit": self.ui.general_pref_form.general_app_set_group.bm_limit_spinner,
            "global_activity_icon": self.ui.general_pref_form.general_app_set_group.activity_combo,

            # Gerber General
            "gerber_plot": self.ui.gerber_pref_form.gerber_gen_group.plot_cb,
            "gerber_solid": self.ui.gerber_pref_form.gerber_gen_group.solid_cb,
            "gerber_multicolored": self.ui.gerber_pref_form.gerber_gen_group.multicolored_cb,
            "gerber_store_color_list": self.ui.gerber_pref_form.gerber_gen_group.store_colors_cb,
            "gerber_circle_steps": self.ui.gerber_pref_form.gerber_gen_group.circle_steps_entry,
            "gerber_def_units": self.ui.gerber_pref_form.gerber_gen_group.gerber_units_radio,
            "gerber_def_zeros": self.ui.gerber_pref_form.gerber_gen_group.gerber_zeros_radio,
            "gerber_clean_apertures": self.ui.gerber_pref_form.gerber_gen_group.gerber_clean_cb,
            "gerber_extra_buffering": self.ui.gerber_pref_form.gerber_gen_group.gerber_extra_buffering,
            "gerber_plot_on_select": self.ui.gerber_pref_form.gerber_gen_group.gerber_plot_on_select_cb,
            "gerber_plot_fill": self.ui.gerber_pref_form.gerber_gen_group.fill_color_entry,
            "gerber_plot_line": self.ui.gerber_pref_form.gerber_gen_group.line_color_entry,
            "gerber_plot_line_enable": self.ui.gerber_pref_form.gerber_gen_group.enable_line_cb,

            # Gerber Options
            "gerber_noncoppermargin": self.ui.gerber_pref_form.gerber_opt_group.noncopper_margin_entry,
            "gerber_noncopperrounded": self.ui.gerber_pref_form.gerber_opt_group.noncopper_rounded_cb,
            "gerber_bboxmargin": self.ui.gerber_pref_form.gerber_opt_group.bbmargin_entry,
            "gerber_bboxrounded": self.ui.gerber_pref_form.gerber_opt_group.bbrounded_cb,

            # Gerber Advanced Options
            "gerber_aperture_display": self.ui.gerber_pref_form.gerber_adv_opt_group.aperture_table_visibility_cb,
            # "gerber_aperture_scale_factor": self.ui.gerber_pref_form.gerber_adv_opt_group.scale_aperture_entry,
            # "gerber_aperture_buffer_factor": self.ui.gerber_pref_form.gerber_adv_opt_group.buffer_aperture_entry,
            "gerber_follow": self.ui.gerber_pref_form.gerber_adv_opt_group.follow_cb,
            "gerber_buffering": self.ui.gerber_pref_form.gerber_adv_opt_group.buffering_radio,
            "gerber_delayed_buffering": self.ui.gerber_pref_form.gerber_adv_opt_group.delayed_buffer_cb,
            "gerber_simplification": self.ui.gerber_pref_form.gerber_adv_opt_group.simplify_cb,
            "gerber_simp_tolerance": self.ui.gerber_pref_form.gerber_adv_opt_group.simplification_tol_spinner,

            # Gerber Export
            "gerber_exp_units": self.ui.gerber_pref_form.gerber_exp_group.gerber_units_radio,
            "gerber_exp_integer": self.ui.gerber_pref_form.gerber_exp_group.format_whole_entry,
            "gerber_exp_decimals": self.ui.gerber_pref_form.gerber_exp_group.format_dec_entry,
            "gerber_exp_zeros": self.ui.gerber_pref_form.gerber_exp_group.zeros_radio,

            # Gerber Editor
            "gerber_editor_sel_limit": self.ui.gerber_pref_form.gerber_editor_group.sel_limit_entry,
            "gerber_editor_newcode": self.ui.gerber_pref_form.gerber_editor_group.addcode_entry,
            "gerber_editor_newsize": self.ui.gerber_pref_form.gerber_editor_group.addsize_entry,
            "gerber_editor_newtype": self.ui.gerber_pref_form.gerber_editor_group.addtype_combo,
            "gerber_editor_newdim": self.ui.gerber_pref_form.gerber_editor_group.adddim_entry,
            "gerber_editor_array_size": self.ui.gerber_pref_form.gerber_editor_group.grb_array_size_entry,
            "gerber_editor_lin_dir": self.ui.gerber_pref_form.gerber_editor_group.grb_axis_radio,
            "gerber_editor_lin_pitch": self.ui.gerber_pref_form.gerber_editor_group.grb_pitch_entry,
            "gerber_editor_lin_angle": self.ui.gerber_pref_form.gerber_editor_group.grb_angle_entry,
            "gerber_editor_circ_dir": self.ui.gerber_pref_form.gerber_editor_group.grb_circular_dir_radio,
            "gerber_editor_circ_angle":
                self.ui.gerber_pref_form.gerber_editor_group.grb_circular_angle_entry,
            "gerber_editor_scale_f": self.ui.gerber_pref_form.gerber_editor_group.grb_scale_entry,
            "gerber_editor_buff_f": self.ui.gerber_pref_form.gerber_editor_group.grb_buff_entry,
            "gerber_editor_ma_low": self.ui.gerber_pref_form.gerber_editor_group.grb_ma_low_entry,
            "gerber_editor_ma_high": self.ui.gerber_pref_form.gerber_editor_group.grb_ma_high_entry,

            # Excellon General
            "excellon_plot": self.ui.excellon_pref_form.excellon_gen_group.plot_cb,
            "excellon_circle_steps": self.ui.excellon_pref_form.excellon_gen_group.circle_steps_entry,
            "excellon_solid": self.ui.excellon_pref_form.excellon_gen_group.solid_cb,
            "excellon_multicolored": self.ui.excellon_pref_form.excellon_gen_group.multicolored_cb,
            "excellon_merge_fuse_tools": self.ui.excellon_pref_form.excellon_gen_group.fuse_tools_cb,
            "excellon_format_upper_in":
                self.ui.excellon_pref_form.excellon_gen_group.excellon_format_upper_in_entry,
            "excellon_format_lower_in":
                self.ui.excellon_pref_form.excellon_gen_group.excellon_format_lower_in_entry,
            "excellon_format_upper_mm":
                self.ui.excellon_pref_form.excellon_gen_group.excellon_format_upper_mm_entry,
            "excellon_format_lower_mm":
                self.ui.excellon_pref_form.excellon_gen_group.excellon_format_lower_mm_entry,
            "excellon_zeros": self.ui.excellon_pref_form.excellon_gen_group.excellon_zeros_radio,
            "excellon_units": self.ui.excellon_pref_form.excellon_gen_group.excellon_units_radio,
            "excellon_update": self.ui.excellon_pref_form.excellon_gen_group.update_excellon_cb,
            "excellon_optimization_type": self.ui.excellon_pref_form.excellon_gen_group.excellon_optimization_radio,
            "excellon_search_time": self.ui.excellon_pref_form.excellon_gen_group.optimization_time_entry,
            "excellon_plot_fill": self.ui.excellon_pref_form.excellon_gen_group.fill_color_entry,
            "excellon_plot_line": self.ui.excellon_pref_form.excellon_gen_group.line_color_entry,

            # Excellon Options
            "excellon_drill_tooldia": self.ui.excellon_pref_form.excellon_opt_group.tooldia_entry,
            "excellon_slot_tooldia": self.ui.excellon_pref_form.excellon_opt_group.slot_tooldia_entry,

            # Excellon Advanced Options
            "excellon_tools_table_display": self.ui.excellon_pref_form.excellon_adv_opt_group.table_visibility_cb,
            "excellon_autoload_db":         self.ui.excellon_pref_form.excellon_adv_opt_group.autoload_db_cb,

            # Excellon Export
            "excellon_exp_units":       self.ui.excellon_pref_form.excellon_exp_group.excellon_units_radio,
            "excellon_exp_format":      self.ui.excellon_pref_form.excellon_exp_group.format_radio,
            "excellon_exp_integer":     self.ui.excellon_pref_form.excellon_exp_group.format_whole_entry,
            "excellon_exp_decimals":    self.ui.excellon_pref_form.excellon_exp_group.format_dec_entry,
            "excellon_exp_zeros":       self.ui.excellon_pref_form.excellon_exp_group.zeros_radio,
            "excellon_exp_slot_type":   self.ui.excellon_pref_form.excellon_exp_group.slot_type_radio,

            # Excellon Editor
            "excellon_editor_sel_limit":    self.ui.excellon_pref_form.excellon_editor_group.sel_limit_entry,
            "excellon_editor_newdia":       self.ui.excellon_pref_form.excellon_editor_group.addtool_entry,
            "excellon_editor_array_size":   self.ui.excellon_pref_form.excellon_editor_group.drill_array_size_entry,
            "excellon_editor_lin_dir":      self.ui.excellon_pref_form.excellon_editor_group.drill_axis_radio,
            "excellon_editor_lin_pitch":    self.ui.excellon_pref_form.excellon_editor_group.drill_pitch_entry,
            "excellon_editor_lin_angle":    self.ui.excellon_pref_form.excellon_editor_group.drill_angle_entry,
            "excellon_editor_circ_dir": self.ui.excellon_pref_form.excellon_editor_group.drill_circular_dir_radio,
            "excellon_editor_circ_angle":
                self.ui.excellon_pref_form.excellon_editor_group.drill_circular_angle_entry,
            # Excellon Slots
            "excellon_editor_slot_direction":
                self.ui.excellon_pref_form.excellon_editor_group.slot_direction_radio,
            "excellon_editor_slot_angle":
                self.ui.excellon_pref_form.excellon_editor_group.slot_angle_spinner,
            "excellon_editor_slot_length":
                self.ui.excellon_pref_form.excellon_editor_group.slot_length_entry,
            # Excellon Slots
            "excellon_editor_slot_array_size":
                self.ui.excellon_pref_form.excellon_editor_group.slot_array_size_entry,
            "excellon_editor_slot_lin_dir": self.ui.excellon_pref_form.excellon_editor_group.slot_array_axis_radio,
            "excellon_editor_slot_lin_pitch":
                self.ui.excellon_pref_form.excellon_editor_group.slot_array_pitch_entry,
            "excellon_editor_slot_lin_angle":
                self.ui.excellon_pref_form.excellon_editor_group.slot_array_angle_entry,
            "excellon_editor_slot_circ_dir":
                self.ui.excellon_pref_form.excellon_editor_group.slot_array_circular_dir_radio,
            "excellon_editor_slot_circ_angle":
                self.ui.excellon_pref_form.excellon_editor_group.slot_array_circular_angle_entry,

            # Geometry General
            "geometry_plot":                self.ui.geo_pref_form.geometry_gen_group.plot_cb,
            "geometry_multicolored":        self.ui.geo_pref_form.geometry_gen_group.multicolored_cb,
            "geometry_circle_steps":        self.ui.geo_pref_form.geometry_gen_group.circle_steps_entry,
            "geometry_merge_fuse_tools":    self.ui.geo_pref_form.geometry_gen_group.fuse_tools_cb,
            "geometry_plot_line":           self.ui.geo_pref_form.geometry_gen_group.line_color_entry,

            # Geometry Options
            "geometry_segx":            self.ui.geo_pref_form.geometry_adv_opt_group.segx_entry,
            "geometry_segy":            self.ui.geo_pref_form.geometry_adv_opt_group.segy_entry,

            # Geometry Export
            "geometry_dxf_format":      self.ui.geo_pref_form.geometry_exp_group.dxf_format_combo,
            "geometry_paths_only":      self.ui.geo_pref_form.geometry_exp_group.svg_paths_only_cb,

            # Geometry Editor
            "geometry_editor_sel_limit":        self.ui.geo_pref_form.geometry_editor_group.sel_limit_entry,
            "geometry_editor_milling_type":     self.ui.geo_pref_form.geometry_editor_group.milling_type_radio,

            # CNCJob General
            "cncjob_plot":              self.ui.cncjob_pref_form.cncjob_gen_group.plot_cb,

            "cncjob_tooldia":           self.ui.cncjob_pref_form.cncjob_gen_group.tooldia_entry,
            "cncjob_coords_type":       self.ui.cncjob_pref_form.cncjob_gen_group.coords_type_radio,
            "cncjob_coords_decimals":   self.ui.cncjob_pref_form.cncjob_gen_group.coords_dec_entry,
            "cncjob_fr_decimals":       self.ui.cncjob_pref_form.cncjob_gen_group.fr_dec_entry,
            "cncjob_steps_per_circle":  self.ui.cncjob_pref_form.cncjob_gen_group.steps_per_circle_entry,
            "cncjob_line_ending":       self.ui.cncjob_pref_form.cncjob_gen_group.line_ending_cb,
            "cncjob_plot_line":         self.ui.cncjob_pref_form.cncjob_gen_group.line_color_entry,
            "cncjob_plot_fill":         self.ui.cncjob_pref_form.cncjob_gen_group.fill_color_entry,
            "cncjob_travel_line":       self.ui.cncjob_pref_form.cncjob_gen_group.tline_color_entry,
            "cncjob_travel_fill":       self.ui.cncjob_pref_form.cncjob_gen_group.tfill_color_entry,

            # CNC Job Options
            "cncjob_plot_kind":         self.ui.cncjob_pref_form.cncjob_opt_group.cncplot_method_radio,
            "cncjob_annotation":        self.ui.cncjob_pref_form.cncjob_opt_group.annotation_cb,

            # CNC Job Advanced Options
            "cncjob_annotation_fontsize":   self.ui.cncjob_pref_form.cncjob_adv_opt_group.annotation_fontsize_sp,
            "cncjob_annotation_fontcolor": self.ui.cncjob_pref_form.cncjob_adv_opt_group.annotation_fontcolor_entry,

            # CNC Job Preprocessors Options
            "cncjob_bed_max_x":     self.ui.cncjob_pref_form.cncjob_pp_group.bed_max_x_entry,
            "cncjob_bed_max_y":     self.ui.cncjob_pref_form.cncjob_pp_group.bed_max_y_entry,
            "cncjob_bed_offset_x":  self.ui.cncjob_pref_form.cncjob_pp_group.bed_offx_entry,
            "cncjob_bed_offset_y":  self.ui.cncjob_pref_form.cncjob_pp_group.bed_offy_entry,
            "cncjob_bed_skew_x":    self.ui.cncjob_pref_form.cncjob_pp_group.bed_skewx_entry,
            "cncjob_bed_skew_y":    self.ui.cncjob_pref_form.cncjob_pp_group.bed_skewy_entry,

            # CNC Job (GCode) Editor
            "cncjob_prepend":               self.ui.cncjob_pref_form.cncjob_editor_group.prepend_text,
            "cncjob_append":                self.ui.cncjob_pref_form.cncjob_editor_group.append_text,

            # Isolation Routing Tool
            "tools_iso_tooldia":        self.ui.plugin_eng_pref_form.tools_iso_group.tool_dia_entry,
            "tools_iso_order":          self.ui.plugin_eng_pref_form.tools_iso_group.iso_order_combo,
            "tools_iso_tool_cutz":      self.ui.plugin_eng_pref_form.tools_iso_group.cutz_entry,
            "tools_iso_newdia":         self.ui.plugin_eng_pref_form.tools_iso_group.newdia_entry,

            "tools_iso_tool_shape":     self.ui.plugin_eng_pref_form.tools_iso_group.tool_shape_combo,  # "C1"
            "tools_iso_cutz":           self.ui.plugin_eng_pref_form.tools_iso_group.cutz_entry,
            "tools_iso_vtipdia":        self.ui.plugin_eng_pref_form.tools_iso_group.tipdia_entry,
            "tools_iso_vtipangle":      self.ui.plugin_eng_pref_form.tools_iso_group.tipangle_entry,

            "tools_iso_passes":         self.ui.plugin_eng_pref_form.tools_iso_group.passes_entry,
            "tools_iso_pad_passes":     self.ui.plugin_eng_pref_form.tools_iso_group.pad_passes_entry,
            "tools_iso_overlap":        self.ui.plugin_eng_pref_form.tools_iso_group.overlap_entry,
            "tools_iso_milling_type":   self.ui.plugin_eng_pref_form.tools_iso_group.milling_type_radio,
            "tools_iso_isotype":        self.ui.plugin_eng_pref_form.tools_iso_group.iso_type_radio,

            "tools_iso_rest":           self.ui.plugin_eng_pref_form.tools_iso_group.rest_cb,
            "tools_iso_combine_passes": self.ui.plugin_eng_pref_form.tools_iso_group.combine_passes_cb,
            "tools_iso_check_valid":    self.ui.plugin_eng_pref_form.tools_iso_group.valid_cb,
            "tools_iso_isoexcept":      self.ui.plugin_eng_pref_form.tools_iso_group.except_cb,
            "tools_iso_selection":      self.ui.plugin_eng_pref_form.tools_iso_group.select_combo,
            "tools_iso_poly_ints":      self.ui.plugin_eng_pref_form.tools_iso_group.poly_int_cb,
            "tools_iso_force":          self.ui.plugin_eng_pref_form.tools_iso_group.force_iso_cb,
            "tools_iso_area_shape":     self.ui.plugin_eng_pref_form.tools_iso_group.area_shape_radio,
            "tools_iso_simplification":     self.ui.plugin_eng_pref_form.tools_iso_group.simplify_cb,
            "tools_iso_simplification_tol": self.ui.plugin_eng_pref_form.tools_iso_group.sim_tol_entry,
            "tools_iso_plotting":       self.ui.plugin_eng_pref_form.tools_iso_group.plotting_radio,

            # #########################################################################################################
            # #########################################################################################################
            # Milling Tool
            # #########################################################################################################
            # #########################################################################################################

            # "tools_mill_milling_type": 'both',
            # Milling Plugin Options
            "tools_mill_tooldia": self.ui.plugin_pref_form.tools_mill_group.cnctooldia_entry,
            # "tools_mill_offset_type":   0,  # _('Path')
            # "tools_mill_offset_value":        0.0,
            # "tools_mill_job_type":      0,  # 'Rough'
            "tools_mill_vtipdia": self.ui.plugin_pref_form.tools_mill_group.tipdia_entry,
            "tools_mill_vtipangle": self.ui.plugin_pref_form.tools_mill_group.tipangle_entry,

            "tools_mill_cutz": self.ui.plugin_pref_form.tools_mill_group.cutz_entry,
            "tools_mill_travelz": self.ui.plugin_pref_form.tools_mill_group.travelz_entry,
            "tools_mill_feedrate": self.ui.plugin_pref_form.tools_mill_group.cncfeedrate_entry,
            "tools_mill_feedrate_z": self.ui.plugin_pref_form.tools_mill_group.feedrate_z_entry,
            "tools_mill_spindlespeed": self.ui.plugin_pref_form.tools_mill_group.cncspindlespeed_entry,
            "tools_mill_dwell": self.ui.plugin_pref_form.tools_mill_group.dwell_cb,
            "tools_mill_dwelltime": self.ui.plugin_pref_form.tools_mill_group.dwelltime_entry,
            "tools_mill_ppname_g": self.ui.plugin_pref_form.tools_mill_group.pp_geometry_name_cb,
            "tools_mill_toolchange": self.ui.plugin_pref_form.tools_mill_group.toolchange_cb,
            "tools_mill_toolchangez": self.ui.plugin_pref_form.tools_mill_group.toolchangez_entry,
            "tools_mill_endz": self.ui.plugin_pref_form.tools_mill_group.endz_entry,
            "tools_mill_endxy": self.ui.plugin_pref_form.tools_mill_group.endxy_entry,
            "tools_mill_depthperpass": self.ui.plugin_pref_form.tools_mill_group.depthperpass_entry,
            "tools_mill_multidepth": self.ui.plugin_pref_form.tools_mill_group.multidepth_cb,

            # Miiling Plugin Advanced Options
            "tools_mill_toolchangexy": self.ui.plugin_pref_form.tools_mill_group.toolchangexy_entry,
            "tools_mill_startz": self.ui.plugin_pref_form.tools_mill_group.gstartz_entry,
            "tools_mill_feedrate_rapid": self.ui.plugin_pref_form.tools_mill_group.feedrate_rapid_entry,
            "tools_mill_extracut": self.ui.plugin_pref_form.tools_mill_group.extracut_cb,
            "tools_mill_extracut_length": self.ui.plugin_pref_form.tools_mill_group.e_cut_entry,
            "tools_mill_z_pdepth": self.ui.plugin_pref_form.tools_mill_group.pdepth_entry,
            "tools_mill_feedrate_probe": self.ui.plugin_pref_form.tools_mill_group.feedrate_probe_entry,
            "tools_mill_spindledir": self.ui.plugin_pref_form.tools_mill_group.spindledir_radio,
            "tools_mill_min_power": self.ui.plugin_pref_form.tools_mill_group.las_min_pwr_entry,
            "tools_mill_f_plunge": self.ui.plugin_pref_form.tools_mill_group.fplunge_cb,

            "tools_mill_area_exclusion": self.ui.plugin_pref_form.tools_mill_group.exclusion_cb,
            "tools_mill_area_shape": self.ui.plugin_pref_form.tools_mill_group.area_shape_radio,
            "tools_mill_area_strategy": self.ui.plugin_pref_form.tools_mill_group.strategy_radio,
            "tools_mill_area_overz": self.ui.plugin_pref_form.tools_mill_group.over_z_entry,
            # Polish
            "tools_mill_polish_margin": self.ui.plugin_pref_form.tools_mill_group.polish_margin_entry,
            "tools_mill_polish_overlap": self.ui.plugin_pref_form.tools_mill_group.polish_over_entry,
            "tools_mill_polish_method": self.ui.plugin_pref_form.tools_mill_group.polish_method_combo,

            # those are still in the Geometry Preferences Form
            "tools_mill_optimization_type": self.ui.geo_pref_form.geometry_gen_group.opt_algorithm_radio,
            "tools_mill_search_time": self.ui.geo_pref_form.geometry_gen_group.optimization_time_entry,

            # Excellon Milling
            "tools_mill_milling_type": self.ui.plugin_pref_form.tools_mill_group.milling_type_radio,
            "tools_mill_milling_dia": self.ui.plugin_pref_form.tools_mill_group.mill_dia_entry,
            "tools_mill_milling_overlap": self.ui.plugin_pref_form.tools_mill_group.overlap_entry,
            "tools_mill_milling_connect": self.ui.plugin_pref_form.tools_mill_group.connect_cb,

            # Autolevelling Tool
            "tools_al_mode":             self.ui.plugin_eng_pref_form.tools_level_group.al_mode_radio,
            "tools_al_method":           self.ui.plugin_eng_pref_form.tools_level_group.al_method_radio,
            "tools_al_rows":             self.ui.plugin_eng_pref_form.tools_level_group.al_rows_entry,
            "tools_al_columns":          self.ui.plugin_eng_pref_form.tools_level_group.al_columns_entry,
            "tools_al_travelz":          self.ui.plugin_eng_pref_form.tools_level_group.ptravelz_entry,
            "tools_al_probe_depth":      self.ui.plugin_eng_pref_form.tools_level_group.pdepth_entry,
            "tools_al_probe_fr":         self.ui.plugin_eng_pref_form.tools_level_group.feedrate_probe_entry,
            "tools_al_controller":       self.ui.plugin_eng_pref_form.tools_level_group.al_controller_combo,
            "tools_al_grbl_jog_step":    self.ui.plugin_eng_pref_form.tools_level_group.jog_step_entry,
            "tools_al_grbl_jog_fr":      self.ui.plugin_eng_pref_form.tools_level_group.jog_fr_entry,
            "tools_al_grbl_travelz":     self.ui.plugin_eng_pref_form.tools_level_group.jog_travelz_entry,

            # Drilling Tool
            "tools_drill_tool_order":   self.ui.plugin_pref_form.tools_drill_group.order_combo,
            "tools_drill_cutz":         self.ui.plugin_pref_form.tools_drill_group.cutz_entry,
            "tools_drill_multidepth":   self.ui.plugin_pref_form.tools_drill_group.mpass_cb,
            "tools_drill_depthperpass": self.ui.plugin_pref_form.tools_drill_group.maxdepth_entry,
            "tools_drill_travelz":      self.ui.plugin_pref_form.tools_drill_group.travelz_entry,
            "tools_drill_endz":         self.ui.plugin_pref_form.tools_drill_group.endz_entry,
            "tools_drill_endxy":        self.ui.plugin_pref_form.tools_drill_group.endxy_entry,

            "tools_drill_feedrate_z":   self.ui.plugin_pref_form.tools_drill_group.feedrate_z_entry,
            "tools_drill_spindlespeed": self.ui.plugin_pref_form.tools_drill_group.spindlespeed_entry,
            "tools_drill_dwell":        self.ui.plugin_pref_form.tools_drill_group.dwell_cb,
            "tools_drill_dwelltime":    self.ui.plugin_pref_form.tools_drill_group.dwelltime_entry,
            "tools_drill_toolchange":   self.ui.plugin_pref_form.tools_drill_group.toolchange_cb,
            "tools_drill_toolchangez":  self.ui.plugin_pref_form.tools_drill_group.toolchangez_entry,
            "tools_drill_ppname_e":     self.ui.plugin_pref_form.tools_drill_group.pp_excellon_name_cb,

            "tools_drill_drill_slots":      self.ui.plugin_pref_form.tools_drill_group.drill_slots_cb,
            "tools_drill_drill_overlap":    self.ui.plugin_pref_form.tools_drill_group.drill_overlap_entry,
            "tools_drill_last_drill":       self.ui.plugin_pref_form.tools_drill_group.last_drill_cb,

            # Advanced Options
            "tools_drill_offset":           self.ui.plugin_pref_form.tools_drill_group.offset_entry,
            "tools_drill_toolchangexy":     self.ui.plugin_pref_form.tools_drill_group.toolchangexy_entry,
            "tools_drill_startz":           self.ui.plugin_pref_form.tools_drill_group.estartz_entry,
            "tools_drill_feedrate_rapid":   self.ui.plugin_pref_form.tools_drill_group.feedrate_rapid_entry,
            "tools_drill_z_pdepth":         self.ui.plugin_pref_form.tools_drill_group.pdepth_entry,
            "tools_drill_feedrate_probe":   self.ui.plugin_pref_form.tools_drill_group.feedrate_probe_entry,
            "tools_drill_spindledir":       self.ui.plugin_pref_form.tools_drill_group.spindledir_radio,
            "tools_drill_min_power":        self.ui.plugin_pref_form.tools_drill_group.las_min_pwr_entry,
            "tools_drill_f_plunge":         self.ui.plugin_pref_form.tools_drill_group.fplunge_cb,
            "tools_drill_f_retract":        self.ui.plugin_pref_form.tools_drill_group.fretract_cb,

            # Area Exclusion
            "tools_drill_area_exclusion":   self.ui.plugin_pref_form.tools_drill_group.exclusion_cb,
            "tools_drill_area_shape":       self.ui.plugin_pref_form.tools_drill_group.area_shape_radio,
            "tools_drill_area_strategy":    self.ui.plugin_pref_form.tools_drill_group.strategy_radio,
            "tools_drill_area_overz":       self.ui.plugin_pref_form.tools_drill_group.over_z_entry,

            # NCC Tool
            "tools_ncc_tools":           self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_tool_dia_entry,
            "tools_ncc_order":           self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_order_combo,
            "tools_ncc_overlap":         self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_overlap_entry,
            "tools_ncc_margin":          self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_margin_entry,
            "tools_ncc_method":          self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_method_combo,
            "tools_ncc_connect":         self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_connect_cb,
            "tools_ncc_contour":         self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_contour_cb,
            "tools_ncc_rest":            self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_rest_cb,
            "tools_ncc_offset_choice":  self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_choice_offset_cb,
            "tools_ncc_offset_value":   self.ui.plugin_eng_pref_form.tools_ncc_group.ncc_offset_spinner,
            "tools_ncc_ref":             self.ui.plugin_eng_pref_form.tools_ncc_group.select_combo,
            "tools_ncc_area_shape":     self.ui.plugin_eng_pref_form.tools_ncc_group.area_shape_radio,
            "tools_ncc_milling_type":    self.ui.plugin_eng_pref_form.tools_ncc_group.milling_type_radio,
            "tools_ncc_cutz":            self.ui.plugin_eng_pref_form.tools_ncc_group.cutz_entry,
            "tools_ncc_tipdia":          self.ui.plugin_eng_pref_form.tools_ncc_group.tipdia_entry,
            "tools_ncc_tipangle":        self.ui.plugin_eng_pref_form.tools_ncc_group.tipangle_entry,
            "tools_ncc_newdia":          self.ui.plugin_eng_pref_form.tools_ncc_group.newdia_entry,
            "tools_ncc_plotting":       self.ui.plugin_eng_pref_form.tools_ncc_group.plotting_radio,
            "tools_ncc_check_valid":    self.ui.plugin_eng_pref_form.tools_ncc_group.valid_cb,

            # CutOut Tool
            "tools_cutout_tooldia":          self.ui.plugin_pref_form.tools_cutout_group.cutout_tooldia_entry,
            "tools_cutout_kind":             self.ui.plugin_pref_form.tools_cutout_group.obj_kind_combo,
            "tools_cutout_margin":          self.ui.plugin_pref_form.tools_cutout_group.cutout_margin_entry,
            "tools_cutout_z":               self.ui.plugin_pref_form.tools_cutout_group.cutz_entry,
            "tools_cutout_depthperpass":    self.ui.plugin_pref_form.tools_cutout_group.maxdepth_entry,
            "tools_cutout_mdepth":          self.ui.plugin_pref_form.tools_cutout_group.mpass_cb,
            "tools_cutout_gapsize":         self.ui.plugin_pref_form.tools_cutout_group.cutout_gap_entry,
            "tools_cutout_gaps_ff":         self.ui.plugin_pref_form.tools_cutout_group.gaps_combo,
            "tools_cutout_convexshape":     self.ui.plugin_pref_form.tools_cutout_group.convex_box,
            "tools_cutout_big_cursor":      self.ui.plugin_pref_form.tools_cutout_group.big_cursor_cb,

            "tools_cutout_gap_type":        self.ui.plugin_pref_form.tools_cutout_group.gaptype_combo,
            "tools_cutout_gap_depth":       self.ui.plugin_pref_form.tools_cutout_group.thin_depth_entry,
            "tools_cutout_mb_dia":          self.ui.plugin_pref_form.tools_cutout_group.mb_dia_entry,
            "tools_cutout_mb_spacing":      self.ui.plugin_pref_form.tools_cutout_group.mb_spacing_entry,

            "tools_cutout_drill_dia":       self.ui.plugin_pref_form.tools_cutout_group.drill_dia_entry,
            "tools_cutout_drill_pitch":     self.ui.plugin_pref_form.tools_cutout_group.drill_pitch_entry,
            "tools_cutout_drill_margin":    self.ui.plugin_pref_form.tools_cutout_group.drill_margin_entry,

            # Paint Area Tool
            "tools_paint_tooldia":       self.ui.plugin_eng_pref_form.tools_paint_group.painttooldia_entry,
            "tools_paint_order":         self.ui.plugin_eng_pref_form.tools_paint_group.paint_order_combo,
            "tools_paint_overlap":       self.ui.plugin_eng_pref_form.tools_paint_group.paintoverlap_entry,
            "tools_paint_offset":        self.ui.plugin_eng_pref_form.tools_paint_group.paintmargin_entry,
            "tools_paint_method":        self.ui.plugin_eng_pref_form.tools_paint_group.paintmethod_combo,
            "tools_paint_selectmethod":       self.ui.plugin_eng_pref_form.tools_paint_group.selectmethod_combo,
            "tools_paint_area_shape":   self.ui.plugin_eng_pref_form.tools_paint_group.area_shape_radio,
            "tools_paint_connect":        self.ui.plugin_eng_pref_form.tools_paint_group.pathconnect_cb,
            "tools_paint_contour":       self.ui.plugin_eng_pref_form.tools_paint_group.contour_cb,
            "tools_paint_plotting":     self.ui.plugin_eng_pref_form.tools_paint_group.paint_plotting_radio,

            "tools_paint_rest":          self.ui.plugin_eng_pref_form.tools_paint_group.rest_cb,
            "tools_paint_cutz":          self.ui.plugin_eng_pref_form.tools_paint_group.cutz_entry,
            "tools_paint_tipdia":        self.ui.plugin_eng_pref_form.tools_paint_group.tipdia_entry,
            "tools_paint_tipangle":      self.ui.plugin_eng_pref_form.tools_paint_group.tipangle_entry,
            "tools_paint_newdia":        self.ui.plugin_eng_pref_form.tools_paint_group.newdia_entry,

            # 2-sided Tool
            "tools_2sided_mirror_axis": self.ui.plugin_eng_pref_form.tools_2sided_group.mirror_axis_radio,
            "tools_2sided_axis_loc":    self.ui.plugin_eng_pref_form.tools_2sided_group.axis_location_radio,
            "tools_2sided_drilldia":    self.ui.plugin_eng_pref_form.tools_2sided_group.drill_dia_entry,
            "tools_2sided_align_type": self.ui.plugin_eng_pref_form.tools_2sided_group.align_type_radio,

            # Film Tool
            "tools_film_shape": self.ui.plugin_pref_form.tools_film_group.convex_box_cb,
            "tools_film_rounded": self.ui.plugin_pref_form.tools_film_group.rounded_cb,
            "tools_film_polarity": self.ui.plugin_pref_form.tools_film_group.film_type_radio,
            "tools_film_boundary": self.ui.plugin_pref_form.tools_film_group.film_boundary_entry,
            "tools_film_scale_stroke": self.ui.plugin_pref_form.tools_film_group.film_scale_stroke_entry,
            "tools_film_color": self.ui.plugin_pref_form.tools_film_group.film_color_entry,

            "tools_film_scale_cb": self.ui.plugin_pref_form.tools_film_group.film_scale_cb,
            "tools_film_scale_type": self.ui.plugin_pref_form.tools_film_group.film_scale_type_combo,  # "length"
            "tools_film_scale_x_entry": self.ui.plugin_pref_form.tools_film_group.film_scalex_entry,
            "tools_film_scale_y_entry": self.ui.plugin_pref_form.tools_film_group.film_scaley_entry,
            "tools_film_scale_ref": self.ui.plugin_pref_form.tools_film_group.film_scale_ref_combo,

            "tools_film_skew_cb": self.ui.plugin_pref_form.tools_film_group.film_skew_cb,
            "tools_film_skew_type": self.ui.plugin_pref_form.tools_film_group.film_skew_type_combo,  # "length"
            "tools_film_skew_x_entry": self.ui.plugin_pref_form.tools_film_group.film_skewx_entry,
            "tools_film_skew_y_entry": self.ui.plugin_pref_form.tools_film_group.film_skewy_entry,
            "tools_film_skew_ref": self.ui.plugin_pref_form.tools_film_group.film_skew_ref_combo,

            "tools_film_mirror_cb": self.ui.plugin_pref_form.tools_film_group.film_mirror_cb,
            "tools_film_mirror_axis_radio": self.ui.plugin_pref_form.tools_film_group.film_mirror_axis,
            "tools_film_file_type_radio": self.ui.plugin_pref_form.tools_film_group.file_type_radio,
            "tools_film_orientation": self.ui.plugin_pref_form.tools_film_group.orientation_radio,
            "tools_film_pagesize": self.ui.plugin_pref_form.tools_film_group.pagesize_combo,
            "tools_film_png_dpi": self.ui.plugin_pref_form.tools_film_group.png_dpi_spinner,

            # Panelize Tool
            "tools_panelize_spacing_columns": self.ui.plugin_pref_form.tools_panelize_group.pspacing_columns,
            "tools_panelize_spacing_rows": self.ui.plugin_pref_form.tools_panelize_group.pspacing_rows,
            "tools_panelize_columns": self.ui.plugin_pref_form.tools_panelize_group.pcolumns,
            "tools_panelize_rows": self.ui.plugin_pref_form.tools_panelize_group.prows,
            "tools_panelize_optimization": self.ui.plugin_pref_form.tools_panelize_group.poptimization_cb,
            "tools_panelize_constrain": self.ui.plugin_pref_form.tools_panelize_group.pconstrain_cb,
            "tools_panelize_constrainx": self.ui.plugin_pref_form.tools_panelize_group.px_width_entry,
            "tools_panelize_constrainy": self.ui.plugin_pref_form.tools_panelize_group.py_height_entry,
            "tools_panelize_panel_type": self.ui.plugin_pref_form.tools_panelize_group.panel_type_radio,

            # Calculators Tool
            "tools_calc_vshape_tip_dia": self.ui.plugin_pref_form.tools_calculators_group.tip_dia_entry,
            "tools_calc_vshape_tip_angle": self.ui.plugin_pref_form.tools_calculators_group.tip_angle_entry,
            "tools_calc_vshape_cut_z": self.ui.plugin_pref_form.tools_calculators_group.cut_z_entry,
            "tools_calc_electro_length": self.ui.plugin_pref_form.tools_calculators_group.pcblength_entry,
            "tools_calc_electro_width": self.ui.plugin_pref_form.tools_calculators_group.pcbwidth_entry,
            "tools_calc_electro_area": self.ui.plugin_pref_form.tools_calculators_group.area_entry,
            "tools_calc_electro_cdensity": self.ui.plugin_pref_form.tools_calculators_group.cdensity_entry,
            "tools_calc_electro_growth": self.ui.plugin_pref_form.tools_calculators_group.growth_entry,

            # Transformations Tool
            "tools_transform_reference": self.ui.plugin_pref_form.tools_transform_group.ref_combo,
            "tools_transform_ref_object": self.ui.plugin_pref_form.tools_transform_group.type_obj_combo,
            "tools_transform_ref_point": self.ui.plugin_pref_form.tools_transform_group.point_entry,

            "tools_transform_rotate": self.ui.plugin_pref_form.tools_transform_group.rotate_entry,

            "tools_transform_skew_x": self.ui.plugin_pref_form.tools_transform_group.skewx_entry,
            "tools_transform_skew_y": self.ui.plugin_pref_form.tools_transform_group.skewy_entry,
            "tools_transform_skew_link": self.ui.plugin_pref_form.tools_transform_group.skew_link_cb,

            "tools_transform_scale_x": self.ui.plugin_pref_form.tools_transform_group.scalex_entry,
            "tools_transform_scale_y": self.ui.plugin_pref_form.tools_transform_group.scaley_entry,
            "tools_transform_scale_link": self.ui.plugin_pref_form.tools_transform_group.scale_link_cb,

            "tools_transform_offset_x": self.ui.plugin_pref_form.tools_transform_group.offx_entry,
            "tools_transform_offset_y": self.ui.plugin_pref_form.tools_transform_group.offy_entry,

            "tools_transform_buffer_dis": self.ui.plugin_pref_form.tools_transform_group.buffer_entry,
            "tools_transform_buffer_factor": self.ui.plugin_pref_form.tools_transform_group.buffer_factor_entry,
            "tools_transform_buffer_corner": self.ui.plugin_pref_form.tools_transform_group.buffer_rounded_cb,

            # SolderPaste Dispensing Tool
            "tools_solderpaste_tools": self.ui.plugin_pref_form.tools_solderpaste_group.nozzle_tool_dia_entry,
            "tools_solderpaste_new": self.ui.plugin_pref_form.tools_solderpaste_group.addtool_entry,
            "tools_solderpaste_margin": self.ui.plugin_pref_form.tools_solderpaste_group.margin_entry,
            "tools_solderpaste_z_start": self.ui.plugin_pref_form.tools_solderpaste_group.z_start_entry,
            "tools_solderpaste_z_dispense": self.ui.plugin_pref_form.tools_solderpaste_group.z_dispense_entry,
            "tools_solderpaste_z_stop": self.ui.plugin_pref_form.tools_solderpaste_group.z_stop_entry,
            "tools_solderpaste_z_travel": self.ui.plugin_pref_form.tools_solderpaste_group.z_travel_entry,
            "tools_solderpaste_z_toolchange": self.ui.plugin_pref_form.tools_solderpaste_group.z_toolchange_entry,
            "tools_solderpaste_xy_toolchange": self.ui.plugin_pref_form.tools_solderpaste_group.xy_toolchange_entry,
            "tools_solderpaste_frxy": self.ui.plugin_pref_form.tools_solderpaste_group.frxy_entry,
            "tools_solderpaste_frz": self.ui.plugin_pref_form.tools_solderpaste_group.frz_entry,
            "tools_solderpaste_fr_rapids": self.ui.plugin_pref_form.tools_solderpaste_group.fr_rapids_entry,
            "tools_solderpaste_frz_dispense": self.ui.plugin_pref_form.tools_solderpaste_group.frz_dispense_entry,
            "tools_solderpaste_speedfwd": self.ui.plugin_pref_form.tools_solderpaste_group.speedfwd_entry,
            "tools_solderpaste_dwellfwd": self.ui.plugin_pref_form.tools_solderpaste_group.dwellfwd_entry,
            "tools_solderpaste_speedrev": self.ui.plugin_pref_form.tools_solderpaste_group.speedrev_entry,
            "tools_solderpaste_dwellrev": self.ui.plugin_pref_form.tools_solderpaste_group.dwellrev_entry,
            "tools_solderpaste_pp": self.ui.plugin_pref_form.tools_solderpaste_group.pp_combo,

            # Subtractor Tool
            "tools_sub_close_paths": self.ui.plugin_pref_form.tools_sub_group.close_paths_cb,
            "tools_sub_delete_sources":  self.ui.plugin_pref_form.tools_sub_group.delete_sources_cb,

            # Corner Markers Tool
            "tools_markers_type": self.ui.plugin_pref_form.tools_markers_group.type_radio,
            "tools_markers_thickness": self.ui.plugin_pref_form.tools_markers_group.thick_entry,
            "tools_markers_length": self.ui.plugin_pref_form.tools_markers_group.l_entry,
            "tools_markers_reference": self.ui.plugin_pref_form.tools_markers_group.ref_radio,
            "tools_markers_offset_x": self.ui.plugin_pref_form.tools_markers_group.offset_x_entry,
            "tools_markers_offset_y": self.ui.plugin_pref_form.tools_markers_group.offset_y_entry,
            "tools_markers_drill_dia": self.ui.plugin_pref_form.tools_markers_group.drill_dia_entry,

            # #######################################################################################################
            # ########################################## PLUGINS 2 ##################################################
            # #######################################################################################################

            # Optimal Tool
            "tools_opt_precision": self.ui.plugin2_pref_form.tools2_optimal_group.precision_sp,

            # Check Rules Tool
            "tools_cr_trace_size": self.ui.plugin2_pref_form.tools2_checkrules_group.trace_size_cb,
            "tools_cr_trace_size_val": self.ui.plugin2_pref_form.tools2_checkrules_group.trace_size_entry,
            "tools_cr_c2c": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_copper2copper_cb,
            "tools_cr_c2c_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_copper2copper_entry,
            "tools_cr_c2o": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_copper2ol_cb,
            "tools_cr_c2o_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_copper2ol_entry,
            "tools_cr_s2s": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_silk2silk_cb,
            "tools_cr_s2s_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_silk2silk_entry,
            "tools_cr_s2sm": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_silk2sm_cb,
            "tools_cr_s2sm_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_silk2sm_entry,
            "tools_cr_s2o": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_silk2ol_cb,
            "tools_cr_s2o_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_silk2ol_entry,
            "tools_cr_sm2sm": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_sm2sm_cb,
            "tools_cr_sm2sm_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_sm2sm_entry,
            "tools_cr_ri": self.ui.plugin2_pref_form.tools2_checkrules_group.ring_integrity_cb,
            "tools_cr_ri_val": self.ui.plugin2_pref_form.tools2_checkrules_group.ring_integrity_entry,
            "tools_cr_h2h": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_d2d_cb,
            "tools_cr_h2h_val": self.ui.plugin2_pref_form.tools2_checkrules_group.clearance_d2d_entry,
            "tools_cr_dh": self.ui.plugin2_pref_form.tools2_checkrules_group.drill_size_cb,
            "tools_cr_dh_val": self.ui.plugin2_pref_form.tools2_checkrules_group.drill_size_entry,

            # QRCode Tool
            "tools_qrcode_version": self.ui.plugin2_pref_form.tools2_qrcode_group.version_entry,
            "tools_qrcode_error": self.ui.plugin2_pref_form.tools2_qrcode_group.error_radio,
            "tools_qrcode_box_size": self.ui.plugin2_pref_form.tools2_qrcode_group.bsize_entry,
            "tools_qrcode_border_size": self.ui.plugin2_pref_form.tools2_qrcode_group.border_size_entry,
            "tools_qrcode_qrdata": self.ui.plugin2_pref_form.tools2_qrcode_group.text_data,
            "tools_qrcode_polarity": self.ui.plugin2_pref_form.tools2_qrcode_group.pol_radio,
            "tools_qrcode_rounded": self.ui.plugin2_pref_form.tools2_qrcode_group.bb_radio,
            "tools_qrcode_fill_color": self.ui.plugin2_pref_form.tools2_qrcode_group.fill_color_entry,
            "tools_qrcode_back_color": self.ui.plugin2_pref_form.tools2_qrcode_group.back_color_entry,
            "tools_qrcode_sel_limit": self.ui.plugin2_pref_form.tools2_qrcode_group.sel_limit_entry,

            # Copper Thieving Tool
            "tools_copper_thieving_clearance": self.ui.plugin2_pref_form.tools2_cfill_group.clearance_entry,
            "tools_copper_thieving_margin": self.ui.plugin2_pref_form.tools2_cfill_group.margin_entry,
            "tools_copper_thieving_area": self.ui.plugin2_pref_form.tools2_cfill_group.area_entry,
            "tools_copper_thieving_reference": self.ui.plugin2_pref_form.tools2_cfill_group.reference_combo,
            "tools_copper_thieving_box_type": self.ui.plugin2_pref_form.tools2_cfill_group.bbox_type_radio,
            "tools_copper_thieving_circle_steps": self.ui.plugin2_pref_form.tools2_cfill_group.circlesteps_entry,
            "tools_copper_thieving_fill_type": self.ui.plugin2_pref_form.tools2_cfill_group.fill_type_combo,
            "tools_copper_thieving_dots_dia": self.ui.plugin2_pref_form.tools2_cfill_group.dot_dia_entry,
            "tools_copper_thieving_dots_spacing": self.ui.plugin2_pref_form.tools2_cfill_group.dot_spacing_entry,
            "tools_copper_thieving_squares_size": self.ui.plugin2_pref_form.tools2_cfill_group.square_size_entry,
            "tools_copper_thieving_squares_spacing":
                self.ui.plugin2_pref_form.tools2_cfill_group.squares_spacing_entry,
            "tools_copper_thieving_lines_size": self.ui.plugin2_pref_form.tools2_cfill_group.line_size_entry,
            "tools_copper_thieving_lines_spacing": self.ui.plugin2_pref_form.tools2_cfill_group.lines_spacing_entry,
            "tools_copper_thieving_rb_margin": self.ui.plugin2_pref_form.tools2_cfill_group.rb_margin_entry,
            "tools_copper_thieving_rb_thickness": self.ui.plugin2_pref_form.tools2_cfill_group.rb_thickness_entry,
            "tools_copper_thieving_only_apds": self.ui.plugin2_pref_form.tools2_cfill_group.only_pads_cb,
            "tools_copper_thieving_mask_clearance": self.ui.plugin2_pref_form.tools2_cfill_group.clearance_ppm_entry,
            "tools_copper_thieving_geo_choice": self.ui.plugin2_pref_form.tools2_cfill_group.ppm_choice_combo,

            # Fiducials Tool
            "tools_fiducials_dia": self.ui.plugin2_pref_form.tools2_fiducials_group.dia_entry,
            "tools_fiducials_margin": self.ui.plugin2_pref_form.tools2_fiducials_group.margin_entry,
            "tools_fiducials_mode": self.ui.plugin2_pref_form.tools2_fiducials_group.mode_radio,
            "tools_fiducials_second_pos": self.ui.plugin2_pref_form.tools2_fiducials_group.pos_radio,
            "tools_fiducials_type": self.ui.plugin2_pref_form.tools2_fiducials_group.fid_type_combo,
            "tools_fiducials_line_thickness": self.ui.plugin2_pref_form.tools2_fiducials_group.line_thickness_entry,

            # Extract Drills Tool
            "tools_extract_hole_type": self.ui.plugin2_pref_form.tools2_edrills_group.method_radio,
            "tools_extract_hole_fixed_dia": self.ui.plugin2_pref_form.tools2_edrills_group.dia_entry,
            "tools_extract_hole_prop_factor": self.ui.plugin2_pref_form.tools2_edrills_group.factor_entry,
            "tools_extract_circular_ring": self.ui.plugin2_pref_form.tools2_edrills_group.circular_ring_entry,
            "tools_extract_oblong_ring": self.ui.plugin2_pref_form.tools2_edrills_group.oblong_ring_entry,
            "tools_extract_square_ring": self.ui.plugin2_pref_form.tools2_edrills_group.square_ring_entry,
            "tools_extract_rectangular_ring": self.ui.plugin2_pref_form.tools2_edrills_group.rectangular_ring_entry,
            "tools_extract_others_ring": self.ui.plugin2_pref_form.tools2_edrills_group.other_ring_entry,
            "tools_extract_circular": self.ui.plugin2_pref_form.tools2_edrills_group.circular_cb,
            "tools_extract_oblong": self.ui.plugin2_pref_form.tools2_edrills_group.oblong_cb,
            "tools_extract_square": self.ui.plugin2_pref_form.tools2_edrills_group.square_cb,
            "tools_extract_rectangular": self.ui.plugin2_pref_form.tools2_edrills_group.rectangular_cb,
            "tools_extract_others": self.ui.plugin2_pref_form.tools2_edrills_group.other_cb,
            "tools_extract_sm_clearance": self.ui.plugin2_pref_form.tools2_edrills_group.clearance_entry,
            "tools_extract_cut_margin": self.ui.plugin2_pref_form.tools2_edrills_group.margin_cut_entry,
            "tools_extract_cut_thickness": self.ui.plugin2_pref_form.tools2_edrills_group.thick_cut_entry,

            # Punch Gerber Tool
            "tools_punch_hole_type": self.ui.plugin2_pref_form.tools2_punch_group.hole_size_radio,
            "tools_punch_hole_fixed_dia": self.ui.plugin2_pref_form.tools2_punch_group.dia_entry,
            "tools_punch_hole_prop_factor": self.ui.plugin2_pref_form.tools2_punch_group.factor_entry,
            "tools_punch_circular_ring": self.ui.plugin2_pref_form.tools2_punch_group.circular_ring_entry,
            "tools_punch_oblong_ring": self.ui.plugin2_pref_form.tools2_punch_group.oblong_ring_entry,
            "tools_punch_square_ring": self.ui.plugin2_pref_form.tools2_punch_group.square_ring_entry,
            "tools_punch_rectangular_ring": self.ui.plugin2_pref_form.tools2_punch_group.rectangular_ring_entry,
            "tools_punch_others_ring": self.ui.plugin2_pref_form.tools2_punch_group.other_ring_entry,
            "tools_punch_circular": self.ui.plugin2_pref_form.tools2_punch_group.circular_cb,
            "tools_punch_oblong": self.ui.plugin2_pref_form.tools2_punch_group.oblong_cb,
            "tools_punch_square": self.ui.plugin2_pref_form.tools2_punch_group.square_cb,
            "tools_punch_rectangular": self.ui.plugin2_pref_form.tools2_punch_group.rectangular_cb,
            "tools_punch_others": self.ui.plugin2_pref_form.tools2_punch_group.other_cb,

            # Invert Gerber Tool
            "tools_invert_margin": self.ui.plugin2_pref_form.tools2_invert_group.margin_entry,
            "tools_invert_join_style": self.ui.plugin2_pref_form.tools2_invert_group.join_radio,

            # Utilities
            # File associations
            "fa_excellon": self.ui.util_pref_form.fa_excellon_group.exc_list_text,
            "fa_gcode": self.ui.util_pref_form.fa_gcode_group.gco_list_text,
            # "fa_geometry": self.ui.util_pref_form.fa_geometry_group.close_paths_cb,
            "fa_gerber": self.ui.util_pref_form.fa_gerber_group.grb_list_text,
            "util_autocomplete_keywords": self.ui.util_pref_form.kw_group.kw_list_text,

        }

        # set the colors of the tab text's to default and the color of the first tab is 'green'
        self.ui.on_pref_tabbar_clicked(0)

    def defaults_read_form(self):
        """
        Will read all the values in the Preferences GUI and update the defaults dictionary.

        :return: None
        """
        for option in self.defaults_form_fields:
            try:
                self.defaults[option] = self.defaults_form_fields[option].get_value()
            except Exception as e:
                self.ui.app.log.error("App.defaults_read_form() --> %s" % str(e))

    def defaults_write_form(self, factor=None, fl_units=None, source_dict=None):
        """
        Will set the values for all the GUI elements in Preferences GUI based on the values found in the
        self.defaults dictionary.

        :param factor:          will apply a factor to the values that written in the GUI elements
        :param fl_units:        current measuring units in FlatCAM: Metric or Inch
        :param source_dict:     the repository of options, usually is the self.defaults
        :return: None
        """

        options_storage = self.defaults if source_dict is None else source_dict

        for option in options_storage:
            if source_dict:
                self.defaults_write_form_field(option, factor=factor, units=fl_units, defaults_dict=source_dict)
            else:
                self.defaults_write_form_field(option, factor=factor, units=fl_units)

    def defaults_write_form_field(self, field, factor=None, units=None, defaults_dict=None):
        """
        Basically it is the worker in the self.defaults_write_form()

        :param field:           the GUI element in Preferences GUI to be updated
        :param factor:          factor to be applied to the field parameter
        :param units:           current FlatCAM measuring units
        :param defaults_dict:   the defaults storage
        :return:                None, it updates GUI elements
        """

        def_dict = self.defaults if defaults_dict is None else defaults_dict

        try:
            value = def_dict[field]
            # log.debug("value is " + str(value) + " and factor is "+str(factor))
            if factor is not None and not isinstance(value, str):
                value *= factor

            form_field = self.defaults_form_fields[field]
            if units is None:
                form_field.set_value(value)
            elif (units == 'IN' or units == 'MM') and (field == 'global_gridx' or field == 'global_gridy'):
                form_field.set_value(value)
        except KeyError:
            pass
        except AttributeError:
            self.ui.app.log.debug(field)

    def show_preferences_gui(self):
        """
        Called to initialize and show the Preferences appGUI

        :return: None
        """
        self.init_preferences_gui()

        self.pref_connect()

        # Initialize the color box's color in Preferences -> Global -> Colors
        self.__init_color_pickers()

        # log.debug("Finished Preferences GUI form initialization.")

    def init_preferences_gui(self):
        self.general_displayed = False
        self.gerber_displayed = False
        self.excellon_displayed = False
        self.geometry_displayed = False
        self.cnc_displayed = False
        self.engrave_displayed = False
        self.plugins_displayed = False
        self.plugins2_displayed = False
        self.util_displayed = False

        gen_form = self.ui.general_pref_form
        try:
            self.ui.general_scroll_area.takeWidget()
        except Exception:
            self.ui.app.log.debug("Nothing to remove")
        self.ui.general_scroll_area.setWidget(gen_form)
        gen_form.show()

    def pref_connect(self):
        self.pref_disconnect()

        self.ui.pref_tab_area.tabBarClicked.connect(self.on_tab_clicked)

        # Button handlers
        self.ui.pref_save_button.clicked.connect(lambda: self.on_save_button(save_to_file=True))
        self.ui.pref_apply_button.clicked.connect(lambda: self.on_save_button(save_to_file=False))
        self.ui.pref_close_button.clicked.connect(self.on_pref_close_button)
        self.ui.pref_defaults_button.clicked.connect(self.on_restore_defaults_preferences)

    def pref_disconnect(self):
        try:
            self.ui.pref_tab_area.tabBarClicked.disconnect()
        except Exception:
            pass

        # Disconnect Button handlers
        try:
            self.ui.pref_save_button.clicked.disconnect()
        except Exception:
            pass

        try:
            self.ui.pref_apply_button.clicked.disconnect()
        except Exception:
            pass

        try:
            self.ui.pref_close_button.clicked.disconnect()
        except Exception:
            pass

        try:
            self.ui.pref_defaults_button.clicked.disconnect()
        except Exception:
            pass

    def clear_preferences_gui(self):
        self.pref_disconnect()
        # try:
        #     self.ui.general_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.gerber_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.excellon_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.geometry_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.cncjob_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.plugins_engraving_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.tools_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.tools2_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")
        #
        # try:
        #     self.ui.fa_scroll_area.takeWidget()
        # except Exception:
        #     self.ui.app.log.debug("Nothing to remove")

    def on_tab_clicked(self, idx):
        if idx == 0 and self.general_displayed is False:
            self.general_displayed = True
            gen_form = self.ui.general_pref_form
            try:
                self.ui.general_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.general_scroll_area.setWidget(gen_form)
            gen_form.show()

        if idx == 1 and self.gerber_displayed is False:
            self.gerber_displayed = True
            ger_form = self.ui.gerber_pref_form
            try:
                self.ui.gerber_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.gerber_scroll_area.setWidget(ger_form)
            ger_form.show()

        if idx == 2 and self.excellon_displayed is False:
            self.excellon_displayed = True
            exc_form = self.ui.excellon_pref_form
            try:
                self.ui.excellon_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.excellon_scroll_area.setWidget(exc_form)
            exc_form.show()

        if idx == 3 and self.geometry_displayed is False:
            self.geometry_displayed = True
            geo_form = self.ui.geo_pref_form
            try:
                self.ui.geometry_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.geometry_scroll_area.setWidget(geo_form)
            geo_form.show()

        if idx == 4 and self.cnc_displayed is False:
            self.cnc_displayed = True
            cnc_form = self.ui.cncjob_pref_form
            try:
                self.ui.cncjob_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.cncjob_scroll_area.setWidget(cnc_form)
            cnc_form.show()

        if idx == 5 and self.engrave_displayed is False:
            self.engrave_displayed = True
            plugins_engraving_form = self.ui.plugin_eng_pref_form
            try:
                self.ui.plugins_engraving_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.plugins_engraving_scroll_area.setWidget(plugins_engraving_form)
            plugins_engraving_form.show()

        if idx == 6 and self.plugins_displayed is False:
            self.plugins_displayed = True
            plugins_form = self.ui.plugin_pref_form
            try:
                self.ui.tools_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.tools_scroll_area.setWidget(plugins_form)
            plugins_form.show()

        if idx == 7 and self.plugins2_displayed is False:
            self.plugins2_displayed = True
            plugins2_form = self.ui.plugin2_pref_form
            try:
                self.ui.tools2_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.tools2_scroll_area.setWidget(plugins2_form)
            plugins2_form.show()

        if idx == 8 and self.util_displayed is False:
            self.util_displayed = True
            fa_form = self.ui.util_pref_form
            try:
                self.ui.fa_scroll_area.takeWidget()
            except Exception:
                self.ui.app.log.debug("Nothing to remove")
            self.ui.fa_scroll_area.setWidget(fa_form)
            fa_form.show()

    def __init_color_pickers(self):
        # Init Gerber Plot Colors
        self.ui.gerber_pref_form.gerber_gen_group.fill_color_entry.set_value(self.defaults['gerber_plot_fill'])
        self.ui.gerber_pref_form.gerber_gen_group.line_color_entry.set_value(self.defaults['gerber_plot_line'])

        self.ui.gerber_pref_form.gerber_gen_group.gerber_alpha_entry.set_value(
            int(self.defaults['gerber_plot_fill'][7:9], 16))    # alpha

        # Init Excellon Plot Colors
        self.ui.excellon_pref_form.excellon_gen_group.fill_color_entry.set_value(
            self.defaults['excellon_plot_fill'])
        self.ui.excellon_pref_form.excellon_gen_group.line_color_entry.set_value(
            self.defaults['excellon_plot_line'])

        self.ui.excellon_pref_form.excellon_gen_group.excellon_alpha_entry.set_value(
            int(self.defaults['excellon_plot_fill'][7:9], 16))

        # Init Geometry Plot Colors
        self.ui.geo_pref_form.geometry_gen_group.line_color_entry.set_value(
            self.defaults['geometry_plot_line'])

        # Init CNCJob Travel Line Colors
        self.ui.cncjob_pref_form.cncjob_gen_group.tfill_color_entry.set_value(
            self.defaults['cncjob_travel_fill'])
        self.ui.cncjob_pref_form.cncjob_gen_group.tline_color_entry.set_value(
            self.defaults['cncjob_travel_line'])

        self.ui.cncjob_pref_form.cncjob_gen_group.cncjob_alpha_entry.set_value(
            int(self.defaults['cncjob_travel_fill'][7:9], 16))      # alpha

        # Init CNCJob Plot Colors
        self.ui.cncjob_pref_form.cncjob_gen_group.fill_color_entry.set_value(
            self.defaults['cncjob_plot_fill'])

        self.ui.cncjob_pref_form.cncjob_gen_group.line_color_entry.set_value(
            self.defaults['cncjob_plot_line'])

        # Init Left-Right Selection colors
        self.ui.general_pref_form.general_gui_group.sf_color_entry.set_value(self.defaults['global_sel_fill'])
        self.ui.general_pref_form.general_gui_group.sl_color_entry.set_value(self.defaults['global_sel_line'])

        self.ui.general_pref_form.general_gui_group.left_right_alpha_entry.set_value(
            int(self.defaults['global_sel_fill'][7:9], 16))

        # Init Right-Left Selection colors
        self.ui.general_pref_form.general_gui_group.alt_sf_color_entry.set_value(
            self.defaults['global_alt_sel_fill'])
        self.ui.general_pref_form.general_gui_group.alt_sl_color_entry.set_value(
            self.defaults['global_alt_sel_line'])

        self.ui.general_pref_form.general_gui_group.right_left_alpha_entry.set_value(
            int(self.defaults['global_sel_fill'][7:9], 16))

        # Init Draw color and Selection Draw Color
        self.ui.general_pref_form.general_gui_group.draw_color_entry.set_value(
            self.defaults['global_draw_color'])

        self.ui.general_pref_form.general_gui_group.sel_draw_color_entry.set_value(
            self.defaults['global_sel_draw_color'])

        # Init Project Items color - Light Theme
        self.ui.general_pref_form.general_gui_group.proj_color_light_entry.set_value(
            self.defaults['global_proj_item_color_light'])

        # Init Project Disabled Items color - Light Theme
        self.ui.general_pref_form.general_gui_group.proj_color_dis_light_entry.set_value(
            self.defaults['global_proj_item_dis_color_light'])

        # Init Project Items color - Dark Theme
        self.ui.general_pref_form.general_gui_group.proj_color_dark_entry.set_value(
            self.defaults['global_proj_item_color_dark'])

        # Init Project Disabled Items color - Dark Theme
        self.ui.general_pref_form.general_gui_group.proj_color_dis_dark_entry.set_value(
            self.defaults['global_proj_item_dis_color_dark'])

        # Init Mouse Cursor color
        self.ui.general_pref_form.general_app_set_group.mouse_cursor_entry.set_value(
            self.defaults['global_cursor_color'])

        # Init the Annotation CNC Job color
        self.ui.cncjob_pref_form.cncjob_adv_opt_group.annotation_fontcolor_entry.set_value(
            self.defaults['cncjob_annotation_fontcolor'])

        # Init the Tool Film color
        self.ui.plugin_pref_form.tools_film_group.film_color_entry.set_value(
            self.defaults['tools_film_color'])

        # Init the Tool QRCode colors
        self.ui.plugin2_pref_form.tools2_qrcode_group.fill_color_entry.set_value(
            self.defaults['tools_qrcode_fill_color'])

        self.ui.plugin2_pref_form.tools2_qrcode_group.back_color_entry.set_value(
            self.defaults['tools_qrcode_back_color'])

    def on_save_button(self, save_to_file=True):
        self.ui.app.log.debug("on_save_button() --> Applying preferences to file.")

        # Preferences saved, update flag
        self.preferences_changed_flag = False

        # Preferences save, update the color of the Preferences Tab text
        for idx in range(self.ui.plot_tab_area.count()):
            if self.ui.plot_tab_area.tabText(idx) == _("Preferences"):
                self.ui.plot_tab_area.tabBar.setTabTextColor(idx, self.old_color)

        # restore the default stylesheet by setting a blank one
        self.ui.pref_apply_button.setStyleSheet("")
        self.ui.pref_apply_button.setIcon(QtGui.QIcon(self.ui.app.resource_location + '/apply32.png'))

        self.inform.emit('%s' % _("Preferences applied."))  # noqa

        # make sure we update the self.current_defaults dict used to undo changes to self.defaults
        self.defaults.current_defaults.update(self.defaults)

        # deal with appearance change
        appearance_settings = QtCore.QSettings("Open Source", "FlatCAM")
        if appearance_settings.contains("appearance"):
            appearance = appearance_settings.value('appearance', type=str)
        else:
            appearance = None

        if appearance_settings.contains("dark_canvas"):
            dark_canvas = appearance_settings.value('dark_canvas', type=bool)
        else:
            dark_canvas = None

        should_restart = False
        appearance_new_val = self.ui.general_pref_form.general_gui_group.appearance_radio.get_value()
        dark_canvas_new_val = self.ui.general_pref_form.general_gui_group.dark_canvas_cb.get_value()

        ge = self.defaults["global_graphic_engine"]
        ge_val = self.ui.general_pref_form.general_app_group.ge_radio.get_value()

        if appearance_new_val != appearance or ge != ge_val or dark_canvas_new_val != dark_canvas:
            msgbox = FCMessageBox(parent=self.ui)
            title = _("Application will restart")
            txt = _("Are you sure you want to continue?")
            msgbox.setWindowTitle(title)  # taskbar still shows it
            msgbox.setWindowIcon(QtGui.QIcon(self.ui.app.resource_location + '/app128.png'))
            msgbox.setText('<b>%s</b>' % title)
            msgbox.setInformativeText(txt)
            msgbox.setIcon(QtWidgets.QMessageBox.Icon.Question)

            bt_yes = msgbox.addButton(_('Yes'), QtWidgets.QMessageBox.ButtonRole.YesRole)
            msgbox.addButton(_('Cancel'), QtWidgets.QMessageBox.ButtonRole.NoRole)

            msgbox.setDefaultButton(bt_yes)
            msgbox.exec()
            response = msgbox.clickedButton()

            if appearance_new_val != appearance:
                if response == bt_yes:
                    appearance_settings.setValue('appearance', appearance_new_val)
                    should_restart = True
                else:
                    self.ui.general_pref_form.general_gui_group.appearance_radio.set_value(appearance)

            if dark_canvas_new_val != dark_canvas:
                if response == bt_yes:
                    appearance_settings.setValue('dark_canvas', dark_canvas_new_val)
                    should_restart = True
                else:
                    self.ui.general_pref_form.general_gui_group.dark_canvas_cb.set_value(dark_canvas)

            # This will write the setting to the platform specific storage.
            del appearance_settings

            if ge != ge_val:
                if response == bt_yes:
                    self.defaults["global_graphic_engine"] = ge_val
                    should_restart = True
                else:
                    self.ui.general_pref_form.general_app_group.ge_radio.set_value(ge)

        # #############################################################################################################
        # ############################  Here is done the actual preferences updates  ##################################
        # #############################################################################################################
        # update the `defaults` dict from the Preferences UI form
        self.defaults_read_form()
        # Apply the `defaults` dict to project options
        self.ui.app.options.update(self.defaults)
        # #############################################################################################################

        if save_to_file or should_restart is True:
            self.save_defaults(silent=False)
            # load the defaults so they are updated into the app
            saved_filename_path = os.path.join(self.data_path, 'current_defaults_%s.FlatConfig' % self.defaults.version)
            self.defaults.load(filename=saved_filename_path, inform=self.inform)

        settgs = QSettings("Open Source", "FlatCAM")

        # save the notebook font size
        fsize = self.ui.general_pref_form.general_app_set_group.notebook_font_size_spinner.get_value()
        settgs.setValue('notebook_font_size', fsize)

        # save the axis font size
        g_fsize = self.ui.general_pref_form.general_app_set_group.axis_font_size_spinner.get_value()
        settgs.setValue('axis_font_size', g_fsize)

        # save the textbox font size
        tb_fsize = self.ui.general_pref_form.general_app_set_group.textbox_font_size_spinner.get_value()
        settgs.setValue('textbox_font_size', tb_fsize)

        # save the HUD font size
        hud_fsize = self.ui.general_pref_form.general_app_set_group.hud_font_size_spinner.get_value()
        settgs.setValue('hud_font_size', hud_fsize)

        # This will write the setting to the platform specific storage.
        del settgs

        if save_to_file:
            # close the tab and delete it
            for idx in range(self.ui.plot_tab_area.count()):
                if self.ui.plot_tab_area.tabText(idx) == _("Preferences"):
                    self.ui.plot_tab_area.tabBar.setTabTextColor(idx, self.old_color)
                    self.ui.plot_tab_area.closeTab(idx)
                    break

        if should_restart is True:
            self.ui.app.on_app_restart()

    def on_restore_defaults_preferences(self):
        """
        Loads the application's factory default settings into ``self.defaults``.

        :return: None
        """
        self.ui.app.log.debug("on_restore_defaults_preferences()")
        self.defaults.reset_to_factory_defaults()
        self.defaults_write_form()
        self.on_preferences_edited()
        self.ui.units_label.setText("[mm]")
        self.inform.emit('[success] %s' % _("Preferences default values are restored."))

    def save_defaults(self, silent=False, data_path=None, first_time=False):
        """
        Saves application default options
        ``self.defaults`` to current_defaults.FlatConfig file.
        Save the toolbars visibility status to the preferences file (current_defaults.FlatConfig) to be
        used at the next launch of the application.

        :param silent:      Whether to display a message in status bar or not; boolean
        :param data_path:   The path where to save the preferences file (current_defaults.FlatConfig)
                            When the application is portable it should be a mobile location.
        :param first_time:  Boolean. If True will execute some code when the app is run first time
        :return:            None
        """
        self.ui.app.log.debug("App.PreferencesUIManager.save_defaults()")

        if data_path is None:
            data_path = self.data_path

        self.defaults.propagate_defaults()

        if first_time is False:
            self.save_toolbar_view()

        # Save the options to disk
        filename = os.path.join(data_path, "current_defaults_%s.FlatConfig" % self.defaults.version)

        try:
            self.defaults.write(filename=filename)
        except Exception as e:
            self.ui.app.log.error("save_defaults() --> Failed to write defaults to file %s" % str(e))
            self.inform.emit('[ERROR_NOTCL] %s %s' % (_("Failed to write defaults to file."), str(filename)))
            return

        if not silent:
            self.inform.emit('[success] %s' % _("Preferences saved."))

        # update the autosave timer
        self.ui.app.save_project_auto_update()

    def save_toolbar_view(self):
        """
        Will save the toolbar view state to the defaults

        :return:            None
        """

        # Save the toolbar view
        tb_status = 0
        if self.ui.toolbarfile.isVisible():
            tb_status += 1

        if self.ui.toolbaredit.isVisible():
            tb_status += 2

        if self.ui.toolbarview.isVisible():
            tb_status += 4

        if self.ui.toolbarplugins.isVisible():
            tb_status += 8

        if self.ui.exc_edit_toolbar.isVisible():
            tb_status += 16

        if self.ui.geo_edit_toolbar.isVisible():
            tb_status += 32

        if self.ui.grb_edit_toolbar.isVisible():
            tb_status += 64

        if self.ui.status_toolbar.isVisible():
            tb_status += 128

        if self.ui.toolbarshell.isVisible():
            tb_status += 256

        self.defaults["global_toolbar_view"] = tb_status

    def on_preferences_edited(self):
        """
        Executed when a preference was changed in the Edit -> Preferences tab.
        Will color the Preferences tab text to Red color.
        :return:
        """
        if isinstance(self.sender(), QtWidgets.QScrollBar):
            return

        if self.preferences_changed_flag is False:
            self.inform.emit('[WARNING_NOTCL] %s' % _("Preferences edited but not saved."))

            for idx in range(self.ui.plot_tab_area.count()):
                if self.ui.plot_tab_area.tabText(idx) == _("Preferences"):
                    self.old_color = self.ui.plot_tab_area.tabBar.tabTextColor(idx)
                    self.ui.plot_tab_area.tabBar.setTabTextColor(idx, QtGui.QColor('red'))

            self.ui.pref_apply_button.color = 'red'
            self.ui.pref_apply_button.setIcon(QtGui.QIcon(self.ui.app.resource_location + '/apply_red32.png'))

            self.preferences_changed_flag = True

    def on_close_preferences_tab(self, parent):
        self.ui.app.log.debug("Preferences GUI was closed.")
        if self.ignore_tab_close_event:
            return

        # restore stylesheet to default for the statusBar icon
        self.ui.pref_status_label.setStyleSheet("")

        self.clear_preferences_gui()

        # disconnect
        for idx in range(self.ui.pref_tab_area.count()):
            for tb in self.ui.pref_tab_area.widget(idx).findChildren(QtCore.QObject):
                try:
                    tb.textEdited.disconnect(self.on_preferences_edited)
                except (TypeError, AttributeError):
                    pass

                try:
                    tb.modificationChanged.disconnect(self.on_preferences_edited)
                except (TypeError, AttributeError):
                    pass

                try:
                    tb.toggled.disconnect(self.on_preferences_edited)
                except (TypeError, AttributeError):
                    pass

                try:
                    tb.valueChanged.disconnect(self.on_preferences_edited)
                except (TypeError, AttributeError):
                    pass

                try:
                    tb.currentIndexChanged.disconnect(self.on_preferences_edited)
                except (TypeError, AttributeError):
                    pass

        # Prompt user to save
        if self.preferences_changed_flag is True:
            msgbox = FCMessageBox(parent=self.ui)
            title = _("Save Preferences")
            txt = _("One or more values are changed.\n"
                    "Do you want to save?")
            msgbox.setWindowTitle(title)  # taskbar still shows it
            msgbox.setWindowIcon(QtGui.QIcon(self.ui.app.resource_location + '/app128.png'))
            msgbox.setText('<b>%s</b>' % title)
            msgbox.setInformativeText(txt)
            msgbox.setIconPixmap(QtGui.QPixmap(self.ui.app.resource_location + '/save_as.png'))

            bt_yes = msgbox.addButton(_('Yes'), QtWidgets.QMessageBox.ButtonRole.YesRole)
            msgbox.addButton(_('No'), QtWidgets.QMessageBox.ButtonRole.NoRole)

            msgbox.setDefaultButton(bt_yes)
            msgbox.exec()
            response = msgbox.clickedButton()

            if response == bt_yes:
                self.on_save_button(save_to_file=True)
                self.inform.emit('[success] %s' % _("Preferences saved."))
            else:
                self.preferences_changed_flag = False
                self.inform.emit('')
                return

    def on_pref_close_button(self):
        # Preferences saved, update flag
        self.preferences_changed_flag = False
        self.ignore_tab_close_event = True

        # restore stylesheet to default for the statusBar icon
        self.ui.pref_status_label.setStyleSheet("")

        self.defaults_write_form(source_dict=self.defaults.current_defaults)

        self.defaults.update(self.defaults.current_defaults)

        # Preferences save, update the color of the Preferences Tab text
        for idx in range(self.ui.plot_tab_area.count()):
            if self.ui.plot_tab_area.tabText(idx) == _("Preferences"):
                self.ui.plot_tab_area.tabBar.setTabTextColor(idx, self.old_color)
                self.ui.plot_tab_area.closeTab(idx)
                break

        self.inform.emit('%s' % _("Preferences closed without saving."))
        self.ignore_tab_close_event = False
