import os
import shutil
import hashlib
import time
import argparse
import logging
from datetime import datetime

def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def sync_folders(source, replica, log_file):
    logging.info(f"Starting sync: {source} -> {replica}")

    for root, dirs, files in os.walk(source):
        replica_root = root.replace(source, replica, 1)

        for dir_name in dirs:
            replica_dir = os.path.join(replica_root, dir_name)
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)
                logging.info(f"Created directory: {replica_dir}")

        for file_name in files:
            source_file = os.path.join(root, file_name)
            replica_file = os.path.join(replica_root, file_name)

            if not os.path.exists(replica_file) or calculate_md5(source_file) != calculate_md5(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied/Updated file: {replica_file}")

    for root, dirs, files in os.walk(replica):
        source_root = root.replace(replica, source, 1)

        for file_name in files:
            replica_file = os.path.join(root, file_name)
            source_file = os.path.join(source_root, file_name)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed file: {replica_file}")

        for dir_name in dirs:
            replica_dir = os.path.join(root, dir_name)
            source_dir = os.path.join(source_root, dir_name)

            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                logging.info(f"Removed directory: {replica_dir}")

    logging.info("Sync completed")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Source folder path")
    parser.add_argument("replica", help="Replica folder path")
    parser.add_argument("interval", type=int, help="Sync interval in seconds")
    parser.add_argument("log_file", help="Log file path")

    args = parser.parse_args()

    logging.basicConfig(filename=args.log_file, level=logging.INFO, 
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    print(f"Sync started. Log file: {args.log_file}")
    
    try:
        while True:
            sync_folders(args.source, args.replica, args.log_file)
            print(f"Sync completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. "
                  f"Next sync in {args.interval} seconds.")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nSync stopped by user.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        logging.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
