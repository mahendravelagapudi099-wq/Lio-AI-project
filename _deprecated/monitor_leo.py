# monitor_leo.py
import subprocess
import time
import os
import csv
from datetime import datetime

def get_leo_stats(pid):
    try:
        # Use tasklist to get memory info
        output = subprocess.check_output(['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV', '/NH']).decode()
        if not output.strip():
            return None
        reader = csv.reader([output])
        row = next(reader)
        # Memory is usually the 5th column in tasklist CSV output
        mem_str = row[4].replace(' K', '').replace(',', '')
        return int(mem_str)
    except Exception as e:
        print(f"Error getting stats: {e}")
        return None

def main():
    # Attempt to start Leo if not running, or find PID
    # For this test, we assume we start it and get the PID
    print("Staritng monitoring...")
    
    # We will look for Main.py in tasklist (python processes)
    # This is a bit tricky, better to start it from this script
    
    log_file = "leo_soak_log.csv"
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Memory_KB"])
        
    print(f"Monitoring started. Logging to {log_file}")
    
    try:
        while True:
            # Find all python processes and check command line? 
            # Simplified: just look for 'python.exe' and assume it's Leo for this environment
            # Or better, let the user know we are monitoring.
            
            # Since I can't easily filter by command line across all OS versions without psutil,
            # I'll just check if any python process exists and take the largest one as a proxy
            # OR ask the user to provide the PID if multiple exist.
            
            output = subprocess.check_output(['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/NH']).decode()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            pids = []
            if output.strip():
                reader = csv.reader(output.strip().split('\n'))
                for row in reader:
                    mem = int(row[4].replace(' K', '').replace(',', ''))
                    pids.append(mem)
                
                total_mem = sum(pids)
                with open(log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([timestamp, total_mem])
                print(f"[{timestamp}] Total Python Memory: {total_mem} KB")
            else:
                print(f"[{timestamp}] No python processes found.")
                
            time.sleep(60) # Log every minute
    except KeyboardInterrupt:
        print("Monitoring stopped.")

if __name__ == "__main__":
    main()
