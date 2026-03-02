import os
import shutil
import time
import logging
import json
import yaml
import pandas as pd
from jinja2 import Environment, FileSystemLoader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DocumentArchitect')

class DocumentArchitectAgent:
    def __init__(self, template_dir, output_dir):
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def generate_document(self, input_data, template_name, output_filename):
        """
        Generates a document from input data using a template.
        """
        try:
            logger.info(f"Generating document using template: {template_name}")
            template = self.env.get_template(template_name)
            content = template.render(data=input_data)
            
            output_path = os.path.join(self.output_dir, output_filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Document generated at: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate document: {e}")
            raise

    def process_file(self, filepath):
        """
        Main processing logic for a given file.
        Determines the type and calls appropriate generation method.
        Returns the output path of the generated document.
        """
        logger.info(f"Processing file: {filepath}")
        
        # Determine file type
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        output_path = None
        
        if ext == '.json':
            with open(filepath, 'r') as f:
                input_data = json.load(f)
            
            # Use 'report_template.md' by default for now
            output_path = self.generate_document(input_data, 'report-template.md', f"{name}_report.md")
        
        elif ext == '.yaml' or ext == '.yml':
            with open(filepath, 'r') as f:
                input_data = yaml.safe_load(f)
            output_path = self.generate_document(input_data, 'report-template.md', f"{name}_report.md")

        elif ext == '.csv':
            logger.info("Detected CSV file. Processing as raw data list.")
            import pandas as pd
            df = pd.read_csv(filepath)
            input_data = df.to_dict(orient='records')
            # For now, just generate a simple report
            report_data = {
                "title": f"CSV Report: {name}",
                "content": f"Found {len(input_data)} records.",
                "summary": "This report was generated from CSV data.",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            output_path = self.generate_document(report_data, 'report-template.md', f"{name}_report.md")
        
        elif ext == '.xlsx':
             logger.info("Detected Excel file. Processing first sheet.")
             import pandas as pd
             df = pd.read_excel(filepath)
             input_data = df.to_dict(orient='records')
             report_data = {
                "title": f"Excel Report: {name}",
                "content": f"Found {len(input_data)} records from first sheet.",
                "summary": "This report was generated from Excel data.",
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
             output_path = self.generate_document(report_data, 'report-template.md', f"{name}_report.md")

        else:
            logger.warning(f"Unsupported file type: {ext}")
            return None
            
        return output_path


if __name__ == "__main__":
    # Test
    agent = DocumentArchitectAgent("./references", "./drafts")
    # Mock data
    data = {"title": "Test Report", "content": "This is a test."}
    # agent.generate_document(data, 'report-template.md', 'test_report.md')
