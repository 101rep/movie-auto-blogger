import paramiko
import json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

script = """
import os, subprocess, json

apps_dir = '/home/master/applications'
posts_found = []

for app in sorted(os.listdir(apps_dir)):
    wp_path = os.path.join(apps_dir, app, 'public_html')
    if os.path.exists(os.path.join(wp_path, 'wp-config.php')):
        cmd = f'wp post list --post_type=post --posts_per_page=3 --format=json --path={wp_path} --allow-root'
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        try:
            posts = json.loads(res.stdout)
            site_url = subprocess.run(f'wp option get siteurl --path={wp_path} --allow-root', shell=True, capture_output=True, text=True).stdout.strip()
            for p in posts:
                posts_found.append({
                    "app": app,
                    "site_url": site_url,
                    "post_id": p.get("ID"),
                    "title": p.get("post_title"),
                    "date": p.get("post_date"),
                    "status": p.get("post_status")
                })
        except Exception as e:
            pass

print(json.dumps(posts_found, indent=2, ensure_ascii=False))
"""

sftp = ssh.open_sftp()
with sftp.file('find_recent_posts.py', 'w') as f:
    f.write(script)
sftp.close()

_, o, e = ssh.exec_command('python3 /home/master/find_recent_posts.py')
out = o.read().decode('utf-8')
print('RECENT POSTS ACROSS APPS:\n', out)

ssh.exec_command('rm -f /home/master/find_recent_posts.py')
ssh.close()
