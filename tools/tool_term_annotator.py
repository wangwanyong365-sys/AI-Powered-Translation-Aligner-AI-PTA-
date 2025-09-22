import os
import csv
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class TermEditDialog(tk.Toplevel):

    def __init__(self, parent, title, source_term="", target_term=""):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
    
        body = ttk.Frame(self)
        self.initial_focus = self._create_widgets(body, source_term, target_term)
        body.pack(padx=15, pady=15)
    
        self._create_buttons()
    
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
    
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        self.initial_focus.focus_set()
        self.wait_window(self)
    
    def _create_widgets(self, master, source_term, target_term):
        ttk.Label(master, text="Source Term:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.source_entry = ttk.Entry(master, width=30)
        self.source_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.source_entry.insert(0, source_term)
    
        ttk.Label(master, text="Target Term:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = ttk.Entry(master, width=30)
        self.target_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.target_entry.insert(0, target_term)
        
        return self.source_entry
    
    def _create_buttons(self):
        button_frame = ttk.Frame(self)
        
        ok_button = ttk.Button(button_frame, text="OK", command=self._ok)
        ok_button.pack(side="left", padx=5, pady=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        cancel_button.pack(side="left", padx=5, pady=5)
        
        button_frame.pack()
        
        self.bind("<Return>", self._ok)
        self.bind("<Escape>", self._cancel)
    
    def _ok(self, event=None):
        source = self.source_entry.get().strip()
        target = self.target_entry.get().strip()
        if not source or not target:
            messagebox.showwarning("Input Error", "Source term and target term cannot be empty.", parent=self)
            return
    
        self.result = (source, target)
        self.destroy()
    
    def _cancel(self, event=None):
        self.destroy()

class TermAnnotatorApp:

    def __init__(self, root):
        self.root = root
        self.current_terms = {}
        self.source_file_path = tk.StringVar()
    
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
        self._load_terminologies()
    
    def _setup_window(self):
        self.root.title("Source Text Term Annotator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        
        default_font = ("Segoe UI", 10)
        self.style.configure("TLabel", font=default_font)
        self.style.configure("TButton", font=default_font, padding=5)
        self.style.configure("TEntry", font=default_font)
        self.style.configure("TCombobox", font=default_font)
        
        self.style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"))
        
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.map("Accent.TButton",
                       background=[("active", "#0078D7")],
                       foreground=[("active", "white")])
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
        top_controls_frame = self._create_top_controls(main_frame)
        top_controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
        text_area_frame = self._create_text_areas(main_frame)
        text_area_frame.grid(row=1, column=0, sticky="nsew")
    
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
    
        self.annotate_button = ttk.Button(
            bottom_frame, text="Start Annotation", command=self._start_annotation, style="Accent.TButton"
        )
        self.annotate_button.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
    
        self.status_label = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_label.grid(row=1, column=0, sticky="ew")
        self._update_status("Ready", "gray")
    
    def _create_top_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Settings")
        frame.columnconfigure(1, weight=1)
    
        ttk.Label(frame, text="Select Terminology:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.term_db_combo = ttk.Combobox(frame, state="readonly")
        self.term_db_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.term_db_combo.bind("<<ComboboxSelected>>", self._on_term_db_selected)
    
        ttk.Label(frame, text="Current Terms:").grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.N))
        term_list_frame = ttk.Frame(frame)
        term_list_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        term_list_frame.rowconfigure(0, weight=1)
        term_list_frame.columnconfigure(0, weight=1)
        
        self.term_listbox = tk.Listbox(term_list_frame, font=("Segoe UI", 10), height=5)
        self.term_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(term_list_frame, orient=tk.VERTICAL, command=self.term_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.term_listbox.config(yscrollcommand=scrollbar.set)
        
        frame.rowconfigure(1, weight=1)
    
        term_actions_frame = ttk.Frame(frame)
        term_actions_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_term_button = ttk.Button(term_actions_frame, text="Add", command=self._add_term, state=tk.DISABLED)
        self.add_term_button.pack(side=tk.LEFT, padx=(0, 5))
        self.modify_term_button = ttk.Button(term_actions_frame, text="Modify", command=self._modify_term, state=tk.DISABLED)
        self.modify_term_button.pack(side=tk.LEFT, padx=(0, 5))
        self.delete_term_button = ttk.Button(term_actions_frame, text="Delete", command=self._delete_term, state=tk.DISABLED)
        self.delete_term_button.pack(side=tk.LEFT)
    
        ttk.Label(frame, text="Select Source File:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry = ttk.Entry(frame, textvariable=self.source_file_path, state="readonly")
        entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        browse_button = ttk.Button(frame, text="Browse...", command=self._browse_source_file)
        browse_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.E)
    
        return frame
    
    def _create_text_areas(self, parent):
        frame = ttk.LabelFrame(parent, text="Text Content")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
    
        ttk.Label(frame, text="Source Text").grid(row=0, column=0, padx=5, pady=5)
        source_text_frame = ttk.Frame(frame)
        source_text_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        source_text_frame.rowconfigure(0, weight=1)
        source_text_frame.columnconfigure(0, weight=1)
        
        self.source_text = tk.Text(source_text_frame, wrap=tk.WORD, font=("Segoe UI", 10), undo=True)
        self.source_text.grid(row=0, column=0, sticky="nsew")
        source_scrollbar = ttk.Scrollbar(source_text_frame, orient=tk.VERTICAL, command=self.source_text.yview)
        source_scrollbar.grid(row=0, column=1, sticky="ns")
        self.source_text.config(yscrollcommand=source_scrollbar.set)
    
        ttk.Label(frame, text="Annotated Text").grid(row=0, column=1, padx=5, pady=5)
        annotated_text_frame = ttk.Frame(frame)
        annotated_text_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        annotated_text_frame.rowconfigure(0, weight=1)
        annotated_text_frame.columnconfigure(0, weight=1)
    
        self.annotated_text = tk.Text(annotated_text_frame, wrap=tk.WORD, font=("Segoe UI", 10), undo=True, state=tk.DISABLED)
        self.annotated_text.grid(row=0, column=0, sticky="nsew")
        annotated_scrollbar = ttk.Scrollbar(annotated_text_frame, orient=tk.VERTICAL, command=self.annotated_text.yview)
        annotated_scrollbar.grid(row=0, column=1, sticky="ns")
        self.annotated_text.config(yscrollcommand=annotated_scrollbar.set)
        
        export_button = ttk.Button(frame, text="Export as .txt", command=self._export_annotated_text)
        export_button.grid(row=2, column=1, sticky=tk.E, padx=5, pady=(10, 0))
    
        return frame
    
    def _update_status(self, text, color="black"):
        self.status_label.config(text=text, foreground=color)
        self.root.update_idletasks()
    
    def _load_terminologies(self):
        term_dir = "terminology"
        if not os.path.exists(term_dir):
            os.makedirs(term_dir)
            messagebox.showinfo("Info", f"The 'terminology' folder has been created.\nPlease put your CSV terminology files in it.", parent=self.root)
            self._update_status("Terminology folder created. Please add files.", "blue")
            return
    
        try:
            csv_files = [f for f in os.listdir(term_dir) if f.endswith('.csv')]
            self.term_db_combo['values'] = csv_files
            if csv_files:
                self.term_db_combo.current(0)
                self._on_term_db_selected(None)
                self._update_status(f"Loaded {len(csv_files)} terminologies.", "green")
            else:
                self._update_status("No .csv files found in the 'terminology' folder.", "orange")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading terminologies: {e}", parent=self.root)
            self._update_status(f"Failed to load terminologies: {e}", "red")
    
    def _on_term_db_selected(self, event):
        filename = self.term_db_combo.get()
        if not filename: return
        
        filepath = os.path.join("terminology", filename)
        self.current_terms = {}
        self.term_listbox.delete(0, tk.END)
    
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if len(row) >= 2 and row[0] and row[1]:
                        source_term, target_term = row[0].strip(), row[1].strip()
                        self.current_terms[source_term] = target_term
                    else:
                        print(f"Warning: Skipping invalid row {i+1} in file '{filename}': {row}")
            self._update_term_listbox()
            self._update_status(f"Successfully loaded '{filename}' with {len(self.current_terms)} terms.", "green")
            for btn in [self.add_term_button, self.modify_term_button, self.delete_term_button]:
                btn.config(state=tk.NORMAL)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File '{filename}' not found.", parent=self.root)
            self._update_status(f"File not found: {filename}", "red")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file '{filename}': {e}", parent=self.root)
            self._update_status(f"Failed to read file '{filename}'", "red")
    
    def _update_term_listbox(self):
        self.term_listbox.delete(0, tk.END)
        for source, target in sorted(self.current_terms.items()):
            self.term_listbox.insert(tk.END, f"{source} → {target}")
    
    def _save_current_terms(self):
        filename = self.term_db_combo.get()
        if not filename:
            self._update_status("Error: No terminology file selected for saving.", "red")
            return False
        
        filepath = os.path.join("terminology", filename)
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for source, target in sorted(self.current_terms.items()):
                    writer.writerow([source, target])
            self._update_status(f"Terminology '{filename}' saved automatically.", "green")
            return True
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save terminology '{filename}':\n{e}", parent=self.root)
            self._update_status(f"Failed to save terminology: {e}", "red")
            return False
    
    def _add_term(self):
        dialog = TermEditDialog(self.root, "Add New Term")
        if dialog.result:
            source, target = dialog.result
            if source in self.current_terms:
                if not messagebox.askyesno("Term Exists", f"Source term '{source}' already exists. Do you want to overwrite it?", parent=self.root):
                    return
            
            self.current_terms[source] = target
            if self._save_current_terms():
                self._update_term_listbox()
                self._update_status(f"Added term: {source} → {target}", "green")
    
    def _modify_term(self):
        selected_indices = self.term_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Invalid Operation", "Please select a term to modify from the list first.", parent=self.root)
            return
    
        selected_item = self.term_listbox.get(selected_indices[0])
        try:
            old_source, old_target = [s.strip() for s in selected_item.split('→')]
        except ValueError:
            messagebox.showerror("Format Error", "Could not parse the selected term line.", parent=self.root)
            return
    
        dialog = TermEditDialog(self.root, "Modify Term", old_source, old_target)
        if dialog.result:
            new_source, new_target = dialog.result
            del self.current_terms[old_source]
            self.current_terms[new_source] = new_target
            
            if self._save_current_terms():
                self._update_term_listbox()
                self._update_status(f"Modified term: {new_source} → {new_target}", "green")
            else:
                del self.current_terms[new_source]
                self.current_terms[old_source] = old_target
    
    def _delete_term(self):
        selected_indices = self.term_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Invalid Operation", "Please select a term to delete from the list first.", parent=self.root)
            return
            
        selected_item = self.term_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the following term?\n\n{selected_item}", parent=self.root):
            try:
                source_to_delete = selected_item.split('→')[0].strip()
                if source_to_delete in self.current_terms:
                    del self.current_terms[source_to_delete]
                    if self._save_current_terms():
                        self._update_term_listbox()
                        self._update_status(f"Deleted term: {source_to_delete}", "green")
            except Exception as e:
                messagebox.showerror("Deletion Failed", f"An error occurred during deletion: {e}", parent=self.root)
    
    def _browse_source_file(self):
        filepath = filedialog.askopenfilename(
            title="Please select the source text file",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            parent=self.root  
        )
        if filepath:
            self.source_file_path.set(filepath)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.source_text.delete("1.0", tk.END)
                    self.source_text.insert("1.0", f.read())
                self._update_status(f"Loaded source file: {os.path.basename(filepath)}", "blue")
            except Exception as e:
                messagebox.showerror("File Read Error", f"Could not read file: {e}", parent=self.root)
                self._update_status(f"File read failed: {e}", "red")
    
    def _export_annotated_text(self):
        content = self.annotated_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Invalid Operation", "No annotated text to export.", parent=self.root)
            return
        
        source_path = self.source_file_path.get()
        default_filename = "annotated_text.txt"
        if source_path:
            base, ext = os.path.splitext(os.path.basename(source_path))
            default_filename = f"{base}_annotated{ext}"
    
        filepath = filedialog.asksaveasfilename(
            title="Export Annotated Text",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            initialfile=default_filename,
            parent=self.root
        )
    
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._update_status(f"File successfully exported to: {os.path.basename(filepath)}", "green")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not write to file: {e}", parent=self.root)
                self._update_status(f"File export failed: {e}", "red")
    
    def _perform_annotation(self, source_text, term_dict):
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        annotated_text = source_text
        for source_term in sorted_terms:
            target_term = term_dict[source_term]
            annotation_tag = f"{source_term}{{{target_term}}}"
            annotated_text = annotated_text.replace(source_term, annotation_tag)
        return annotated_text
    
    def _start_annotation(self):
        source_text = self.source_text.get("1.0", tk.END).strip()
        if not self.current_terms:
            messagebox.showwarning("Invalid Operation", "Please select and load a valid terminology first.", parent=self.root)
            return
        if not source_text:
            messagebox.showwarning("Invalid Operation", "Source text content cannot be empty.", parent=self.root)
            return
    
        self.annotate_button.config(state=tk.DISABLED)
        self._update_status("Annotating, please wait...", "orange")
        
        try:
            result = self._perform_annotation(source_text, self.current_terms)
            self.annotated_text.config(state=tk.NORMAL)
            self.annotated_text.delete("1.0", tk.END)
            self.annotated_text.insert("1.0", result)
            self.annotated_text.config(state=tk.DISABLED)
            self._update_status("Annotation complete!", "green")
        except Exception as e:
            self._update_status(f"An error occurred during annotation: {e}", "red")
            messagebox.showerror("Annotation Failed", f"An unknown error occurred: {e}", parent=self.root)
        finally:
            self.annotate_button.config(state=tk.NORMAL)
    
    def _on_closing(self):
        self.root.destroy()