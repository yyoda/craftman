import os
import time
import logging
import json
import sys

# Add parent directory to sys.path to resolve imports when running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.inbox_manager import InboxManager
from src.agents.document_architect import DocumentArchitectAgent

# Configuration (Relative paths need care when called from tools)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_DIR = os.path.join(PROJECT_ROOT, "inbox")
DRAFTS_DIR = os.path.join(PROJECT_ROOT, "drafts")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "archive")
REFERENCES_DIR = os.path.join(PROJECT_ROOT, "references")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CraftsmanTools')

class CraftsmanTools:
    def __init__(self):
        self.inbox_mgr = InboxManager(INBOX_DIR)
        self.architect = DocumentArchitectAgent(template_dir=REFERENCES_DIR, output_dir=DRAFTS_DIR)
        self._ensure_directories()

    def _ensure_directories(self):
        dirs = [INBOX_DIR, DRAFTS_DIR, OUTPUTS_DIR, ARCHIVE_DIR, REFERENCES_DIR]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)

    def list_inbox_files(self):
        """
        Lists files currently available in the inbox.
        Returns a list of filenames.
        """
        try:
            files = self.inbox_mgr.list_files()
            logger.info(f"Listed {len(files)} files in inbox.")
            return files
        except Exception as e:
            logger.error(f"Error listing inbox: {e}")
            return []

    def process_file_by_name(self, filename):
        """
        Processes a specific file from the inbox by its name.
        """
        filepath = os.path.join(INBOX_DIR, filename)
        if not os.path.exists(filepath):
            return {"status": "error", "message": f"File not found: {filename}"}

        try:
            logger.info(f"Processing file: {filepath}")
            output_path = self.architect.process_file(filepath)
            
            # Archive the file
            archive_path = os.path.join(ARCHIVE_DIR, filename)
            if os.path.exists(archive_path):
                name, ext = os.path.splitext(filename)
                timestamp = time.strftime("%Y%m%d%H%M%S")
                archive_path = os.path.join(ARCHIVE_DIR, f"{name}_{timestamp}{ext}")
            
            os.rename(filepath, archive_path)
            
            return {
                "status": "success", 
                "message": "Document generated successfully.", 
                "output_path": output_path,
                "archived_input": archive_path
            }
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            return {"status": "error", "message":Str(e)}

    def process_all_files(self):
        """
        Processes all files in the inbox.
        Returns a summary report.
        """
        files = self.inbox_mgr.list_files()
        results = []
        
        for filename in files:
            res = self.process_file_by_name(filename)
            results.append({"filename": filename, "result": res})
            
        return results

# Expose functions for potential direct import or tool wrapping
_tools = CraftsmanTools()

def list_files_tool():
    """Wrapper function to list files in inbox."""
    return _tools.list_inbox_files()

def process_file_tool(filename):
    """Wrapper function to process a single file."""
    return _tools.process_file_by_name(filename)

def process_all_tool():
    """Wrapper function to process all files."""
    return _tools.process_all_files()

if __name__ == "__main__":
    # Simple test
    print("Files:", list_files_tool())
