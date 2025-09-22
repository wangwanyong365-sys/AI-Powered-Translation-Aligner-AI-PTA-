import tkinter as tk
from tkinter import ttk, messagebox
from app_utils import save_settings

class APIProviderDialog(tk.Toplevel):
    def __init__(self, parent, provider_name=None, provider_data=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.result = None
        self.original_name = provider_name
        self.provider_data = provider_data.copy() if provider_data else {}
        self.all_provider_names = list(parent.parent.settings['api_providers'].keys())
        self.is_editing = provider_name is not None
        
        self.title("Edit API Provider" if self.is_editing else "Add API Provider")
        self.resizable(False, False)

        self._setup_vars()
        
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(expand=True, fill="both")

        self._create_widgets(main_frame)
        self._load_data()

        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_window(self)

    def _setup_vars(self):
        self.provider_name_var = tk.StringVar()
        self.provider_type_var = tk.StringVar()
        self.base_url_var = tk.StringVar()
        self.azure_endpoint_var = tk.StringVar()
        self.api_version_var = tk.StringVar()
        self.model_names_var = tk.StringVar()

    def _create_widgets(self, parent):
        form_frame = ttk.Frame(parent)
        form_frame.pack(expand=True, fill="both")

        ttk.Label(form_frame, text="Provider Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame, textvariable=self.provider_name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Provider Type:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.type_combo = ttk.Combobox(form_frame, textvariable=self.provider_type_var, state="readonly", values=["Standard", "Azure OpenAI", "Azure DeepSeek"])
        self.type_combo.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.type_combo.bind("<<ComboboxSelected>>", self._on_type_change)

        self.standard_frame = ttk.Frame(form_frame)
        self.standard_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Label(self.standard_frame, text="Base URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.standard_frame, textvariable=self.base_url_var, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.azure_frame = ttk.Frame(form_frame)
        self.azure_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        ttk.Label(self.azure_frame, text="Azure Endpoint:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.azure_frame, textvariable=self.azure_endpoint_var, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.api_version_label = ttk.Label(self.azure_frame, text="API Version:")
        self.api_version_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.api_version_entry = ttk.Entry(self.azure_frame, textvariable=self.api_version_var, width=40)
        self.api_version_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ttk.Label(form_frame, text="Model Names:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(form_frame, textvariable=self.model_names_var, width=40).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Label(form_frame, text="(Comma-separated)").grid(row=4, column=1, sticky="w", padx=5)

        button_frame = ttk.Frame(parent, padding=(0, 10, 0, 0))
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save", command=self._ok).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side="right")

    def _on_type_change(self, event=None):
        ptype = self.provider_type_var.get()
        if ptype == "Standard":
            self.standard_frame.grid()
            self.azure_frame.grid_remove()
        else:
            self.standard_frame.grid_remove()
            self.azure_frame.grid()
            if ptype == "Azure OpenAI":
                self.api_version_label.grid()
                self.api_version_entry.grid()
            else: # Azure DeepSeek
                self.api_version_label.grid_remove()
                self.api_version_entry.grid_remove()

    def _load_data(self):
        if self.is_editing:
            self.provider_name_var.set(self.original_name)
            
            if "base_url" in self.provider_data:
                self.provider_type_var.set("Standard")
                self.base_url_var.set(self.provider_data.get("base_url", ""))
            elif "azure_endpoint" in self.provider_data:
                if "api_version" in self.provider_data:
                    self.provider_type_var.set("Azure OpenAI")
                    self.api_version_var.set(self.provider_data.get("api_version", ""))
                else:
                    self.provider_type_var.set("Azure DeepSeek")
                self.azure_endpoint_var.set(self.provider_data.get("azure_endpoint", ""))
            
            model_names = self.provider_data.get("model_names", [])
            self.model_names_var.set(", ".join(model_names))
        else:
            self.provider_type_var.set("Standard")
        
        self._on_type_change()

    def _ok(self):
        name = self.provider_name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Provider Name cannot be empty.", parent=self)
            return

        if name != self.original_name and name in self.all_provider_names:
            messagebox.showerror("Error", "A provider with this name already exists.", parent=self)
            return

        new_data = {}
        ptype = self.provider_type_var.get()
        if ptype == "Standard":
            new_data["base_url"] = self.base_url_var.get().strip()
        elif ptype == "Azure OpenAI":
            new_data["azure_endpoint"] = self.azure_endpoint_var.get().strip()
            new_data["api_version"] = self.api_version_var.get().strip()
        elif ptype == "Azure DeepSeek":
            new_data["azure_endpoint"] = self.azure_endpoint_var.get().strip()
        
        models_str = self.model_names_var.get().strip()
        new_data["model_names"] = [m.strip() for m in models_str.split(',') if m.strip()]
        new_data["api_keys"] = self.provider_data.get("api_keys", {})

        self.result = (name, new_data)
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


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
        
        self.tab_api_perf = ttk.Frame(notebook, padding="10")
        self.tab_providers = ttk.Frame(notebook, padding="10")
        self.tab_output = ttk.Frame(notebook, padding="10")
        
        notebook.add(self.tab_api_perf, text=" API & Performance ")
        notebook.add(self.tab_providers, text=" API Providers ")
        notebook.add(self.tab_output, text=" File Output ")
        
        self._create_api_performance_settings(self.tab_api_perf)
        self._create_api_providers_settings(self.tab_providers)
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

    def _create_api_providers_settings(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)

        list_frame = ttk.Frame(parent_frame)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.providers_listbox = tk.Listbox(list_frame, height=10)
        self.providers_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.providers_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.providers_listbox.config(yscrollcommand=scrollbar.set)

        self._populate_providers_list()

        button_frame = ttk.Frame(parent_frame)
        button_frame.grid(row=0, column=1, sticky="ns")

        ttk.Button(button_frame, text="Add...", command=self._add_provider).pack(pady=2, fill="x")
        ttk.Button(button_frame, text="Modify...", command=self._modify_provider).pack(pady=2, fill="x")
        ttk.Button(button_frame, text="Delete", command=self._delete_provider).pack(pady=2, fill="x")

    def _populate_providers_list(self):
        self.providers_listbox.delete(0, tk.END)
        providers = sorted(self.parent.settings['api_providers'].keys())
        for provider in providers:
            self.providers_listbox.insert(tk.END, provider)

    def _add_provider(self):
        dialog = APIProviderDialog(self)
        if dialog.result:
            name, data = dialog.result
            self.parent.settings['api_providers'][name] = data
            self._populate_providers_list()

    def _modify_provider(self):
        selected_indices = self.providers_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a provider to modify.", parent=self)
            return
        
        name = self.providers_listbox.get(selected_indices[0])
        data = self.parent.settings['api_providers'][name]

        dialog = APIProviderDialog(self, provider_name=name, provider_data=data)
        if dialog.result:
            new_name, new_data = dialog.result
            del self.parent.settings['api_providers'][name]
            self.parent.settings['api_providers'][new_name] = new_data
            self._populate_providers_list()

    def _delete_provider(self):
        selected_indices = self.providers_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a provider to delete.", parent=self)
            return

        name = self.providers_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the provider '{name}'?", parent=self):
            del self.parent.settings['api_providers'][name]
            self._populate_providers_list()

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
            self.parent._refresh_api_settings_ui()
            self.destroy()
        except tk.TclError:
            messagebox.showerror("Invalid Input", "Please ensure all values are valid integers.", parent=self)