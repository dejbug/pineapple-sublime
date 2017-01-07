import sublime
import sublime_plugin


class EditKeybindingsCommand(sublime_plugin.TextCommand):

	def run(self, edit):
		batch = [
			(	"edit_settings", {
					"base_file": ("${packages}/Default"
						"/Default ($platform).sublime-keymap"),
					"default": "[\n\t$0\n]\n"} ),
			(	"set_layout", {
					"cells": [[0, 0, 1, 1], [0, 1, 1, 2]],
					"cols": [0.0, 1.0],
					"rows": [0.0, 0.5, 1.0] } ), ]

		wnd = self.view.window()
		wnd.run_command(*batch[0])
		wnd = sublime.windows()[-1]
		wnd.run_command(*batch[1])
		
