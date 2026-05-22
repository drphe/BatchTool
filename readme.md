# 🛠️ TRÌNH QUẢN LÝ FILE BATCH (.BAT) CHUYÊN NGHIỆP

Chào mừng bạn đến với **Batch Tool** – Giải pháp giao diện đồ họa (GUI) nhỏ gọn, tiện lợi được phát triển nhằm giúp bạn gom cụm, theo dõi và thực thi toàn bộ các kịch bản tự động hóa hoặc tinh chỉnh hệ thống (`.bat`) trên Windows một cách trực quan mà không cần gõ lệnh thủ công.

\---

## ✨ Các Tính Năng Nổi Bật

* **📺 Giao Diện Đồ Họa Trực Quan:** Quên đi việc nhập số mệt mỏi trên cửa sổ CMD. Giờ đây bạn chỉ cần click chọn file bằng chuột.
* **📝 Hỗ Trợ Mô Tả Tiếng Việt:** Đọc trực tiếp các dòng ghi chú, mô tả công dụng được cài cắm riêng bên trong từng file `.bat` (Hỗ trợ tiếng Việt có dấu chuẩn UTF-8).
* **🛡️ Kích Hoạt Quyền Admin Thông Minh:** Tích hợp nút chạy riêng biệt bằng quyền **Administrator** (UAC). Dù phần mềm chạy ở quyền thường, bạn vẫn có thể đẩy riêng file `.bat` được chọn lên quyền tối cao một cách dễ dàng.
* **🔄 Làm Mới Tức Thì (Hot Reload):** Bật nút làm mới để quét lại thư mục ngay lập tức khi bạn vừa thêm, sửa hoặc xóa bất kỳ file `.bat` nào bên ngoài.
* **🛠️ Chỉnh Sửa Mã Nhanh:** Mở file code đang chọn bằng Notepad chỉ với một cú click để chỉnh sửa thuật toán tiện lợi.

\---

## 📂 Cấu Trúc Thư Mục Chuẩn

Để phần mềm hoạt động chính xác nhất, bạn hãy sắp xếp các file chung một thư mục theo cấu trúc sau:

```text
📁 Thu-Muc-Cong-Cu/
├── 📄 HoanUpdateWindows.bat
├── 📄 TaoODiaAo.bat
└── 📄 BackupItunes.bat

## Cấu trúc Tệp .Bat
Phần đầu file .bat cần thêm chcp 65001 >null để hỗ trợ Tiếng Việt và dòng title để đặt tiêu đề cho file .bat.

```text
@echo off
chcp 65001 >nul
:: MOTA: Tạo symbolic link, để chuyển thư mục dữ liệu từ ổ C:\ sang ổ đĩa khác nhé.
title Công cụ tạo Symbolic Link tự động


## Câu lệnh để biên tập sang .exe

python -m PyInstaller --noconsole --onefile --icon=icon.ico BatchTool.py

