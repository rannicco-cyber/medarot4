import os
import struct
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
import utils

# Adapted from https://github.com/Sanqui/romhacking/blob/master/telefang/punika.py
def decompress_tileset(rom, offset):
    rom.seek(offset)
    compressed = utils.read_byte(rom)
    total = utils.read_short(rom)
    data = []
    original = [compressed] + list(total.to_bytes(2, byteorder='little'))
    if compressed:
        while len(data) < total:
            modes = utils.read_short(rom)
            original += list(modes.to_bytes(2, byteorder='little'))
            for mode in bin(modes)[2:].zfill(16)[::-1]:
                if int(mode) == 1:
                    e = rom.read(1)
                    d = rom.read(1)
                    original += [struct.unpack("B", e)[0], struct.unpack("B", d)[0]]
                    loc = -(struct.unpack("<H", e+d)[0]  & 0x07ff)
                    num = ((struct.unpack("<B", d)[0] >> 3) & 0x1f) + 0x03
                    loc += len(data)-1
                    for j in range(num):
                        if loc < 0:
                            raise "Unknown location"
                        else:
                            data.append(data[loc+j])
                else:
                    d = utils.read_byte(rom)
                    data.append(d)
                    original.append(d)
                if len(data) == total: # We'll read bytes that we don't need to if we don't check this here
                    break
    elif compressed == 0:
        data = [utils.read_byte(rom) for i in range(0,total)]
        original += data
    else:
        raise "Unknown compression flag (expect 0 or 1)"
    return data, original

MAX_DISTANCE = 0x7FF
MIN_MATCH = 3
MAX_MATCH = 34
MODE_BYTES = 2
HEADER_BYTES = 3


def _best_match(data, pos, prev_positions):
    """Return useful (distance, length) matches at pos."""
    if pos + MIN_MATCH > len(data):
        return []

    key = bytes(data[pos:pos + 3])
    candidates = prev_positions.get(key, ())
    out = []

    # Newest first. All candidates are within the 0x7ff window.
    for src in reversed(candidates):
        distance = pos - src - 1
        if distance < 0:
            continue
        if distance > MAX_DISTANCE:
            break

        max_len = min(MAX_MATCH, len(data) - pos)
        # Overlap is legal in MALIAS, so compare using modulo distance.
        length = 0
        while length < max_len:
            if data[src + (length % (pos - src))] != data[pos + length]:
                break
            length += 1

        if length >= MIN_MATCH:
            out.append((distance, length))

    return out


def compress_tileset(file):
    data = list(file.read())
    total = len(data)

    if total == 0:
        return [0, 0, 0]

    # Build a 3-byte match index. Positions older than the 0x7ff window are
    # discarded as we advance through the data.
    positions = {}
    for i in range(max(0, total - 1)):
        if i + 3 <= total:
            positions.setdefault(bytes(data[i:i + 3]), []).append(i)

    # DP state is (position, command_count_mod_16).
    # dp[pos][m] = minimum payload + mode-word bytes from this point onward.
    INF = 10**9
    dp = [[INF] * 16 for _ in range(total + 1)]
    choice = [[None] * 16 for _ in range(total + 1)]

    # At the end, the final partial command group still has its 2-byte mode
    # word, so account for it here.
    for m in range(16):
        dp[total][m] = MODE_BYTES

    for pos in range(total - 1, -1, -1):
        # Current position's 3-byte key candidates must include only previous
        # positions. The prebuilt index contains future positions too.
        key = bytes(data[pos:pos + 3]) if pos + 3 <= total else None
        candidates = []
        if key is not None:
            candidates = positions.get(key, ())

        useful_matches = []
        if candidates:
            for src in reversed(candidates):
                if src >= pos:
                    continue
                distance = pos - src - 1
                if distance > MAX_DISTANCE:
                    break

                max_len = min(MAX_MATCH, total - pos)
                overlap_distance = pos - src
                length = 0
                while length < max_len:
                    if data[src + (length % overlap_distance)] != data[pos + length]:
                        break
                    length += 1

                if length >= MIN_MATCH:
                    useful_matches.append((distance, length))

        for m in range(16):
            next_m = (m + 1) & 15
            group_cost = MODE_BYTES if next_m == 0 else 0

            # Literal.
            cost = 1 + group_cost + dp[pos + 1][next_m]
            if cost < dp[pos][m]:
                dp[pos][m] = cost
                choice[pos][m] = (1, None, None)

            # Match. Consider every legal length for every distance.
            # Shorter matches can improve the suffix alignment, so unlike v2
            # we must not discard them.
            for distance, length in useful_matches:
                for use_len in range(MIN_MATCH, length + 1):
                    end = pos + use_len
                    cost = 2 + group_cost + dp[end][next_m]
                    if cost < dp[pos][m]:
                        dp[pos][m] = cost
                        choice[pos][m] = (use_len, distance, True)

    # Reconstruct command list.
    commands = []
    pos = 0
    m = 0
    while pos < total:
        c = choice[pos][m]
        if c is None:
            raise RuntimeError(f"DP reconstruction failed at {pos}, mode {m}")

        length, distance, is_match = c
        if is_match:
            commands.append((1, distance, length))
        else:
            commands.append((0, data[pos], 1))
        pos += length
        m = (m + 1) & 15

    # Build stream.
    out = [0x01] + list(total.to_bytes(2, byteorder='little'))

    for group_start in range(0, len(commands), 16):
        group = commands[group_start:group_start + 16]
        modes = 0
        for bit, command in enumerate(group):
            if command[0]:
                modes |= 1 << bit
        out += list(modes.to_bytes(2, byteorder='little'))

        for command in group:
            if command[0]:
                _, distance, length = command
                encoded = distance | ((length - 3) << 11)
                out += list(encoded.to_bytes(2, byteorder='little'))
            else:
                out.append(command[1])

    # If compressed form is not smaller than literal form, use the official
    # uncompressed representation. This is also useful for tiny/chaotic data.
    raw_size = HEADER_BYTES + total
    if len(out) >= raw_size:
        return [0x00] + list(total.to_bytes(2, byteorder='little')) + data

    return out


# Returns a mapped tileset table, index is required only if the same tileset is repeated in multiple table entries
def get_tileset(tileset_name, index = -1, override_offset = -1):
    base_offset = 0
    if override_offset == -1:
        if index == -1:
            idx_tbl = utils.read_table('scripts/res/meta_tileset_index.tbl')
            hits = [idx for idx in idx_tbl if idx_tbl[idx] == tileset_name]
            if len(hits) != 1:
                raise f"Found more or less than one entry for {tileset_name}, provide an index if it appears more than once"
            index = hits[0]
        
        offsets = utils.read_table('scripts/res/meta_tileset_load_offsets.tbl')
        base_offset = (int(offsets[index], 16) // 0x10) & 0xFF
    else:
        base_offset = override_offset

    tbl = utils.read_list(f'scripts/res/tilesets/{tileset_name}.lst', base_offset)
    # If not explicitly defined, '0' generally refers to 'space'
    if 0 not in tbl:
        tbl[0] = ' '
    return tbl

if __name__ == "__main__":
    operation = int(sys.argv[1])
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    offset = int(sys.argv[4])

    with open(input_file, 'rb') as i, open(output_file, 'wb') as o:
        if operation == 0: # Decompress
            o.write(bytearray(decompress_tileset(i, offset)[0]))
        elif operation == 1: # Compress
            o.write(bytearray(compress_tileset(i)))