import re
import datetime
import time
from config import CONFIG
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
from elasticsearch import Elasticsearch
from telegram_message import send

log_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC) \[(\d+)\] (\w+@\w+)\s*(.*)"

log_file_pattern = 'postgresql-%Y-%m-%d_%H%M%S.log'

es = Elasticsearch(
    hosts=CONFIG.elastic_search,
    api_key=CONFIG.elastic_api_key
)


class LogFileHandler(FileSystemEventHandler):
    def __init__(self, log_filename):
        self.log_filename = log_filename

    def on_modified(self, event):
        if event.src_path == self.log_filename:
            self.read_new_lines()

    def read_new_lines(self):
        """Read new lines from the log file."""
        with open(self.log_filename, 'r') as file:
            # Move to the end of the file
            file.seek(0, os.SEEK_END)
            while True:
                line = file.readline()
                if not line:
                    break
                print(line, end='')  # Print new line without adding extra newline
                parse_log_line(line)


def get_latest_log_filename(base_directory):
    """Get the latest log filename matching the pattern in the base directory."""
    log_pattern = r'postgresql-\d{4}-\d{2}-\d{2}_\d{6}\.log'
    latest_file = None
    latest_time = 0

    for filename in os.listdir(base_directory):
        if re.match(log_pattern, filename):
            file_path = os.path.join(base_directory, filename)
            file_time = os.path.getmtime(file_path)
            if file_time > latest_time:
                latest_time = file_time
                latest_file = file_path

    return latest_file


def monitor_logs(base_directory):
    """Monitor the log file for changes."""
    current_filename = get_latest_log_filename(base_directory)
    if current_filename is None:
        print("No log files found in the specified directory.")
        return

    # Create an event handler
    event_handler = LogFileHandler(current_filename)
    observer = Observer()

    # Schedule the observer to monitor the directory containing the log files
    observer.schedule(event_handler, path=base_directory, recursive=False)
    observer.start()

    try:
        print(f"Monitoring: {current_filename}")
        while True:
            new_filename = get_latest_log_filename(base_directory)
            if new_filename and new_filename != current_filename:
                print(f"Switching to new log file: {new_filename}")
                current_filename = new_filename
                event_handler.log_filename = current_filename  # Update the event handler to the new file
            time.sleep(1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def parse_connection_info(connection_str: str):
    # Regular expression to extract host and port
    pattern = r"host=([\d.]+) port=(\d+)"
    match = re.search(pattern, connection_str)

    if match:
        host = match.group(1)
        port = match.group(2)
        return host, port
    return "", 0


def parse_log_line(line):
    match = re.search(r"\[(\d+)\]\s*\[.*\]\s*LOG:\s*(.*)", line)
    if match:
        pid, statement = match.group(1), match.group(2)
        if statement.startswith("connection received:"):
            host, port = parse_connection_info(statement)
            connected_at = datetime.datetime
            print(f"connected from{host} : ,{port} @ {connected_at}")
            document = {"host": host, "port": port, "connecting_at": connected_at}
            es.index(index=CONFIG.index_replica, body=document)
            if host not in CONFIG.white_list_ip:
                send(f"receive attempt login from iP : {host} to PostgresDb")


if __name__ == "__main__":
    monitor_logs("/var/lib/postgresql/14/main/pg_log")
