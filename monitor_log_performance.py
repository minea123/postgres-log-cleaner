import datetime
import re
import enum
from typing import List, Dict, Optional

# Define regex patterns to match the log format
log_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3} UTC) \[(\d+)\] (\w+@\w+)\s*(.*)"

# Define a duration threshold in ms (e.g., queries longer than 100ms)
SLOW_QUERY_THRESHOLD = 1.0


class ConnectionState(enum.Enum):
    Receive = 1
    Authenticated = 2,
    Authorized = 3,
    Disconnected = 4


class Connection:
    def __init__(self, from_host: str, connected_at: datetime.datetime = None, user: str = "", database: str = "",
                 pid=0,
                 authorized=True):
        self.from_host = from_host
        self.connected_at = connected_at
        self.user = user
        self.database = database
        self.authorized = authorized
        self.pid = pid
        self.session_time = ""
        self.client_port = 0
        self.method = ""
        self.state = ConnectionState.Receive

    def close_connection(self, session_time):
        # session_time, user, database, host, port
        self.session_time = session_time


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
        self.parameters = ""
        if line.startswith("LOG"):
            log_pattern = r'LOG: \s*(.*)'
            match = re.search(log_pattern, line)
            if match:
                self.line = match.group(1)

        elif line.startswith("DETAIL"):
            detail_pattern = r'DETAIL: \s*(.*)'
            match = re.search(detail_pattern, line)
            if match:
                self.line = match.group(1)
                self.parameters = match.group(1)

        self.duration = 0.0
        self.complete_duration = False
        self.detail = ""
        self.statement = ""
        self.host = ""
        self.port = 0

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
    # pattern = r'execute\s+(.*)'
    pattern = r"(execute\s+([^:]+)):(.*)"
    match = re.search(pattern, execute_str)
    if match:
        return match.group(2), match.group(3)
    return "", ""


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
        self.queues: Dict[int, List[Log]] = {}
        self.open_connections: Dict[int, List[Connection]] = {}
        self.close_connections: Dict[int, List[Connection]] = {}
        self.statements = []
        self.execute_query: Dict[int, Dict[str:Log]] = {}
        self.complete_logs: Dict[int, List[Log]] = {}
        self.complete_query: List[Statement] = []

    def allocate_connection(self, pid: int, conn: Connection):
        conn.pid = pid
        if pid in self.open_connections:
            self.open_connections[pid].append(conn)
        else:
            self.open_connections[pid] = []
            self.open_connections[pid].append(conn)

    def last_open_connection(self, pid: int) -> Optional[Connection]:
        if pid in self.open_connections:
            items = self.open_connections[pid]
            if len(items) > 0:
                return items[len(items) - 1]
        else:
            conn = Connection("")
            self.open_connections[pid] = [conn]
            return conn
        return None

    def remove_open_connection(self, pid: int, from_host="", database="", user="") -> Optional[Connection]:
        if pid not in self.open_connections:
            return None
        items = self.open_connections[pid]
        if len(items) > 0:
            open_conn = items[len(items) - 1]
            if open_conn:
                if open_conn.user == user and open_conn.database == database and open_conn.from_host == from_host:
                    items.remove(open_conn)
                    return open_conn
        return None

    def close_connection(self, pid: int, conn: Connection):
        if pid not in self.close_connections:
            self.close_connections[pid] = []
        self.close_connections[pid].append(conn)

    def add_log(self, pid: int, log: Log):
        if pid not in self.queues:
            self.queues[pid] = []
        self.queues[pid].append(log)

    def first_log(self, pid: int) -> Optional[Log]:
        if pid in self.queues:
            queue_items = self.queues.get(pid)
            if len(queue_items) > 0:
                first_item = queue_items[0]
                return first_item
        return None

    def remove_first_log(self, log: Log):
        if log.pid in self.queues:
            queue_items = self.queues.get(log.pid)
            try:
                queue_items.remove(log)
                if log.pid not in self.complete_logs:
                    self.complete_logs[log.pid] = []

                self.complete_logs[log.pid].append(log)
            except Exception as e:
                print(e)

    def log_final_statement(self, log: Log):
        last_conn = self.last_open_connection(log.pid)
        statement = Statement()
        if last_conn:
            statement.connection = last_conn
        statement.duration = log.duration
        statement.query = log.statement
        statement.params = log.parameters
        self.statements.append(statement)

    def add_running_query(self, pid: int, log: Log):
        if pid in self.execute_query:
            running = self.execute_query[pid]
            running[log.execute_id] = log
        else:
            self.execute_query[pid] = {}
            self.execute_query[pid][log.execute_id] = log

    def running_query(self, pid: int, execute_id) -> Optional[Log]:
        if pid in self.execute_query:
            running = self.execute_query[pid]
            if execute_id in running:
                return running[execute_id]
        return None

    def end_query(self, pid: int, execute_id, duration) -> Optional[Log]:
        if pid in self.execute_query:
            running = self.execute_query[pid]
            if execute_id in running:
                instance_query: Log = running[execute_id]
                del running[execute_id]
                instance_query.duration = instance_query.duration + duration
                # self.complete_query.append( instance_query)

        return None

    def clear_connection(self):
        for pid in list(self.close_connections.keys()):
            connections = self.close_connections[pid]
            print(f"remove len of connection : {len(connections)}")
            del self.close_connections[pid]

    def clear_queue(self):
        for pid in list(self.queues.keys()):
            items = self.queues.get(pid)
            for item in self.items:
                if item.complete_duration:
                    items.remove(item)
                    if len(items) == 0:
                        del self.queues[pid]



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
            if log_item.parameters != "":
                first_item = con_statements.first_log(pid)
                if first_item:
                    first_item.parameters = log_item.parameters
            elif log_item.line.startswith("duration:"):
                duration = parse_duration(log_item.line)
                first_item = con_statements.first_log(pid)
                if first_item:
                    first_item.complete_duration = True
                    first_item.duration = duration
                    con_statements.log_final_statement(first_item)
                    if first_item.execute_id != "":
                        con_statements.add_running_query(log_item.pid, first_item)
                    elif first_item.de_allocate != "":
                        con_statements.end_query(log_item.pid, log_item.execute_id, duration)
                    else:
                        print("check ", log_item)
                    con_statements.remove_first_log(first_item)
                con_statements.clear_queue()

            elif log_item.line.startswith("execute"):
                id, exec_str = parse_execution(log_item.line)
                log_item.statement = exec_str
                log_item.execute_id = id
                con_statements.add_log(log_item.pid, log_item)

            elif log_item.line.startswith("statement:"):
                statement_str = parse_statement(log_item.line)
                if statement_str.startswith("DEALLOCATE"):
                    action, id = statement_str.split(" ")
                    log_item.de_allocate = id
                    log_item.execute_id = id

                else:
                    log_item.statement = statement_str
                con_statements.add_log(log_item.pid, log_item)
                # statement: SELECT
                # statement: SELECT pg_catalog.pg_current_wal_lsn()
                # statement: SELECT pg_catalog.pg_is_in_recovery()

            elif log_item.line.startswith("connection authenticated:"):
                identity, method = parse_identity(log_item.line)
                conn = con_statements.last_open_connection(log_item.pid)
                if conn:
                    conn.user = identity
                    conn.method = method
                    conn.state = ConnectionState.Authenticated
            elif log_item.line.startswith("connection authorized:"):
                user, database = parse_authorized_user_database(log_item.line)
                conn = con_statements.last_open_connection(log_item.pid)
                if conn:
                    conn.user = user
                    conn.database = database
                    conn.state = ConnectionState.Authorized

            elif log_item.line.startswith("disconnection:"):
                session_time, user, database, host, port = parse_disconnection_info(log_item.line)
                last_open = con_statements.remove_open_connection(pid, host, database, user)
                if last_open:
                    last_open.session_time = session_time
                    last_open.state = ConnectionState.Disconnected
                    con_statements.close_connection(log_item.pid, last_open)

                con_statements.clear_connection()

        else:
            match = re.search(r"\[(\d+)\]\s*\[.*\]\s*LOG:\s*(.*)", line)
            if match:
                pid, statement = match.group(1), match.group(2)
                if statement.startswith("connection received:"):
                    host, port = parse_connection_info(statement)
                    connection = Connection(host, port)
                    con_statements.allocate_connection(pid, connection)
            else:
                if log_item and not log_item.complete_duration and log_item.statement != "":
                    log_item.append_statement(line)

    return con_statements


# Example usage
if __name__ == "__main__":
    # parse_slow_queries("./tests/postgresql-2024-09-17_044552.log")

    # # Load logs from file or input stream
    log_file_path = "./tests/postgresql-2024-09-17_044552.log"  # Replace with your log file path
    with open(log_file_path, 'r') as log_file:
        log_lines = log_file.readlines()

    slow_queries = parse_slow_queries(log_lines)
    print(slow_queries)
    #
    # # Output slow queries
    # for query in slow_queries:
    #     print(
    #         f"Timestamp: {query['timestamp']}, User: {query['user']}, DB: {query['db']}, Duration: {query['duration_ms']} ms")
    #     print(f"Query: {query['query']}")
    #     print("-" * 80)
