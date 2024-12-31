import subprocess

# Define Git commands
BRANCH_NAME = "update-code"
COMMIT_MESSAGE = "Automated update to trading bot"

def run_git_command(command):
    try:
        subprocess.run(command, check=True, text=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")

# Automate Git operations
def automate_git_update():
    run_git_command(f"git checkout -B {BRANCH_NAME}")  # Create or switch to the update branch
    run_git_command("git add .")                      # Stage all changes
    run_git_command(f"git commit -m \"{COMMIT_MESSAGE}\"")  # Commit changes
    run_git_command(f"git push origin {BRANCH_NAME}")  # Push to GitHub

if __name__ == "__main__":
    automate_git_update()
