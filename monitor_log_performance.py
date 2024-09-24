import datetime
import re
from typing import List, Dict, Optional

# Define regex patterns to match the log format
log_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC) \[(\d+)\] (\w+@\w+)\s*(.*)"

# Define a duration threshold in ms (e.g., queries longer than 100ms)
SLOW_QUERY_THRESHOLD = 1.0


class Connection:
    def __init__(self, from_host: str, connected_at: datetime.datetime, user: str, database: str, pid="",
                 authorized=True):
        self.from_host = from_host
        self.connected_at = connected_at
        self.user = user
        self.database = database
        self.authorized = authorized
        self.pid = pid
        self.session_time = ""
        self.client_port = 0
        


class Statement:
    def __init__(self):
        self.connection: Optional[Connection] = None
        self.query = ""
        self.duration = 0.0
        self.params = ""


class Log:
    def __init__(self, date, pid, user_at_db, line=""):
        self.date = date
        self.pid = pid
        self.user_at_db = str(user_at_db)
        user, db = self.user_at_db.split("@")
        self.user = user
        self.db = db
        self.line = line
        self.duration = 0.0
        self.complete_duration = False
        self.detail = ""
        self.statement = ""
        self.host = ""
        self.port = 0
        self.parameters = ""
        self.execute_id = ""
        self.de_allocate = ""
        self.deallocate_duration = 0.0

    def append_statement(self, line):
        self.statement = f"{self.statement} \n {line}"

    def add_duration(self, duration: float):
        self.duration = duration
        self.complete_duration = True


def parse_duration(duration_str):
    # Regular expression to extract the numeric part of the duration
    pattern = r"duration: ([\d.]+) ms"
    match = re.search(pattern, duration_str)

    if match:
        ms = float(match.group(1))  # Extract duration in milliseconds
        return ms
    return 0.0


# connection received: host=172.31.9.23 port=60802
def parse_connection_info(connection_str: str):
    # Regular expression to extract host and port
    pattern = r"host=([\d.]+) port=(\d+)"
    match = re.search(pattern, connection_str)

    if match:
        host = match.group(1)
        port = match.group(2)
        return host, port
    return "", 0


# identity="appdev" method=md5 (/etc/postgresql/14/main/pg_hba.conf:105)
def parse_identity(line: str):
    pattern = r'identity="([^"]+)" method=(\w+)'
    match = re.search(pattern, line)
    if match:
        return match.group(1), match.group(2)


# 2024-09-17 04:45:54.676 UTC [1034989] appdev@sms_mjqe_prod LOG:  connection authorized: user=appdev database=sms_mjqe_prod SSL enabled (protocol=TLSv1.3, cipher=TLS_AES_256_GCM_SHA384, bits=256)
def parse_authorized_user_database(log_str):
    # Regular expression to extract user and database
    pattern = r'user=([\w]+) database=([\w]+)'
    match = re.search(pattern, log_str)

    if match:
        user = match.group(1)
        database = match.group(2)
        return user, database
    return "", ""


# LOG:  statement: DEALLOCATE pdo_stmt_0000000a
def parse_statement(log_str):
    # Regular expression to capture the string after 'statement:'
    pattern = r'statement:\s*(.*)'
    match = re.search(pattern, log_str)
    if match:
        return match.group(1)
    else:
        return None


def parse_execution(execute_str: str):
    pattern = r'execute\s+(.*)'
    match = re.search(pattern, execute_str)
    if match:
        return match.group(1)
    return ""


def parse_disconnection_info(log_str):
    # Regular expression to capture session time, user, database, host, and port
    pattern = r'disconnection: session time: (\d+:\d+:\d+\.\d+) user=(\w+) database=(\w+) host=([\d\.]+) port=(\d+)'
    match = re.search(pattern, log_str)

    if match:
        session_time = match.group(1).strip()
        user = match.group(2).strip()
        database = match.group(3).strip()
        host = match.group(4).strip()
        port = match.group(5).strip()
        return session_time, user, database, host, port
    return "", "", "", "", "0"


class ConstructStatement:
    def __init__(self):
        self.items: List[Log] = []
        self.queues: Dict[str, List[Log]] = {}
        self.open_connections: Dict[str, List[Connection]] = {}
        self.close_connections: Dict[str, List[Connection]] = {}

    def last_log(self, pid: str):
        if pid in self.queues:
            queue_items = self.queues.get(pid)
            if len(queue_items) > 0:
                first_item = queue_items[0]
                return first_item



# Function to parse logs
def parse_slow_queries(log_lines):
    con_statements = ConstructStatement()
    current_query = None
    log_item = None
    for line in log_lines:
        log_match = re.match(log_pattern, line)
        if log_match:
            print(f"matched : {log_match.groups()}")
            str_date, pid, user_at_db, statement_string = log_match.groups()
            log_item = Log(str_date, pid, user_at_db, statement_string)
            if log_item.line.startswith("duration:"):
                duration = parse_duration(log_item.line)
                last_item = con_statements.last_log(pid)
                if last_item:
                    last_item.complete_duration = True
                    last_item.duration = duration

            elif log_item.line.startswith("execute"):
                exec_str = parse_execution(log_item.line)
                id, query = exec_str.split(":")

            elif log_item.line.startswith("statement:"):
                statement_str = parse_statement(log_item.line)
                _, id = statement_str.split(" ")
            elif log_item.line.startswith("connection received:"):
                host, port = parse_connection_info(log_item.line)
            elif log_item.line.startswith("connection authenticated:"):
                identity, method = parse_identity(log_item.line)
            elif log_item.line.startswith("connection authorized:"):
                user, database = parse_authorized_user_database(log_item.line)
            elif log_item.line.startswith("disconnection:"):
                session_time, user, database, host, port = parse_disconnection_info(log_item.line)


        else:
            if log_item and not log_item.complete_duration and log_item.statement != "":
                log_item.append_statement(line)

    # Check if the line has a duration
    # duration_match =
    # if duration_match:
    #     duration = float(duration_match.group("duration"))
    #     timestamp = duration_match.group("timestamp")
    #     user = duration_match.group("user")
    #     db = duration_match.group("db")
    #
    #     # If a query follows this duration, we assume the query is related to the same duration
    #     if current_query:
    #         if duration >= SLOW_QUERY_THRESHOLD:
    #             slow_queries.append({
    #                 'timestamp': timestamp,
    #                 'user': user,
    #                 'db': db,
    #                 'duration_ms': duration,
    #                 'query': current_query
    #             })
    #         current_query = None
    #     continue
    #
    # # Check if the line contains a query statement
    # query_match = query_pattern.search(line)
    # if query_match:
    #     current_query = query_match.group("query")

    return slow_queries


# Example usage
if __name__ == "__main__":
    # parse_slow_queries("./tests/postgresql-2024-09-17_044552.log")

    # # Load logs from file or input stream
    log_file_path = "./tests/postgresql-2024-09-17_044552.log"  # Replace with your log file path
    with open(log_file_path, 'r') as log_file:
        log_lines = log_file.readlines()

    slow_queries = parse_slow_queries(log_lines)
    #
    # # Output slow queries
    # for query in slow_queries:
    #     print(
    #         f"Timestamp: {query['timestamp']}, User: {query['user']}, DB: {query['db']}, Duration: {query['duration_ms']} ms")
    #     print(f"Query: {query['query']}")
    #     print("-" * 80)
