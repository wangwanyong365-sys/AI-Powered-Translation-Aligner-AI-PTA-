import tkinter as tk
from tkinter import messagebox, scrolledtext
from ui_settings import SettingsDialog

class AppMenuBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.annotator_window = None
        self.post_editor_window = None
        self._create_menus()

    def _create_menus(self):
        settings_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Options...", command=self._open_settings)

        tools_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Term Annotator", command=self._open_annotator)
        tools_menu.add_command(label="Post-editing", command=self._open_post_editor)

        help_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about_info)
        help_menu.add_command(label="View License", command=self._show_license_info)
    
    def _open_settings(self):
        SettingsDialog(self.parent)

    def _open_annotator(self):
        if self.annotator_window and self.annotator_window.winfo_exists():
            self.annotator_window.lift()
            self.annotator_window.focus_force()
            return
        
        from tools.tool_term_annotator import TermAnnotatorApp
        self.annotator_window = tk.Toplevel(self.parent)
        TermAnnotatorApp(self.annotator_window)

    def _open_post_editor(self):
        if self.post_editor_window and self.post_editor_window.winfo_exists():
            self.post_editor_window.lift()
            self.post_editor_window.focus_force()
            return

        from tools.tool_post_editing import PostEditingWindow
        self.post_editor_window = PostEditingWindow(self.parent)

    def _show_about_info(self):
        messagebox.showinfo(
            "About",
            "Wanyong Wang\n"
            "Email: wangwanyong365@hotmail.com\n\n"
            "Dechao Li\n"
            "Email: ctdechao@polyu.edu.hk\n\n"
            "Department of Language Science and Technology (LST)\n"            
            "The Hong Kong Polytechnic University\n"
            "Kowloon, Hong Kong, China\n",
            parent=self.parent
        )

    def _show_license_info(self):
        license_window = tk.Toplevel(self.parent)
        license_window.title("MIT License")
        license_window.geometry("600x500")
        text_area = scrolledtext.ScrolledText(license_window, wrap=tk.WORD, font=("Segoe UI", 10))
        text_area.pack(expand=True, fill="both", padx=10, pady=10)
        mit_license_text = """MIT License

Copyright (c) 2025 Wanyong Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
        text_area.insert(tk.INSERT, mit_license_text)
        text_area.config(state=tk.DISABLED)