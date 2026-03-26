"""
setup_github.py
One-time setup: creates the SAP-Hackfest repo under your GitHub account
and pushes the local code. Run this ONCE after setting GITHUB_TOKEN in .env.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN", "")
if not TOKEN or "your_github_token_here" in TOKEN:
    print("❌ GITHUB_TOKEN not set in .env")
    print("   Create one at: https://github.com/settings/tokens")
    print("   Make sure to check the 'repo' scope")
    sys.exit(1)

from github import Github, Auth

g    = Github(auth=Auth.Token(TOKEN))
user = g.get_user()
username = user.login
print(f"✅ Logged in as: {username}")

# ── Create repo if it doesn't exist ────────────────────────────────────────────
repo_name = "SAP-Hackfest"
try:
    repo = g.get_repo(f"{username}/{repo_name}")
    print(f"✅ Repo already exists: {repo.html_url}")
except Exception:
    print(f"Creating repo {username}/{repo_name}...")
    repo = user.create_repo(
        repo_name,
        description="VIGIL-AI — AI-Assisted Verilog Verification Platform",
        private=False,
        auto_init=False,
    )
    print(f"✅ Created: {repo.html_url}")

# ── Update github_client.py with the correct repo name ────────────────────────
client_file = "github_client.py"
with open(client_file, "r") as f:
    content = f.read()

old = 'REPO_NAME = "RisheekeshKG/SAP-Hackfest"'
new = f'REPO_NAME = "{username}/{repo_name}"'
if old in content:
    content = content.replace(old, new)
    with open(client_file, "w") as f:
        f.write(content)
    print(f"✅ Updated github_client.py → {username}/{repo_name}")
else:
    # Already updated or different format — patch generically
    import re
    content = re.sub(r'REPO_NAME\s*=\s*"[^"]+"', f'REPO_NAME = "{username}/{repo_name}"', content)
    with open(client_file, "w") as f:
        f.write(content)
    print(f"✅ Patched github_client.py → {username}/{repo_name}")

# Also update app.py GitHub link
app_file = "app.py"
with open(app_file, "r") as f:
    app_content = f.read()
app_content = app_content.replace("RisheekeshKG/SAP-Hackfest", f"{username}/{repo_name}")
with open(app_file, "w") as f:
    f.write(app_content)
print(f"✅ Updated app.py links → {username}/{repo_name}")

# ── Set up git remote and push ─────────────────────────────────────────────────
remote_url = f"https://{TOKEN}@github.com/{username}/{repo_name}.git"

# Check current remote
result = subprocess.run(["git", "remote", "get-url", "origin"],
                        capture_output=True, text=True)
current_remote = result.stdout.strip()

if current_remote != remote_url:
    print("\nUpdating git remote origin...")
    subprocess.run(["git", "remote", "set-url", "origin", remote_url], check=True)
    print(f"✅ Remote set to: https://github.com/{username}/{repo_name}.git")

print("\nPushing code to GitHub...")
push_result = subprocess.run(
    ["git", "push", "-u", "origin", "main", "--force"],
    capture_output=True, text=True
)

if push_result.returncode != 0:
    # Try 'master' branch
    push_result = subprocess.run(
        ["git", "push", "-u", "origin", "master:main", "--force"],
        capture_output=True, text=True
    )

if push_result.returncode == 0:
    print(f"✅ Code pushed to GitHub!")
else:
    print("⚠️  Push failed — you may need to configure git user first:")
    print(push_result.stderr)
    print("\nRun these commands manually:")
    print(f'  git remote set-url origin https://YOUR_TOKEN@github.com/{username}/{repo_name}.git')
    print(f'  git push -u origin main')

print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅ Setup Complete!                                          ║
║                                                              ║
║  Repo: https://github.com/{username}/{repo_name:<25}  ║
║                                                              ║
║  Next: Add these GitHub Secrets in your repo settings:       ║
║   • GOOGLE_API_KEY  = your Gemini key                        ║
║   • VIGIL_GITHUB_TOKEN = your GitHub token                   ║
║                                                              ║
║  Settings URL:                                               ║
║  github.com/{username}/{repo_name}/settings/secrets/actions ║
╚══════════════════════════════════════════════════════════════╝
""")

print("Now run:  streamlit run app.py")
