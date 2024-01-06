import os
import glob
import logging

import click

def parsing_xml(folder_path: str) -> list:
    """function to get all files xml
    :return: list[tuple(xml, image)]"""
    list_files = []
    for root, subdir, filenames in os.walk(folder_path):
        for file in filenames:
            if file.endswith(".xml"):
                xml_path = os.path.join(root, file)
                # Get the file name without the extension
                filename_without_extension, _ = os.path.splitext(file)
                # Use glob to find the corresponding image file
                image_pattern = os.path.join(root, filename_without_extension + '.*')
                image_paths = glob.glob(image_pattern)
                #remove xml
                image_paths = [path for path in image_paths if not path.endswith('.xml')]
                # Associate the XML file with the image file (if found)
                if image_paths:
                    image_path = image_paths[0]
                    list_files.append((xml_path, image_path))
    return list_files

def get_workers() -> int:
    """get half the available cpu cores if more of 3"""
    cpu_cores = os.cpu_count() // 2

    # Check if the result is greater than 3
    if cpu_cores > 3:
        logging.info(
            f"Using {str(cpu_cores)} workers for kraken engine", exc_info=True)
        return cpu_cores
    elif os.cpu_count() < 3:
        logging.error(
            f"CPU not powerful enough, need at least 3 cores to run kraken engine.", exc_info=True)
        click.echo(
                f"CPU not powerful enough, you need at least 3 cores to run kraken engine.")
    else:
        logging.info(
            f"Using 3 workers for kraken engine", exc_info=True)
        return 3