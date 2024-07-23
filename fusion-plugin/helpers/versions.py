import os
import subprocess

from ..config import ROOT_DIR

from ..lib import fusion360utils as futil

def _get_last_commit_date(file_path):
    try:
        # Get the absolute path of the file
        file_path = os.path.abspath(file_path)
        
        
        # Get the last commit date of the file
        last_commit_date = subprocess.check_output(['git', 'log', '-1', '--format=%cd', '--', ROOT_DIR], cwd=ROOT_DIR)
        last_commit_date = last_commit_date.strip().decode('utf-8')
        
        return last_commit_date
    except subprocess.CalledProcessError:
        return None

def get_last_commit_date():
    futil.log("Checking it Version")
    p = os.path.dirname(__file__)
    futil.log(str(p))
    return _get_last_commit_date(p)

def _git_pull(repo_path):
    try:
        # Change directory to the repository path
        os.chdir(repo_path)

        # Run git pull command
        result = subprocess.run(['git', 'pull'], capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def git_pull():
    futil.log("Git pull...")
    p = os.path.dirname(__file__)
    futil.log(str(p))
    return _git_pull(p)
    
    