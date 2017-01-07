import sublime
import sublime_plugin
import pydoc

from User.dejlib import Setting


class Settings(object):

	def __init__(self):
		self.syntax = Setting("syntax")
		self.scheme = Setting("color_scheme")


class QuickTempSetSyntaxCommand(sublime_plugin.TextCommand):

	def run(self, edit, action="reset", syntax=None, scheme=None):
		assert action in ("reset", "set", "toggle")

		settings = Settings()

		print(settings.syntax.get())
		print(settings.scheme.get())

		if action == "reset":
			settings.syntax.reset()
			settings.scheme.reset()

		elif action == "set":
			if syntax: settings.syntax.set(syntax)
			if scheme: settings.scheme.set(scheme)

		elif action == "toggle":
			if None != settings.syntax.old:
				settings.syntax.reset()
			elif syntax:
				settings.syntax.set(syntax)

			if None != settings.scheme.old:
				settings.scheme.reset()
			elif scheme:
				settings.scheme.set(scheme)

