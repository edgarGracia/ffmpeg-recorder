import argparse
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from loguru import logger


@logger.catch
def extract_date(
    file_path: Path,
    date_re: str,
    date_format: str
) -> datetime | None:
    """Extract a datetime from a file path.

    Args:
        file_path (Path): Path to a file.
        date_re (str): Regular expression of the date in the filename.
        date_format (str): Date format.

    Returns:
        datetime | None: A datetime object or None
    """
    match = re.search(date_re, file_path.stem)
    if match:
        date = match.group(0)
        date = datetime.strptime(date, date_format)
        return date
    else:
        return None


@logger.catch
def list_files(
    root_path: Path,
    file_extensions: list[str],
    date_re: str,
    date_format: str,
    files={}
) -> dict:
    """Recursively list all the files in a folder. Return a dict for each one
    with its size and date (parsed from the filename).

    Args:
        root_path (Path): Root path to start listing files.
        file_extensions (list[str]): List of file extensions to list.
        date_re (str): Regular expression for the date in the filenames.
        date_format (str): Date format in the filenames.
        files (dict, optional): Dict where the listed files will be added.
            Defaults to {}.

    Returns:
        dict: A dict where each key is a file path and values are dicts with
            the size in bytes and the parsed datetime object.
    """
    for file in root_path.iterdir():
        if file.is_file():
            if file.suffix.lower() in file_extensions:
                size = file.stat().st_size
                date = extract_date(file, date_re, date_format)
                if date is None:
                    logger.warning(f"Can not parse date from File {file}")
                else:
                    files[file] = {"size": size, "date": date}
        elif file.is_dir():
            list_files(file, file_extensions, date_re, date_format, files)
    return files


@logger.catch
def remove_file(file_path: Path):
    """Remove a file.

    Args:
        file_path (Path): File path to remove.
    """
    logger.debug(f"Removing {file_path}")
    file_path.unlink()


@logger.catch
def remove_old(files: dict, max_days: int) -> dict:
    """Remove the files older than the given days.

    Args:
        files (dict): Dict with the files.
        max_days (int): Maximum days a file can exists.

    Returns:
        dict: The same ``files`` dict without the removed files.
    """
    max_old_date = datetime.now() - timedelta(days=max_days)
    file_paths = list(files.keys())
    for file_path in file_paths:
        date = files[file_path]["date"]
        if date < max_old_date:
            remove_file(file_path)
            del (files[file_path])
    return files


@logger.catch
def remove_bigger(files: dict, max_size: int) -> dict:
    """Remove the oldest files when the total size of all the files is greater
    than ``max_size``.

    Args:
        files (dict): Dict with the files.
        max_size (int): Total maximum size.

    Returns:
        dict: The same ``files`` dict without the removed files.
    """
    total_size = sum([f["size"] for f in files.values()])
    if total_size > max_size:
        logger.info(f"Maximum size reached ({total_size} > {max_size})")

        # Sort files by date
        file_paths_list = sorted(
            list(files.keys()), key=lambda x: files[x]["date"]
        )

        # Remove the oldest file until the total size is lower than ``max_size``
        while file_paths_list and total_size > max_size:
            first_file = file_paths_list.pop(0)
            size = files[first_file]["size"]
            total_size -= size
            remove_file(first_file)
            del(files[first_file])

    return files


def main(config_path: Path):
    """Periodically list the files in a folder recursively and:
    a) delete those that exceeds a maximum existence time.
    b) when a maximum total size is reached, delete the oldest ones.

    Args:
        config_path (Path): Path to the configuration yaml.
    """
    logger.info("Storage Manager started")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info(f"Using config:\n{config}")

    files_path = Path(config["files_path"])
    file_extensions = [str(e).lower() for e in config["file_extensions"]]
    max_days = config["max_days"]
    max_size = config["max_size"]
    update_time = float(config["update_time"])

    while True:
        # List file
        files = list_files(
            files_path,
            file_extensions,
            config["date_re"],
            config["date_format"]
        )

        # Check time limit
        if max_days is not None:
            files = remove_old(files, float(max_days))

        # Check size limit
        if max_size is not None:
            files = remove_bigger(files, float(max_size))
        
        time.sleep(update_time)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("storage_config.yaml")
    )
    ap.add_argument(
        "-l",
        "--log-level",
        default="INFO"
    )
    args = ap.parse_args()
    logger.remove()
    logger.add(sys.stderr, level=args.log_level)
    main(args.config)
