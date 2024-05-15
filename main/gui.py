import pytz
import os
import sys
import threading
import keyboard
from asciimatics.event import KeyboardEvent
from asciimatics.widgets import Frame, Layout, Divider, Button, CheckBox, Text, TextBox, Widget, Label, ListBox
from asciimatics.effects import Print
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from asciimatics.renderers import BarChart, FigletText
from time import sleep
from datetime import datetime
from PIL import Image

import env
from env import log, get_config_option, set_config_option
from upload import refresh_hashfile
from display import show, kill, get_status

# initial variables
anims = refresh_hashfile(True)
progress = 0
default_tz = pytz.timezone('America/New_York')

runtime_vars = {
    "RGB": env.rgb,
    "AUDIO": env.audio,
    "SCRIPTS": env.scripts,
    "LOOP": env.loop,
    "VOLUME": env.vol,
    "debug": env.debug
}

runtime_anims = [("(none)", "")]

# cool loading bar that i may or may not implement
class LoadingBar(Print):
    def __init__(self, screen):
        global progress
#        loading = [
#        self.add_widget(Print(screen, FigletText("ProotOS v{}".format(env.version), font='trek'), screen.height//2+2, screen.width//20, colour=env.theme_color, bg=0))
#        ]

        super().__init__(screen, BarChart(1, screen.width - 20, [lambda:progress], char="/", scale=100, labels=False, axes=0, border=False, colour=env.theme_color), x=10, y=(screen.height - 3), speed=1, transparent=False)

    def _update(self, frame_no):
        global progress
        if progress >= 100:
            raise NextScene("animations")
        else:
            progress += 100
            super()._update(frame_no)

# we have to make a funny tab layout to insert in every page because asciimatics is shit
class TabButtons(Layout):
    def __init__(self, frame, active_tab_idx):
        cols = [1, 1, 1, 1, 1]
        super().__init__(cols)
        self._frame = frame

        tabs = [
                Button("ANIMATIONS", lambda:self._on_click("animations")),
                Button("AUDIO", lambda:self._on_click("audio")),
                Button("SCRIPTS", lambda:self._on_click("scripts")),
                Button("SETTINGS", lambda:self._on_click("settings")),
                Button("< QUIT >", lambda:self._on_click("quit"))
        ]

        for i, btn in enumerate(tabs):
            self.add_widget(btn, i)
            self.add_widget(Divider(draw_line=True, height=2), i).custom_colour = "disabled"

        # this is basically calling the layout again and disabling the current root page
        # so you cant 'reload' the frame
        tabs[active_tab_idx].disabled = True

    def _on_click(self, page):
        if page == "quit":
            kill()
            log("Manual GUI quit. Exiting...")
            raise StopApplication("Manual Quit")
        else:
            log("Drawing '{}' page...".format(page))
            raise NextScene(page)

# same thing for the bottom status tab
class StatusTab(Layout):
    def __init__(self, frame):
        cols = [1, 1, 1, 1]
        super().__init__(cols)
        self._frame = frame

        self.info = [
            Label("", name="status.anim", align="^"),
            Label("", name="status.audio", align="^"),
            Label("", name="status.scripts", align="^"),
            Label("", name="status.time", align="^")
        ]

        for i, txt in enumerate(self.info):
            self.add_widget(txt, i)
            txt.custom_colour = 'title'

    def update(self, frame_no):
        self.info[0].text = ("[RGB] " if runtime_vars["RGB"] else "") + ("[LOOP] " if runtime_vars["LOOP"] else "") + ("" if len(get_status()[0]) < 2 else os.path.basename(get_status()[0]['filepath']))
        self.info[1].text = "Audio OFF" if not runtime_vars["AUDIO"] else f"Volume: {runtime_vars['VOLUME']}"
        self.info[1].custom_colour = 'red' if not runtime_vars["AUDIO"] else 'title'
        self.info[2].text = "Scripts OFF" if not runtime_vars["SCRIPTS"] else "Scripts ON"
        self.info[2].custom_colour = 'red' if not runtime_vars["SCRIPTS"] else 'title'
        self.info[3].text = datetime.now().strftime('%I:%M %p %Z')

        for i, txt in enumerate(self.info):
            txt.update(frame_no)


# and also funny options layout for every page because, you guessed it, asciimatics is shit
class AnimationsPageOptions(Layout):
    def __init__(self, frame):
        cols = [1, 1, 1]
        super().__init__(cols)
        self._frame = frame

        self.options = [
                CheckBox("RGB Enabled", on_change=lambda:self._mode_switch("rgb"), name="RGB"),
                CheckBox("Looping Enabled", on_change=lambda:self._mode_switch("loop"), name="LOOP"),
                Button("Kill Anims", lambda:kill())
        ]


        for i, btn in enumerate(self.options):
            self.add_widget(btn, i)
            self.add_widget(Divider(draw_line=True), i)

    def _mode_switch(self, mode):
        if mode == "rgb":
            runtime_vars["RGB"] = self.options[0].value
        elif mode == "loop":
            runtime_vars["LOOP"] = self.options[1].value

class AnimationsPage(Frame):
    def __init__(self, screen):
        super().__init__(screen,
                         screen.height,
                         screen.width,
                         can_scroll=False,
                         data=runtime_vars,
                         title=env.protogen)

        # customization stuff
        self.palette['background'] = [0,Screen.A_BOLD,0]
        self.palette['button'] = [7,Screen.A_BOLD,0]
        self.palette['control'] = [7,Screen.A_BOLD,0]
        self.palette['selected_control'] = [0,Screen.A_BOLD,7]
        self.palette['field'] = [7,Screen.A_BOLD,0]
        self.palette['selected_field'] = [0,Screen.A_BOLD,7]
        self.palette['edit_text'] = [7,Screen.A_BOLD,0]
        self.palette['focus_edit_text'] = [0,Screen.A_BOLD,7]
        self.palette['focus_field'] = [7,Screen.A_BOLD,0]
        self.palette['selected_focus_field'] = [0,Screen.A_BOLD,7]
        self.palette['focus_button'] = [0,Screen.A_BOLD,7]
        self.palette['focus_control'] = [0,Screen.A_BOLD,7]
        self.palette['selected_focus_control'] = [0,Screen.A_BOLD,7]
        self.palette['red'] = [1,Screen.A_BOLD,0]

        # more customiation stuff
        self.palette['disabled'] = [0,Screen.A_BOLD,0]
        self.palette['title'] = [env.theme_color,Screen.A_BOLD,0]
        self.palette['borders'] = [env.theme_color,Screen.A_BOLD,0]
        self.palette['label'] = [7,Screen.A_BOLD,0]

        self.add_layout(TabButtons(self, 0))
        self.add_layout(AnimationsPageOptions(self))

        this_page = Layout([1, 1, 1, 1, 1], fill_frame=True)
        self.add_layout(this_page)

        column = 0
        for page_key, page_value in anims.items():
            for anim_key, anim_values in page_value.items():
                if not page_key == "0":
                    runtime_anims.append((anim_key, anim_values['streamfile']))

                    func = lambda a=anim_values: self.display_relay(a)
                    this_page.add_widget(Button(anim_key.replace('_',' ').title(), func), column)

                    debug(f"Dynamically created button for '{anim_key}'")

                    if column > 3:
#                        for i in range(5):
#                            this_page.add_widget(Divider(draw_line=False), i)
                        column = 0
                    else:
                        column += 1
        log(runtime_anims)
        self.add_layout(StatusTab(self))
        self.fix()

    def display_relay(self, streamfile):
        # check if the looping checkbox is toggled first
        looping = 3 if not runtime_vars["LOOP"] else 0
        log(f"Requesting '{streamfile}' {f'with {looping} loops' if looping > 0 else ''}")
        show(streamfile, loops=looping)

class AudioPageOptions(Layout):
    def __init__(self, frame):
        cols = [1, 1, 1]
        super().__init__(cols)
        self._frame = frame

        self.options = [
                CheckBox("Audio Enabled", on_change=lambda:self._mode_switch("toggle"), name="AUDIO"),
                Button("Volume Up", lambda:self._mode_switch("up")),
                Button("Volume Down", lambda:self._mode_switch("down"))
        ]

        for i, btn in enumerate(self.options):
            self.add_widget(btn, i)
            self.add_widget(Divider(draw_line=True), i)

    def _mode_switch(self, mode):
        if mode == "toggle":
            runtime_vars["AUDIO"] = self.options[0].value
            self.options[1].disabled = not self.options[0].value
            self.options[2].disabled = not self.options[0].value
        elif mode == "up":
            if not runtime_vars["AUDIO"]:
                log("Audio currently muted")
            elif runtime_vars["AUDIO"]:
                if runtime_vars["VOLUME"] >= 20000:
                    log("Volume: " + str(runtime_vars["VOLUME"]))
                else:
                    runtime_vars["VOLUME"] += 250
#                    log("Volume: " + str(runtime_vars["VOLUME"]))

        elif mode == "down":
            if not runtime_vars["AUDIO"]:
                log("Audio currently muted")
            elif runtime_vars["AUDIO"]:
                if 0 >= runtime_vars["VOLUME"]:
                    log("Volume: " + str(runtime_vars["VOLUME"]))
                else:
                    runtime_vars["VOLUME"] -= 250
 #                   log("Volume: " + str(runtime_vars["VOLUME"]))

class AudioPage(Frame):
    def __init__(self, screen):
        super().__init__(screen,
                         screen.height,
                         screen.width,
                         data=runtime_vars,
                         can_scroll=False,
                         title=env.protogen)

        self.add_layout(TabButtons(self, 1))
        self.add_layout(AudioPageOptions(self))

        this_page = Layout([1], fill_frame=True)
        self.add_layout(this_page)
        # add your widgets here

        self.add_layout(StatusTab(self))
        self.fix()

class ScriptsPageOptions(Layout):
    def __init__(self, frame):
        cols = [1]
        super().__init__(cols)
        self._frame = frame

        self.options = [
                CheckBox("Scripts Enabled", on_change=lambda:self._mode_switch("scripts"), name="SCRIPTS")
        ]

        for i, btn in enumerate(self.options):
            self.add_widget(btn, i)
            self.add_widget(Divider(draw_line=True), i)

    def _mode_switch(self, mode):
        if mode == "scripts":
            runtime_vars["SCRIPTS"] = self.options[0].value

class ScriptsPage(Frame):
    def __init__(self, screen):
        super().__init__(screen,
                         screen.height,
                         screen.width,
                         data=runtime_vars,
                         can_scroll=False,
                         title=env.protogen)

        self.add_layout(TabButtons(self, 2))
        self.add_layout(ScriptsPageOptions(self))

        this_page = Layout([1], fill_frame=True)
        self.add_layout(this_page)
        # add your widgets here

        self.add_layout(StatusTab(self))
        self.fix()

class SettingsPage(Frame):
    def __init__(self, screen):
        super().__init__(screen,
                         screen.height,
                         screen.width,
                         can_scroll=True,
                         title=env.protogen)

        self.add_layout(TabButtons(self, 3))

        this_page = Layout([1], fill_frame=True)
        self.add_layout(this_page)

        # settings categories
        self.defaults = [
            Label("changes are saved immediately", name="", align="^"),
            Divider(draw_line=False),
            Label("Default Startup Options", align="^"),
            Divider(draw_line=True),
            CheckBox("", label="RGB Enabled", on_change=lambda:self._update_setting("advanced.rgb", self.defaults[4]), name="advanced.rgb"),
            CheckBox("", label="Looping Enabled", on_change=lambda:self._update_setting("advanced.loop", self.defaults[5]), name="advanced.loop"),
            CheckBox("", label="Audio Enabled", on_change=lambda:self._update_setting("advanced.audio", self.defaults[6]), name="advanced.audio"),
            Text(label="Default Volume:", on_change=lambda:self._update_setting("advanced.volume", self.defaults[7]), name="advanced.volume"),
            CheckBox("", label="Scripts Enabled",on_change=lambda:self._update_setting("advanced.scripts", self.defaults[8]), name="advanced.scripts"),
            Text(label="Selection Sensitivity:", on_change=lambda:self._update_setting("advanced.sensitivity", self.defaults[9]), name="advanced.sensitivity"),
            ListBox(1, runtime_anims, label="Startup Animation", on_change=lambda:self._update_setting("advanced.startup_anim",self.defaults[10]), name="advanced.startup_anim")
        ]

        self.customization = [
            Divider(draw_line=False),
            Label("Protogen Customization", align="^"),
            Divider(draw_line=True),
            Text(label="Name:", on_change=lambda:self._update_setting("preferences.name", self.customization[3]), name="preferences.name")
        ]

        self.wifi = [
            Divider(draw_line=False),
            Label("WiFi Setup", align="^"),
            Divider(draw_line=True),
            CheckBox("", label="WiFi Updates Allowed", on_change=lambda:self._update_setting("system.wifi_enabled", self.wifi[3]), name="system.wifi_enabled"),
            Text(label="WiFi Name (SSID):", on_change=lambda:self._update_setting("system.wifi_ssid", self.wifi[4]), name="system.wifi_ssid"),
            Text(label="WiFi Password:", on_change=lambda:self._update_setting("system.wifi_pw", self.wifi[5]), name="system.wifi_pw")
        ]

        self.config = [
            Divider(draw_line=False),
            Label("Additional Config", align="^"),
            Divider(draw_line=True),
            CheckBox("", label="Debug Mode (additional logging)", on_change=lambda:self._update_setting("system.debug_on", self.config[3]), name="system.debug_on")
        ]

        self.settings = self.defaults + self.customization + self.wifi + self.config

        for i, options in enumerate(self.settings):
            this_page.add_widget(options)

            if "label." in str(type(options)):
                options.custom_colour = 'title'
            else:
                options.disabled = False

            if "checkbox." in str(type(options)):
                options.value = get_config_option(options.name)

            if "text." in str(type(options)):
                options.value = str(get_config_option(options.name))

        self.defaults[10].value = get_config_option("advanced.startup_anim")

#        self.add_layout(StatusTab(self))
        self.fix()

    def _next_focus(self):
        pass

    def _update_setting(self, setting, pointer):
        # get the exact value and strip it of whitespace, except if it's a wifi setting
        # (just in case the password or SSID has a leading or trailing whitespace
        new_value = pointer.value.strip() if (type(pointer.value) == type('') and "wifi_" not in setting) else pointer.value

        # update the debug var during runtime since its important
        if setting == "system.debug_on":
            runtime_vars["debug"] = new_value

        set_config_option(setting, new_value)

    def _default_animation(self):
        raise NextScene("settings.default_animation")

def debug(msg, errno=0):
    if runtime_vars["debug"]:
        log(msg, err_id=errno)

def get_runtime_vars():
    return runtime_vars

def global_shortcuts(event):
    if isinstance(event, KeyboardEvent):
        code = event.key_code

        # global quit
        if code in (17, 24):
            kill()
            log("Manual GUI quit. Exiting...")
            raise StopApplication("Manual Quit")

def display(screen, scene):
    scenes = [
        Scene([AnimationsPage(screen)], -1, name="animations"),
        Scene([AudioPage(screen)], -1, name="audio"),
        Scene([ScriptsPage(screen)], -1, name="scripts"),
        Scene([SettingsPage(screen)], -1, name="settings")
    ]

    # don't play the loading screen if there's no boot anim
    if anims.get('0').get('boot_anim') is not None:
        scenes.insert(0, Scene([LoadingBar(screen)], -1))

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True, unhandled_input=global_shortcuts)

def main():
    last_scene = None
    while True:
        try:
            Screen.wrapper(display, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

if __name__ == "__main__":
    main()
