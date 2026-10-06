import zstandard as zstd # zstandard is a Python library that provides bindings for the Zstandard compression algorithm. It allows you to compress and decompress data using the Zstandard algorithm, which is known for its high compression ratios and fast decompression speeds.
 

def compress_data(data: bytes) -> bytes:
    compressor = zstd.ZstdCompressor(level=3)
    return compressor.compress(data)


def decompress_data(data: bytes) -> bytes:
    decompressor = zstd.ZstdDecompressor()
    return decompressor.decompress(data)