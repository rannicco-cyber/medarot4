#!/bin/python

import os, sys, glob
from io import BytesIO

sys.path.append(os.path.join(os.path.dirname(__file__), 'common'))
from common import tilesets

prebuilt_root = sys.argv[1]

print("Test that tileset compression preserves the decompressed result")

for filename in glob.glob(os.path.join(prebuilt_root, '*.malias')):
    with open(filename, 'rb') as f:
        print(f"\tTesting {filename}")

        original_data = list(f.read())
        compressed_data = original_data[0]
        assert compressed_data != 0

        # Decode the prebuilt MALIAS data.
        with open(filename, 'rb') as original_file:
            decompressed_data, _ = tilesets.decompress_tileset(
                original_file, 0
            )

        # Compress the decoded tileset using the new compressor.
        recompressed_data = tilesets.compress_tileset(
            BytesIO(bytes(decompressed_data))
        )

        # The compressed representation does not need to be byte-identical.
        # The requirement is that recompression is lossless.
        redecompressed_data, _ = tilesets.decompress_tileset(
            BytesIO(bytes(recompressed_data)), 0
        )

        assert decompressed_data == redecompressed_data

print("OK!")
