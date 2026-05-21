# stress_test.py
# ANACONDA Daemon Memory Leak & Stress Test Harness
# Classification: BLACK PROJECT // SOVEREIGN

import os
import sys
import time
import subprocess
import psutil

# Configuration
RUNTIME_PATH = r"C:\RegimeOS\language\anaconda\bin\anaconda-runtime.py"
SCRIPT_PATH = r"C:\RegimeOS\language\anaconda\src\examples\financial_ingester.air"
LOG_PATH = r"C:\RegimeOS\language\anaconda\stress_test_log.md"
POLL_INTERVAL = 0.5  # 0.5 seconds sleep between ingester runs
MONITOR_DURATION = 180  # Monitor for 180 seconds (3 minutes)
LOG_INTERVAL = 30  # Log snapshot every 30 seconds (to capture enough data points in 3 minutes)

def initialize_log():
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        f.write("# ANACONDA Stress Test & Memory Leak Analysis Log\n")
        f.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("| Timestamp | Elapsed (s) | Iterations | RSS Memory (bytes) | RSS Memory (MB) | Drift (MB) | Extrapolated Hourly Growth (MB) |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n")

def append_log(elapsed, iterations, rss, drift, hourly_growth):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    rss_mb = rss / (1024 * 1024)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"| {timestamp} | {elapsed} | {iterations} | {rss} | {rss_mb:.4f} MB | {drift:.4f} MB | {hourly_growth:.4f} MB |\n")

def main():
    print("====================================================")
    print("      ANACONDA DAEMON PRODUCTION STRESS TEST")
    print("====================================================")
    
    initialize_log()
    
    # Set env variables for daemon mode with fast polling
    env = dict(os.environ)
    env["DAEMON_MODE"] = "true"
    env["POLL_INTERVAL"] = str(POLL_INTERVAL)
    
    print("[*] Launching ANACONDA Financial Ingester daemon in secure runtime...")
    python_exe = sys.executable
    proc = subprocess.Popen(
        [python_exe, RUNTIME_PATH, SCRIPT_PATH],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait a moment for process to initialize
        time.sleep(2)
        if proc.poll() is not None:
            stdout, stderr = proc.communicate()
            print(f"[!] Process failed to start:\nStdout: {stdout}\nStderr: {stderr}")
            sys.exit(1)
            
        p = psutil.Process(proc.pid)
        initial_rss = p.memory_info().rss
        initial_rss_mb = initial_rss / (1024 * 1024)
        print(f"[+] Daemon running under PID: {proc.pid}")
        print(f"[+] Initial RAM Usage (RSS): {initial_rss_mb:.4f} MB")
        
        start_time = time.time()
        last_log_time = start_time
        
        while True:
            current_time = time.time()
            elapsed = current_time - start_time
            
            if elapsed >= MONITOR_DURATION:
                break
                
            # Log memory usage at set intervals
            if current_time - last_log_time >= LOG_INTERVAL:
                try:
                    rss = p.memory_info().rss
                    rss_mb = rss / (1024 * 1024)
                    drift_mb = rss_mb - initial_rss_mb
                    
                    # Extrapolate to hourly growth
                    # elapsed is in seconds; 1 hour = 3600 seconds
                    hourly_growth_mb = (drift_mb / elapsed) * 3600.0 if elapsed > 0 else 0.0
                    
                    iterations = int(elapsed / POLL_INTERVAL)
                    append_log(int(elapsed), iterations, rss, drift_mb, hourly_growth_mb)
                    
                    print(f"[*] Snapshot: Elapsed={int(elapsed)}s | Iterations={iterations} | RSS={rss_mb:.4f} MB | Drift={drift_mb:.4f} MB | Est. Hourly Growth={hourly_growth_mb:.4f} MB")
                    
                    # Check for memory leak threshold
                    if hourly_growth_mb > 1.0 and elapsed > 20:
                        print(f"\n[!] WARN_MEMORY_LEAK: Extrapolated memory growth exceeds 1MB/hour threshold! (Current: {hourly_growth_mb:.4f} MB/hour)")
                        # Kill the process and raise error
                        proc.terminate()
                        sys.exit(99)
                        
                    last_log_time = current_time
                except psutil.NoSuchProcess:
                    print("[!] Daemon process terminated unexpectedly.")
                    break
                    
            time.sleep(1)
            
        # Final check
        rss = p.memory_info().rss
        rss_mb = rss / (1024 * 1024)
        drift_mb = rss_mb - initial_rss_mb
        hourly_growth_mb = (drift_mb / MONITOR_DURATION) * 3600.0
        
        print("\n====================================================")
        print("                 STRESS TEST COMPLETE")
        print("====================================================")
        print(f"Total Duration: {MONITOR_DURATION} seconds")
        print(f"Total Iterations: {int(MONITOR_DURATION / POLL_INTERVAL)}")
        print(f"Final RAM RSS: {rss_mb:.4f} MB")
        print(f"Total Drift: {drift_mb:.4f} MB")
        print(f"Extrapolated Hourly Drift Rate: {hourly_growth_mb:.4f} MB/hour")
        
        if hourly_growth_mb <= 1.0:
            print("[+] SUCCESS: Memory usage remains stable (growth <= 1MB/hour).")
        else:
            print("[!] FAILURE: Memory leak detected.")
            sys.exit(99)
            
    finally:
        if proc.poll() is None:
            print("[*] Terminating daemon process...")
            proc.terminate()
            proc.wait()
            print("[*] Daemon process terminated.")

if __name__ == "__main__":
    main()
