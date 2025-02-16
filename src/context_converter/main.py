"""
Main entry point for HTML-to-Markdown conversion
"""

import logging
from context_converter.converter import HTMLToMarkdownConverter
from context_converter.formatter import DatasetFormatter
from context_converter.utils import load_json_files, save_output_in_chunks, chunk_dataset

async def main(
    input_pattern: str = "output*.json",
    chunk_size: int = 500,
    output_file: str = "converted.md"
):
    """
    Execute conversion pipeline with configurable parameters
    
    :param input_pattern: Glob pattern for input JSON files
    :param chunk_size: Number of entries per processing chunk
    :param output_file: Name/path for output Markdown file
    """
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize components
        converter = HTMLToMarkdownConverter()
        formatter = DatasetFormatter(converter)
        
        # Async load
        data = await load_json_files(input_pattern)
        
        # Sync processing with chunked output
        for chunk in chunk_dataset(data, chunk_size):
            markdown_content = formatter.format_dataset(chunk)
            await save_output_in_chunks(output_file, markdown_content)
            
        logging.info(f"Successfully converted {len(data)} entries to {output_file}")
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())