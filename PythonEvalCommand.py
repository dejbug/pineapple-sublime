import sublime
import sublime_plugin


class PythonEvalCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		# self.view.insert(edit, 0, type(Exception))
		for region in self.view.sel():
			selection_text = self.view.substr(region)

			try:
				evaluated_text = str(eval(selection_text))

			except:
				sublime.status_message("eval failed!")

			else:
				self.view.replace(edit, region, evaluated_text)
