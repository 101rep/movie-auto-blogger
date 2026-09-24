import os
import subprocess

desktop = os.path.expanduser(r"~\OneDrive\바탕 화면")
if not os.path.exists(desktop):
    desktop = os.path.expanduser(r"~\Desktop")

shortcut_script = f"""
$sh = New-Object -ComObject WScript.Shell
$linkPath = "{desktop}\\Threads Revenue Engine V3.lnk"
$link = $sh.CreateShortcut($linkPath)
$link.TargetPath = "powershell.exe"
$link.Arguments = '-ExecutionPolicy Bypass -NoProfile -File "C:\\Users\\ktaeh\\OneDrive\\바탕 화면\\안티그래비티\\Threads Revenue Engine\\run_all.ps1"'
$link.WorkingDirectory = "C:\\Users\\ktaeh\\OneDrive\\바탕 화면\\안티그래비티\\Threads Revenue Engine"
$link.IconLocation = "C:\\Users\\ktaeh\\OneDrive\\바탕 화면\\안티그래비티\\Threads Revenue Engine\\tre_icon.ico,0"
$link.Description = "Threads Revenue Engine V3 - AI Content Commerce OS"
$link.Save()

$linkPath2 = "{desktop}\\AI Content Commerce OS 대시보드.lnk"
$link2 = $sh.CreateShortcut($linkPath2)
$link2.TargetPath = "powershell.exe"
$link2.Arguments = '-ExecutionPolicy Bypass -NoProfile -File "C:\\Users\\ktaeh\\OneDrive\\바탕 화면\\안티그래비티\\Threads Revenue Engine\\run_all.ps1"'
$link2.WorkingDirectory = "C:\\Users\\ktaeh\\OneDrive\\바탕 화면\\안티그래비티\\Threads Revenue Engine"
$link2.IconLocation = "C:\\Users\\ktaeh\\OneDrive\\바탕 화면\\안티그래비티\\Threads Revenue Engine\\tre_icon.ico,0"
$link2.Description = "Threads Revenue Engine V3 - AI Content Commerce OS"
$link2.Save()

Write-Host "Shortcuts verified and saved successfully!"
"""

ps_path = "scripts/update_shortcuts.ps1"
with open(ps_path, "w", encoding="utf-8-sig") as f:
    f.write(shortcut_script)

res = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_path], capture_output=True, text=True)
print(res.stdout)
if res.stderr:
    print(res.stderr)
