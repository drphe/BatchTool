@echo off
chcp 65001 >nul
:: MOTA: Tạo symbolic link, để chuyển thư mục dữ liệu từ ổ C:\ sang ổ đĩa khác nhé.
title Công cụ tạo Symbolic Link tự động
cls

:: -------------------------------------------------------------------------
:: Kiem tra quyen Administrator (Bat buoc de chay lenh mklink)
:: -------------------------------------------------------------------------
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [THONG BAO] Ban chua chay script nay bang quyen Administrator!
    echo LUU Y: De tao Symbolic Link thi bat buoc phai dung quyen Admin.
    echo.
    goto :ask_admin_error
)

:: Neu co quyen Admin, nhay den khoi lenh chinh
goto :main_script

:ask_admin_error
set "admin_choice="
set /p "admin_choice=Ban co muon mo file nay bang Notepad de SUA CODE khong? (Y/N): "

if /i "%admin_choice%"=="Y" (
    echo.
    echo Dang mo file bang Notepad...
    start notepad.exe "%~f0"
    exit /b
)
if /i "%admin_choice%"=="N" (
    echo.
    echo Dang thoat...
    timeout /t 2 >nul
    exit /b
)

echo Lua chon khong hop le. Vui long nhap Y hoac N.
echo.
goto :ask_admin_error


:: -------------------------------------------------------------------------
:: KHOI LENH CHINH (KHI DA CO QUYEN ADMIN)
:: -------------------------------------------------------------------------
:main_script
echo =========================================================================
echo                CONG CU TAO SYMBOLIC LINK (LIEN KET MEM)
echo =========================================================================
echo.

:ask_create
set "choice="
set /p "choice=Ban co muon tao symbolic link khong? (Y/N): "

if /i "%choice%"=="N" (
    echo.
    echo Da huy bo thao tac. Khong co thay doi nao duoc thuc hien.
    goto :exit_script
)
if /i "%choice%"=="Y" goto :get_paths

echo [LOI] Lua chon khong hop le. Vui long nhap Y (Co) hoac N (Khong).
goto :ask_create

:: -------------------------------------------------------------------------
:: Nhap duong dan Goc va Dich
:: -------------------------------------------------------------------------
:get_paths
echo.
echo -------------------------------------------------------------------------
echo LUU Y: Ban co the copy truc tiep duong dan tu File Explorer vao day.
echo Tieu chuan duong dan khong can boc dau ngoac kep "", script se tu xu ly.
echo -------------------------------------------------------------------------
echo.

:input_old
set "OLD_DIR="
set /p "OLD_DIR=1. Nhap duong dan thu muc GOC (Vi du: C:\Users\...\MobileSync): "
:: Xoa dau ngoac kep neu nguoi dung quen tay nhap vao
set "OLD_DIR=%OLD_DIR:"=%"

if "%OLD_DIR%"=="" (
    echo [LOI] Duong dan goc khong duoc de trong!
    goto :input_old
)

:: --- DOAN MA KIEM TRA SYMBOLIC LINK CUA THU MUC GOC ---
if exist "%OLD_DIR%" (
    :: Trich xuat ten thu muc va duong dan cha de quet thuoc tinh Link
    for %%I in ("%OLD_DIR%") do (
        set "parent_dir=%%~dpI"
        set "folder_name=%%~nxI"
    )
    
    :: Gọi xau chuoi de check thuoc tinh <SYMLINKD> cua Windows
    setlocal enabledelayedexpansion
    dir /a:l "!parent_dir!" 2>nul | findstr /i /c:"<SYMLINKD>" | findstr /i /c:"!folder_name!" >nul
    if !errorLevel! equ 0 (
        endlocal
        echo.
        echo [THONG BAO] Thu muc goc nay DA LA mot Symbolic Link tu truoc!
        goto :ask_open_folder
    )
    endlocal
)
:: ------------------------------------------------------

:input_new
set "NEW_DIR="
set /p "NEW_DIR=2. Nhap duong dan thu muc DICH moi (Vi du: K:\BACKUP\ITUNE_BACKUP): "
set "NEW_DIR=%NEW_DIR:"=%"

if "%NEW_DIR%"=="" (
    echo [LOI] Duong dan dich khong duoc de trong!
    goto :input_new
)

:: Kiem tra neu duong dan goc va dich giong nhau
if /i "%OLD_DIR%"=="%NEW_DIR%" (
    echo [LOI] Thu muc goc va thu muc dich khong duoc trung nhau!
    goto :get_paths
)

:: -------------------------------------------------------------------------
:: Tien hanh xu ly tao thu muc, di doi du lieu va lam Link
:: -------------------------------------------------------------------------
echo.
echo [+] Dang kiem tra va khoi tao thu muc dich...
if not exist "%NEW_DIR%" (
    mkdir "%NEW_DIR%"
    echo   - Da tao thu muc dich: "%NEW_DIR%"
)

if exist "%OLD_DIR%" (
    echo [+] Dang sao chep du lieu tu thu muc goc sang thu muc dich...
    echo   (Qua trinh nay co the mat vai phut tuy thuoc vao dung luong file)
    xcopy "%OLD_DIR%" "%NEW_DIR%" /E /I /H /Y >nul
    
    echo [+] Dang xoa thu muc goc cu de chuan bi tao link...
    rmdir "%OLD_DIR%" /S /Q
)

echo [+] Dang tien hanh tao Symbolic Link...
mklink /D "%OLD_DIR%" "%NEW_DIR%"

if %errorLevel% equ 0 (
    echo.
    echo =========================================================================
    echo [THANH CONG] Da tao xong Symbolic Link!
    echo Goc:  "%OLD_DIR%" 
    echo ---^> Mui ten tro den dich: "%NEW_DIR%"
    echo =========================================================================
) else (
    echo.
    echo [LOI] Co loi xay ra trong qua trinh tao Symlink. 
    echo Vui long kiem tra xem thu muc goc cu da thuc su duoc xoa sach chua.
)
goto :exit_script


:: -------------------------------------------------------------------------
:: TINH NANG HOI MO THU MUC KHI DA CO LINK
:: -------------------------------------------------------------------------
:ask_open_folder
set "open_choice="
set /p "open_choice=Ban co muon mo thu muc nay trong File Explorer de kiem tra khong? (Y/N): "

if /i "%open_choice%"=="Y" (
    echo Dang mo thu muc...
    explorer.exe "%OLD_DIR%"
    goto :exit_script
)
if /i "%open_choice%"=="N" (
    goto :exit_script
)

echo Lua chon khong hop le. Vui long nhap Y hoac N.
echo.
goto :ask_open_folder


:exit_script
echo.
echo Bam phim bat ky de thoat...
pause >nul
exit /b