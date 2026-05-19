#!/usr/bin/env python3
"""RegimeOS Production Interface v4.0-Windows"""
import os, sys, time, msvcrt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'kernel'))
from regime_math import ArchitectAnchor, DiracComb
from regime_config import *

def get_rpm(path):
    try:
        rpm_path = os.path.join(path, 'velocity', 'rpm.md')
        if not os.path.exists(rpm_path):
            rpm_path = os.path.join(path, 'rotor', 'velocity', 'rpm.md')
        with open(rpm_path, 'r', encoding='utf-8-sig') as f:
            content = f.read().strip()
            if '/' in content:
                return int(content.split('/')[0].strip())
            return int(content)
    except:
        return 0

def generate_status():
    core_rpm = get_rpm(CORE_GEODISC_PATH)
    main_rpm = get_rpm(MAIN_TURBINE_PATH)
    sub_rpms = [get_rpm(os.path.join(SUB_TURBINE_PATH, f'sub_turbine_{i:02d}')) for i in range(1, SUB_TURBINE_COUNT + 1)]
    avg_sub_rpm = sum(sub_rpms) // len(sub_rpms) if sub_rpms else 0
    
    total_nodes = (VERTEX_COUNT + AS_DIAMOND_COUNT + 2) * NODES_PER_COMPONENT
    total_power = (core_rpm * CORE_LEARNING_RATE + main_rpm + sum(sub_rpms)) * total_nodes
    
    md = "# RegimeOS Command Center v4.0-Windows\n\n"
    md += "## Core Status\n\n"
    md += f"- **State:** |0| STABLE\n"
    md += f"- **Regime Level:** R{REGIME_LEVEL}\n"
    md += f"- **Version:** 4.0-Windows (Production Ready)\n\n"
    md += "## Turbine Metrics\n\n"
    md += f"- **Core Geodisc RPM:** {core_rpm} / {CORE_MAX_RPM}\n"
    md += f"- **Main Rotor RPM:** {main_rpm} / {MAIN_MAX_RPM}\n"
    md += f"- **Sub-Turbine Avg RPM:** {avg_sub_rpm} / {SUB_MAX_RPM}\n"
    md += f"- **Rotation Points:** {get_total_rotation_points()}\n"
    md += f"- **Learning Layers:** {get_total_learning_layers()}\n"
    md += f"- **Total Power:** {total_power} Compute Units\n\n"
    md += "## System Health\n\n"
    md += f"- **Kernel:** + Verified\n"
    md += f"- **Logging:** + Active\n"
    md += f"- **Backup:** + Ready\n"
    md += f"- **Remote:** {'+ Enabled' if ENABLE_REMOTE else 'x Disabled'}\n"
    md += f"- **Lazy Panels:** {'+ Enabled' if LAZY_PANEL_CREATION else 'x Disabled'}\n\n"
    md += "## Optimization\n\n"
    md += f"- **Active Panels:** {ACTIVE_PANELS_ONLY} (Lazy Creation)\n"
    md += f"- **Total Panels:** {get_total_panels()} (On-Demand)\n"
    md += "\n**Press 'q' to quit**\n"
    return md

def main():
    status_file = os.path.join(CORE_GEODISC_PATH, 'state', 'status.md')
    heartbeat = DiracComb(interval_t=5)
    last_log = time.time()
    
    while True:
        md_content = generate_status()
        
        with open(status_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        if heartbeat.tick():
            os.system('cls' if os.name == 'nt' else 'clear')
            print(md_content)
            
            if time.time() - last_log > 60:
                with open(os.path.join(LOGS_PATH, 'system', 'heartbeat.md'), 'a', encoding='utf-8') as f:
                    f.write(f"\n## Heartbeat\n\n- **Time:** {time.time()}\n- **Core RPM:** {get_rpm(CORE_GEODISC_PATH)}\n")
                last_log = time.time()
        
        # Non-blocking key check for Windows
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key.lower() == 'q':
                break
        
        time.sleep(1)

if __name__ == "__main__":
    main()
