import os
import logging
import importlib.util
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DocumentArchitect')

class DocumentArchitectAgent:
    """
    Document Architect Agent.
    
    Responsible for executing "recipes" - Python scripts that generate documents.
    These recipes are picked up from the inbox and executed to produce drafts.
    """
    def __init__(self, inbox_dir, drafts_dir):
        self.inbox_dir = inbox_dir
        self.drafts_dir = drafts_dir
        
        # Ensure directories exist
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.drafts_dir, exist_ok=True)
        
        logger.info(f"Initialized DocumentArchitectAgent watching {self.inbox_dir}, outputting to {self.drafts_dir}")

    def execute_recipe(self, recipe_path):
        """
        Dynamically loads and executes a Python recipe file.
        The recipe file must have a `generate(output_dir)` function.
        """
        recipe_name = os.path.basename(recipe_path)
        logger.info(f"Executing recipe: {recipe_name}")
        
        try:
            # Load the module dynamically
            spec = importlib.util.spec_from_file_location("recipe_module", recipe_path)
            if spec is None or spec.loader is None:
                logger.error(f"Could not load spec for recipe: {recipe_path}")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for generate function
            if not hasattr(module, 'generate'):
                logger.error(f"Recipe {recipe_name} does not contain a 'generate(output_dir)' function.")
                return False
            
            # Execute generation
            logger.info(f"Calling generate() for {recipe_name}...")
            start_time = time.time()
            result = module.generate(self.drafts_dir)
            end_time = time.time()
            
            logger.info(f"Recipe {recipe_name} executed successfully in {end_time - start_time:.2f}s. Result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute recipe {recipe_name}: {e}", exc_info=True)
            return False

    def process_inbox(self):
        """
        Iterates over Python files in the inbox and executes them as recipes.
        """
        logger.info(f"Checking inbox {self.inbox_dir} for recipes...")
        try:
            files = [f for f in os.listdir(self.inbox_dir) if f.endswith('.py')]
        except FileNotFoundError:
             logger.warning(f"Inbox directory {self.inbox_dir} does not exist.")
             return []

        if not files:
            logger.info("No recipe files (.py) found in inbox.")
            return []

        results = []
        for filename in files:
            file_path = os.path.join(self.inbox_dir, filename)
            logger.info(f"Found recipe: {filename}")
            
            result = self.execute_recipe(file_path)
            results.append((filename, result))
            
        return results

if __name__ == "__main__":
    # simple test if run directly
    import argparse
    parser = argparse.ArgumentParser(description='Run Document Architect Agent')
    parser.add_argument('--inbox', default='inbox', help='Inbox directory')
    parser.add_argument('--drafts', default='drafts', help='Drafts directory')
    args = parser.parse_args()

    agent = DocumentArchitectAgent(args.inbox, args.drafts)
    agent.process_inbox()
