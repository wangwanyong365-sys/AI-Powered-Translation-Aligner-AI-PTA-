

import os
import re
import csv
import json
import threading
import datetime
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext

import openai
import pandas as pd



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
        ttk.Label(master, text="源术语:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.source_entry = ttk.Entry(master, width=30)
        self.source_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.source_entry.insert(0, source_term)
    
        ttk.Label(master, text="目标术语:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = ttk.Entry(master, width=30)
        self.target_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.target_entry.insert(0, target_term)
        
        return self.source_entry
    
    def _create_buttons(self):
        button_frame = ttk.Frame(self)
        
        ok_button = ttk.Button(button_frame, text="确定", command=self._ok, style="Accent.TButton")
        ok_button.pack(side="left", padx=5, pady=5)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=self._cancel)
        cancel_button.pack(side="left", padx=5, pady=5)
        
        button_frame.pack()
        
        self.bind("<Return>", self._ok)
        self.bind("<Escape>", self._cancel)
    
    def _ok(self, event=None):
        source = self.source_entry.get().strip()
        target = self.target_entry.get().strip()
        if not source or not target:
            messagebox.showwarning("输入错误", "源术语和目标术语均不能为空。", parent=self)
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
        """配置主窗口属性"""
        self.root.title("源文本术语标注")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """配置 ttk 控件的样式和主题"""
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.title_font = ("微软雅黑", 12, "bold")
        self.default_font = ("微软雅黑", 10)
        self.status_font = ("微软雅黑", 9)
        self.accent_font = ("微软雅黑", 11, "bold")
        self.style.configure("TLabel", font=self.default_font)
        self.style.configure("TButton", font=self.default_font, padding=5)
        self.style.configure("TEntry", font=self.default_font)
        self.style.configure("TCombobox", font=self.default_font)
        self.style.configure("TLabelframe", font=self.default_font, padding=10)
        self.style.configure("TLabelframe.Label", font=self.title_font, foreground="#333")
        self.style.configure("Accent.TButton", font=self.accent_font, padding=(10, 8), background="#0078D7", foreground="white")
        self.style.map("Accent.TButton", background=[("active", "#005a9e"), ("pressed", "#004578"), ("disabled", "#a0a0a0")])
        self.style.configure("Status.TLabel", font=self.status_font, padding=5)
        self.style.configure("Ready.Status.TLabel", foreground="gray")
        self.style.configure("Info.Status.TLabel", foreground="blue")
        self.style.configure("Processing.Status.TLabel", foreground="orange")
        self.style.configure("Success.Status.TLabel", foreground="green")
        self.style.configure("Error.Status.TLabel", foreground="red")
    
    def _create_widgets(self):
        """创建并布局所有界面控件"""
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
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
            bottom_frame, text="开始标注", style="Accent.TButton", command=self._start_annotation
        )
        self.annotate_button.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), ipady=5)
    
        self.status_label = ttk.Label(
            main_frame, text="准备就绪", anchor=tk.W, style="Ready.Status.TLabel"
        )
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_top_controls(self, parent):
        """创建顶部用于选择术语库和源文件的控件"""
        frame = ttk.LabelFrame(parent, text="设置")
        frame.columnconfigure(1, weight=1)
    
        ttk.Label(frame, text="选择术语库:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.term_db_combo = ttk.Combobox(frame, state="readonly", font=self.default_font)
        self.term_db_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.term_db_combo.bind("<<ComboboxSelected>>", self._on_term_db_selected)
    
        ttk.Label(frame, text="当前术语:").grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.N))
        term_list_frame = ttk.Frame(frame)
        term_list_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        term_list_frame.rowconfigure(0, weight=1)
        term_list_frame.columnconfigure(0, weight=1)
        
        self.term_listbox = tk.Listbox(term_list_frame, font=self.default_font, height=5)
        self.term_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(term_list_frame, orient=tk.VERTICAL, command=self.term_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.term_listbox.config(yscrollcommand=scrollbar.set)
        
        frame.rowconfigure(1, weight=1)
    
        term_actions_frame = ttk.Frame(frame)
        term_actions_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_term_button = ttk.Button(term_actions_frame, text="增加", command=self._add_term, state=tk.DISABLED)
        self.add_term_button.pack(side=tk.LEFT, padx=(0, 5))
        self.modify_term_button = ttk.Button(term_actions_frame, text="修改", command=self._modify_term, state=tk.DISABLED)
        self.modify_term_button.pack(side=tk.LEFT, padx=(0, 5))
        self.delete_term_button = ttk.Button(term_actions_frame, text="删除", command=self._delete_term, state=tk.DISABLED)
        self.delete_term_button.pack(side=tk.LEFT)
    
        ttk.Label(frame, text="选择源文件:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry = ttk.Entry(frame, textvariable=self.source_file_path, state="readonly")
        entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        browse_button = ttk.Button(frame, text="浏览...", command=self._browse_source_file)
        browse_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.E)
    
        return frame
    
    def _create_text_areas(self, parent):
        """创建源文本和标注后文本的显示区域"""
        frame = ttk.LabelFrame(parent, text="文本内容")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
    
        ttk.Label(frame, text="源文本", font=self.title_font).grid(row=0, column=0, padx=5, pady=5)
        source_text_frame = ttk.Frame(frame)
        source_text_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        source_text_frame.rowconfigure(0, weight=1)
        source_text_frame.columnconfigure(0, weight=1)
        
        self.source_text = tk.Text(source_text_frame, wrap=tk.WORD, font=self.default_font, undo=True)
        self.source_text.grid(row=0, column=0, sticky="nsew")
        source_scrollbar = ttk.Scrollbar(source_text_frame, orient=tk.VERTICAL, command=self.source_text.yview)
        source_scrollbar.grid(row=0, column=1, sticky="ns")
        self.source_text.config(yscrollcommand=source_scrollbar.set)
    
        ttk.Label(frame, text="标注后文本", font=self.title_font).grid(row=0, column=1, padx=5, pady=5)
        annotated_text_frame = ttk.Frame(frame)
        annotated_text_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        annotated_text_frame.rowconfigure(0, weight=1)
        annotated_text_frame.columnconfigure(0, weight=1)
    
        self.annotated_text = tk.Text(annotated_text_frame, wrap=tk.WORD, font=self.default_font, undo=True, state=tk.DISABLED)
        self.annotated_text.grid(row=0, column=0, sticky="nsew")
        annotated_scrollbar = ttk.Scrollbar(annotated_text_frame, orient=tk.VERTICAL, command=self.annotated_text.yview)
        annotated_scrollbar.grid(row=0, column=1, sticky="ns")
        self.annotated_text.config(yscrollcommand=annotated_scrollbar.set)
        
        export_button = ttk.Button(frame, text="导出为 .txt", command=self._export_annotated_text)
        export_button.grid(row=2, column=1, sticky=tk.E, padx=5, pady=(10, 0))
    
        return frame
    
    def _update_status(self, text, level="info"):
        """更新状态栏的文本和颜色。"""
        style_map = {
            "ready": "Ready.Status.TLabel", "info": "Info.Status.TLabel",
            "processing": "Processing.Status.TLabel", "success": "Success.Status.TLabel",
            "error": "Error.Status.TLabel"
        }
        self.status_label.config(text=text, style=style_map.get(level.lower(), "Info.Status.TLabel"))
        self.root.update_idletasks()
    
    def _load_terminologies(self):
        """扫描 'terminology' 文件夹并加载术语库列表"""
        term_dir = "terminology"
        if not os.path.exists(term_dir):
            os.makedirs(term_dir)
            messagebox.showinfo("提示", f"已创建 'terminology' 文件夹。\n请将您的 CSV 术语库放入其中。", parent=self.root)
            self._update_status("术语库文件夹已创建，请添加文件。", level="info")
            return
    
        try:
            csv_files = [f for f in os.listdir(term_dir) if f.endswith('.csv')]
            self.term_db_combo['values'] = csv_files
            if csv_files:
                self.term_db_combo.current(0)
                self._on_term_db_selected(None)
                self._update_status(f"已加载 {len(csv_files)} 个术语库。", level="info")
            else:
                self._update_status("在 'terminology' 文件夹中未找到任何 .csv 文件。", level="error")
        except Exception as e:
            messagebox.showerror("错误", f"加载术语库时出错: {e}", parent=self.root)
            self._update_status(f"加载术语库失败: {e}", level="error")
    
    def _on_term_db_selected(self, event):
        """当用户在下拉菜单中选择一个术语库时调用"""
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
                        print(f"警告：跳过文件 '{filename}' 中的无效行 {i+1}: {row}")
            self._update_term_listbox()
            self._update_status(f"已成功加载术语库 '{filename}'，共 {len(self.current_terms)} 个术语。", level="success")
            for btn in [self.add_term_button, self.modify_term_button, self.delete_term_button]:
                btn.config(state=tk.NORMAL)
        except FileNotFoundError:
            messagebox.showerror("错误", f"文件 '{filename}' 未找到。", parent=self.root)
            self._update_status(f"文件未找到: {filename}", level="error")
        except Exception as e:
            messagebox.showerror("错误", f"读取文件 '{filename}' 时出错: {e}", parent=self.root)
            self._update_status(f"读取文件 '{filename}' 失败", level="error")
    
    def _update_term_listbox(self):
        """根据 current_terms 字典刷新 Listbox 内容"""
        self.term_listbox.delete(0, tk.END)
        for source, target in sorted(self.current_terms.items()):
            self.term_listbox.insert(tk.END, f"{source} → {target}")
    
    def _save_current_terms(self):
        """将当前的术语字典保存回对应的 CSV 文件"""
        filename = self.term_db_combo.get()
        if not filename:
            self._update_status("错误：没有选择任何术语库文件进行保存。", level="error")
            return False
        
        filepath = os.path.join("terminology", filename)
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for source, target in sorted(self.current_terms.items()):
                    writer.writerow([source, target])
            self._update_status(f"术语库 '{filename}' 已自动保存。", level="success")
            return True
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存术语库 '{filename}':\n{e}", parent=self.root)
            self._update_status(f"保存术语库失败: {e}", level="error")
            return False
    
    def _add_term(self):
        """打开对话框添加新术语"""
        dialog = TermEditDialog(self.root, "增加新术语")
        if dialog.result:
            source, target = dialog.result
            if source in self.current_terms:
                if not messagebox.askyesno("术语已存在", f"源术语 '{source}' 已存在，要覆盖它吗？", parent=self.root):
                    return
            
            self.current_terms[source] = target
            if self._save_current_terms():
                self._update_term_listbox()
                self._update_status(f"已添加术语：{source} → {target}", level="success")
    
    def _modify_term(self):
        """修改选中的术语"""
        selected_indices = self.term_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("操作无效", "请先在列表中选择一个要修改的术语。", parent=self.root)
            return
    
        selected_item = self.term_listbox.get(selected_indices[0])
        try:
            old_source, old_target = [s.strip() for s in selected_item.split('→')]
        except ValueError:
            messagebox.showerror("格式错误", "无法解析选中的术语行。", parent=self.root)
            return
    
        dialog = TermEditDialog(self.root, "修改术语", old_source, old_target)
        if dialog.result:
            new_source, new_target = dialog.result
            del self.current_terms[old_source]
            self.current_terms[new_source] = new_target
            
            if self._save_current_terms():
                self._update_term_listbox()
                self._update_status(f"已修改术语：{new_source} → {new_target}", level="success")
            else:
                del self.current_terms[new_source]
                self.current_terms[old_source] = old_target
    
    def _delete_term(self):
        """删除选中的术语"""
        selected_indices = self.term_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("操作无效", "请先在列表中选择一个要删除的术语。", parent=self.root)
            return
            
        selected_item = self.term_listbox.get(selected_indices[0])
        if messagebox.askyesno("确认删除", f"您确定要删除以下术语吗？\n\n{selected_item}", parent=self.root):
            try:
                source_to_delete = selected_item.split('→')[0].strip()
                if source_to_delete in self.current_terms:
                    del self.current_terms[source_to_delete]
                    if self._save_current_terms():
                        self._update_term_listbox()
                        self._update_status(f"已删除术语: {source_to_delete}", level="success")
            except Exception as e:
                messagebox.showerror("删除失败", f"删除时发生错误: {e}", parent=self.root)
    
    def _browse_source_file(self):
        """打开文件对话框让用户选择源文本文件"""

        filepath = filedialog.askopenfilename(
            title="请选择源文本文件",
            filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*")),
            parent=self.root  
        )
        if filepath:
            self.source_file_path.set(filepath)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.source_text.delete("1.0", tk.END)
                    self.source_text.insert("1.0", f.read())
                self._update_status(f"已加载源文件: {os.path.basename(filepath)}", level="info")
            except Exception as e:
                messagebox.showerror("文件读取错误", f"无法读取文件: {e}", parent=self.root)
                self._update_status(f"文件读取失败: {e}", level="error")
    
    def _export_annotated_text(self):
        """将标注后的文本导出为 txt 文件"""
        content = self.annotated_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("操作无效", "没有可导出的标注后文本。", parent=self.root)
            return
        
        source_path = self.source_file_path.get()
        default_filename = "annotated_text.txt"
        if source_path:
            base, ext = os.path.splitext(os.path.basename(source_path))
            default_filename = f"{base}_annotated{ext}"
    
        filepath = filedialog.asksaveasfilename(
            title="导出标注后的文本",
            defaultextension=".txt",
            filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*")),
            initialfile=default_filename,
            parent=self.root
        )
    
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._update_status(f"文件已成功导出到: {os.path.basename(filepath)}", level="success")
            except Exception as e:
                messagebox.showerror("导出失败", f"无法写入文件: {e}", parent=self.root)
                self._update_status(f"文件导出失败: {e}", level="error")
    
    def _perform_annotation(self, source_text, term_dict):
        """核心标注逻辑。按术语长度从长到短的顺序进行替换。"""
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        annotated_text = source_text
        for source_term in sorted_terms:
            target_term = term_dict[source_term]
            annotation_tag = f"{source_term}{{{target_term}}}"
            annotated_text = annotated_text.replace(source_term, annotation_tag)
        return annotated_text
    
    def _start_annotation(self):
        """开始执行标注过程"""
        source_text = self.source_text.get("1.0", tk.END).strip()
        if not self.current_terms:
            messagebox.showwarning("操作无效", "请先选择并加载一个有效的术语库。", parent=self.root)
            return
        if not source_text:
            messagebox.showwarning("操作无效", "源文本内容不能为空。", parent=self.root)
            return
    
        self.annotate_button.config(state=tk.DISABLED)
        self._update_status("正在标注中，请稍候...", level="processing")
        
        try:
            result = self._perform_annotation(source_text, self.current_terms)
            self.annotated_text.config(state=tk.NORMAL)
            self.annotated_text.delete("1.0", tk.END)
            self.annotated_text.insert("1.0", result)
            self.annotated_text.config(state=tk.DISABLED)
            self._update_status("标注完成！", level="success")
        except Exception as e:
            self._update_status(f"标注过程中发生错误: {e}", level="error")
            messagebox.showerror("标注失败", f"发生未知错误: {e}", parent=self.root)
        finally:
            self.annotate_button.config(state=tk.NORMAL)
    
    def _on_closing(self):
        """处理窗口关闭事件"""
        self.root.destroy()





SETTINGS_FILE = "settings.json"
ERROR_LOG_FILE = "error_log.txt"
API_PROVIDERS = {
    "DeepSeek": "https://api.deepseek.com",
    "SiliconFlow": "https://api.siliconflow.cn/v1",
    "OpenAI": "https://api.openai.com/v1"
}


def log_error(error_message):
    """将错误信息追加到日志文件。"""
    try:
        with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_error = traceback.format_exc()
            f.write(f"--- {timestamp} ---\n")
            f.write(f"{error_message}\n")
            f.write(f"Traceback:\n{full_error}\n\n")
    except Exception as e:
        print(f"写入错误日志失败: {e}")


def load_settings():
    """从 settings.json 加载所有设置。如果文件不存在或无效，则返回默认设置。"""
    default_settings = {

        "max_tokens": 8000,
        "context_before": 1,
        "context_after": 1,
        "api_keys": {},
        "model_names": ["deepseek-chat", "deepseek-coder"],
        "prompts": {
            "默认翻译 Prompt": (
                "You are a professional, accurate, and faithful translator. "
                "Please translate the text from the \"[Text to Translate]\" section into American English.\n"
                "Directly output the translated content of that section ONLY. "
                "Do not provide any explanations, annotations, or any other extraneous text.\n\n"
                "{context}"
            )
        }
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            for key, value in default_settings.items():
                settings.setdefault(key, value)
            return settings
    except (json.JSONDecodeError, Exception) as e:
        log_error(f"加载 settings.json 失败: {e}. 将使用默认设置。")
        return default_settings

def save_settings(settings):
    """将设置字典保存到 settings.json。"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("错误", f"保存设置文件失败: {e}")
        log_error(f"保存 settings.json 失败: {e}")


def split_text_into_paragraphs(text):
    """将文本按一个或多个空行拆分为段落列表。"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def translate_single_paragraph(client, model_name, full_prompt, max_tokens):
    """发送单个请求到 AI 进行翻译。"""
    try:
        lines = full_prompt.split('\n', 1)
        system_message = lines[0]
        user_message = lines[1] if len(lines) > 1 else ""
        
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            stream=False,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_message = f"API 调用失败: {e}"
        log_error(error_message)
        return f"【翻译失败: {str(e)[:50]}...】"


class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.selected_files = []
        self.annotator_window = None
    
        self._setup_style()
        self._setup_ui()
        self._post_ui_setup()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """关闭窗口前保存设置。"""
        self.settings['max_tokens'] = self.max_tokens_var.get()
        self.settings['context_before'] = self.context_before_var.get()
        self.settings['context_after'] = self.context_after_var.get()
        save_settings(self.settings)
        self.destroy()
    
    def _setup_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Accent.TButton", font=("微软雅黑", 12, "bold"), padding=(10, 5))
        self.style.map("Accent.TButton", background=[("active", "#005f9e"), ("!disabled", "#0078d4")], foreground=[("!disabled", "white")])
        self.style.configure("TLabelFrame.Label", font=("微软雅黑", 11, "bold"))
    
    def _setup_ui(self):
        self.title("AI-Powered Translation Aligner (AI-PTA) v0.7")
        self.geometry("800x850") 
        self.minsize(600, 700)
    
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="工具(Tools)", menu=tools_menu)
        tools_menu.add_command(label="术语标注器(Term Annotator)", command=self._open_annotator)
    
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="帮助(Help)", menu=help_menu)
        help_menu.add_command(label="关于(About)", command=self._show_about_info)
        help_menu.add_command(label="查看许可证(License)", command=self._show_license_info)
    
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
        files_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        files_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        self.file_listbox = tk.Listbox(files_frame, height=5, font=("微软雅黑", 10))
        self.file_listbox.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        browse_button = ttk.Button(files_frame, text="选择 TXT 文件...", command=self._on_browse_files)
        browse_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="e")
    
        settings_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="10")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=5)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1) 
    
        ttk.Label(settings_frame, text="最大 Token 数:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.max_tokens_var = tk.IntVar(value=self.settings.get("max_tokens", 8000))
        ttk.Entry(settings_frame, textvariable=self.max_tokens_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
        ttk.Label(settings_frame, text="上文段落数:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.context_before_var = tk.IntVar(value=self.settings.get("context_before", 1))
        ttk.Entry(settings_frame, textvariable=self.context_before_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(settings_frame, text="下文段落数:").grid(row=1, column=2, sticky="w", padx=20, pady=5)
        self.context_after_var = tk.IntVar(value=self.settings.get("context_after", 1))
        ttk.Entry(settings_frame, textvariable=self.context_after_var, width=10).grid(row=1, column=3, sticky="w", padx=5, pady=5)
    
        ttk.Label(settings_frame, text="API 服务商:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.api_provider_var = tk.StringVar(value="DeepSeek")
        ttk.Combobox(settings_frame, textvariable=self.api_provider_var, values=list(API_PROVIDERS.keys()), state="readonly").grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
        ttk.Label(settings_frame, text="API Key:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        api_key_frame = ttk.Frame(settings_frame)
        api_key_frame.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        api_key_frame.columnconfigure(0, weight=1)
        self.api_key_var = tk.StringVar()
        self.api_key_combo = ttk.Combobox(api_key_frame, textvariable=self.api_key_var)
        self.api_key_combo.grid(row=0, column=0, sticky="ew")
        self.api_key_combo.bind("<<ComboboxSelected>>", self._on_api_key_select)
        self.api_key_combo.bind("<KeyRelease>", self._on_api_key_typed) 
        api_btn_frame = ttk.Frame(api_key_frame)
        api_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(api_btn_frame, text="保存", command=self._save_api_key, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(api_btn_frame, text="删除", command=self._delete_api_key, width=5).pack(side=tk.LEFT, padx=2)
    
        ttk.Label(settings_frame, text="模型名称 (可选):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        model_frame = ttk.Frame(settings_frame)
        model_frame.grid(row=4, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        model_frame.columnconfigure(0, weight=1)
        self.model_name_var = tk.StringVar()
        self.model_name_combo = ttk.Combobox(model_frame, textvariable=self.model_name_var)
        self.model_name_combo.grid(row=0, column=0, sticky="ew")
        model_btn_frame = ttk.Frame(model_frame)
        model_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(model_btn_frame, text="保存", command=self._save_model_name, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(model_btn_frame, text="删除", command=self._delete_model_name, width=5).pack(side=tk.LEFT, padx=2)
    
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt 管理", padding="10")
        prompt_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)
        prompt_selection_frame = ttk.Frame(prompt_frame)
        prompt_selection_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        prompt_selection_frame.columnconfigure(1, weight=1)
        ttk.Label(prompt_selection_frame, text="选择 Prompt:").grid(row=0, column=0, padx=(0, 5))
        self.prompt_var = tk.StringVar()
        self.prompt_combo = ttk.Combobox(prompt_selection_frame, textvariable=self.prompt_var, state="readonly")
        self.prompt_combo.grid(row=0, column=1, sticky="ew")
        self.prompt_combo.bind("<<ComboboxSelected>>", self._on_prompt_select)
        btn_frame = ttk.Frame(prompt_selection_frame)
        btn_frame.grid(row=0, column=2, padx=(10, 0))
        ttk.Button(btn_frame, text="添加", command=self._add_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="保存", command=self._save_current_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除", command=self._delete_prompt).pack(side=tk.LEFT, padx=2)
        self.prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=8, font=("微软雅黑", 10))
        self.prompt_text.grid(row=1, column=0, sticky="nsew")
        prompt_scrollbar = ttk.Scrollbar(prompt_frame, orient=tk.VERTICAL, command=self.prompt_text.yview)
        prompt_scrollbar.grid(row=1, column=1, sticky="ns")
        self.prompt_text.config(yscrollcommand=prompt_scrollbar.set)
    
        self.start_button = ttk.Button(main_frame, text="开始处理", style="Accent.TButton", command=self._start_processing)
        self.start_button.grid(row=3, column=0, pady=10, ipady=5, sticky="ew")
        
        self.status_label = ttk.Label(self, text="准备就绪", padding="5 2", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_status("准备就绪", "gray")
    
    def _open_annotator(self):
        """打开术语标注器窗口。"""
        if self.annotator_window and self.annotator_window.winfo_exists():
            self.annotator_window.lift()
            self.annotator_window.focus_force()
            return
        self.annotator_window = tk.Toplevel(self)
        app = TermAnnotatorApp(self.annotator_window)

    def _post_ui_setup(self):
        """UI 创建完成后，加载数据并初始化控件状态"""
        self._update_prompt_combo()
        if self.settings['prompts']:
            first_prompt_name = list(self.settings['prompts'].keys())[0]
            self.prompt_var.set(first_prompt_name)
            self._on_prompt_select()
        
        self._update_api_key_combo()
        self._update_model_name_combo()
        if self.settings['model_names']:
            self.model_name_var.set(self.settings['model_names'][0])
    
    def _show_about_info(self):
        messagebox.showinfo(
            "关于",
            "王万涌\n\n"
            "Wanyong Wang\n"
            "Department of Language Science and Technology (LST)\n"
            "The Hong Kong Polytechnic University\n"
            "Kowloon, Hong Kong, China\n"
            "Email: wangwanyong365@hotmail.com"
        )
    
    def _show_license_info(self):
        license_window = tk.Toplevel(self)
        license_window.title("MIT 许可证 (MIT License)")
        license_window.geometry("600x500")
        text_area = scrolledtext.ScrolledText(license_window, wrap=tk.WORD, font=("微软雅黑", 10))
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

    def _get_current_api_key(self):
        displayed_text = self.api_key_var.get().strip()
        return self.settings['api_keys'].get(displayed_text, displayed_text)
    
    def _update_api_key_combo(self):
        self.api_key_combo['values'] = list(self.settings['api_keys'].keys())
    
    def _on_api_key_select(self, event=None):
        selected_name = self.api_key_combo.get()
        if selected_name in self.settings['api_keys']:
            self.api_key_var.set(selected_name)
            self.api_key_combo.config(show="")
    
    def _on_api_key_typed(self, event=None):
        current_text = self.api_key_var.get()
        self.api_key_combo.config(show="" if current_text in self.settings['api_keys'] else "●")
    
    def _save_api_key(self):
        key_or_name = self.api_key_var.get().strip()
        if not key_or_name: return messagebox.showwarning("警告", "API Key 不能为空。")
        if key_or_name in self.settings['api_keys']: return messagebox.showinfo("提示", "这是一个已保存的 API Key 名称，无需重复保存。")
        
        name = simpledialog.askstring("保存 API Key", "请输入该 Key 的一个易记名称:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.settings['api_keys'] and not messagebox.askyesno("覆盖确认", f"名称 '{name}' 已存在。要用新 Key 覆盖它吗？"):
                return
            self.settings['api_keys'][name] = key_or_name
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_combo.set(name)
            self.api_key_combo.config(show="")
            messagebox.showinfo("成功", f"API Key '{name}' 已保存。")
    
    def _delete_api_key(self):
        name = self.api_key_combo.get()
        if not name or name not in self.settings['api_keys']: return messagebox.showerror("错误", "请先选择一个要删除的 API Key。")
        if messagebox.askyesno("确认删除", f"确定要删除 API Key '{name}' 吗？"):
            del self.settings['api_keys'][name]
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_var.set("")
            self.api_key_combo.config(show="●")
    
    def _update_model_name_combo(self):
        self.model_name_combo['values'] = self.settings.get('model_names', [])
    
    def _save_model_name(self):
        name = self.model_name_var.get().strip()
        if not name: return messagebox.showwarning("警告", "模型名称不能为空。")
        if name not in self.settings['model_names']:
            self.settings['model_names'].append(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            messagebox.showinfo("成功", f"模型 '{name}' 已保存到列表。")
        else:
            messagebox.showinfo("提示", f"模型 '{name}' 已存在于列表中。")
    
    def _delete_model_name(self):
        name = self.model_name_var.get().strip()
        if not name or name not in self.settings['model_names']: return messagebox.showerror("错误", "当前输入的模型名称不在列表中。")
        if messagebox.askyesno("确认删除", f"确定要从列表中删除模型 '{name}' 吗？"):
            self.settings['model_names'].remove(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            self.model_name_var.set("")
    
    def _update_prompt_combo(self):
        self.prompt_combo['values'] = list(self.settings['prompts'].keys())
    
    def _on_prompt_select(self, event=None):
        name = self.prompt_var.get()
        if name in self.settings['prompts']:
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", self.settings['prompts'][name])
    
    def _add_prompt(self):
        name = simpledialog.askstring("新 Prompt", "请输入新 Prompt 的名称:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.settings['prompts']: return messagebox.showerror("错误", "该名称已存在！")
            self.settings['prompts'][name] = f"这是 '{name}' 的 Prompt。\n请在此输入指令，并使用 {{context}} 作为占位符。"
            save_settings(self.settings)
            self._update_prompt_combo()
            self.prompt_var.set(name)
            self._on_prompt_select()
    
    def _save_current_prompt(self):
        name = self.prompt_var.get()
        if not name: return messagebox.showerror("错误", "没有选中的 Prompt 可保存。")
        content = self.prompt_text.get("1.0", tk.END).strip()
        if "{context}" not in content and not messagebox.askyesno("警告", "当前 Prompt 未找到占位符 '{context}'。\n这可能导致无法正确插入原文和上下文。\n是否仍要保存？"):
            return
        self.settings['prompts'][name] = content
        save_settings(self.settings)
        messagebox.showinfo("成功", f"Prompt '{name}' 已保存。")
    
    def _delete_prompt(self):
        name = self.prompt_var.get()
        if not name: return messagebox.showerror("错误", "请选择一个要删除的 Prompt。")
        if len(self.settings['prompts']) <= 1: return messagebox.showwarning("警告", "不能删除最后一个 Prompt。")
        if messagebox.askyesno("确认删除", f"确定要删除 Prompt '{name}' 吗？"):
            del self.settings['prompts'][name]
            save_settings(self.settings)
            self._update_prompt_combo()
            first_name = list(self.settings['prompts'].keys())[0]
            self.prompt_var.set(first_name)
            self._on_prompt_select()
    
    def _on_browse_files(self):
        files = filedialog.askopenfilenames(title="请选择 TXT 文件", filetypes=[("Text files", "*.txt")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, tk.END)
            for file in self.selected_files: self.file_listbox.insert(tk.END, os.path.basename(file))
            self._update_status(f"已选择 {len(self.selected_files)} 个文件", "blue")
    
    def _update_status(self, text, color):
        self.status_label.config(text=text, foreground=color)
        self.update_idletasks()
    
    def _start_processing(self):
        if not self.selected_files: return messagebox.showerror("错误", "请先选择 TXT 文件。")
        if not self._get_current_api_key(): return messagebox.showerror("错误", "API Key 不能为空。")
        if not self.prompt_text.get("1.0", tk.END).strip(): return messagebox.showerror("错误", "Prompt 内容不能为空。")
    
        self.start_button.config(state=tk.DISABLED)
        self._update_status("正在处理中，请稍候...", "orange")
    
        threading.Thread(target=self._processing_task, daemon=True).start()
    
    def _processing_task(self):
        try:
            provider_name = self.api_provider_var.get()
            api_key = self._get_current_api_key()
            model_name = self.model_name_var.get().strip() or "deepseek-chat"
            base_url = API_PROVIDERS.get(provider_name)
            user_prompt_template = self.prompt_text.get("1.0", tk.END).strip()
            context_before = self.context_before_var.get()
            context_after = self.context_after_var.get()
            max_tokens_value = self.max_tokens_var.get()
    
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
            total_files = len(self.selected_files)
            for i, file_path in enumerate(self.selected_files):
                file_name = os.path.basename(file_path)
                dir_name = os.path.splitext(file_name)[0]
                output_dir = os.path.join(os.path.dirname(file_path), dir_name)
                os.makedirs(output_dir, exist_ok=True)
                
                self.after(0, self._update_status, f"[{i+1}/{total_files}] 正在读取: {file_name}", "orange")
    
                with open(file_path, 'r', encoding='utf-8') as f: original_text = f.read()
                
                paragraphs = split_text_into_paragraphs(original_text)
                if not paragraphs:
                    log_error(f"文件 {file_name} 为空或不包含有效段落，已跳过。")
                    continue
    
                translated_paragraphs, total_paragraphs = [], len(paragraphs)
                
                for j, para in enumerate(paragraphs):
                    self.after(0, self._update_status, f"[{i+1}/{total_files}] 翻译 {file_name} 段落 ({j+1}/{total_paragraphs})", "orange")
                    
                    context_parts = []
                    start = max(0, j - context_before)
                    if start < j:
                        context_parts.extend(["[Previous Context]"] + paragraphs[start:j] + [""])
                    
                    context_parts.extend(["[Text to Translate]", para])
                    
                    end = min(total_paragraphs, j + 1 + context_after)
                    if j + 1 < end:
                        context_parts.extend(["\n[Next Context]"] + paragraphs[j+1:end])
    
                    full_prompt = user_prompt_template.format(context="\n".join(context_parts))
                    translated_para = translate_single_paragraph(client, model_name, full_prompt, max_tokens_value)
                    translated_paragraphs.append(translated_para)
    
                full_translated_text = "\n\n".join(translated_paragraphs)
                translated_file_path = os.path.join(output_dir, f"{dir_name}_translated.txt")
                with open(translated_file_path, 'w', encoding='utf-8') as f: f.write(full_translated_text)
    
                self.after(0, self._update_status, f"[{i+1}/{total_files}] 生成 Excel 文件...", "orange")
                df = pd.DataFrame({'原文': paragraphs, '译文': translated_paragraphs})
                df.to_excel(os.path.join(output_dir, f"{dir_name}_corpus.xlsx"), index=False, engine='openpyxl')
    
            self.settings['max_tokens'] = self.max_tokens_var.get()
            self.settings['context_before'] = self.context_before_var.get()
            self.settings['context_after'] = self.context_after_var.get()
            save_settings(self.settings)
    
            self.after(0, self._update_status, "处理完成！所有文件已保存在各自的文件夹中。", "green")
    
        except Exception as e:
            error_message = f"处理失败：{e}"
            log_error(f"发生严重错误，处理流程中断. 错误: {e}")
            self.after(0, self._update_status, error_message, "red")
            self.after(0, messagebox.showerror, "发生错误", f"{e}\n\n详细信息已记录到 error_log.txt")
        
        finally:
            self.after(0, lambda: self.start_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()