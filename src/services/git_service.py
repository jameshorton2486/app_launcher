"""
Git Service
Handles all git operations for projects using GitPython
"""

import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List, Callable

# Try to import GitPython
try:
    import git
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GITPYTHON_AVAILABLE = True
except ImportError:
    GITPYTHON_AVAILABLE = False
    git = None
    Repo = None
    InvalidGitRepositoryError = Exception
    GitCommandError = Exception

# Try to import logger
try:
    from src.utils.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.NullHandler())


class GitService:
    """Service for git operations using GitPython"""
    
    def __init__(self):
        """Initialize GitService"""
        if not GITPYTHON_AVAILABLE:
            logger.warning("GitPython not available. Git operations will be limited.")
        
        self._status_callbacks: List[Callable] = []
        self._monitoring = False
        self._monitor_thread = None
        self._projects_cache = {}
    
    def register_status_callback(self, callback: Callable):
        """
        Register a callback to be called when git status updates
        
        Args:
            callback: Function that takes (project_id, status_dict) as arguments
        """
        if callback not in self._status_callbacks:
            self._status_callbacks.append(callback)
    
    def unregister_status_callback(self, callback: Callable):
        """Unregister a status callback"""
        if callback in self._status_callbacks:
            self._status_callbacks.remove(callback)
    
    def _notify_status_update(self, project_id: str, status: Dict):
        """Notify all registered callbacks of a status update"""
        for callback in self._status_callbacks:
            try:
                callback(project_id, status)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")
    
    def _get_repo(self, repo_path: str) -> Optional[Repo]:
        """
        Get GitPython Repo object for a path
        
        Args:
            repo_path: Path to git repository
            
        Returns:
            Repo object or None if not a valid git repo
        """
        if not GITPYTHON_AVAILABLE:
            return None
        
        if not os.path.exists(repo_path):
            return None
        
        git_dir = os.path.join(repo_path, '.git')
        if not os.path.exists(git_dir):
            return None
        
        try:
            return Repo(repo_path)
        except InvalidGitRepositoryError:
            return None
        except Exception as e:
            logger.error(f"Error opening repository {repo_path}: {e}")
            return None
    
    def get_status(self, repo_path: str) -> Dict:
        """
        Get git repository status
        
        Args:
            repo_path: Path to git repository
            
        Returns:
            {
                'clean': bool,
                'uncommitted': int,
                'ahead': int,
                'behind': int,
                'branch': str,
                'status_text': str
            }
        """
        status = {
            'clean': True,
            'uncommitted': 0,
            'ahead': 0,
            'behind': 0,
            'branch': '',
            'status_text': 'unknown'
        }
        
        if not GITPYTHON_AVAILABLE:
            status['status_text'] = 'gitpython not available'
            return status
        
        repo = self._get_repo(repo_path)
        if not repo:
            status['status_text'] = 'not a git repo'
            return status
        
        try:
            # Get current branch
            try:
                status['branch'] = repo.active_branch.name
            except:
                status['branch'] = 'detached' if repo.head.is_detached else 'unknown'
            
            # Check for uncommitted changes
            uncommitted_files = [item for item in repo.index.diff(None)]
            untracked_files = repo.untracked_files
            status['uncommitted'] = len(uncommitted_files) + len(untracked_files)
            status['clean'] = status['uncommitted'] == 0
            
            # Check ahead/behind if tracking remote
            try:
                if repo.active_branch.tracking_branch():
                    tracking = repo.active_branch.tracking_branch()
                    commits_ahead = list(repo.iter_commits(f"{tracking}..{repo.active_branch}"))
                    commits_behind = list(repo.iter_commits(f"{repo.active_branch}..{tracking}"))
                    status['ahead'] = len(commits_ahead)
                    status['behind'] = len(commits_behind)
            except:
                # No tracking branch or other error
                pass
            
            # Determine status text
            if not status['clean']:
                status['status_text'] = 'uncommitted'
            elif status['ahead'] > 0 and status['behind'] > 0:
                status['status_text'] = 'diverged'
            elif status['ahead'] > 0:
                status['status_text'] = 'ahead'
            elif status['behind'] > 0:
                status['status_text'] = 'behind'
            else:
                status['status_text'] = 'clean'
        
        except Exception as e:
            logger.error(f"Error getting git status for {repo_path}: {e}")
            status['status_text'] = 'error'
        
        return status
    
    def pull(self, repo_path: str) -> Tuple[bool, str]:
        """
        Pull latest changes from remote
        
        Args:
            repo_path: Path to git repository
            
        Returns:
            Tuple of (success, message)
        """
        if not GITPYTHON_AVAILABLE:
            return False, "GitPython not available"
        
        repo = self._get_repo(repo_path)
        if not repo:
            return False, "Not a git repository"
        
        try:
            # Fetch first to update remote tracking branches
            repo.remotes.origin.fetch()
            
            # Pull changes
            origin = repo.remotes.origin
            origin.pull()
            
            logger.info(f"Successfully pulled changes for {repo_path}")
            return True, "Successfully pulled latest changes"
        
        except GitCommandError as e:
            error_msg = str(e)
            if 'authentication' in error_msg.lower() or 'permission' in error_msg.lower():
                return False, "Authentication error: Check your credentials"
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                return False, "Network error: Check your internet connection"
            else:
                return False, f"Git error: {error_msg}"
        
        except Exception as e:
            logger.error(f"Error pulling changes for {repo_path}: {e}")
            return False, f"Error: {str(e)}"
    
    def push(self, repo_path: str) -> Tuple[bool, str]:
        """
        Push commits to remote
        
        Args:
            repo_path: Path to git repository
            
        Returns:
            Tuple of (success, message)
        """
        if not GITPYTHON_AVAILABLE:
            return False, "GitPython not available"
        
        repo = self._get_repo(repo_path)
        if not repo:
            return False, "Not a git repository"
        
        try:
            origin = repo.remotes.origin
            origin.push()
            
            logger.info(f"Successfully pushed changes for {repo_path}")
            return True, "Successfully pushed commits"
        
        except GitCommandError as e:
            error_msg = str(e)
            if 'authentication' in error_msg.lower() or 'permission' in error_msg.lower():
                return False, "Authentication error: Check your credentials"
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                return False, "Network error: Check your internet connection"
            else:
                return False, f"Git error: {error_msg}"
        
        except Exception as e:
            logger.error(f"Error pushing changes for {repo_path}: {e}")
            return False, f"Error: {str(e)}"
    
    def get_last_commit(self, repo_path: str) -> Dict:
        """
        Get last commit information
        
        Args:
            repo_path: Path to git repository
            
        Returns:
            {
                'hash': str,
                'message': str,
                'author': str,
                'timestamp': datetime,
                'time_ago': str
            }
        """
        commit_info = {
            'hash': '',
            'message': '',
            'author': '',
            'timestamp': None,
            'time_ago': 'unknown'
        }
        
        if not GITPYTHON_AVAILABLE:
            return commit_info
        
        repo = self._get_repo(repo_path)
        if not repo:
            return commit_info
        
        try:
            # Get the latest commit
            if not repo.heads:
                return commit_info
            
            commit = repo.head.commit
            
            commit_info['hash'] = commit.hexsha[:8]
            commit_info['message'] = commit.message.strip().split('\n')[0]  # First line only
            commit_info['author'] = commit.author.name
            commit_info['timestamp'] = commit.committed_datetime
            
            # Calculate time ago
            now = datetime.now(commit.committed_datetime.tzinfo) if commit.committed_datetime.tzinfo else datetime.now()
            delta = now - commit.committed_datetime
            
            if delta.days > 0:
                commit_info['time_ago'] = f"{delta.days}d ago"
            elif delta.seconds >= 3600:
                hours = delta.seconds // 3600
                commit_info['time_ago'] = f"{hours}h ago"
            elif delta.seconds >= 60:
                minutes = delta.seconds // 60
                commit_info['time_ago'] = f"{minutes}m ago"
            else:
                commit_info['time_ago'] = "just now"
        
        except Exception as e:
            logger.error(f"Error getting last commit for {repo_path}: {e}")
        
        return commit_info
    
    def clone(self, url: str, destination: str) -> Tuple[bool, str]:
        """
        Clone a repository
        
        Args:
            url: Repository URL
            destination: Destination directory
            
        Returns:
            Tuple of (success, message)
        """
        if not GITPYTHON_AVAILABLE:
            return False, "GitPython not available"
        
        if os.path.exists(destination):
            return False, "Destination directory already exists"
        
        try:
            # Create parent directory if needed
            parent_dir = os.path.dirname(destination)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            # Clone repository
            Repo.clone_from(url, destination)
            
            logger.info(f"Successfully cloned {url} to {destination}")
            return True, "Successfully cloned repository"
        
        except GitCommandError as e:
            error_msg = str(e)
            if 'authentication' in error_msg.lower() or 'permission' in error_msg.lower():
                return False, "Authentication error: Check your credentials"
            elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                return False, "Network error: Check your internet connection"
            else:
                return False, f"Git error: {error_msg}"
        
        except Exception as e:
            logger.error(f"Error cloning repository {url}: {e}")
            return False, f"Error: {str(e)}"
    
    def get_all_statuses(self, projects: List[Dict]) -> Dict:
        """
        Batch check status for all projects
        
        Args:
            projects: List of project dictionaries with 'id' and 'path' keys
            
        Returns:
            Dictionary mapping project_id to status_dict
        """
        statuses = {}
        
        for project in projects:
            project_id = project.get('id') or project.get('name', 'unknown')
            repo_path = project.get('path', '')
            
            if not repo_path:
                continue
            
            try:
                status = self.get_status(repo_path)
                statuses[project_id] = status
            except Exception as e:
                logger.error(f"Error getting status for project {project_id}: {e}")
                statuses[project_id] = {
                    'clean': False,
                    'uncommitted': 0,
                    'ahead': 0,
                    'behind': 0,
                    'branch': '',
                    'status_text': 'error'
                }
        
        return statuses
    
    def start_status_monitoring(self, projects: List[Dict], interval: int = 60):
        """
        Start background thread that refreshes git status periodically
        
        Args:
            projects: List of project dictionaries
            interval: Refresh interval in seconds (default: 60)
        """
        if self._monitoring:
            return
        
        self._monitoring = True
        
        def monitor_loop():
            while self._monitoring:
                try:
                    statuses = self.get_all_statuses(projects)
                    
                    # Notify callbacks for each project
                    for project in projects:
                        project_id = project.get('id') or project.get('name', 'unknown')
                        if project_id in statuses:
                            self._notify_status_update(project_id, statuses[project_id])
                    
                    # Cache statuses
                    self._projects_cache = statuses
                
                except Exception as e:
                    logger.error(f"Error in git status monitoring: {e}")
                
                # Sleep for interval
                for _ in range(interval):
                    if not self._monitoring:
                        break
                    time.sleep(1)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info(f"Started git status monitoring (interval: {interval}s)")
    
    def stop_status_monitoring(self):
        """Stop the background status monitoring thread"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
        logger.info("Stopped git status monitoring")
