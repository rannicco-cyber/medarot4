import csv
import glob
import hashlib
import os
import sys
from io import BytesIO

sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from common import tilesets


if len(sys.argv) < 2:
    print("Usage: python test_tilesets.py <prebuilt_tilesets_dir> [output.csv]")
    sys.exit(1)

prebuilt_root = sys.argv[1]
output_csv = sys.argv[2] if len(sys.argv) >= 3 else "tileset_compression_report.csv"

rows = []
round_trip_failures = []
invalid_headers = []

files = sorted(glob.glob(os.path.join(prebuilt_root, '*.malias')))

print(f"Found {len(files)} MALIAS files.")
print("Testing compression and round-trip decompression...")

for index, filename in enumerate(files, 1):
    print(f"[{index:3}/{len(files)}] {os.path.basename(filename)}", flush=True)

    with open(filename, 'rb') as f:
        original_data = list(f.read())

    original_flag = original_data[0]
    if original_flag not in (0, 1):
        invalid_headers.append((filename, original_flag))

    with open(filename, 'rb') as original_file:
        decompressed_data, _ = tilesets.decompress_tileset(original_file, 0)

    recompressed_data = tilesets.compress_tileset(
        BytesIO(bytes(decompressed_data))
    )

    redecompressed_data, _ = tilesets.decompress_tileset(
        BytesIO(bytes(recompressed_data)), 0
    )

    decompressed_match = decompressed_data == redecompressed_data

    if not decompressed_match:
        round_trip_failures.append(filename)

    original_size = len(original_data)
    recompressed_size = len(recompressed_data)
    delta = recompressed_size - original_size

    if delta < 0:
        result = "smaller"
    elif delta > 0:
        result = "larger"
    else:
        result = "same"

    rows.append({
        "filename": os.path.basename(filename),
        "original_size": original_size,
        "recompressed_size": recompressed_size,
        "delta_bytes": delta,
        "result": result,
        "original_flag": original_flag,
        "recompressed_flag": recompressed_data[0],
        "decompressed_size": len(decompressed_data),
        "round_trip_match": decompressed_match,
        "original_sha256": hashlib.sha256(bytes(original_data)).hexdigest(),
        "recompressed_sha256": hashlib.sha256(bytes(recompressed_data)).hexdigest(),
    })

with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys() if rows else [
        "filename", "original_size", "recompressed_size", "delta_bytes",
        "result", "original_flag", "recompressed_flag", "decompressed_size",
        "round_trip_match", "original_sha256", "recompressed_sha256"
    ])
    writer.writeheader()
    writer.writerows(rows)

smaller = sum(r["result"] == "smaller" for r in rows)
same = sum(r["result"] == "same" for r in rows)
larger = sum(r["result"] == "larger" for r in rows)
total_original = sum(r["original_size"] for r in rows)
total_recompressed = sum(r["recompressed_size"] for r in rows)

print(f"Tilesets tested:        {len(rows)}")
print(f"Round-trip failures:    {len(round_trip_failures)}")
print(f"Invalid MALIAS headers: {len(invalid_headers)}")
print(f"Smaller:                {smaller}")
print(f"Same size:              {same}")
print(f"Larger:                 {larger}")
print(f"Reference total:        {total_original} bytes")
print(f"Recompressed total:     {total_recompressed} bytes")
print(f"Total delta:            {total_recompressed - total_original:+d} bytes")
print(f"CSV report:             {output_csv}")

if round_trip_failures:
    print("\nRound-trip failures:")
    for filename in round_trip_failures:
        print(f"  {filename}")

if invalid_headers:
    print("\nInvalid MALIAS headers:")
    for filename, flag in invalid_headers:
        print(f"  {filename}: 0x{flag:02X}")

sys.exit(1 if round_trip_failures or invalid_headers else 0)
