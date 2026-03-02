# Craftsman Core Skill
This skill allows the AI agent to interact directly with the Craftsman Document Generation Engine.
It provides capabilities to scan the inbox for new data files and trigger the document generation process for specific files or all pending files.

## Tools

### list_inbox_files
Lists all files currently waiting in the `inbox/` directory. Use this to check what needs processing.
- Returns: A list of filenames.

### process_file
Triggers the document generation process for a single specified file.
- Parameters:
  - `filename`: The name of the file in the inbox to process (e.g., "data.json").
- Returns: A JSON object containing status, message, output path, and archive path.

### process_all_files
Triggers the document generation process for ALL files currently in the inbox.
- Returns: A list of result objects for each processed file.

## Web Research & Data Collection
You can help the user by gathering information from the web and placing it into the inbox.
When the user asks to "Research topic X" or "Find data about Y":

1. Use your search tools to gather relevant information.
2. Structure the findings into a JSON or Markdown file.
   - For JSON, include fields like `title`, `summary`, `content`, `source_urls`.
   - For Markdown, use headers and bullet points.
3. Save this file to the `inbox/` directory using the `create_file` tool.
   - Example path: `inbox/research_topic_x.json`
4. Inform the user that the data has been collected and is ready for processing.

## Usage Guidelines
- When a user asks "Check for new files" or "What's in the inbox?", use `list_inbox_files`.
- When a user asks to "Process the report" or "Generate document from [file]", use `process_file`.
- If the user says "Run everything" or "Process all", use `process_all_files`.
- Always report the result of the operation back to the user, including the path of the generated document.
