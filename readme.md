# Postgres Log & WAL File Cleaner

This Python script is designed to clean up old files (older than a specific age) in a given directory. It is primarily used for cleaning PostgreSQL log files and WAL (Write-Ahead Log) files to free up disk space. The project also includes cron scripts to easily schedule cleanups and offers a to-do list for future improvements like monitoring PostgreSQL, pgpool2, and sending alerts for slow queries.

## Features
- **Delete files older than a specific age**: Specify how many days old the files should be before they are deleted.
- **Configurable directory**: The base directory for cleaning can be specified via command-line arguments or through a `config.properties` file.
- **Crontab ready scripts**: Two shell scripts (`cron_clean_pg_log.sh` and `cron_clean_old_wal.sh`) are provided for easy scheduling using cron jobs.
- **Primarily for PostgreSQL**: Clean up PostgreSQL log files and WAL files, but can be adapted for other file types as well.

## To-Do List

### Planned Enhancements
- **Monitor slow queries**: Track slow queries by analyzing the PostgreSQL `pg_log` files, and send alerts if slow queries exceed a defined threshold.
- **Monitor synchronization status**: Monitor and log the sync status between the master and slave PostgreSQL nodes, and raise alerts if any synchronization issues are detected.
- **Monitor pgpool2 status**:
    - Check if pgpool2 is up or down.
    - Monitor the active and standby node status in pgpool2 and send alerts if there's a failure or unexpected state.
- **Email notifications**: Send email alerts for slow queries, node synchronization failures, or pgpool2 issues (e.g., master node down, failover issues).

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
    - [Command-Line Arguments](#command-line-arguments)
    - [Using Configuration File](#using-configuration-file)
- [Crontab Setup](#crontab-setup)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Requirements
- Python 3.x
- `os`, `sys`, `shutil`, `datetime` Python libraries (standard libraries)
- `psycopg2` (optional, for querying PostgreSQL databases directly in future enhancements)
- `smtplib` (optional, for sending email alerts)

## Installation
Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/engleangs/postgres-log-cleaner
cd postgres-log-cleaner
```

Make sure Python 3 is installed on your system.

## Usage

### Command-Line Arguments

You can run the script by specifying the base directory and file age via command-line arguments:

```bash
python clean_logs.py -d /path/to/logs -a 30
```

- `-d`: The base directory where the script will search for old files.
- `-a`: The age in days. Files older than this will be deleted.

### Using Configuration File

Alternatively, you can use a `config.properties` file to provide the directory and file age:

1. Create a `config.properties` file in the project root with the following content:

   ```
   clean_path=/path/to/logs
   age=30
   ```

2. Run the script without arguments:

   ```bash
   python clean_logs.py
   ```

If no arguments are provided and no `config.properties` file is found, the script will prompt for the directory and age.

## Crontab Setup

You can automate the cleanup process using the provided cron scripts. Two scripts are available:

1. **`cron_clean_pg_log.sh`**: Cleans up PostgreSQL log files.
2. **`cron_clean_old_wal.sh`**: Cleans up old WAL files.

### Adding to Crontab

To schedule these scripts using cron:

1. Edit the crontab file:
   ```bash
   crontab -e
   ```

2. Add the following lines to schedule the cleanup:

   ```bash
   # Clean PostgreSQL log files every day at 2 AM
   0 2 * * * /path/to/cron_clean_pg_log.sh

   # Clean old WAL files every Sunday at 3 AM
   0 3 * * 0 /path/to/cron_clean_old_wal.sh
   ```

Make sure the scripts are executable:
```bash
chmod +x cron_clean_pg_log.sh
chmod +x cron_clean_old_wal.sh
```

### Sample `cron_clean_pg_log.sh`:

```bash
#!/bin/bash
python /path/to/clean_logs.py -d /var/lib/postgresql/data/pg_log -a 30
```

### Sample `cron_clean_old_wal.sh`:

```bash
#!/bin/bash
python /path/to/clean_logs.py -d /var/lib/postgresql/data/pg_wal -a 7
```

## Configuration

The `config.properties` file supports the following properties:

- `directory`: The base directory for file cleanup.
- `age`: The age threshold (in days) for deleting old files.

Example `config.properties`:

```properties
clean_path=/var/lib/postgresql/data/pg_log
age=30
```

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue.

1. Fork the repository
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to adjust the content as needed, and replace placeholder paths with your actual paths and repository URLs!