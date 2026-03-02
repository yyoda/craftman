import os
import time
import logging
import sys
from agents.inbox_manager import InboxManager
from agents.document_architect import DocumentArchitectAgent

# Configuration
INBOX_DIR = "inbox"
DRAFTS_DIR = "drafts"
OUTPUTS_DIR = "outputs"
ARCHIVE_DIR = "archive"
REFERENCES_DIR = "references"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('Main')

def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [INBOX_DIR, DRAFTS_DIR, OUTPUTS_DIR, ARCHIVE_DIR, REFERENCES_DIR]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            # logger.info(f"Created directory: {d}")

def process_single_file(filepath, architect):
    logger.info(f"Processing file: {filepath}")
    try:
        architect.process_file(filepath)
        
        # Move source file to archive
        filename = os.path.basename(filepath)
        archive_path = os.path.join(ARCHIVE_DIR, filename)
        
        # Handle duplicate archive names (simple rename strategy)
        if os.path.exists(archive_path):
            name, ext = os.path.splitext(filename)
            timestamp = time.strftime("%Y%m%d%H%M%S")
            archive_path = os.path.join(ARCHIVE_DIR, f"{name}_{timestamp}{ext}")

        os.rename(filepath, archive_path)
        logger.info(f"Archived input file to: {archive_path}")

    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")

def interactive_menu(inbox_mgr, architect):
    while True:
        print("\n=== Craftsman Engine Menu ===")
        print("1. Scan Inbox (List files)")
        print("2. Process ALL files in Inbox")
        print("3. Process specific file")
        print("q. Quit")
        
        choice = input("Select an option > ").strip().lower()
        
        if choice == '1':
            files = inbox_mgr.list_files()
            if files:
                print(f"\n[Files in {INBOX_DIR}]")
                for i, f in enumerate(files, 1):
                    print(f"{i}. {f}")
            else:
                print("\n[Inbox is empty]")

        elif choice == '2':
            files = inbox_mgr.scan_files()
            if not files:
                print("\n[No files to process]")
                continue
            
            confirm = input(f"Are you sure you want to process {len(files)} files? (y/n) > ")
            if confirm.lower() == 'y':
                for fp in files:
                    process_single_file(fp, architect)
                print("\n[All files processed]")
        
        elif choice == '3':
            files = inbox_mgr.list_files()
            if not files:
                print("\n[No files to process]")
                continue
            
            print(f"\n[Select file to process]")
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
            
            try:
                idx_str = input("Enter file number (or 0 to cancel) > ").strip()
                if not idx_str.isdigit():
                    continue
                idx = int(idx_str)
                if idx == 0:
                    continue
                
                if 1 <= idx <= len(files):
                    filename = files[idx-1]
                    filepath = os.path.join(INBOX_DIR, filename)
                    process_single_file(filepath, architect)
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

        elif choice == 'q':
            print("Exiting...")
            break
        
        else:
            print("Invalid option.")

def main():
    ensure_directories()
    
    # Initialize Agents
    inbox_mgr = InboxManager(INBOX_DIR)
    architect = DocumentArchitectAgent(template_dir=REFERENCES_DIR, output_dir=DRAFTS_DIR)
    
    # Check if CLI args are provided (future extension)
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'scan':
            files = inbox_mgr.list_files()
            for f in files: print(f)
            
        elif command == 'process-all':
            files = inbox_mgr.scan_files()
            for fp in files: process_single_file(fp, architect)
            
        else:
            print(f"Unknown command: {command}")
            print("Usage: python src/main.py [scan|process-all]")
    else:
        # Start interactive mode
        interactive_menu(inbox_mgr, architect)

if __name__ == "__main__":
    main()
