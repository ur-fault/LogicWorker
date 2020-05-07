import sys
import clr
sys.path.append("C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\WPF")
clr.AddReference("System.Windows.Forms")
clr.AddReference('DarkUI')
clr.AddReference("PresentationCore")

from DarkUI.Controls import *
import DarkUI.Forms as DarkForms
import System.Windows.Forms as WinForms
from System.Windows.Forms import ProgressBar
from System.Windows.Media import Brushes
from System.Security import SecurityException
from System import Decimal
from System.Threading import Thread, ThreadStart, ApartmentState, ParameterizedThreadStart
from System.Drawing import (
    Size,
    Point,
    Color,
    Font,
    FontStyle,
    FontFamily,
    ContentAlignment
)

import LogicGenerator as lg
import RandomTruthTableGenerator as rttg
import TableGeneratorFromLogic as tgfl
import parsers

from os import path as path
import threading


# from watermark_textbox import WaterMarkDarkTextBox
home_dir = path.expanduser('~/Documents')


def set_all_components(form, comps):
    for comp in comps:
        form.Controls.Add(comp)
        

def start_the_thread(obj, *args):
    t = Thread(lambda: obj.run_command(*args))
    t.Start()
    return t


class main_form(DarkForms.DarkForm):
    def __init__(self):
        self.InitComponents()

    def InitComponents(self):
        # Main form's main settings
        self.width = 480
        self.height = 241

        self.Text = 'LogicWorker'
        self.Name = 'main_form'
        h = WinForms.SystemInformation.CaptionHeight
        self.ClientSize = Size(self.width, self.height)
        self.MinimumSize = Size(self.width, self.height + h)
        self.MaximumSize = Size(self.width, self.height + h)
        self.FormBorderStyle = WinForms.FormBorderStyle.FixedSingle
        self.MaximizeBox = False

        # Some properities
        self.font_family = FontFamily('Consolas')
        self.font = Font(self.font_family, 25.0 - 12.0, FontStyle.Bold)
        self.button_font = Font(
            self.font_family, 25.0 - 15.0, FontStyle.Regular)

        # Define components
        self.lg_button = DarkButton()
        self.rttg_button = DarkButton()
        self.tgfl_button = DarkButton()

        self.lg_label = DarkLabel()
        self.rttg_label = DarkLabel()
        self.tgfl_label = DarkLabel()

        # Define components's settings
        #       Buttons
        self.lg_button.Size = Size(160, 25)
        self.lg_button.Location = Point(20, 30 - 12)
        self.lg_button.Text = 'Run LG program'
        self.lg_button.Font = self.button_font
        self.lg_button.Click += self.run_lg

        self.rttg_button.Size = Size(160, 25)
        self.rttg_button.Location = Point(20, 100 - 12)
        self.rttg_button.Text = 'Run RTTG program'
        self.rttg_button.Font = self.button_font
        self.rttg_button.Click += self.run_rttg

        self.tgfl_button.Size = Size(160, 25)
        self.tgfl_button.Location = Point(20, 170 - 12)
        self.tgfl_button.Text = 'Run TGFL program'
        self.tgfl_button.Font = self.button_font
        self.tgfl_button.Click += self.run_tgfl

        #       Labels
        self.lg_label.Size = Size(300, 50)
        self.lg_label.Location = Point(190, 30 - 12)
        self.lg_label.Text = 'Calculate logic based on truth table'
        self.lg_label.Font = self.font

        self.rttg_label.Size = Size(300, 50)
        self.rttg_label.Location = Point(190, 100 - 12)
        self.rttg_label.Text = 'Generate random truth table with n inputs and m outputs'
        self.rttg_label.Font = self.font

        self.tgfl_label.Size = Size(280, 75)
        self.tgfl_label.Location = Point(190, 170 - 12)
        self.tgfl_label.Text = 'Find all input/output combinations of logic and save it as truth table'
        self.tgfl_label.Font = self.font

        # Add all components to controls
        set_all_components(self, [
            self.lg_button,
            self.rttg_button,
            self.tgfl_button,
            
            self.lg_label,
            self.rttg_label,
            self.tgfl_label
        ])

    def run(self):
        # WinForms.Application.EnableVisualStyles()
        WinForms.Application.Run(self)

    # Functions for running app
    def run_lg(self, sender, args):
        print('Pressed lg')
        position = self.Location
        self.Hide()
        lg_form = LG_form(self)
        lg_form.FormClosed += lambda sender, args: self.Close()
        lg_form.Show()
        lg_form.SetDesktopLocation(position.X, position.Y)

    def run_rttg(self, sender, args):
        print('Pressed rttg')
        print('Pressed lg')
        position = self.Location
        self.Hide()
        rttg_form = RTTG_form(self)
        rttg_form.FormClosed += lambda sender, args: self.Close()
        rttg_form.Show()
        rttg_form.SetDesktopLocation(position.X, position.Y)

    def run_tgfl(self, sender, args):
        print('Pressed tgfl')


class LG_form(DarkForms.DarkForm):
    # region init
    def __init__(self, parent_form):
        self.main_form = parent_form
        self.open_path = ''
        self.save_path = ''
        self.enable_tabs = False
        self.tabs_count = 4
        
        self.open_file_dialog = WinForms.OpenFileDialog()
        self.save_file_dialog = WinForms.SaveFileDialog()
        
        self.saving = False
        self.running = False
        self.t = None

        self.InitDialogs()
        self.InitComponents()
        
    def InitDialogs(self):
        # Create dialogs
        self.open_file_dialog = WinForms.OpenFileDialog()
        self.save_file_dialog = WinForms.SaveFileDialog()
        
        # Set properities for dialogs
        self.open_file_dialog.AddExtension = True
        self.open_file_dialog.InitialDirectory = home_dir
        self.open_file_dialog.DefaultExt = 'ttbl'
        self.open_file_dialog.Filter = 'Truth table files (*.ttbl)|*.ttbl'
        self.open_file_dialog.CheckFileExists = True
        self.open_file_dialog.CheckPathExists = True
        self.open_file_dialog.RestoreDirectory = True
        
        self.save_file_dialog.InitialDirectory = home_dir
        self.save_file_dialog.DefaultExt = 'logic'
        self.save_file_dialog.Filter = 'Logic circuit files (*.logic)|*.logic|Json logic files (*.json)|*.json'
        self.save_file_dialog.RestoreDirectory = True
        self.save_file_dialog.CheckPathExists = True

    def InitComponents(self):
        # LG form's main settings
        self.width = 480
        self.height = 240

        self.Text = 'LogicWorker - Logic Generator'
        self.Name = 'LG_form'
        h = WinForms.SystemInformation.CaptionHeight
        self.ClientSize = Size(self.width, self.height)
        self.MinimumSize = Size(self.width, self.height + h)
        self.MaximumSize = Size(self.width, self.height + h)
        self.FormBorderStyle = WinForms.FormBorderStyle.FixedSingle
        self.MaximizeBox = False

        # Some properities
        self.font_family = FontFamily('Consolas')
        self.font = Font(
            self.font_family, 25.0 - 15.0, FontStyle.Regular)
        self.button_font = Font(
            self.font_family, 25.0 - 15.0, FontStyle.Regular)
        self.entry_font = Font(
            self.font_family, 25.0 - 14.0, FontStyle.Bold)
        self.run_button_font = Font(
            self.font_family, 25.0 - 13.0, FontStyle.Bold)
        
        # Define components
        self.json_indent_numupdown = DarkNumericUpDown()
        
        self.force_creation_checkbox = DarkCheckBox()
        
        self.force_creation_label = DarkLabel()
        self.json_indent_label = DarkLabel()
        self.horizontal_divider_indent_force_label = DarkLabel()
        self.task_label = DarkLabel()
        
        self.open_path_entry = DarkTextBox()
        self.save_path_entry = DarkTextBox()
        
        self.open_path_button = DarkButton()
        self.save_path_button = DarkButton()
        self.back_button = DarkButton()
        self.run_button = DarkButton()

        # Define components's settings
        #       NumericUpDown
        self.json_indent_numupdown.Size = Size(100, 12)
        self.json_indent_numupdown.Location = Point(15, 92 - 15)
        self.json_indent_numupdown.Font = self.entry_font
        self.json_indent_numupdown.Enabled = False
        self.json_indent_numupdown.Value = Decimal(4)
        self.json_indent_numupdown.Minimum = Decimal(0)
        self.json_indent_numupdown.ValueChanged += self.tab_numeric_value_changed
        
        #       Checkboxes
        self.force_creation_checkbox.Size = Size(20, 20)
        self.force_creation_checkbox.Location = Point(100, 124 - 15 + 15)
        # self.force_creation_checkbox.BorderStyle = WinForms.FormBorderStyle.FixedSingle
        # self.force_creation_checkbox.Font = self.font
        # self.force_creation_checkbox.Text = 'Force file creation, even if in table file wasn\'t any true outputs logic will be created'
        
        #       Labels
        self.force_creation_label.Size = Size(300, 50)
        self.force_creation_label.Location = Point(125, 124 - 15 + 3)
        self.force_creation_label.Font = self.font
        self.force_creation_label.Text = 'Force file creation, even if in table file wasn\'t any true outputs logic will be created.'
        
        self.json_indent_label.Size = Size(300, 50)
        self.json_indent_label.Location = Point(125, 92 - 15 - 3)
        self.json_indent_label.Font = self.font
        self.json_indent_label.Text = 'Indent used with json file format (zero for \'ugly\' json).'
        
        self.horizontal_divider_indent_force_label.Size = Size(480, 2)
        self.horizontal_divider_indent_force_label.Location = Point(0, 124 - 15)
        self.horizontal_divider_indent_force_label.BorderStyle = WinForms.FormBorderStyle.FixedSingle
        
        self.task_label.Size = Size(170 + 15, 25)
        self.task_label.Location = Point(155 - 15, 195)
        self.task_label.Font = self.font
        self.task_label.TextAlign = ContentAlignment.MiddleCenter
        self.task_label.Text = ''
        self.task_label.BorderStyle = WinForms.FormBorderStyle.FixedSingle
        
        #       TextBoxes
        self.open_path_entry.Size = Size(300, 12)
        self.open_path_entry.Location = Point(15, 20 - 15)
        self.open_path_entry.Font = self.entry_font
        self.open_path_entry.ReadOnly = True
        self.open_path_entry.Text = 'Choose input file'
        
        self.save_path_entry.Size = Size(300, 12)
        self.save_path_entry.Location = Point(15, 56 - 15)
        self.save_path_entry.Font = self.entry_font
        self.save_path_entry.ReadOnly = True
        self.save_path_entry.Text = 'Choose output file'
        
        
        #       Buttons
        self.open_path_button.Size = Size(125, 25)
        self.open_path_button.Location = Point(325, 20 - 15)
        self.open_path_button.Font = self.button_font
        self.open_path_button.Text = 'Choose file'
        self.open_path_button.Click += self.open_path_button_click
        
        self.save_path_button.Size = Size(125, 25)
        self.save_path_button.Location = Point(325, 56 - 15)
        self.save_path_button.Font = self.button_font
        self.save_path_button.Text = 'Choose file'
        self.save_path_button.Click += self.save_path_button_click
        
        self.back_button.Size = Size(125, 25)
        self.back_button.Location = Point(15, 195)
        self.back_button.Font = self.button_font
        self.back_button.Text = 'Back'
        self.back_button.Click += self.back_button_click
        
        self.run_button.Size = Size(125, 25)
        self.run_button.Location = Point(340 - 15, 195)
        self.run_button.Font = self.run_button_font
        self.run_button.Text = 'Start'
        self.run_button.Click += self.run_button_click

        # Add all components to controls
        #       Draw on top
        set_all_components(self, [
            self.horizontal_divider_indent_force_label
        ])
        
        #       Draw below
        set_all_components(self, [
            self.json_indent_numupdown,
            
            self.force_creation_checkbox,
            
            self.force_creation_label,
            self.json_indent_label,
            self.task_label,
            
            self.open_path_entry,
            self.save_path_entry,
            
            self.open_path_button,
            self.save_path_button,
            self.back_button,
            self.run_button
        ])
    # endregion
    
    def run_command(self, progress):
        self.running = True
        print('Running command')
        
        lg.print_output = True
        lg.tab_count = self.tabs_count
        
        try:
            progress.Value = 1
            self.task_label.Text = 'Generating table'
            table = lg.Table(self.open_path)
            if len(table.trues) <= 0:
                self.task_label.Text = 'Zero trues in output'
                return
            
            progress.Value += 1
            self.task_label.Text = 'Generating conditions'
            conditions = lg.make_condition_nodes(table)
            
            progress.Value += 1
            self.task_label.Text = 'Assigning nodes'
            res = lg.assign_nodes_to_outputs(conditions, table, self.open_path)
            table = None
            conditions = None
            if len(res) > 0:
                end_nodes = res
            else:
                end_nodes = None
            res = None
            
            progress.Value += 1
            self.task_label.Text = 'Saving'
            if self.enable_tabs:
                parsers.save_json(self.save_path, end_nodes, self.tabs_count)
            else:
                parsers.save_logic(self.save_path, end_nodes)
            
            progress.Value += 1
            self.task_label.Text = 'Saved'
            progress.Hide()
        except MemoryError as me:
            progress.Value = 0
            progress.Hide()
            self.task_label.Text = 'MemoryError'
        
        self.back_button.Enabled = True
        self.run_button.Enabled = True
        
        self.running = False
        
    # Components's events
    # region events
    def run_button_click(self, sender, args):
        if len(self.open_path) > 0 and len(self.save_path):
            self.open_path_entry.BackColor = Color.FromArgb(69, 73, 74)
            self.save_path_entry.BackColor = Color.FromArgb(69, 73, 74)
            
            self.progress = ProgressBar()
            self.progress.Size = Size(435, 25)
            self.progress.Location = Point(15, 192 - 25 - 5)
            self.progress.Maximum = 5
            self.progress.BackColor = Color.FromArgb(69, 73, 74)
            self.Controls.Add(self.progress)
            
            self.back_button.Enabled = False
            self.run_button.Enabled = False
            
            self.t = threading.Thread(target=self.run_command, args=(self.progress,))
            self.t.start()
        elif len(self.open_path) <= 0 and len(self.save_path) <= 0:
            self.open_path_entry.BackColor = Color.Red
            self.save_path_entry.BackColor = Color.Red
        elif len(self.open_path) <= 0:
            self.open_path_entry.BackColor = Color.Red
            self.save_path_entry.BackColor = Color.FromArgb(69, 73, 74)
        elif len(self.save_path) <= 0:
            self.save_path_entry.BackColor = Color.Red
            self.open_path_entry.BackColor = Color.FromArgb(69, 73, 74)
            
    
    def open_path_button_click(self, sender, args):
        if self.open_file_dialog.ShowDialog() == WinForms.DialogResult.OK:
            try:
                self.open_path = self.open_file_dialog.FileName
                self.open_path_entry.Text = self.open_path
            except SecurityException as se:
                WinForms.MessageBox.Show(f'Security error.\n\nError message: {se.Message}\n\nDetails:\n\n{se.StackTrace}')
                
    
    def save_path_button_click(self, sender, args):
        if self.save_file_dialog.ShowDialog() == WinForms.DialogResult.OK:
            try:
                self.save_path = self.save_file_dialog.FileName
                self.enable_tabs = False if path.splitext(self.save_path)[1] == '.logic' else True
                self.json_indent_numupdown.Enabled = self.enable_tabs
                self.save_path_entry.Text = self.save_path
            except SecurityException as se:
                WinForms.MessageBox.Show(f'Security error.\n\nError message: {se.Message}\n\nDetails:\n\n{se.StackTrace}')
             
                
    def back_button_click(self, sender, args):
        if self.running:
            self.t.terminate()
            self.progress.Hide()
            self.progress = None
            self.running = False
            self.t = None
            
        print('Pressed back')
        position = self.Location
        self.Hide()
        mform = main_form()
        mform.FormClosed += lambda sender, args: self.Close()
        mform.Show()
        mform.SetDesktopLocation(position.X, position.Y)
                
    
    def tab_numeric_value_changed(self, sender, args):
        self.tabs_count = self.json_indent_numupdown.Value
        print('Indent value changed to ' + str(self.tabs_count))
    # endregion
    
    


class RTTG_form(DarkForms.DarkForm):
    # region init
    def __init__(self, parent_form):
        self.main_form = parent_form
        self.open_path = ''
        self.save_path = ''
        self.enable_tabs = False
        self.tabs_count = 4
        
        self.open_file_dialog = WinForms.OpenFileDialog()
        self.save_file_dialog = WinForms.SaveFileDialog()
        
        self.saving = False
        self.running = False
        self.t = None

        self.InitDialogs()
        self.InitComponents()
        
    def InitDialogs(self):
        # Create dialogs
        self.open_file_dialog = WinForms.OpenFileDialog()
        self.save_file_dialog = WinForms.SaveFileDialog()
        
        # Set properities for dialogs
        self.open_file_dialog.AddExtension = True
        self.open_file_dialog.InitialDirectory = home_dir
        self.open_file_dialog.DefaultExt = 'ttbl'
        self.open_file_dialog.Filter = 'Truth table files (*.ttbl)|*.ttbl'
        self.open_file_dialog.CheckFileExists = True
        self.open_file_dialog.CheckPathExists = True
        self.open_file_dialog.RestoreDirectory = True
        
        self.save_file_dialog.InitialDirectory = home_dir
        self.save_file_dialog.DefaultExt = 'logic'
        self.save_file_dialog.Filter = 'Logic circuit files (*.logic)|*.logic|Json logic files (*.json)|*.json'
        self.save_file_dialog.RestoreDirectory = True
        self.save_file_dialog.CheckPathExists = True

    def InitComponents(self):
        # LG form's main settings
        self.width = 480
        self.height = 240

        self.Text = 'LogicWorker - Random Truth Table Generator'
        self.Name = 'RTTG_form'
        h = WinForms.SystemInformation.CaptionHeight
        self.ClientSize = Size(self.width, self.height)
        self.MinimumSize = Size(self.width, self.height + h)
        self.MaximumSize = Size(self.width, self.height + h)
        self.FormBorderStyle = WinForms.FormBorderStyle.FixedSingle
        self.MaximizeBox = False

        # Some properities
        self.font_family = FontFamily('Consolas')
        self.font = Font(
            self.font_family, 25.0 - 15.0, FontStyle.Regular)
        self.button_font = Font(
            self.font_family, 25.0 - 15.0, FontStyle.Regular)
        self.entry_font = Font(
            self.font_family, 25.0 - 14.0, FontStyle.Bold)
        self.run_button_font = Font(
            self.font_family, 25.0 - 13.0, FontStyle.Bold)
        
        # Define components
        self.input_count_numupdown = DarkNumericUpDown()
        self.output_count_numupdown = DarkNumericUpDown()
        
        self.task_label = DarkLabel()
        
        self.save_path_entry = DarkTextBox()
        
        self.save_path_button = DarkButton()
        self.back_button = DarkButton()
        self.run_button = DarkButton()

        # Define components's settings
        #       NumericUpDown
        self.input_count_numupdown.Size = Size(100, 12)
        self.input_count_numupdown.Location = Point(15, 56 - 15)
        self.input_count_numupdown.Font = self.entry_font
        self.input_count_numupdown.Enabled = False
        self.input_count_numupdown.Value = Decimal(4)
        self.input_count_numupdown.Minimum = Decimal(1)
        self.input_count_numupdown.ValueChanged += self.tab_numeric_value_changed
        
        self.output_count_numupdown.Size = Size(100, 12)
        self.output_count_numupdown.Location = Point(240, 56 - 15)
        self.output_count_numupdown.Font = self.entry_font
        self.output_count_numupdown.Enabled = False
        self.output_count_numupdown.Value = Decimal(1)
        self.output_count_numupdown.Minimum = Decimal(1)
        self.output_count_numupdown.ValueChanged += self.tab_numeric_value_changed
        
        #       Checkboxes
        
        #       Labels
        self.task_label.Size = Size(170 + 15, 25)
        self.task_label.Location = Point(155 - 15, 195)
        self.task_label.Font = self.font
        self.task_label.TextAlign = ContentAlignment.MiddleCenter
        self.task_label.Text = ''
        self.task_label.BorderStyle = WinForms.FormBorderStyle.FixedSingle
        
        #       TextBoxes
        self.save_path_entry.Size = Size(300, 12)
        self.save_path_entry.Location = Point(15, 20 - 15)
        self.save_path_entry.Font = self.entry_font
        self.save_path_entry.ReadOnly = True
        self.save_path_entry.Text = 'Choose output file'
        
        
        #       Buttons
        self.save_path_button.Size = Size(125, 25)
        self.save_path_button.Location = Point(325, 20 - 15)
        self.save_path_button.Font = self.button_font
        self.save_path_button.Text = 'Choose file'
        self.save_path_button.Click += self.save_path_button_click
        
        self.back_button.Size = Size(125, 25)
        self.back_button.Location = Point(15, 195)
        self.back_button.Font = self.button_font
        self.back_button.Text = 'Back'
        self.back_button.Click += self.back_button_click
        
        self.run_button.Size = Size(125, 25)
        self.run_button.Location = Point(340 - 15, 195)
        self.run_button.Font = self.run_button_font
        self.run_button.Text = 'Start'
        self.run_button.Click += self.run_button_click

        # Add all components to controls
        #       Draw on top
        set_all_components(self, [
        ])
        
        #       Draw below
        set_all_components(self, [
            self.input_count_numupdown,
            self.output_count_numupdown,
            
            self.task_label,
            
            self.save_path_entry,
            
            self.save_path_button,
            self.back_button,
            self.run_button
        ])
    # endregion
    
    def run_command(self, progress):
        self.running = True
        print('Running command')
        
        lg.print_output = True
        lg.tab_count = self.tabs_count
        
        try:
            progress.Value = 1
        except MemoryError as me:
            progress.Value = 0
            progress.Hide()
            self.task_label.Text = 'MemoryError'
        
        self.back_button.Enabled = True
        self.run_button.Enabled = True
        
        self.running = False
        
    # Components's events
    # region events
    def run_button_click(self, sender, args):
        if len(self.open_path) > 0 and len(self.save_path):
            self.open_path_entry.BackColor = Color.FromArgb(69, 73, 74)
            self.save_path_entry.BackColor = Color.FromArgb(69, 73, 74)
            
            self.progress = ProgressBar()
            self.progress.Size = Size(435, 25)
            self.progress.Location = Point(15, 192 - 25 - 5)
            self.progress.Maximum = 5
            self.progress.BackColor = Color.FromArgb(69, 73, 74)
            self.Controls.Add(self.progress)
            
            self.back_button.Enabled = False
            self.run_button.Enabled = False
            
            self.t = threading.Thread(target=self.run_command, args=(self.progress,))
            self.t.start()
        elif len(self.open_path) <= 0 and len(self.save_path) <= 0:
            self.open_path_entry.BackColor = Color.Red
            self.save_path_entry.BackColor = Color.Red
        elif len(self.open_path) <= 0:
            self.open_path_entry.BackColor = Color.Red
            self.save_path_entry.BackColor = Color.FromArgb(69, 73, 74)
        elif len(self.save_path) <= 0:
            self.save_path_entry.BackColor = Color.Red
            self.open_path_entry.BackColor = Color.FromArgb(69, 73, 74)
                
    
    def save_path_button_click(self, sender, args):
        if self.save_file_dialog.ShowDialog() == WinForms.DialogResult.OK:
            try:
                self.save_path = self.save_file_dialog.FileName
                self.enable_tabs = False if path.splitext(self.save_path)[1] == '.logic' else True
                self.json_indent_numupdown.Enabled = self.enable_tabs
                self.save_path_entry.Text = self.save_path
            except SecurityException as se:
                WinForms.MessageBox.Show(f'Security error.\n\nError message: {se.Message}\n\nDetails:\n\n{se.StackTrace}')
             
                
    def back_button_click(self, sender, args):
        if self.running:
            self.t.terminate()
            self.progress.Hide()
            self.progress = None
            self.running = False
            self.t = None
            
        print('Pressed back')
        position = self.Location
        self.Hide()
        mform = main_form()
        mform.FormClosed += lambda sender, args: self.Close()
        mform.Show()
        mform.SetDesktopLocation(position.X, position.Y)
                
    
    def tab_numeric_value_changed(self, sender, args):
        self.tabs_count = self.json_indent_numupdown.Value
        print('Indent value changed to ' + str(self.tabs_count))
    # endregion


def main_form_thread():
    mform = main_form()
    mform.run()
    

def main():
    print('start thread')
    thread = Thread(ThreadStart(main_form_thread))
    print('set thread apartment STA')
    thread.SetApartmentState(ApartmentState.STA)
    thread.Start()
    thread.Join()


if __name__ == '__main__':
    main()
