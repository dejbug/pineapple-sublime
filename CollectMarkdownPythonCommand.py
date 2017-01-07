import sublime
import sublime_plugin

from User import dejlib


BACKUP_FORMAT = "collect_markdown_python_%s_backup"


def print_status(text, prefix="collect_markdown_python:"):
	"""Print |text| to Sublime Text's status bar."""
	sublime.status_message("%s %s" % (prefix, text))


def is_markdown(view):
	"""True if the view contains a markdown syntax'ed text."""
	return view.score_selector(0, "text.html.markdown") > 0


def is_extended_markdown(view):
	"""True if the view contains 'Markdown Extended'
	syntax'ed text.
	"""
	return view.settings().get("syntax").endswith(
		"Markdown Extended.sublime-syntax")


class UndoFilter(sublime_plugin.EventListener):
	"""This will monitor undo events and modify them
	so that the correct action is taken when in the
	undo history we navigate past our command.

	Specifically, if the last command we are undo-ing
	from (or redo-ing to) was our command, we have to
	restore (or set) the settings that our command is
	modifying; ST3 apparently won't do it for us.
	"""

	def on_text_command(self, view, cmd, args):
		
		# -- The user has hit the undo key somewhere.
		if cmd == "undo":
			# -- Fetch the command we are undoing from.
			#	Fetch it from the active view's undo history.
			undo_from = view.command_history(0, False)
			# -- Check whether it was our command.
			if undo_from[0] == "collect_markdown_python":
				# return ("collect_markdown_python", {"action": "undo"})

				# -- Yes, we are undoing our own command, so
				#	make sure that we reset everything we
				#	modified back to how it was before.
				setter = dejlib.SyntaxSetter(view, BACKUP_FORMAT)
				setter.reset()
				# -- We have modified only the syntax so we're
				#	done.

		# -- The user has hit the redo key somewhere.
		elif cmd == "redo_or_repeat":
			# -- Get the command that we are redoing to.
			redo_to = view.command_history(1, False)
			# -- Is it ours?
			if redo_to[0] == "collect_markdown_python":

				# -- Yes, so load the full dict of arguments
				#	that the command was executed with, not
				#	just the ones that had been explicitly
				#	specified (e.g. in the keybinding).
				last_args = dejlib.Setting(
					"last_collect_markdown_python_args",
					backup_format=None)
				args = last_args.get()
				args.update(redo_to[1])
				
				# -- We need only modify the syntax here.
				setter = dejlib.SyntaxSetter(view, BACKUP_FORMAT)
				setter.set(args["syntax"], args["def_ext"], args["wrap"])


class CollectMarkdownPythonCommand(sublime_plugin.TextCommand):
	"""To be used on a MarkdownExtended view.

	action -- If "all", copy the entire markdown text but
			comment out everything that isn't e.g. Python
			code. If "under cursors", copy only what is e.g.
			Python code and has a cursor in it.
	selector -- e.g. "source.python"
	comment_prefix -- (if action=="all") Use this prefix to
			comment out the non-selected for lines.
	segment_separator -- (if action=="under cursors") Use this
			suffix to separate the strips of e.g. Python code in
			the output.
	preserve_viewport -- (if action=="all" and open_scratch=True)
			Scroll the output to where the markdown file was at.
	strict -- Only run if file has ExtendedMarkdown syntax on.
	open_scratch -- Open a separate tab to write the output to.
	"""

	@dejlib.def_args_storer
	def run(self, edit,
			action="all",
			
			strict=True,
			selector="source.python",
			syntax="Python",
			def_ext="py",
			wrap=False,

			comment_prefix="# ",
			segment_separator="\n",
			
			preserve_viewport=True,
			open_scratch=False,
			):

		assert action in ("all", "under cursors", "reset")

		if not is_markdown(self.view):
			print_status("text is not in markdown")
			return

		if strict and not is_extended_markdown(self.view):
			print_status("(strict) syntax is not ExtendedMarkdown")
			return

		last_args = dejlib.Setting(
			"last_collect_markdown_python_args",
			backup_format=None)
		last_args.set(self.run._def_args)

		text = ""

		if action == "reset":
			setter = dejlib.SyntaxSetter(self.view, BACKUP_FORMAT)
			setter.reset()

		elif action == "all":

			for ok, r in dejlib.scoped_iter_lines(self.view, selector):
				if not ok: text += comment_prefix
				text += self.view.substr(r)

		elif action == "under cursors":

			for point in dejlib.get_points(self.view):
				r = dejlib.get_point_segment(self.view, point, selector)
				if r:
					text += self.view.substr(r)
					text += segment_separator

		if text:
			if open_scratch:
				if preserve_viewport: 
					port = self.view.viewport_position()
				view = dejlib.open_scratch_view(text=text)
				if preserve_viewport: 
					view.set_viewport_position(port)
			else:
				dejlib.replace_contents(self.view, edit, text)
				setter = dejlib.SyntaxSetter(self.view, BACKUP_FORMAT)
				setter.set(syntax, def_ext, wrap)

		else:
			print_status("nothing to collect")

