#!/bin/python

import glob
import os
import shutil
import subprocess
import sys
import tempfile
from io import BytesIO

sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from common import tilesets


def find_rgbgfx(repo_root, explicit=None):
    candidates = []
    if explicit:
        candidates.append(explicit)
    env_rgbgfx = os.environ.get('RGBGFX')
    if env_rgbgfx:
        candidates.append(env_rgbgfx)
    candidates.extend([
        os.path.join(repo_root, 'rgbgfx.exe'),
        os.path.join(repo_root, 'rgbgfx'),
        'rgbgfx.exe',
        'rgbgfx',
    ])

    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
        found = shutil.which(candidate)
        if found:
            return found

    return None


def convert_png(rgbgfx, png_file, raw_file):
    result = subprocess.run(
        [rgbgfx, '-d', '2', '-o', raw_file, png_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: rgbgfx failed for {png_file}")
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip())
        raise SystemExit(result.returncode)


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    source_root = os.path.abspath(
        sys.argv[1] if len(sys.argv) > 1 else os.path.join(repo_root, 'gfx', 'tilesets')
    )
    explicit_rgbgfx = sys.argv[2] if len(sys.argv) > 2 else None

    rgbgfx = find_rgbgfx(repo_root, explicit_rgbgfx)
    if not rgbgfx:
        print("ERROR: Could not find rgbgfx.")
        print("Put rgbgfx.exe in the repository root, add it to PATH, or pass its path as the second argument.")
        return 1

    files = sorted(glob.glob(os.path.join(source_root, '*.png')))
    if not files:
        print(f"ERROR: No PNG files found in {source_root}")
        return 1

    print("Test that tileset compression preserves source data")
    print(f"Source: {source_root}")
    print(f"rgbgfx: {rgbgfx}")
    print(f"Found {len(files)} PNG files.")
    print()

    failures = []

    with tempfile.TemporaryDirectory(prefix='medarot4_tileset_test_') as temp_dir:
        for index, png_file in enumerate(files, 1):
            name = os.path.basename(png_file)
            raw_file = os.path.join(temp_dir, f'{index:04d}.2bpp')

            print(f"[{index:3}/{len(files)}] {name}", flush=True)

            try:
                # Use the same 2bpp conversion used by the normal tileset build.
                convert_png(rgbgfx, png_file, raw_file)

                with open(raw_file, 'rb') as f:
                    original_data = f.read()

                compressed_data = tilesets.compress_tileset(BytesIO(original_data))
                redecompressed_data, _ = tilesets.decompress_tileset(
                    BytesIO(bytes(compressed_data)), 0
                )

                if original_data != bytes(redecompressed_data):
                    failures.append((name, len(original_data), len(redecompressed_data)))
                    print("       FAIL: decompressed data differs", flush=True)

            except Exception as exc:
                failures.append((name, 'error', str(exc)))
                print(f"       FAIL: {exc}", flush=True)

    print()
    print(f"Tilesets tested:     {len(files)}")
    print(f"Round-trip failures: {len(failures)}")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(f"  {failure}")
        return 1

    print("OK!")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
