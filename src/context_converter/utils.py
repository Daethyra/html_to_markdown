"""
File handling utilities with async I/O
"""

import glob
import json
import aiofiles
import logging

async def load_json_files(pattern):
    """
    Load and merge JSON files matching glob pattern
    
    :param pattern: File matching pattern (e.g., "data/*.json")
    :return: Combined list of JSON entries
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
    Append processed content to output file
    
    :param file_path: Output file path
    :param content: Markdown content to append
    """
    try:
        async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
            await f.write(content + "\n\n")
            logging.debug(f"Wrote {len(content)} chars to {file_path}")
    except Exception as e:
        logging.error(f"Failed to write output: {str(e)}")

def chunk_dataset(data, chunk_size):
    """
    Split dataset into memory-safe chunks
    
    :param data: Full dataset list
    :param chunk_size: Entries per chunk
    :yield: Sequential chunks of dataset
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]