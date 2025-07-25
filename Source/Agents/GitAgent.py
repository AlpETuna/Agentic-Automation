from strands import Agent
import git
import os
from datetime import datetime

class GitAgent:
    def __init__(self, repo_path="."):
        self.agent = Agent(
            name="git_manager",
            system_prompt="""You are a Git version control specialist.
            You help manage code repositories, create meaningful commit messages,
            and organize project versions. Always follow Git best practices."""
        )
        self.repo_path = repo_path
        
    def initialize_repo(self, remote_url=None):
        try:
            if not os.path.exists(os.path.join(self.repo_path, '.git')):
                repo = git.Repo.init(self.repo_path)
                if remote_url:
                    repo.create_remote('origin', remote_url)
                return {"status": "success", "message": "Repository initialized"}
            else:
                return {"status": "exists", "message": "Repository already exists"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def commit_changes(self, files, message=None):
        try:
            repo = git.Repo(self.repo_path)
            
            # Add files
            for file in files:
                repo.index.add([file])
            
            # Generate commit message if not provided
            if not message:
                message = self._generate_commit_message(files)
            
            # Commit
            commit = repo.index.commit(message)
            
            return {
                "status": "success",
                "commit_hash": commit.hexsha,
                "message": message
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def push_to_remote(self, branch="main"):
        try:
            repo = git.Repo(self.repo_path)
            origin = repo.remote('origin')
            origin.push(branch)
            return {"status": "success", "message": f"Pushed to {branch}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_branch(self, branch_name):
        try:
            repo = git.Repo(self.repo_path)
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
            return {"status": "success", "message": f"Created and switched to {branch_name}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _generate_commit_message(self, files):
        prompt = f"""
        Generate a concise, descriptive Git commit message for these files:
        {', '.join(files)}
        
        Follow conventional commit format and be specific about what was changed.
        """
        
        response = self.agent(prompt)
        return str(response).strip()