"""
Unit tests for fraud injection functions in cdr_generator.py
Run with: pytest -v
"""

import pytest
from cdr_generator import make_baseline, inject_irsf, inject_wangiri, inject_simbox

def test_inject_irsf_creates_premium_calls():
    subs, nums, devs, cdrs = make_baseline(100, 50)
    before_len = len(cdrs)
    premium_numbers = inject_irsf(cdrs, bursts=2, burst_size=10)
    after_len = len(cdrs)
    assert after_len > before_len
    assert any(call["callee"] in premium_numbers for call in cdrs)

def test_inject_wangiri_creates_short_calls():
    subs, nums, devs, cdrs = make_baseline(100, 50)
    inject_wangiri(cdrs, attempts=50)
    short_calls = [c for c in cdrs if c["duration"] <= 3 and c["caller_country"] == "INTL"]
    assert len(short_calls) > 0

def test_inject_simbox_links_multiple_numbers():
    subs, nums, devs, cdrs = make_baseline(100, 50)
    inject_simbox(cdrs, nums, device_count=1, numbers_per_device=10)
    sim_calls = [c for c in cdrs if c["caller_device"].startswith("SIMBOX_IMEI")]
    assert len(sim_calls) > 0
