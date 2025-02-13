"""
Main entry point for HTML-to-Markdown conversion pipeline.
Handles file processing and chunked output writing.
"""

import logging
import asyncio
from converter import HTMLToMarkdownConverter
from formatter import DatasetFormatter
from utils import load_json_files, save_output_in_chunks, chunk_dataset

async def main(
    input_pattern: str = "output*.json",
    chunk_size: int = 1000,
    output_file: str = "converted_output.md"
):
    """
    Execute conversion pipeline with configurable parameters.
    
    Args:
        input_pattern: Glob pattern for input JSON files
        chunk_size: Number of entries per processing chunk
        output_file: Name/path for output Markdown file
    """
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize core components
        converter = HTMLToMarkdownConverter()
        formatter = DatasetFormatter(converter)
        
        # Load and process data
        data = await load_json_files(input_pattern)
        for chunk in chunk_dataset(data, chunk_size):
            markdown_content = await formatter.format_dataset(chunk)
            await save_output_in_chunks(output_file, markdown_content)
            
        logging.info("Conversion completed successfully")
        
    except Exception as e:
        logging.error(f"Fatal error in main pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())