# benchmark.py
# ANACONDA Math and Execution Benchmark Suite
# Classification: BLACK PROJECT // SOVEREIGN

import sys
import os
import time
import statistics
import subprocess

# Ensure ANACONDA src is in path
sys.path.insert(0, r"C:\RegimeOS\language\anaconda")
from src.kernel.regime_math import RegimeDecimal

def clean_data(data):
    """Discards outliers (>3σ) from a dataset."""
    if len(data) < 2:
        return data
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    if stdev == 0:
        return data
    return [x for x in data if abs(x - mean) <= 3 * stdev]

def run_micro_benchmark(op_type, iterations=10000):
    # Pre-warm and pre-create operands
    if op_type == "add":
        f_a, f_b = 0.1, 0.2
        d_a = RegimeDecimal.from_float(0.1)
        d_b = RegimeDecimal.from_float(0.2)
        
        # Native benchmark
        native_times = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            _ = f_a + f_b
            t1 = time.perf_counter_ns()
            native_times.append(t1 - t0)
            
        # RegimeDecimal benchmark
        decimal_times = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            _ = d_a + d_b
            t1 = time.perf_counter_ns()
            decimal_times.append(t1 - t0)
            
    elif op_type == "mul":
        f_a, f_b = 1.25, 0.8
        d_a = RegimeDecimal.from_float(1.25)
        d_b = RegimeDecimal.from_float(0.8)
        
        native_times = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            _ = f_a * f_b
            t1 = time.perf_counter_ns()
            native_times.append(t1 - t0)
            
        decimal_times = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            _ = d_a * d_b
            t1 = time.perf_counter_ns()
            decimal_times.append(t1 - t0)
            
    elif op_type == "div":
        f_a, f_b = 1.0, 3.0
        d_a = RegimeDecimal.from_float(1.0)
        d_b = RegimeDecimal.from_float(3.0)
        
        native_times = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            _ = f_a / f_b
            t1 = time.perf_counter_ns()
            native_times.append(t1 - t0)
            
        decimal_times = []
        for _ in range(iterations):
            t0 = time.perf_counter_ns()
            _ = d_a / d_b
            t1 = time.perf_counter_ns()
            decimal_times.append(t1 - t0)
            
    else:
        raise ValueError("Invalid operation type")
        
    cleaned_native = clean_data(native_times)
    cleaned_decimal = clean_data(decimal_times)
    
    return {
        "native": {
            "mean": statistics.mean(cleaned_native),
            "median": statistics.median(cleaned_native),
            "stdev": statistics.stdev(cleaned_native) if len(cleaned_native) > 1 else 0
        },
        "decimal": {
            "mean": statistics.mean(cleaned_decimal),
            "median": statistics.median(cleaned_decimal),
            "stdev": statistics.stdev(cleaned_decimal) if len(cleaned_decimal) > 1 else 0
        }
    }

def run_macro_benchmark():
    """Runs the ported ingester script under ANACONDA vs native Python and measures overall time."""
    python_exe = sys.executable
    
    # 1. Native Ingester run
    native_script = r"C:\RegimeOS\bin\financial_ingester.py"
    native_times = []
    
    print("[*] Running native Python daemon benchmark...")
    for _ in range(5):
        t0 = time.perf_counter_ns()
        subprocess.run([python_exe, native_script], capture_output=True, env=dict(os.environ, DAEMON_MODE="false"))
        t1 = time.perf_counter_ns()
        native_times.append((t1 - t0) / 1e6) # to milliseconds
        
    # 2. ANACONDA Ingester run
    anaconda_runtime = r"C:\RegimeOS\language\anaconda\bin\anaconda-runtime.py"
    anaconda_script = r"C:\RegimeOS\language\anaconda\src\examples\financial_ingester.air"
    anaconda_times = []
    
    print("[*] Running ANACONDA sandboxed daemon benchmark...")
    for _ in range(5):
        t0 = time.perf_counter_ns()
        subprocess.run([python_exe, anaconda_runtime, anaconda_script], capture_output=True, env=dict(os.environ, DAEMON_MODE="false"))
        t1 = time.perf_counter_ns()
        anaconda_times.append((t1 - t0) / 1e6) # to milliseconds
        
    clean_native = clean_data(native_times)
    clean_anaconda = clean_data(anaconda_times)
    
    native_mean = statistics.mean(clean_native)
    anaconda_mean = statistics.mean(clean_anaconda)
    overhead = (anaconda_mean / native_mean) * 100.0 if native_mean > 0 else 100.0
    
    return {
        "native_mean_ms": native_mean,
        "anaconda_mean_ms": anaconda_mean,
        "overhead_percent": overhead
    }

def main():
    print("====================================================")
    print("      ANACONDA PRODUCTION BENCHMARK SUITE")
    print("====================================================")
    
    # Run micro-benchmarks
    print("\n--- 1. Math Kernel Micro-Benchmarks (10,000 Iterations) ---")
    for op in ["add", "mul", "div"]:
        res = run_micro_benchmark(op)
        print(f"\nOperation: {op.upper()}")
        print(f"  Native Float   : Mean={res['native']['mean']:.2f} ns | Median={res['native']['median']:.2f} ns | StdDev={res['native']['stdev']:.2f} ns")
        print(f"  RegimeDecimal  : Mean={res['decimal']['mean']:.2f} ns | Median={res['decimal']['median']:.2f} ns | StdDev={res['decimal']['stdev']:.2f} ns")
        print(f"  Micro-Ratio    : {(res['decimal']['mean'] / res['native']['mean']):.2f}x speed overhead")
        
    # Run macro-benchmarks
    print("\n--- 2. End-to-End Daemon Macro-Benchmarks (5 Runs) ---")
    res_macro = run_macro_benchmark()
    print(f"\n  Native Python Ingester Mean Run Time: {res_macro['native_mean_ms']:.2f} ms")
    print(f"  ANACONDA Secure Ingester Mean Run Time: {res_macro['anaconda_mean_ms']:.2f} ms")
    print(f"  Relative Performance Overhead        : {res_macro['overhead_percent']:.2f}% of native Python")
    
    if res_macro['overhead_percent'] <= 150.0:
        print("\n[+] SUCCESS: ANACONDA performance is within the authorized 150% threshold limit.")
    else:
        print("\n[!] WARNING: ANACONDA performance exceeds the 150% threshold limit.")

if __name__ == "__main__":
    main()
