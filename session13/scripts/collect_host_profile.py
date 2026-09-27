#!/usr/bin/env python3
from __future__ import annotations
import json, platform, subprocess
from datetime import datetime, timezone
from pathlib import Path
import torch
ROOT = Path(__file__).resolve().parents[1]

def sysctl(k):
    try:
        return subprocess.check_output(["sysctl", "-n", k], text=True).strip()
    except Exception:
        return ""

def main():
    mem = sysctl("hw.memsize")
    profile = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_brand": sysctl("machdep.cpu.brand_string"),
        "physical_cpus": sysctl("hw.physicalcpu_max"),
        "logical_cpus": sysctl("hw.logicalcpu_max"),
        "ram_bytes": int(mem) if mem.isdigit() else mem,
        "ram_gb": round(int(mem) / (1024**3), 2) if mem.isdigit() else None,
        "pytorch": torch.__version__,
        "mps_available": bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()),
    }
    out = ROOT / "results/host_profile.json"
    out.write_text(json.dumps(profile, indent=2))
    print(out)

if __name__ == "__main__":
    main()
