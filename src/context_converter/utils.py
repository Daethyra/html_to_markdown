"""
Utility functions for file handling and dataset management.
Maintains async I/O operations for better performance.
"""

import glob
import json
import aiofiles
import logging

async def load_json_files(pattern):
    """
    Load and merge JSON files matching glob pattern.
    
    Args:
        pattern: File matching pattern (e.g., "data/*.json")
        
    Returns:
        Combined list of JSON entries
    """
    aggregated = []
    for file_path in glob.glob(pattern):
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                content = await f.read()
                aggregated.extend(json.loads(content))
        except Exception as e:
            logging.error(f"Failed to load {file_path}: {str(e)}")
    return aggregated

async def save_output_in_chunks(file_path, content):
    """
    Append processed content to output file.
    
    Args:
        file_path: Output file path
        content: Markdown content to append
    """
    try:
        async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
            await f.write(content + "\n\n")
    except Exception as e:
        logging.error(f"Failed to write output: {str(e)}")

def chunk_dataset(data, chunk_size):
    """
    Split dataset into manageable chunks.
    
    Args:
        data: Full dataset list
        chunk_size: Entries per chunk
        
    Yields:
        Sequential chunks of dataset
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]