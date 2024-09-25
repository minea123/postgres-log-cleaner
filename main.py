import argparse
import config
import clean_file
import logging
import telegram_message


def main():
    parser = argparse.ArgumentParser(description="Process clean file especially logs or old wal file")
    parser.add_argument("--d", type=str, help="base directory", required=False)
    parser.add_argument("--a", type=int, help="duration in day", required=False)
    arg = parser.parse_args()
    logging.debug(f"Reading config file from :{config.CONFIG.config_path}")
    base_directory = arg.d if arg.d else config.CONFIG.base_path
    duration = arg.a if arg.a else config.CONFIG.age
    logging.debug(f"base dir : {base_directory} , duration older than : {duration} days")
    total_file, total_file_size = clean_file.clean_file(base_directory, duration)
    logging.debug(f"Done clean file :")
    size_in_format = clean_file.format_file_size(total_file_size)
    logging.debug(f"Total file : {total_file} , size :  {size_in_format}")
    telegram_message.send(f" clean file at {base_directory} #: {total_file}, size: {size_in_format}")


if __name__ == "__main__":
    main()
