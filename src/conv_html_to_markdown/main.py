"""
This module serves as the main entry point for the HTML to Markdown conversion project.

It contains the main function which loads, processes, and saves the dataset. The processing involves converting HTML content to Markdown and formatting it into a structured form. The dataset is processed in chunks to optimize memory usage and performance.

The module also includes functions for processing individual chunks of the dataset and for processing and collecting data from all chunks in parallel using multithreading.

Functions:
    process_dataset_chunk(chunk): Processes a single chunk of the dataset.
    main(): Main function to load, process, and save the dataset.
    process_and_collect_data(chunks, max_threads): Process the data chunks in parallel and collect the results.
"""


import logging
from typing import List
from concurrent.futures import ThreadPoolExecutor
from typing import List
from converter import HTMLToMarkdownConverter
from formatter import DatasetFormatter
from utils import load_json_files, save_output_in_chunks, chunk_dataset


def process_dataset_chunk(chunk):
    """
    Processes a single chunk of the dataset.
    """
    try:
        formatter = DatasetFormatter(HTMLToMarkdownConverter())
        return formatter.format_dataset(chunk)
    except Exception as e:
        logging.error("Error processing dataset chunk: %s", e)
        return ""


def main(pattern: str = "output*.json", 
         chunk_size: int = 512, 
         max_threads: int = 15, 
         output_file_name: str = "gpt-crawler-curated_markdown.md") -> None:
    """
    Main function to load, process, and save the dataset.

    :param pattern: Pattern to match JSON files.
    :param chunk_size: Size of chunks to split the dataset into.
    :param max_threads: Maximum number of threads to use.
    :param output_file_name: Name of the output file.
    """
    logging.basicConfig(level=logging.INFO)

    try:
        original_data = load_json_files(pattern)
        chunks = list(chunk_dataset(original_data, chunk_size))
        formatted_contents = process_and_collect_data(chunks, max_threads)
        save_output_in_chunks(output_file_name, formatted_contents)
        logging.info("Conversion process successful. Exiting program.")
    except Exception as e:
        logging.error("An error occurred in the main function: %s", e)


def process_and_collect_data(chunks: List[Chunk], max_threads: int) -> List[Result]:
    """
    Process the data chunks in parallel and collect the results.

    Args:
        chunks (List[Chunk]): The list of data chunks to be processed.
        max_threads (int): The maximum number of threads to be used for parallel processing.

    Returns:
        List[Result]: The list of results obtained from processing each chunk.
    """
    logging.info("Processing and saving dataset in chunks.")
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        return [result for result in executor.map(process_dataset_chunk, chunks)]


if __name__ == "__main__":
    main()
