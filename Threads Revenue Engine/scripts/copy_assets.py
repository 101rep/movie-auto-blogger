import os
import shutil

scripts_dir = os.path.dirname(os.path.abspath(__file__))
tre_dir = os.path.dirname(scripts_dir)
workspace_dir = os.path.dirname(tre_dir)

src_templates = os.path.join(workspace_dir, "01_Threads_쿠팡_자동화", "app", "templates")
dst_templates = os.path.join(tre_dir, "apps", "backend", "tre", "templates")

src_static = os.path.join(workspace_dir, "01_Threads_쿠팡_자동화", "app", "static")
dst_static = os.path.join(tre_dir, "apps", "backend", "tre", "static")

os.makedirs(dst_templates, exist_ok=True)
os.makedirs(dst_static, exist_ok=True)

for item in os.listdir(src_templates):
    s = os.path.join(src_templates, item)
    d = os.path.join(dst_templates, item)
    if os.path.isfile(s):
        shutil.copy2(s, d)
    elif os.path.isdir(s):
        shutil.copytree(s, d, dirs_exist_ok=True)

for item in os.listdir(src_static):
    s = os.path.join(src_static, item)
    d = os.path.join(dst_static, item)
    if os.path.isfile(s):
        shutil.copy2(s, d)
    elif os.path.isdir(s):
        shutil.copytree(s, d, dirs_exist_ok=True)

print("Copied templates:", len(os.listdir(dst_templates)))
print("Copied static:", os.listdir(dst_static))
