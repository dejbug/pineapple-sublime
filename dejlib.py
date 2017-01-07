import sublime
import inspect


def get_points(view):
	"""Get the list of cursor positions."""
	return [region.b for region in view.sel()]


def replace_contents(view, edit, text=""):
	r = sublime.Region(0, view.size())
	view.replace(edit, r, text)


def open_scratch_view(wnd=None,
		text=None, syntax='Python', def_ext='py',
		wrap=True, scratch=True):
	"""Open a tab as if e.g. a Python file was opened from memory."""
	wnd = wnd or sublime.active_window()
	view = sublime.active_window().new_file()
	view.set_scratch(scratch)
	view.settings().set("word_wrap", wrap)
	view.settings().set('default_extension', def_ext)
	view.assign_syntax('Packages/{0}/{0}.sublime-syntax'.format(syntax))
	if text: view.run_command("insert_snippet", {"contents": text})
	return view


class LoopIndexBreaker(object):
	def __init__(self, break_at_index=-1):
		self.break_at_index = break_at_index
		self.index = 0

	def reset(self):
		self.index = 0

	def should_break(self):
		self.index += 1
		return self.break_at_index == self.index - 1

	def info(self, func):
		return ("%s: hard break at loop index %d in"
			" func '%s' in file '%s'" % (
			self.__class__.__name__, self.break_at_index,
			func.__name__, __file__))


def iter_lines(view, start=0, skipper=None, break_at_loop_index=-1):
	"""Iterate through every line.
	
	start -- The point (i.e. char offset) at which to begin.
	skipper -- e.g. lambda r: False
	break_at_loop_index -- fail-safe to prevent infinite
		loops; set to -1 to disable this feature, or to some
		positive integer to stop the loop after this many
		iterations.
	"""
	loop_breaker = LoopIndexBreaker(break_at_loop_index)
	
	s = view.size()
	r = view.full_line(start)
	while True:
		if loop_breaker.should_break():
			print(loop_breaker.info(iter_lines))
			break
		if not (skipper and skipper(r)):
			yield r
		if r.b == s: break
		r = view.full_line(r.b)


def scoped_iter_lines(view, selector="source.python", start=0, skipper=None):
	"""Iterate through every line and return a (bool,str)-tuple
	with the boolean marking e.g. valid Python lines.

	start -- see: iter_lines()
	skipper -- see: iter_lines()
	"""
	for r in iter_lines(view, 0, skipper):
		if view.score_selector(r.a, selector) > 0:
			yield True, r
		else:
			yield False, r


def get_point_segment(view, point=None, selector="source.python"):
	"""Return the entire range, containing 'point', which
	matches the 'selector' scope. In other words, get e.g.
	all the Python source surrounding the current cursor
	position.
	"""
	point = point or get_points(view)[-1]
	if view.score_selector(point, selector) > 0:
		for r in view.find_by_selector(selector):
			if r.contains(point):
				return r


class SyntaxSetter(object):
	def __init__(self, view, backup_format="%s_backup"):
		self.view = view
		self.backup_format = backup_format

	def set(self, syntax="Python", def_ext="py", wrap=True):
		Setting("word_wrap", self.backup_format).set(wrap)
		Setting("default_extension", self.backup_format).set(def_ext)
		Setting("syntax", self.backup_format).set(
			"Packages/{0}/{0}.sublime-syntax".format(syntax))

	def reset(self):
		Setting("word_wrap", self.backup_format).reset()
		Setting("default_extension", self.backup_format).reset()
		Setting("syntax", self.backup_format).reset()


class Setting(object):

	def __init__(self, key, backup_format="%s_backup"):
		"""Set a setting but make it resettable to
		the original value. Set 'backup_format' to 'None'
		to disable backup logic.
		"""
		self.key = key
		self.backup_format = backup_format

	def get(self):
		"""Get the value of this setting."""
		return self.conf.get(self.key)

	def set(self, value):
		"""Set the value of this setting. If the backup
		slot is empty, the current value is backed up."""
		old = self.get_backup()
		if None == old:
			cur = self.conf.get(self.key)
			self.set_backup(cur)
		if None != value:
			self.conf.set(self.key, value)

	def reset(self):
		"""Restore this setting's backup value, if any."""
		old = self.get_backup()
		if None != old:
			self.conf.set(self.key, old)
			self.set_backup(None)

	def get_backup(self):
		try: backup_key = self.backup_format % self.key
		except: return None
		else: return self.conf.get(backup_key)

	def set_backup(self, value):
		try: backup_key = self.backup_format % self.key
		except: pass
		else: return self.conf.set(backup_key, value)

	@property
	def conf(self):
		"""Sublime's global settings object."""
		return sublime.active_window().active_view().settings()

	@property
	def old(self):
		"""This setting's backup value, if any."""
		return self.get_backup()


def def_args_storer(func):
	spec = inspect.getargspec(func)
	args_dict = dict(zip(
		reversed(spec.args),
		reversed(spec.defaults)))
	setattr(func, "_def_args", args_dict)
	return func

