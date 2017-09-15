# pineapple-sublime
Fresh odds and ends to render Sublime Text 3 more opinionated about matters of text editing taste.
# howto install
Just copy what you need into your `User` path. Most scripts depend on `dejlib.py`, so make sure to copy that one too. Other than that, just read the source for info.
# where is my `User` path?
Open the Sublime Text 3 console (`View->Show Console`) then type `import os.path` then type `os.path.join(sublime.packages_path(), "User")`.
# how to set up keybindings for commands?
Open the keybindings window (`Preferences->Key Bindings`). To the right (or lower) pane, add relevant lines of the following form:

```javascript
[
	// ... all the other stuff already present in the file, if any.
	// (Make sure a comma is the final char.)

    {
    	// Trigger when 'ALT + M' is pressed.
    	"keys": ["alt+m"],
		// Execute 'QuickTempSetSyntaxCommand.py'
    	"command": "quick_temp_set_syntax",
    	// Pass the following keyword args to QuickTempSetSyntaxCommand.run()'.
        "args": {
            "action": "toggle",
            "syntax": "Packages/Markdown Extended/Syntaxes/Markdown Extended.sublime-syntax",
            "scheme": "Packages/Monokai Extended/Monokai Extended Bright.tmTheme",
        }
    },
]
```

Enjoy.
