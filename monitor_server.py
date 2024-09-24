import psutil

from telegram_message import send
import logging
from config import CONFIG


def check_disk_usage():
    """Check disk usage for all mounted partitions."""
    disk_partitions = psutil.disk_partitions()
    alert_triggered = False
    for partition in disk_partitions:
        usage = psutil.disk_usage(partition.mountpoint)
        usage_percentage = usage.percent

        if usage_percentage > CONFIG.disk_threshold:
            alert_triggered = True
            message = (f"WARNING: Disk usage on partition {partition.device} "
                       f"({partition.mountpoint}) is at {usage_percentage}%!")
            send(message)
    if not alert_triggered:
        logging.debug("All disks are within safe usage limits.")


def check_cpu_usage():
    """Check CPU usage percentage."""
    cpu_percentage = psutil.cpu_percent(interval=1)
    if cpu_percentage > CONFIG.cpu_threshold:
        message = f"WARNING: CPU usage is at {cpu_percentage}%!"
        send(message)
    else:
        logging.debug("CPU usage is within safe limits.")


def check_memory_usage():
    """Check memory (RAM) usage and report in GB."""
    memory = psutil.virtual_memory()

    # Convert memory values from bytes to GB
    total_memory_gb = memory.total / (1024 ** 3)
    available_memory_gb = memory.available / (1024 ** 3)

    # Calculate used memory as total - available
    used_memory_gb = total_memory_gb - available_memory_gb
    memory_percentage = (used_memory_gb / total_memory_gb) * 100

    logging.info(f"Total memory: {total_memory_gb:.2f} GB")
    logging.info(f"Used memory: {used_memory_gb:.2f} GB ({memory_percentage:.2f}% used)")
    logging.info(f"Available memory: {available_memory_gb:.2f} GB")

    if memory_percentage > CONFIG.memory_threshold:
        message = (f"WARNING: Memory usage is at {memory_percentage:.2f}%! "
                   f"Used memory: {used_memory_gb:.2f} GB out of {total_memory_gb:.2f} GB.")
        send(message)
    else:
        logging.debug("Memory usage is within safe limits.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    check_disk_usage()
    check_memory_usage()
    check_cpu_usage()
