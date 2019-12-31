#!/usr/bin/env python3

import npyscreen # For creating the interface
from pathlib import Path # For accessing files
import datetime # For timestamping log entries
from modt_status import read_status # For reading the current status from the MOD-t
from load_filament import load_filament # For loading the filament
from unload_filament import unload_filament # For unloading the filament
from send_gcode import send_gcode # For sending the g-code

logpath = Path('/tmp/Mod-t')
last_time = datetime.datetime.utcnow() # Defines last_time


# Read the current status from the MOD-t
def update_status():
    global status
    global temp_prefix
    global last_time
    status = read_status()
    current_time = datetime.datetime.utcnow() # Store the current UTC time
    if current_time - last_time >= datetime.timedelta(seconds = 2): # This checks if at least two seconds have passed since last_time
        with logpath.open('a') as logfile:
            logfile.write('\n\n' + current_time.strftime('%Y-%m-%dT%H:%M:%S+00:00') + '\n' + str(status)) # This monstrosity simply adds a blank line, the current UTC date and time in ISO 8601 format, and the Mod-t's status to the log file; the format is hard coded to prevent it being broken in the future
            last_time = current_time # Reset last_time
    # 105.78° appears to be the mininum temperature the Mod-t's thermistor can read
    temp_prefix=''
    if status.get('status').get('extruder_temperature') == 105.78:
        temp_prefix='≤'

update_status()

# Define tui objects
# Define the NPSAppManaged object; this helps when switching between forms
class application(npyscreen.NPSAppManaged):
    keypress_timeout_default = 5
    def while_waiting(self):
        update_status()
        state_display.value = 'Current State: ' + status.get('status').get('state') + ' | Extruder Temperature: ' + temp_prefix + str(status.get('status').get('extruder_temperature')) + '°C'
        state_display.display()    
    def adjust_widgets(self):
        update_status()
        state_display.value = 'Current State: ' + status.get('status').get('state') + ' | Extruder Temperature: ' + temp_prefix + str(status.get('status').get('extruder_temperature')) + '°C'
        state_display.display()
    def onStart(self):
        self.addForm('MAIN', main_form, name = 'MOD-t Control') # Assigned to reference state display
        self.addForm('load', load_form, name = 'Load Filament')
        self.addForm('unload', unload_form, name = 'Unload Filament')
        self.addForm('send', send_form, name = 'Send G-Code')
        self.addForm('flash', flash_form, name = 'Flash Firmware')

# Define the MAIN form class
class main_form(npyscreen.FormBaseNew):
    # Allow resizing the tui to be smaller than when it was created
    FIX_MINIMUM_SIZE_WHEN_CREATED = False
    # Runs when the main form is created    
    def create(self):
       # Add a lot of buttons
       self.add(npyscreen.ButtonPress, relx = 4, rely = 4, when_pressed_function = quit_button, name = '[Quit]')
       self.add(npyscreen.ButtonPress, relx = 4, rely = 6, when_pressed_function = load_button, name = '[Load Filament]')
       self.add(npyscreen.ButtonPress, relx = 4, rely = 8, when_pressed_function = unload_button, name = '[Unload Filament]')
       self.add(npyscreen.ButtonPress, relx = 4, rely = 10, when_pressed_function = send_button, name = '[Send G-Code]')
       self.add(npyscreen.ButtonPress, relx = 4, rely = 12, when_pressed_function = flash_button, name = '[Flash Firmware]')
       self.add(npyscreen.ButtonPress, relx = 4, rely = 14, when_pressed_function = view_button, name = '[View Log]')
       global state_display
       state_display = self.add(npyscreen.FixedText, relx = 3, rely = -3, value = 'Current State: ' + status.get('status').get('state') + ' | Extruder Temperature: ' + temp_prefix + str(status.get('status').get('extruder_temperature')) + '°C')

#Functions to perform when a button is pressed
def quit_button():
    exit(0)
def load_button():
    app.switchForm('load')
def unload_button():
    app.switchForm('unload')
def send_button():
    app.switchForm('send')
def flash_button():
    app.switchForm('flash')
def view_button():
    pass




class load_form(npyscreen.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 60
    SHOW_ATX = 10
    SHOW_ATY = 2
    def create(self):
        self.add(npyscreen.FixedText, relx = 2, rely = 2, value = 'Please confirm to initiate filament loading.')
        self.add(npyscreen.ButtonPress, relx = 4, rely = -3, when_pressed_function = load_cancel, name = 'Cancel')
        self.add(npyscreen.ButtonPress, relx = -15, rely = -3, when_pressed_function = load_confirm, name = 'Confirm')

def load_cancel():
    app.switchFormPrevious()
def load_confirm():
    load_filament()
    app.switchFormPrevious()




class unload_form(npyscreen.FormBaseNew):
    DEFAULT_LINES = 12
    DEFAULT_COLUMNS = 60
    SHOW_ATX = 10
    SHOW_ATY = 2
    def create(self):
        self.add(npyscreen.FixedText, relx = 2, rely = 2, value = 'Please confirm to initiate filament unloading.')
        self.add(npyscreen.ButtonPress, relx = 4, rely = -3, when_pressed_function = unload_cancel, name = 'Cancel')
        self.add(npyscreen.ButtonPress, relx = -15, rely = -3, when_pressed_function = unload_confirm, name = 'Confirm')

def unload_cancel():
    app.switchFormPrevious()
def unload_confirm():
    unload_filament()
    app.switchFormPrevious()




class send_form(npyscreen.FormBaseNew):
    def create(self):
        global gcode_path
        global optimize
        gcode_path = self.add(npyscreen.TitleFilename, relx = 2, rely = 2, name = 'Path to g-code:')
        optimize = self.add(npyscreen.Checkbox, relx = 2, rely = 6, name = 'Optimize')
        self.add(npyscreen.ButtonPress, relx = 4, rely = -3, when_pressed_function = send_cancel, name = 'Cancel')
        self.add(npyscreen.ButtonPress, relx = -15, rely = -3, when_pressed_function = send_confirm, name = 'Confirm')
        self.add(npyscreen.FixedText, relx = 17, rely = -3, value = '[' + status.get('status').get('state') + ']')

def send_cancel():
    app.switchFormPrevious()
def send_confirm():
    global gcode_path
    global optimize
    gcode_path = Path(gcode_path.value)    
    optimize_path = Path('/tmp/modt_optimized_gcode.gcode')    
    if optimize.value == True:
        optimize_gcode(str(gcode_path), str(optimize_path))
        gcode_path = optimize_path
    send_gcode(gcode_path)    
    if optimize_path.is_file:
        optimize_path.unlink(missing_ok = True)



class flash_form(npyscreen.FormBaseNew):
    def create(self):
        firmware_path = self.add(npyscreen.TitleFilename, relx = 2, rely = 2, name = 'Path to firmware:')
        self.add(npyscreen.ButtonPress, relx = 4, rely = -3, when_pressed_function = flash_cancel, name = 'Cancel')
        self.add(npyscreen.ButtonPress, relx = -15, rely = -3, when_pressed_function = flash_confirm, name = 'Confirm')
        self.add(npyscreen.FixedText, relx = 17, rely = -3, name = '[' + status.get('printer').get('firmware').get('version') + ']', color = 'DEFAULT')

def flash_cancel():
    app.switchFormPrevious()

def flash_confirm():
    import os
    os.system("espeak-ng 'Flash Firmware Test'")






# Run the tui
app = application()
app.run()
