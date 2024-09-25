import psycopg2
import logging
from config import CONFIG
from telegram_message import send


def get_replication_status():
    connection = psycopg2.connect(
        host=CONFIG.db_master,
        port=CONFIG.db_master_port,
        database=CONFIG.db_master_db,
        user=CONFIG.db_master_user,
        password=CONFIG.db_master_password
    )
    cursor = connection.cursor()
    connected_slaves = {}
    try:
        sql = """ SELECT 
            client_addr, 
            state, 
            sync_state,
            sent_lsn,
            write_lsn,
            flush_lsn,
            replay_lsn,
			replay_lag,
			write_lag,
			flush_lag
         
            FROM pg_stat_replication;"""
        # Execute the query
        cursor.execute(sql)

        # Fetch and print results
        rows = cursor.fetchall()
        for row in rows:
            client_ip, state, sync_state, sent_lsn, write_lsn, flush_lsn, replay_lsn, replay_lag, write_lag, flush_lag = row
            logging.info(f"Replication Info: {row}")
            print(f"Client Address: {row[0]}")
            print(f"State: {row[1]}")
            print(f"Sync State: {row[2]}")
            print(f"Sent LSN: {row[3]}")
            print(f"Write LSN: {row[4]}")
            print(f"Flush LSN: {row[5]}")
            print(f"Replay LSN: {row[6]}")
            print(f"Replay Lag: {row[7]}")
            print(f"Write Lag: {row[8]}")
            print(f"Flush Lag: {row[9]}")
            print("\n")
            if replay_lag.seconds > 0 or write_lag.seconds > 0 or flush_lag.seconds > 0:
                send(
                    f"postgres db slave nodes [{client_ip}]  state: {state} ,sync : {sync_state} , sent_lsn:{sent_lsn},write_lsn:{write_lsn}, flush_lsn:{flush_lsn} has delay or lag replay_lag\t:{replay_lag} , \t write_lag: {write_lag} \t flush_lag : {flush_lag}")
            connected_slaves[client_ip] = True
        cursor.close()
        connection.close()

    except Exception as e:
        logging.error(f"error connecting to postgresql {e}")
    config_slaves = CONFIG.db_slaves.split(",")
    for slave_ip in config_slaves:
        if slave_ip not in connected_slaves:
            send(f"postgres db slave nodes {slave_ip} not connected to master : {CONFIG.db_master} as replica, please "
                 f"check!")


if __name__ == "__main__":
    get_replication_status()
