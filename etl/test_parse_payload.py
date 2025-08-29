import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "etl_module", Path(__file__).resolve().parent / "etl.py"
)
etl = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(etl)  # type: ignore
parse_payload = etl.parse_payload


def test_parse_payload_with_arrays():
    payload = {
        "object": {"internal_sensors_temperature": 22.5},
        "rxInfo": [{"rssi": -70, "snr": 5}, {"rssi": -72}],
    }
    mapping = [
        {
            "json_path": "{object,internal_sensors_temperature}",
            "metric": "object_internal_sensors_temperature",
            "unit": "°C",
        },
        {"json_path": "{rxInfo,0,rssi}", "metric": "rxInfo_0_rssi", "unit": "dBm"},
    ]

    metrics, fails = parse_payload(payload, mapping)
    assert not fails
    assert (
        "object_internal_sensors_temperature",
        22.5,
        "°C",
        "object_internal_sensors_temperature",
    ) in metrics
    assert (
        "rxInfo_0_rssi",
        -70.0,
        "dBm",
        "rxInfo_0_rssi",
    ) in metrics
