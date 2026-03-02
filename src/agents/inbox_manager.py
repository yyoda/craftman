import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('InboxManager')

class InboxManager:
    def __init__(self, inbox_dir):
        self.inbox_dir = inbox_dir

    def ensure_inbox_exists(self):
        if not os.path.exists(self.inbox_dir):
            os.makedirs(self.inbox_dir)
            logger.info(f"Created inbox directory: {self.inbox_dir}")

    def scan_files(self):
        """
        Scans the inbox directory for files.
        Returns a list of full file paths.
        """
        self.ensure_inbox_exists()
        files = []
        for filename in os.listdir(self.inbox_dir):
            filepath = os.path.join(self.inbox_dir, filename)
            
            # Filter out directories and hidden files
            if os.path.isfile(filepath) and not filename.startswith('.'):
                files.append(filepath)
        
        return files

    def list_files(self):
        """
        Returns a list of filenames (not full paths) for display.
        """
        self.ensure_inbox_exists()
        return [
            f for f in os.listdir(self.inbox_dir) 
            if os.path.isfile(os.path.join(self.inbox_dir, f)) and not f.startswith('.')
        ]
