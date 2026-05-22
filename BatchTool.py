import os
import subprocess
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox, ttk, filedialog

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def read_bat_info(file_path):
    """
    Quét file .bat một lần duy nhất để lấy đồng thời:
    - Dòng mô tả (MOTA)
    - Tiêu đề (TITLE) nếu có cấu hình bên trong file
    """
    mota = "(Chưa cấu hình dòng mô tả :: MOTA: trong file .bat)"
    title_val = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        try:
            with open(file_path, 'r', encoding='cp1258', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            lines = []

    # Quét tối đa 15 dòng đầu để tìm các từ khóa cấu hình
    for line in lines[:15]:
        line_strip = line.strip()
        line_upper = line_strip.upper()
        
        # 1. Tìm mô tả
        if "MOTA:" in line_upper:
            parts = line_strip.split("MOTA:", 1)
            if len(parts) > 1:
                mota = parts[1].strip()
                
        # 2. Tìm Tiêu đề (Title) bên trong file .bat
        if line_upper.startswith("TITLE "):
            title_text = line_strip[6:].strip()
            title_text = title_text.replace('"', '').replace("'", "")
            if title_text:
                title_val = title_text
                
    return mota, title_val

class BatManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Trình Quản Lý File Batch Tool - BS Phe")
        
        # Cấu hình cửa sổ ra chính giữa màn hình máy tính
        window_width = 950
        window_height = 540
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        self.style.configure("TButton", font=("Segoe UI", 9), padding=3)
        self.style.configure("Admin.TButton", font=("Segoe UI", 10, "bold"), foreground="green")
        
        if getattr(sys, 'frozen', False):
            self.default_dir = os.path.dirname(sys.executable)
        else:
            try:
                self.default_dir = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                self.default_dir = os.getcwd()
                
        self.current_dir = self.default_dir
        self.bat_files = []
        self.selected_file_path = None
        
        # Biến quản lý chế độ hiển thị danh sách (1: Hiện Title, 2: Chỉ hiện tên file)
        self.display_mode = tk.IntVar(value=1)
        
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # KHU VỰC THÔNG TIN PHÍA TRÊN & DUYỆT THƯ MỤC
        header_frame = ttk.Frame(self.root, padding=10)
        header_frame.pack(fill=tk.X)
        
        is_admin = check_admin()
        status_text = "ADMINISTRATOR (Cao nhất)" if is_admin else "USER THƯỜNG"
        status_color = "green" if is_admin else "orange"
        
        lbl_status_title = ttk.Label(header_frame, text="Trạng thái hệ thống: ")
        lbl_status_title.pack(side=tk.LEFT)
        lbl_status = tk.Label(header_frame, text=status_text, font=("Segoe UI", 9, "bold"), fg=status_color)
        lbl_status.pack(side=tk.LEFT)
        
        dir_frame = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        dir_frame.pack(fill=tk.X)
        
        ttk.Label(dir_frame, text="Thư mục: ", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        
        self.ent_dir = ttk.Entry(dir_frame, font=("Segoe UI", 9, "italic"))
        self.ent_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_browse = ttk.Button(dir_frame, text="📁 Duyệt...", width=10, command=self.browse_directory)
        btn_browse.pack(side=tk.LEFT, padx=2)
        
        btn_default = ttk.Button(dir_frame, text="🏠 Mặc định", width=15, command=self.reset_to_default_dir)
        btn_default.pack(side=tk.LEFT, padx=2)

        # TÙY CHỌN CHẾ ĐỘ HIỂN THỊ
        view_option_frame = ttk.Frame(self.root, padding=(10, 0, 10, 5))
        view_option_frame.pack(fill=tk.X)
        
        ttk.Label(view_option_frame, text="Chế độ hiển thị danh sách: ", font=("Segoe UI", 9, "italic")).pack(side=tk.LEFT, padx=(0, 10))
        
        rdo_title = ttk.Radiobutton(view_option_frame, text="⭐ Ưu tiên tiêu đề (Title)", variable=self.display_mode, value=1, command=self.update_listbox_view)
        rdo_title.pack(side=tk.LEFT, padx=10)
        
        rdo_filename = ttk.Radiobutton(view_option_frame, text="📄 Chỉ hiện tên file (.bat)", variable=self.display_mode, value=2, command=self.update_listbox_view)
        rdo_filename.pack(side=tk.LEFT, padx=10)

        # KHU VỰC THÂN MÁY (CHIA ĐÔI THÔNG TIN)
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # BÊN TRÁI: Danh sách tập lệnh
        left_frame = ttk.LabelFrame(main_frame, text=" Danh sách chức năng / Tập lệnh ")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.listbox = tk.Listbox(left_frame, font=("Segoe UI", 10), bd=1, selectmode=tk.SINGLE, 
                                  highlightthickness=0, activestyle='none', bg="white")
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_file)
        
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # BÊN PHẢI: Khung hiển thị chi tiết mô tả và tổ hợp nút bấm hành động
        right_frame = ttk.LabelFrame(main_frame, text=" Chi tiết & Hành động ")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(5, 0))
        
        ttk.Label(right_frame, text="Mô tả chức năng file:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.txt_desc = tk.Text(right_frame, font=("Segoe UI", 10), height=5, width=48, wrap=tk.WORD, 
                                bg="#f5f5f5", bd=1, relief=tk.SOLID, padx=5, pady=5)
        self.txt_desc.pack(fill=tk.X, pady=(5, 5), padx=10)
        self.txt_desc.config(state=tk.DISABLED)
        
        edit_desc_frame = ttk.Frame(right_frame)
        edit_desc_frame.pack(fill=tk.X, padx=10, pady=(0, 15))
        
        self.btn_edit_desc = ttk.Button(edit_desc_frame, text="✏️ Sửa mô tả", width=15, command=self.enable_edit_desc, state=tk.DISABLED)
        self.btn_edit_desc.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_save_desc = ttk.Button(edit_desc_frame, text="💾 Lưu mô tả", width=15, command=self.save_custom_desc, state=tk.DISABLED)
        self.btn_save_desc.pack(side=tk.LEFT)
        
        self.btn_run_user = ttk.Button(right_frame, text="🚀 Chạy với quyền USER thường", command=self.run_user, state=tk.DISABLED)
        self.btn_run_user.pack(fill=tk.X, pady=3, padx=10)
        
        self.btn_run_admin = ttk.Button(right_frame, text="🛡️ Chạy với quyền ADMINISTRATOR", style="Admin.TButton", command=self.run_admin, state=tk.DISABLED)
        self.btn_run_admin.pack(fill=tk.X, pady=3, padx=10)
        
        self.btn_edit = ttk.Button(right_frame, text="📝 Mở bằng Notepad để sửa toàn bộ Code", command=self.edit_code, state=tk.DISABLED)
        self.btn_edit.pack(fill=tk.X, pady=3, padx=10)
        
        ttk.Separator(right_frame, orient='horizontal').pack(fill=tk.X, pady=12, padx=10)
        
        btn_refresh = ttk.Button(right_frame, text="🔄 Làm mới danh sách thư mục", command=self.refresh_list)
        btn_refresh.pack(fill=tk.X, padx=10, pady=(0, 5))

    def browse_directory(self):
        selected_dir = filedialog.askdirectory(initialdir=self.current_dir, title="Chọn thư mục chứa file .bat")
        if selected_dir:
            self.current_dir = os.path.abspath(selected_dir)
            self.refresh_list()

    def reset_to_default_dir(self):
        if self.current_dir != self.default_dir:
            self.current_dir = self.default_dir
            self.refresh_list()

    def refresh_list(self):
        """Quét và thu thập dữ liệu sâu từ thư mục hiện hành"""
        if not os.path.exists(self.current_dir):
            return
            
        files = [f for f in os.listdir(self.current_dir) if f.lower().endswith('.bat')]
        self.bat_files = []
        
        for file in files:
            full_path = os.path.join(self.current_dir, file)
            desc, title_val = read_bat_info(full_path)
            self.bat_files.append({
                "name": file, 
                "path": full_path, 
                "desc": desc,
                "title": title_val
            })
            
        # Nạp dữ liệu lên Listbox theo chế độ đang chọn
        self.update_listbox_view(reset_selection=False)

    def update_listbox_view(self, reset_selection=False):
        """Cập nhật lại giao diện hiển thị của Listbox dựa trên nút Radio được tích chọn"""
        prev_selected_path = None if reset_selection else self.selected_file_path
        self.listbox.delete(0, tk.END)
        
        self.ent_dir.config(state=tk.NORMAL)
        self.ent_dir.delete(0, tk.END)
        self.ent_dir.insert(0, self.current_dir)
        self.ent_dir.config(state=tk.DISABLED)
        
        target_select_idx = -1

        for idx, file_data in enumerate(self.bat_files):
            if prev_selected_path and file_data["path"] == prev_selected_path:
                target_select_idx = idx

            # XỬ LÝ ƯU TIÊN TIÊU ĐỀ: Bỏ hoàn toàn chuỗi tên file gốc đi theo yêu cầu của bạn
            if self.display_mode.get() == 1 and file_data["title"]:
                display_name = f" ⭐ {file_data['title']}"
            else:
                display_name = f"  📄 {file_data['name']}"
                
            self.listbox.insert(tk.END, display_name)
            
        if target_select_idx != -1:
            self.listbox.select_set(target_select_idx)
            self.listbox.see(target_select_idx)
        else:
            self.txt_desc.config(state=tk.NORMAL, bg="#f5f5f5")
            self.txt_desc.delete('1.0', tk.END)
            self.txt_desc.config(state=tk.DISABLED)
            
            self.toggle_buttons(tk.DISABLED)
            self.btn_edit_desc.config(state=tk.DISABLED)
            self.btn_save_desc.config(state=tk.DISABLED)
            self.selected_file_path = None

    def on_select_file(self, event):
        selection = self.listbox.curselection()
        if selection:
            idx = selection[0]
            if idx < len(self.bat_files):
                file_data = self.bat_files[idx]
                self.selected_file_path = file_data["path"]
                
                self.txt_desc.config(state=tk.NORMAL, bg="#f5f5f5")
                self.txt_desc.delete('1.0', tk.END)
                self.txt_desc.insert(tk.END, file_data["desc"])
                self.txt_desc.config(state=tk.DISABLED)
                
                self.toggle_buttons(tk.NORMAL)
                self.btn_edit_desc.config(state=tk.NORMAL)
                self.btn_save_desc.config(state=tk.DISABLED)

    def enable_edit_desc(self):
        if self.selected_file_path:
            self.txt_desc.config(state=tk.NORMAL, bg="white")
            self.txt_desc.focus_set()
            self.btn_save_desc.config(state=tk.NORMAL)
            self.btn_edit_desc.config(state=tk.DISABLED)

    def save_custom_desc(self):
        if not self.selected_file_path:
            return
            
        new_desc = self.txt_desc.get('1.0', tk.END).strip()
        if not new_desc:
            messagebox.showwarning("Cảnh báo", "Nội dung mô tả không được để trống hoàn toàn!")
            return

        try:
            lines = []
            try:
                with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(self.selected_file_path, 'r', encoding='cp1258', errors='ignore') as f:
                    lines = f.readlines()

            # 1. KIỂM TRA VÀ BỔ SUNG CHCP 65001 >NUL
            has_chcp = False
            echo_off_idx = -1
            
            for idx, line in enumerate(lines[:10]):
                line_upper = line.strip().upper()
                if "CHCP 65001" in line_upper:
                    has_chcp = True
                if "@ECHO OFF" in line_upper:
                    echo_off_idx = idx

            if not has_chcp:
                chcp_line = "chcp 65001 >nul\n"
                if echo_off_idx != -1:
                    lines.insert(echo_off_idx + 1, chcp_line)
                else:
                    lines.insert(0, chcp_line)

            # 2. THAY THẾ HOẶC TẠO MỚI DÒNG MÔ TẢ
            mota_found = False
            for i in range(min(10, len(lines))):
                if "MOTA:" in lines[i].upper():
                    prefix = lines[i].split("MOTA:", 1)[0]
                    lines[i] = f"{prefix}MOTA: {new_desc}\n"
                    mota_found = True
                    break
            
            if not mota_found:
                inserted = False
                for i in range(min(10, len(lines))):
                    if "CHCP 65001" in lines[i].upper():
                        lines.insert(i + 1, f":: MOTA: {new_desc}\n")
                        inserted = True
                        break
                if not inserted:
                    lines.insert(0, f":: MOTA: {new_desc}\n")

            with open(self.selected_file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
                
            messagebox.showinfo("Thành công", "Đã cập nhật mô tả và đồng bộ bảng mã Tiếng Việt (chcp 65001) vào file .bat!")
            
            # Khóa lại ô văn bản sau khi lưu
            self.txt_desc.config(state=tk.DISABLED, bg="#f5f5f5")
            self.btn_edit_desc.config(state=tk.NORMAL)
            self.btn_save_desc.config(state=tk.DISABLED)
            
            # TỰ ĐỘNG QUÉT VÀ NẠP LẠI TOÀN BỘ THƯ MỤC THEO YÊU CẦU CỦA BẠN
            self.refresh_list()
            
        except Exception as e:
            messagebox.showerror("Lỗi ghi file", f"Không thể lưu chỉnh sửa file .bat:\n{e}")

    def toggle_buttons(self, state):
        self.btn_run_user.config(state=state)
        self.btn_run_admin.config(state=state)
        self.btn_edit.config(state=state)

    def run_user(self):
        if self.selected_file_path:
            subprocess.Popen(f'start cmd /c "{self.selected_file_path}"', shell=True)

    def run_admin(self):
        if self.selected_file_path:
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", f"/c \"{self.selected_file_path}\"", None, 1)
            except Exception as e:
                messagebox.showerror("Lỗi thực thi", f"Không thể kích hoạt quyền Admin:\n{e}")

    def edit_code(self):
        if self.selected_file_path:
            subprocess.Popen(f'notepad.exe "{self.selected_file_path}"', shell=True)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = BatManagerGUI(root)
        root.mainloop()
    except Exception as error:
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror("Lỗi khởi động hệ thống", f"Ứng dụng gặp lỗi khi khởi chạy:\n{error}")