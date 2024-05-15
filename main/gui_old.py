#!/usr/bin/env python3

from asciimatics.widgets import Frame, TextBox, Layout, Label, Divider, Text,CheckBox, Button, VerticalDivider, Widget
from asciimatics.event import KeyboardEvent
from asciimatics.effects import Print, Background
from asciimatics.renderers import BarChart, ImageFile, ColourImageFile, FigletText
from asciimatics.scene import Scene
from asciimatics.screen import Screen, Canvas
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from asciimatics.parsers import AsciimaticsParser
from time import sleep
from random import randint

import subprocess
import keyboard
import random
import sys
import time
import os

activeFace = True
activeCamera = False
button_timeout = 0.4
vol = 5000
rgb = False
loop = True
audio = True

progress = 0
last_scene = None

default_data = {
	"RGB": rgb,
	"LOOP": loop,
	"AUDIO": audio,
}

class ProgressBar(Print):
	def __init__(self, screen):
		super(ProgressBar, self).__init__(
			screen,
			BarChart(
				1, screen.width - 20, [self.get_progress],
				char="/",
				scale=100,
				labels=False,
				axes=0,
				border=False,
				colour=3),
			x=10,
			y=(screen.height - 3),
			speed=2,
			transparent=False)

	def _update(self, frame_no):
		global progress
		if progress >= 100:
			raise StopApplication("Load Finished")
		else:
			progress += 1
			super(ProgressBar, self)._update(frame_no)

	def get_progress(self):
		return progress
74
def load(screen):
	scenes = []

	effects = [
		Print(screen, ImageFile("icon.png", screen.height - 18),0),
		Print(screen, FigletText("ProtOS v1.4",font='trek'), screen.height//2+2, screen.width//20, colour=3, bg=0),
		ProgressBar(screen)
	]

	scenes.append(Scene(effects))
	screen.play(scenes, stop_on_resize=False)


class Rasputin(Frame):
	def __init__(self,screen):
		super().__init__(screen, screen.height, screen.width, can_scroll=False, data=default_data, has_border=True, title="R4SPUT1N")

		layout1 = Layout([24,1,25,25,25], fill_frame=False)
		layout2 = Layout([100], fill_frame=True)
		layout3 = Layout([12,2,12,1,74], fill_frame=False)
		self.add_layout(layout1)
		self.add_layout(layout3)
		self.add_layout(layout2)

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

		self.palette['disabled'] = [7,Screen.A_BOLD,0]
		self.palette['title'] = [3,Screen.A_BOLD,0]
		self.palette['borders'] = [3,Screen.A_BOLD,0]
		self.palette['label'] = [7,Screen.A_BOLD,0]

		self.con = layout2.add_widget(TextBox(Widget.FILL_FRAME, label="CONSOLE:", parser=AsciimaticsParser(), name="CONSOLE", line_wrap=True, readonly=True, as_string=True))
		self.con.custom_colour = 'title'
		self.con.hide_cursor = True
		self.con.disabled = True

		layout3.add_widget(Button("VOL -", self._volDown), 0)
		layout3.add_widget(VerticalDivider(), 1)
		layout3.add_widget(Button("VOL +", self._volUp), 2)
		layout3.add_widget(VerticalDivider(), 3)
		layout3.add_widget(Divider(draw_line=True), 0)
		layout3.add_widget(Divider(draw_line=True), 1)
		layout3.add_widget(Divider(draw_line=True), 2)
		layout3.add_widget(Divider(draw_line=True), 3)

		layout1.add_widget(CheckBox("RGB", on_change=self._toggleRGB, name="RGB"), 0)
		layout1.add_widget(Divider(draw_line=False), 0)
		layout1.add_widget(CheckBox("LOOP", on_change=self._toggleLoop, name="LOOP"), 0)
		layout1.add_widget(Divider(draw_line=False), 0)
		layout1.add_widget(CheckBox("AUDIO", on_change=self._toggleAudio, name="AUDIO"), 0)
		layout1.add_widget(Divider(draw_line=True), 0)

		layout1.add_widget(Button("PAIR SPEAKER", self._pairBluetoothSpeaker), 0)
		layout1.add_widget(Divider(draw_line=True), 0)

#		layout1.add_widget(Button("RANDOM AUDIO", self._playAudioRandom), 0)
#		layout1.add_widget(Divider(draw_line=False), 0)
		layout1.add_widget(Button("SHORT AUDIO", self._playAudioShort), 0)
		layout1.add_widget(Divider(draw_line=False), 0)
		layout1.add_widget(Button("MED AUDIO", self._playAudioMed), 0)
		layout1.add_widget(Divider(draw_line=False), 0)
		layout1.add_widget(Button("LONG AUDIO", self._playAudioLong), 0)
		layout1.add_widget(Divider(draw_line=False), 0)
		layout1.add_widget(Button("YA RASPUTIN", self._playAudioName), 0)
		layout1.add_widget(Divider(draw_line=True), 0)


		layout1.add_widget(VerticalDivider(), 1)
		layout1.add_widget(Button("Attention", self.pf1, name="Attention"), 2)
		layout1.add_widget(Button("Yes", self.pf2), 3)
		layout1.add_widget(Button("No", self.pf3), 4)
#		layout1.add_widget(Divider(draw_line=False), 2)
#		layout1.add_widget(Divider(draw_line=False), 3)
#		layout1.add_widget(Divider(draw_line=False), 4)
		layout1.add_widget(Button("Annoyed", self.pf4), 2)
		layout1.add_widget(Button("Blink 2", self.pf5), 3)
		layout1.add_widget(Button("Blink 3", self.pf6), 4)
		layout1.add_widget(Button("Charging", self.pf7), 2)
		layout1.add_widget(Button("Coffee", self.pf8), 3)
		layout1.add_widget(Button("Cry", self.pf9), 4)
		layout1.add_widget(Button("Dizzy", self.pf10), 2)
		layout1.add_widget(Button("Error", self.pf11), 3)
		layout1.add_widget(Button("Heart Eyes", self.pf12), 4)
		layout1.add_widget(Button("Laugh", self.pf13), 2)
		layout1.add_widget(Button("Load", self.pf14), 3)
		layout1.add_widget(Button("Low Battery", self.pf15), 4)
		layout1.add_widget(Button("Music", self.pf16), 2)
		layout1.add_widget(Button("Happy", self.pf17), 3)
		layout1.add_widget(Button("Sleep", self.pf18), 4)
		layout1.add_widget(Button("Sorry", self.pf19), 2)
		layout1.add_widget(Button("Vaporwave", self.pf20), 3)
		layout1.add_widget(Button("Glitch", self.pf21), 4)
		layout1.add_widget(Button("Ahegao", self.pf22), 2)
		layout1.add_widget(Button("Sheesh", self.pf23), 3)
		layout1.add_widget(Button("Ratio", self.pf24), 4)
		layout1.add_widget(Button("Pacman", self.pf25), 2)
		layout1.add_widget(Button("X Eyes", self.pf26), 3)
		layout1.add_widget(Button("O Eyes", self.pf27), 4)
		layout1.add_widget(Button("OwO", self.pf29), 2)
		layout1.add_widget(Button("UwU", self.pf31), 3)
		layout1.add_widget(Button("Big UwU", self.pf30), 4)
		layout1.add_widget(Button("Big OwO", self.pf28), 2)
		layout1.add_widget(Button("Boot Up", self.pf32), 3)
		layout1.add_widget(Button("Boot Down", self.pf33), 4)
		layout1.add_widget(Button("QR", self.pf34), 2)
		layout1.add_widget(Button("Amgery", self.pf35), 3)
		layout1.add_widget(Button("BK Mode", self.pf36), 4)
		layout1.add_widget(Button("Sunglasses", self.pf37), 2)
		layout1.add_widget(Button("Lua", self.pf38), 3)
		layout1.add_widget(Button("Boykisser", self.pf39), 4)
		layout1.add_widget(Button("Smug", self.pf40), 2)

		layout1.add_widget(Divider(draw_line=False), 3)
		layout1.add_widget(Divider(draw_line=False), 4)
		layout1.add_widget(Divider(draw_line=True), 2)

		layout1.add_widget(Button("CLEAR CLI", self.clearLog), 2)
		layout1.add_widget(Divider(draw_line=True), 2)
		layout1.add_widget(Divider(draw_line=True), 3)
		layout1.add_widget(Button("KILL FACE", self.forceKill), 3)
		layout1.add_widget(Divider(draw_line=True), 3)
		layout1.add_widget(Divider(draw_line=True), 4)
		layout1.add_widget(Button("< QUIT >", self.exitEvent), 4)
		layout1.add_widget(Divider(draw_line=True), 4)

		self.fix()
		global audio
		global loop
		global rgb
		global vol
		vol = 10000
		audio = True
		loop = True
		rgb = False
		sleep(1)
		self.defaultFace()

	def process_event(self, event):

		if activeCamera:
			sleep(0)
		if activeFace:
			sleep(0)
#		self.log(str(rgb))
#		self.log(str(loop))
#		self.log(str(audio))
		return super(Rasputin, self).process_event(event)
	def exitEvent(self):
		self.endCurrentFace()
		self.log("Goodbye!")
		sleep(0.1)
		sys.exit(0)
	def log(self, text):
		self.con.value += "${7,1}" + text + "\n"
	def clearLog(self):
		self.con.value = None

	def _toggleRGB(self):
		global rgb
		rgb = not rgb
	def _toggleLoop(self):
		global loop
		loop = not loop
	def _toggleAudio(self):
		global audio
		global vol
		audio = not audio
		if (vol >= 0):
			vol = 0
		elif (0 >= vol):
			vol = 5000
	def _volUp(self):
		global audio
		global vol

		if (not audio):
			self.log("Audio currently muted")
		elif (audio):
			if (vol >= 20000):
				self.log("Volume: " + str(vol))
			else:
				vol += 250
				self.log("Volume: " + str(vol))
	def _volDown(self):
		global audio
		global vol

		if (not audio):
			self.log("Audio currently muted")
		elif (audio):
			if (0 >= vol):
				self.log("Volume: " + str(vol))
			else:
				vol -= 250
				self.log("Volume: " + str(vol))

	def _playAudioRandom(self):
		temp = random.randint(1,3)

		if audio:
			if (temp == 1):
				self._playAudioShort()
			if (temp == 2):
				self._playAudioMed()
			if (temp == 3):
				self._playAudioLong()
	def _playAudioShort(self):
		global audio
		global vol
		cmd = "mpg123 -a 2 -f " + str(vol) + " /home/admin/rasputin/sounds/talk_short" + str(random.randint(1,2)) + ".mp3 &"
		if audio:
			self.log("> " + cmd)
			subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	def _playAudioMed(self):
		global audio
		global vol
		cmd = "mpg123 -a 2 -f " + str(vol) + " /home/admin/rasputin/sounds/talk_med" + str(random.randint(1,4)) + ".mp3 &"
		if audio:
			self.log("> " + cmd)
			subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	def _playAudioLong(self):
		global audio
		global vol
		cmd = "mpg123 -a 2 -f " + str(vol) + " /home/admin/rasputin/sounds/talk_long" + str(random.randint(1,2)) + ".mp3 &"
		if audio:
			self.log("> " + cmd)
			subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	def _playAudioName(self):
		global audio
		global vol
		cmd = "mpg123 -a 2 -f " + str(vol) + " /home/admin/rasputin/sounds/ya_rasputin.mp3 &"
		if audio:
			self.log("> " + cmd)
			subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

	def _pairBluetoothSpeaker(self):
		self.log("> ./bt_speaker.sh")
		proc = subprocess.run('./bt_speaker.sh', shell=True, capture_output=True, text=True)
		if "Failed" not in proc.stdout:
			self.log("SUCCESS")
		else:
			self.log("FAILED")
	def pf0(self, anim, speed):
		global rgb
		global loop
		global activeFace

		if rgb:
			speed -= 60
		speed = str(speed)

		cmd_root = "./led-image-viewer"
		cmd_path = " ~/rasputin/faces/"
		cmd = cmd_root + " --led-slowdown-gpio=4 --led-limit-refresh=90 --led-gpio-mapping=adafruit-hat --led-brightness=100 --led-cols=128 --led-rows=32 -D" + speed
		if loop:
			anim += "_loop"
			cmd += " --led-daemon"
		elif not loop:
			cmd += " -l1"
		if rgb:
			anim = "rgb_" + anim
		anim += ".proot"

		if activeFace:
			self.endCurrentFace()
		if not activeFace:
			activeFace = True
			cmd = cmd + cmd_path + anim
			self.log("> " + anim)
			subprocess.run(cmd,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			if loop:
				activeFace = True
			if not loop:
				self.defaultFace()

	def pf1(self):
		self.pf0("attention", 75)
	def pf2(self):
		self.pf0("yes", 75)
	def pf3(self):
		self.pf0("no", 75)
	def pf4(self):
		self.pf0("blink1", 60)
	def pf5(self):
		self.pf0("blink2", 60)
	def pf6(self):
		self.pf0("blink3", 60)
	def pf7(self):
		self.pf0("charging", 80)
	def pf8(self):
		self.pf0("coffee", 90)
	def pf9(self):
		self.pf0("cry", 70)
	def pf10(self):
		self.pf0("dizzy", 90)
	def pf11(self):
		self.pf0("error", 60)
	def pf12(self):
		self.pf0("heart", 70)
	def pf13(self):
		self.pf0("laugh", 85)
	def pf14(self):
		self.pf0("load", 80)
	def pf15(self):
		self.pf0("lowbattery", 80)
	def pf16(self):
		self.pf0("music", 70)
	def pf17(self):
		self.pf0("party", 75)
	def pf18(self):
		self.pf0("sleep", 120)
	def pf19(self):
		self.pf0("sorry", 65)
	def pf20(self):
		self.pf0("vapor", 5000)
	def pf21(self):
		self.pf0("glitch", 60)
	def pf22(self):
		global loop
		self.pf0("ahegao", 2000)
		if loop:
			global audio
			global vol
			cmd = "mpg123 -a 2 -f " + str(vol) + " /home/admin/rasputin/sounds/usb.mp3 &"
			if audio:
				self.log("> " + cmd)
				subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
	def pf23(self):
		self.pf0("sheesh", 60)
	def pf24(self):
		self.pf0("ratio", 30)
	def pf25(self):
		self.pf0("pacman", 50)
	def pf26(self):
		self.pf0("xeyes", 60)
	def pf27(self):
		self.pf0("oeyes", 60)
	def pf28(self):
		self.pf0("owo2", 120)
	def pf29(self):
		self.pf0("owo1", 60)
	def pf30(self):
		self.pf0("uwu2", 120)
	def pf31(self):
		self.pf0("uwu1", 60)
	def pf32(self):
		self.pf0("boot", 16)
	def pf33(self):
		global loop

		self.pf0("bootdown", 30)
		if not loop:
			self.forceKill()
	def pf34(self):
		global rgb

		if not rgb:
			self.pf0("qr", 2000)
		else:
			self.pf0("qr", 120)
	def pf35(self):
		self.pf0("angery", 3000)
	def pf36(self):
		self.pf0("bk", 3000)
	def pf37(self):
		self.pf0("glasses", 3000)
	def pf38(self):
		self.pf0("lua", 2000)
	def pf39(self):
		self.pf0("boykisser", 3000)
	def pf40(self):
		self.pf0("smug", 3000)

	def forceKill(self):
#		self.clearLog()
		self.endCurrentFace()
		self.log("KILLED ACTIVE ANIM")

	def endCurrentFace(self):
		global activeFace
#		subprocess.run('pgrep -f /home/admin/rasputin/faces | sudo xargs kill -s SIGINT &> /dev/null', shell=True, stdout=subprocess.PIPE)
		subprocess.run('pgrep -f led-image-viewe | sudo xargs kill -s SIGINT', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#		self.log("Killed active face")
		activeFace = False

	def defaultFace(self):
		global activeFace
		global rgb
		anim = "blink2.proot"
		speed = "50"
		cmd_root = "./led-image-viewer"
		cmd_path = " ~/rasputin/faces/"
		if rgb:
			anim = "rgb_" + anim
			speed = "10"
		if activeFace:
			self.endCurrentFace()
		cmd = cmd_root + " --led-slowdown-gpio=4 --led-limit-refresh=60 --led-gpio-mapping=adafruit-hat --led-brightness=100 --led-cols=128 --led-rows=32 --led-daemon -D" + speed
		if not activeFace:
			activeFace = True
			cmd = "sudo " + cmd + cmd_path + anim
#			self.log("> " + anim)
			subprocess.run(cmd,shell=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def main(screen, scene):
	_scenes = [
#		Background(screen, bg=4),
		Scene([Rasputin(screen)], -1, name="Rasputin"),
	]

	screen.play(_scenes, stop_on_resize=True, start_scene=scene, allow_int=True)


# MAIN EXEC
#

#subprocess.run('./default_face.sh &', shell=True)
#sleep(1)
#Screen.wrapper(load)


while True:
	try:
		sleep(0.1)
		Screen.wrapper(main, catch_interrupt=True, arguments=[last_scene])
		sys.exit(0)
	except ResizeScreenError as e:
		last_scene = e.scene
