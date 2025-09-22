import tkinter as tk
from tkinter import ttk, messagebox
from app_utils import save_settings

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.transient(parent)
        self.title("Options")
        self.grab_set()
        self.resizable(False, False)

        self._create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(expand=True, fill="both")
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill="both", pady=5)
        
        self.tab_api = ttk.Frame(notebook, padding="10")
        self.tab_output = ttk.Frame(notebook, padding="10")
        
        notebook.add(self.tab_api, text=" API & Performance ")
        notebook.add(self.tab_output, text=" File Output ")
        
        self._create_api_performance_settings(self.tab_api)
        self._create_file_output_settings(self.tab_output)
        
        self._create_buttons()

    def _create_api_performance_settings(self, parent_frame):
        self.max_tokens = tk.IntVar(value=self.parent.settings.get("max_tokens", 8000))
        self.context_before = tk.IntVar(value=self.parent.settings.get("context_before", 1))
        self.context_after = tk.IntVar(value=self.parent.settings.get("context_after", 1))
        self.retry_attempts = tk.IntVar(value=self.parent.settings.get("retry_attempts", 3))
        self.paragraph_timeout = tk.IntVar(value=self.parent.settings.get("paragraph_timeout", 300))
        self.request_interval = tk.IntVar(value=self.parent.settings.get("request_interval", 5))

        ttk.Label(parent_frame, text="Max Tokens:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=self.max_tokens, width=15).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(parent_frame, text="Previous Paragraphs (Context):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=self.context_before, width=15).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(parent_frame, text="Next Paragraphs (Context):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=self.context_after, width=15).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(parent_frame, text="Retry Attempts on Failure:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=self.retry_attempts, width=15).grid(row=3, column=1, sticky="w", padx=5, pady=5)
    
        ttk.Label(parent_frame, text="Retry on Timeout (seconds):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=self.paragraph_timeout, width=15).grid(row=4, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(parent_frame, text="Request Interval (seconds):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(parent_frame, textvariable=self.request_interval, width=15).grid(row=5, column=1, sticky="w", padx=5, pady=5)

    def _create_file_output_settings(self, parent_frame):
        self.output_format_var = tk.StringVar(value=self.parent.settings.get("output_format", "Both"))
        self.output_location_var = tk.StringVar(value=self.parent.settings.get("output_location", "Subfolder"))

        ttk.Label(parent_frame, text="Output File Format:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        format_combo = ttk.Combobox(parent_frame, textvariable=self.output_format_var, state="readonly", width=25)
        format_combo['values'] = ("Table (.xlsx) and Text (.txt)", "Table (.xlsx) only", "Text (.txt) only")
        format_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        self.format_map = {
            "Table (.xlsx) and Text (.txt)": "Both",
            "Table (.xlsx) only": "Excel",
            "Text (.txt) only": "Text"
        }
        self.reverse_format_map = {v: k for k, v in self.format_map.items()}
        format_combo.set(self.reverse_format_map.get(self.output_format_var.get()))

        ttk.Label(parent_frame, text="Output Location:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        location_combo = ttk.Combobox(parent_frame, textvariable=self.output_location_var, state="readonly", width=25)
        location_combo['values'] = ("In a new subfolder", "In the source file's directory")
        location_combo.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        self.location_map = {
            "In a new subfolder": "Subfolder",
            "In the source file's directory": "Source Root"
        }
        self.reverse_location_map = {v: k for k, v in self.location_map.items()}
        location_combo.set(self.reverse_location_map.get(self.output_location_var.get()))

    def _create_buttons(self):
        button_frame = ttk.Frame(self, padding="10")
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save", command=self._save_and_close).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right")
        
    def _save_and_close(self):
        try:
            new_interval = self.request_interval.get()
            if new_interval < 0:
                messagebox.showerror("Invalid Input", "Request interval cannot be negative.", parent=self)
                return
            
            self.parent.settings['max_tokens'] = self.max_tokens.get()
            self.parent.settings['context_before'] = self.context_before.get()
            self.parent.settings['context_after'] = self.context_after.get()
            self.parent.settings['retry_attempts'] = self.retry_attempts.get()
            self.parent.settings['paragraph_timeout'] = self.paragraph_timeout.get()
            self.parent.settings['request_interval'] = new_interval
            
            selected_format = self.format_map.get(self.output_format_var.get(), "Both")
            self.parent.settings['output_format'] = selected_format
            
            selected_location = self.location_map.get(self.output_location_var.get(), "Subfolder")
            self.parent.settings['output_location'] = selected_location
            
            save_settings(self.parent.settings)
            messagebox.showinfo("Success", "Settings saved.", parent=self)
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please ensure all values are valid integers.", parent=self)