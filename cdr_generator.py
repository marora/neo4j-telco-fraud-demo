"""
cdr_generator.py

Synthetic Call Detail Record (CDR) Generator with Fraud Injection.
---------------------------------------------------------------

This script generates a hybrid dataset of baseline telecom call records
and injects fraud scenarios (IRSF, Wangiri, SIM Box) for use in graph
databases such as Neo4j.

Features:
- Configurable number of subscribers, calls, and fraud parameters.
- Outputs CSV files for subscribers, phone numbers, devices, and calls.
- Can be used for graph-based fraud detection demonstrations.

Usage:
    python cdr_generator.py --calls 10000 --subscribers 1000 \
        --output ./data/import --fraud IRSF,WANGIRI,SIMBOX
"""

import random
import os
import argparse
from datetime import datetime, timedelta, timezone
from faker import Faker
import pandas as pd
from tqdm import tqdm
import yaml

fake = Faker()
random.seed(42)


def rand_msisdn(country_code: str = "+1") -> str:
    """
    Generate a random phone number (MSISDN) string.
    
    Args:
        country_code (str): Prefix for the number, default "+1".
    
    Returns:
        str: A synthetic phone number.
    """
    return country_code + str(random.randint(2000000000, 9999999999))[1:]


def make_baseline(num_calls: int, num_subscribers: int, start_dt: datetime = None):
    """
    Generate a baseline dataset of subscribers, numbers, devices, and CDRs.

    Args:
        num_calls (int): Number of baseline calls to generate.
        num_subscribers (int): Number of subscribers to simulate.
        start_dt (datetime, optional): Start time for simulation window.

    Returns:
        tuple: (subscribers, numbers, devices, cdrs) as lists of dicts.
    """
    if start_dt is None:
        start_dt = datetime.now() - timedelta(days=7)

    subscribers, numbers, devices, cdrs = [], [], [], []
    subs_nums, num_to_device = {}, {}

    # Create subscribers with phone numbers
    for sid in range(1, num_subscribers + 1):
        subscribers.append({"subscriber_id": sid, "name": fake.name()})
        subs_nums[sid] = []
        for _ in range(random.choice([1, 1, 1, 2, 3])):  # 1-3 numbers
            num = rand_msisdn()
            subs_nums[sid].append(num)
            numbers.append({
                "number": num,
                "subscriber_id": sid,
                "type": "mobile",
                "country": "US"
            })

    # Create devices and attach to numbers
    for did in range(1, int(num_subscribers * 1.2) + 1):
        devices.append({
            "device_id": did,
            "imei": f"IMEI{100000000000000 + did}",
            "ip": f"10.0.{did % 255}.{random.randint(1, 254)}"
        })
    for n in numbers:
        num_to_device[n["number"]] = random.choice(devices)["imei"]

    # Baseline calls
    dt = start_dt
    for _ in tqdm(range(num_calls), desc="Generating baseline calls"):
        caller, callee = random.sample(numbers, 2)
        ts = dt + timedelta(seconds=random.randint(1, 3600 * 24 * 7))
        dur = max(1, int(random.expovariate(1 / 120)))  # mean 120s
        cost = round(dur * 0.0015, 4)
        cdrs.append({
            "caller": caller["number"],
            "callee": callee["number"],
            "timestamp": int(ts.timestamp() * 1000),
            "start_time": ts.isoformat(),
            "duration": dur,
            "cost": cost,
            "caller_device": num_to_device[caller["number"]],
            "callee_device": num_to_device[callee["number"]],
            "caller_country": "US",
            "callee_country": "US"
        })

    return subscribers, numbers, devices, cdrs


def inject_irsf(cdrs: list, bursts: int = 5, burst_size: int = 200) -> list:
    """
    Inject International Revenue Share Fraud (IRSF) patterns.

    Args:
        cdrs (list): Existing CDR list.
        bursts (int): Number of bursts to inject.
        burst_size (int): Number of calls per burst.

    Returns:
        list: List of premium numbers used.
    """
    premium_prefixes = ["+882", "+979", "+4499", "+2739", "+880"]
    premium_numbers = [p + str(random.randint(1000000, 9999999)) for p in premium_prefixes]

    for _ in range(bursts):
        start = random.choice(cdrs)["timestamp"]
        callers = random.sample([c["caller"] for c in cdrs], k=50)
        for _ in range(burst_size):
            caller = random.choice(callers)
            callee = random.choice(premium_numbers)
            ts = start + random.randint(0, 10 * 60 * 1000)
            dur = random.randint(30, 300)
            cost = round(dur * 0.05 + random.random(), 3)
            cdrs.append({
                "caller": caller,
                "callee": callee,
                "timestamp": ts,
                "start_time": datetime.fromtimestamp(ts / 1000).isoformat(),
                "duration": dur,
                "cost": cost,
                "caller_device": "UNKNOWN",
                "callee_device": "UNKNOWN",
                "caller_country": "US",
                "callee_country": "PREMIUM"
            })
    return premium_numbers


def inject_wangiri(cdrs: list, attempts: int = 500):
    """
    Inject Wangiri ("one ring") fraud patterns.

    Args:
        cdrs (list): Existing CDR list.
        attempts (int): Number of fraudulent attempts to simulate.
    """
    intl_callers = [f"+{cc}{random.randint(10000000, 99999999)}"
                    for cc in [44, 49, 33, 91] for _ in range(50)]

    for _ in range(attempts):
        caller = random.choice(intl_callers)
        callee = random.choice([c["caller"] for c in cdrs])
        ts = random.choice(cdrs)["timestamp"] + random.randint(0, 3600 * 1000)
        cdrs.append({
            "caller": caller,
            "callee": callee,
            "timestamp": ts,
            "start_time": datetime.fromtimestamp(ts / 1000).isoformat(),
            "duration": random.randint(1, 3),
            "cost": 0.0,
            "caller_device": "EXT",
            "callee_device": "UNKNOWN",
            "caller_country": "INTL",
            "callee_country": "US"
        })


def inject_simbox(cdrs: list, numbers: list, device_count: int = 3, numbers_per_device: int = 100):
    """
    Inject SIM Box fraud patterns where many numbers share one device.

    Args:
        cdrs (list): Existing CDR list.
        numbers (list): List of phone number dicts.
        device_count (int): Number of fraudulent devices.
        numbers_per_device (int): Numbers per device.
    """
    large_devices = [f"SIMBOX_IMEI_{i+1}" for i in range(device_count)]
    all_numbers = [n["number"] for n in numbers]
    sampled = random.sample(all_numbers, k=min(len(all_numbers), device_count * numbers_per_device))

    idx = 0
    for imei in large_devices:
        for _ in range(numbers_per_device):
            if idx >= len(sampled): break
            num = sampled[idx]
            idx += 1
            for _ in range(random.randint(5, 25)):
                target = random.choice(all_numbers)
                ts = random.choice(cdrs)["timestamp"] + random.randint(0, 3600 * 24 * 1000)
                dur = random.randint(10, 300)
                cost = round(dur * 0.0015, 4)
                cdrs.append({
                    "caller": num,
                    "callee": target,
                    "timestamp": ts,
                    "start_time": datetime.fromtimestamp(ts / 1000).isoformat(),
                    "duration": dur,
                    "cost": cost,
                    "caller_device": imei,
                    "callee_device": "UNKNOWN",
                    "caller_country": "US",
                    "callee_country": "US"
                })


def write_csvs(subscribers: list, numbers: list, devices: list, cdrs: list, outdir: str = "data"):
    """
    Write subscribers, numbers, devices, and CDRs to CSV files.

    Args:
        subscribers (list): Subscriber dicts.
        numbers (list): Number dicts.
        devices (list): Device dicts.
        cdrs (list): Call records.
        outdir (str): Output directory path.
    """
    os.makedirs(outdir, exist_ok=True)
    pd.DataFrame(subscribers).to_csv(os.path.join(outdir, "subscribers.csv"), index=False)
    pd.DataFrame(numbers).to_csv(os.path.join(outdir, "numbers.csv"), index=False)
    pd.DataFrame(devices).to_csv(os.path.join(outdir, "devices.csv"), index=False)
    pd.DataFrame(sorted(cdrs, key=lambda x: x["timestamp"])).to_csv(
        os.path.join(outdir, "cdrs.csv"), index=False
    )


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic CDR dataset with fraud patterns.")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to YAML config file.")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        cfg = yaml.safe_load(f)

    subs, nums, devs, cdrs = make_baseline(
        num_calls=cfg["baseline"]["calls"],
        num_subscribers=cfg["baseline"]["subscribers"]
    )

    if cfg["fraud"]["irsf"]["enabled"]:
        inject_irsf(cdrs, bursts=cfg["fraud"]["irsf"]["bursts"], burst_size=cfg["fraud"]["irsf"]["burst_size"])
    if cfg["fraud"]["wangiri"]["enabled"]:
        inject_wangiri(cdrs, attempts=cfg["fraud"]["wangiri"]["attempts"])
    if cfg["fraud"]["simbox"]["enabled"]:
        inject_simbox(
            cdrs, nums,
            device_count=cfg["fraud"]["simbox"]["device_count"],
            numbers_per_device=cfg["fraud"]["simbox"]["numbers_per_device"]
        )

    write_csvs(subs, nums, devs, cdrs, outdir=cfg["baseline"]["output"])
    print(f"[INFO] Dataset written to {cfg['baseline']['output']}")

if __name__ == "__main__":
    main()
