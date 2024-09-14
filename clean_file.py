import os
import re
from datetime import datetime, timedelta


# Function to check if a file is a PostgreSQL WAL file
def is_wal_file(filename: str):
    # PostgreSQL WAL file naming pattern (24 hex characters)
    wal_pattern = r'^[0-9A-Fa-f]{24}$'

    # Match the filename with the pattern
    if re.match(wal_pattern, filename):
        return True
    return False


def is_log_file(filename: str):
    return filename.endswith(".log")


def format_file_size(size_in_bytes):
    """
    Format the file size from bytes to a human-readable format (KB, MB, GB).

    :param size_in_bytes: File size in bytes.
    :return: Formatted file size as a string with appropriate unit.
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 ** 2:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 ** 3:
        return f"{size_in_bytes / 1024 ** 2:.2f} MB"
    else:
        return f"{size_in_bytes / 1024 ** 3:.2f} GB"


def get_file_age_and_size(file_path):
    """Calculate the age of the file in days based on the last modification time."""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Get the file's modification time
    file_mtime = os.path.getmtime(file_path)

    # Convert the modification time to a datetime object
    file_mtime_date = datetime.fromtimestamp(file_mtime)

    # Get the current date
    now = datetime.now()

    # Calculate the difference in days
    age = (now - file_mtime_date).days
    size = os.path.getsize(file_path)
    return age, size


def clean_file(directory='/var/lib/postgresql/14/main/pg_log', total_day=30):
    print(f"Begin to clean file older than {total_day} days in path : {directory}")
    if not os.path.exists(directory):
        raise Exception(f"Not found path : {directory}")
    # Directory where the files are located
    # Iterate through all files in the directory
    total_file = 0
    total_file_size = 0
    for filename in os.listdir(directory):
        if not is_wal_file(filename) and not is_log_file(filename):
            print(f"{filename} is not WAL file or log file")
            continue

        file_path = os.path.join(directory, filename)
        file_age, file_size = get_file_age_and_size(file_path)
        if file_age < total_day:
            try:
                # Delete the file
                os.remove(file_path)
                total_file += 1
                total_file_size += file_size
                print(f"Remove file :{file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")
    return total_file, total_file_size


def format_number(value, decimal_places=2):
    """
    Format a number with thousands separators and a specified number of decimal places.

    :param value: The number to format.
    :param decimal_places: The number of decimal places to include (default is 2).
    :return: Formatted number as a string.
    """
    # Format number with thousands separators and decimal places
    formatted_value = f"{value:,.{decimal_places}f}"
    return formatted_value


if __name__ == "__main__":
    # Example usage
    file_size_bytes = 123456789
    formatted_size = format_file_size(file_size_bytes)
    print(formatted_size)
    # Example usage
    number = 1234567
    formatted_number = format_number(number, decimal_places=2)
    print(formatted_number)
