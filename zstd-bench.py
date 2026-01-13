import zstandard as zstd
from zstandard import ZstdCompressionParameters as zcp
import time
from pathlib import Path
import sys


def init_test_params():
    default_l3 = zcp.from_level(3)
    test_params = [
        (f"L2", zcp.from_level(2)),
        (f"L3", zcp.from_level(3)),
        (f"L4", zcp.from_level(4)),
        (f"L5", zcp.from_level(5)),
    ]
    for dw in [+1, +2, +3]:
        for dc in [+0, +1]:
            for dh in [+1, +2, +3]:
                for dm in [0, +1]:
                    test_params.append(
                        (f"L3|w{dw:+2}|c{dc:+2}|h{dh:+2}|m{dm:+2}",
                            zcp.from_level(3,
                                           # strategy=zstd.STRATEGY_DFAST,
                                           window_log=default_l3.window_log + dw,
                                           chain_log=default_l3.chain_log + dc,
                                           hash_log=default_l3.hash_log + dh,
                                           min_match=default_l3.min_match + dm))
                    )
    return test_params


def run_bench(input_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    original_size = len(data)

    # Level 3 baseline
    cctx = zstd.ZstdCompressor(level=3)
    start = time.time()
    compressed = cctx.compress(data)
    comp_time = time.time() - start

    baseline_size = len(compressed)
    baseline_cr = original_size / baseline_size
    baseline_cs = original_size / comp_time

    test_params = init_test_params()

    results = []
    for desc, compression_params in test_params:
        try:
            cctx = zstd.ZstdCompressor(compression_params=compression_params)

            start = time.time()
            compressed = cctx.compress(data)
            comp_time = time.time() - start

            dctx = zstd.ZstdDecompressor()
            decompressed = dctx.decompress(compressed)
            assert decompressed == data

            size = len(compressed)
            cr = original_size / size
            cs = original_size / comp_time

            cr_delta = (cr / baseline_cr - 1) * 100
            cs_delta = (cs / baseline_cs - 1) * 100

            results.append({
                'desc': desc,
                'ratio': cr,
                'ratio_imp': cr_delta,
                'comp_speed': cs,
                'speed_change': cs_delta,
                'size_mb': size/(1024*1024)
            })

            print(f"{desc:20s}: {cr:5.2f}x ({cr_delta:+5.1f}%) | "
                  f"{cs/2**20:5.0f} MB/s ({cs_delta:+5.1f}%) | "
                  f"{size/(1024*1024):5.2f} MB")
        except Exception as e:
            print(f"{desc:20s}: ERROR - {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} PAYLOAD_FILE')
        exit()
    run_bench(Path(sys.argv[1]))
