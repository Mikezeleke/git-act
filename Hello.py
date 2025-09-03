import os
import argparse
import shutil
import time
import hashlib


def main():
    command_parser = argparse.ArgumentParser("Command line argument")

    command_parser.add_argument("source", help="path to source folder")
    command_parser.add_argument("replica", help="path to replica folder")
    command_parser.add_argument("interval", type=int, help="interval between synchronizations")
    command_parser.add_argument("amount", type=int, help="amount of synchronizations")
    command_parser.add_argument("logfile", help="path to logfile")

    try:
        args = command_parser.parse_args()
    except ValueError as e:
        print("Argument error ", e)
        return

    if not os.path.exists(args.source) or not os.path.isdir(args.source):
        print(f"'{args.source}' does not exist")
        return

    for i in range(args.amount):
        sync_folders(args.source, args.replica, args.logfile)
        if i < args.amount:
            time.sleep(args.interval)

    hashfile(args.source)


def sync_folders(source, replica, log_path):
    if not os.path.exists(replica):
        os.makedirs(replica, exist_ok=True)
        logfile(f"created a replica folder: '{replica}'", log_path)

    if not os.access(replica, os.W_OK):
        logfile(f"permission required '{replica}'", log_path)
        return

    for entry in os.listdir(source):
        source_list_path = os.path.join(source, entry)
        replica_list_path = os.path.join(replica, entry)
        if os.path.isdir(source_list_path):
            if not os.path.exists(replica_list_path):
                os.makedirs(replica_list_path, exist_ok=True)
                logfile(f"Created folder'{replica_list_path}'", log_path)
            sync_folders(source_list_path, replica_list_path, log_path)
        else:
            if not os.path.exists(replica_list_path):
                shutil.copy(source_list_path, replica_list_path)
                logfile(f"Copied file from'{source_list_path}' to '{replica_list_path}'", log_path)

    for item in os.listdir(replica):
        source_list_path = os.path.join(source, item)
        replica_list_path = os.path.join(replica, item)
        if not os.path.exists(source_list_path):
            if os.path.isfile(replica_list_path):
                os.remove(replica_list_path)
                logfile(f"Removed file '{replica_list_path}'", log_path)
            else:
                shutil.rmtree(replica_list_path)
                logfile(f"Removed folder '{replica_list_path}'", log_path)


def logfile(output, log_path):
    print(output)

    try:
        with open(log_path, "a") as log_file:
            log_file.write(output + "\n")
    except Exception as e:
        print("unable to log to file:", e)


def hashfile(source):
    for file in os.listdir(source):
        source_path = os.path.join(source, file)
        if os.path.isdir(source_path):
            hashfile(source_path)
        elif os.path.isfile(source_path):
            try:
                with open(source_path, "rb") as h:
                    open_file = h.read()
                hashed_file = hashlib.md5(open_file).hexdigest()
                print(hashed_file)

            except Exception as e:
                print("Couldn't hash this file: ", e)

            break


if __name__ == "__main__":
    main()


