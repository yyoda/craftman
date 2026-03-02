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

def process_single_file(filepath, architect, auto_archive=False):
    logger.info(f"Processing file: {filepath}")
    
    # Check for guidelines to remind the Architect
    try:
        if os.path.exists(REFERENCES_DIR):
            guidelines = [f for f in os.listdir(REFERENCES_DIR) 
                          if not f.startswith('.') and 'guide' in f.lower()]
            if guidelines:
                print(f"🔔 Context Reminder: Apply rules from {', '.join(guidelines)} during generation.")
    except Exception:
        pass

    try:
        architect.process_file(filepath)
        print(f"✅ Draft created for {os.path.basename(filepath)}")
        
        # Move source file to archive
        if auto_archive:
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

def list_available_resources():
    """List templates and guidelines in references directory."""
    resources = {"templates": [], "guidelines": []}
    try:
        if not os.path.exists(REFERENCES_DIR):
            return resources
        
        for f in os.listdir(REFERENCES_DIR):
            if f.startswith('.'): continue
            
            f_lower = f.lower()
            if f_lower.endswith(('.docx', '.pptx', '.potx', '.dotx')):
                resources["templates"].append(f)
            elif f_lower.endswith(('.md', '.txt', '.pdf')) and 'guide' in f_lower:
                resources["guidelines"].append(f)
                
    except Exception as e:
        logger.error(f"Error checking resources: {e}")
    return resources

def interactive_menu(inbox_mgr, architect):
    while True:
        # Check resources on every loop to keep AI context fresh
        resources = list_available_resources()
        
        print("\n=== Craftsman Engine Menu ===")
        
        if resources["templates"]:
            print(f"📂 Custom Templates ({len(resources['templates'])}):")
            for t in resources["templates"]:
                print(f"   - references/{t}")
            print("   👉 AI Note: Prioritize these over default templates.")
        
        if resources["guidelines"]:
            print(f"📘 Style Guidelines ({len(resources['guidelines'])}):")
            for g in resources["guidelines"]:
                print(f"   - references/{g}")
            print("   👉 AI Note: Read these guidelines using 'read_file' before generating content.")
            
        if resources["templates"] or resources["guidelines"]:
             print("-----------------------------")
        print("1. [Input Watcher] Scan Inbox (List files)")
        print("2. [Document Architect] Process ALL files (Draft Only)")
        print("3. [Document Architect] Process specific file (Draft Only)")
        print("4. [Delivery Manager] Archive processed inputs")
        print("q. Quit")
        
        choice = input("Select an option > ").strip().lower()
        
        if choice == '1':
            print("\n🤖 Input Watcher: Scanning for new data...")
            files = inbox_mgr.list_files()
            if files:
                print(f"[Files in {INBOX_DIR}]")
                for i, f in enumerate(files, 1):
                    filepath = os.path.join(INBOX_DIR, f)
                    size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
                    print(f"{i}. {f} ({size} bytes)")
                
                print("\n💡 Input Watcher Tip: Next, ask AI to Create a Plan.")
                print("   Example: 'Analyze inbox/FILE and save a plan to drafts/plan_FILE.md'")
            else:
                print("[Inbox is empty]")

        elif choice == '2':
            files = inbox_mgr.scan_files()
            if not files:
                print("\n[No files to process]")
                continue
            
            confirm = input(f"Generate drafts for {len(files)} files? (y/n) > ")
            if confirm.lower() == 'y':
                print("\n🤖 Document Architect: Starting batch draft generation...")
                for fp in files:
                    process_single_file(fp, architect, auto_archive=False)
                print("\n✅ Batch processing completed. Check 'drafts/' folder.")
        
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
                    
                    print(f"\n🤖 Document Architect: Processing {filename}...")
                    process_single_file(filepath, architect, auto_archive=False)
                    print(f"✅ Draft created. Original file remains in inbox.")
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Invalid input.")

        elif choice == '4':
            print("\n🤖 Delivery Manager: Moving processed files to archive...")
            files = inbox_mgr.list_files()
            if not files:
                print("[No files in inbox to archive]")
            else:
                # In a real scenario, we might want to select which files to archive
                confirm = input(f"Archive ALL {len(files)} files in inbox? (y/n) > ")
                if confirm.lower() == 'y':
                    for f in files:
                        src = os.path.join(INBOX_DIR, f)
                        dst = os.path.join(ARCHIVE_DIR, f)
                        
                        if os.path.exists(dst):
                             name, ext = os.path.splitext(f)
                             timestamp = time.strftime("%Y%m%d%H%M%S")
                             dst = os.path.join(ARCHIVE_DIR, f"{name}_{timestamp}{ext}")
                        
                        os.rename(src, dst)
                        print(f"Archived: {f}")
                    print("✅ Archive completed.")

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
