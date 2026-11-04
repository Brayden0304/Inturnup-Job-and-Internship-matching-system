from flask import Blueprint, render_template, redirect, url_for, Response, request, send_file
from flask_login import current_user
import io
import zipfile

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/download-desktop-shortcut")
def download_desktop_shortcut():
    """Generates a secure ZIP file containing the Windows Shortcut (.url) and a 1-click batch installer.
    Packaging in a ZIP guarantees that Chrome and Microsoft Edge will not rename the file to .download.
    """
    target_url = request.host_url
    shortcut_content = (
        "[InternetShortcut]\r\n"
        f"URL={target_url}\r\n"
        "IconIndex=0\r\n"
        "HotKey=0\r\n"
    )
    bat_content = (
        "@echo off\r\n"
        'set "DESKTOP=%USERPROFILE%\\Desktop"\r\n'
        f'echo [InternetShortcut] > "%DESKTOP%\\InternUp.url"\r\n'
        f'echo URL={target_url} >> "%DESKTOP%\\InternUp.url"\r\n'
        'echo IconIndex=0 >> "%DESKTOP%\\InternUp.url"\r\n'
        'echo HotKey=0 >> "%DESKTOP%\\InternUp.url"\r\n'
        'echo.\r\n'
        'echo ========================================================\r\n'
        'echo  [SUCCESS] InternUp shortcut created on your Desktop!\r\n'
        'echo  Location: %DESKTOP%\\InternUp.url\r\n'
        'echo ========================================================\r\n'
        'timeout /t 3 >nul\r\n'
    )

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("InternUp.url", shortcut_content)
        zip_file.writestr("Add_To_Desktop.bat", bat_content)

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="InternUp_Desktop_Shortcut.zip"
    )

