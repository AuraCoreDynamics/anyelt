namespace AnyElt.Core.IO;

using System.IO.Compression;

/// <summary>
/// Lightweight, zero-dependency PNG encoder.
/// Produces valid, standard PNG 1.2 bitstreams from raw pixel matrices (Grayscale, RGB, RGBA).
/// </summary>
public static class PngEncoder
{
    private static readonly byte[] PngSignature = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];

    public static byte[] EncodeGrayscale8(byte[] pixels, int width, int height)
    {
        return Encode(pixels, width, height, colorType: 0, bitDepth: 8, bytesPerPixel: 1);
    }

    public static byte[] EncodeRgb24(byte[] pixels, int width, int height)
    {
        return Encode(pixels, width, height, colorType: 2, bitDepth: 8, bytesPerPixel: 3);
    }

    public static byte[] EncodeRgba32(byte[] pixels, int width, int height)
    {
        return Encode(pixels, width, height, colorType: 6, bitDepth: 8, bytesPerPixel: 4);
    }

    private static byte[] Encode(byte[] pixels, int width, int height, byte colorType, byte bitDepth, int bytesPerPixel)
    {
        using var ms = new MemoryStream();
        ms.Write(PngSignature);

        // 1. IHDR Chunk (13 bytes)
        byte[] ihdrData = new byte[13];
        WriteBigEndianInt(ihdrData, 0, width);
        WriteBigEndianInt(ihdrData, 4, height);
        ihdrData[8] = bitDepth;
        ihdrData[9] = colorType;
        ihdrData[10] = 0; // Compression (Deflate)
        ihdrData[11] = 0; // Filter (Adaptive)
        ihdrData[12] = 0; // Interlace (None)
        WriteChunk(ms, "IHDR"u8, ihdrData);

        // 2. IDAT Chunk: Filtered scanlines with Deflate
        int stride = width * bytesPerPixel;
        byte[] rawScanlines = new byte[height * (stride + 1)];

        for (int y = 0; y < height; y++)
        {
            int scanlineStart = y * (stride + 1);
            rawScanlines[scanlineStart] = 0; // Filter type 0 (None)
            int srcOffset = y * stride;
            int lengthToCopy = Math.Min(stride, Math.Max(0, pixels.Length - srcOffset));
            if (lengthToCopy > 0)
            {
                Array.Copy(pixels, srcOffset, rawScanlines, scanlineStart + 1, lengthToCopy);
            }
        }

        byte[] compressedData;
        using (var compMs = new MemoryStream())
        {
            // Write zlib header: CM/CINFO (0x78) and FLG (0x9C = default compression)
            compMs.WriteByte(0x78);
            compMs.WriteByte(0x9C);

            using (var deflate = new DeflateStream(compMs, CompressionLevel.Optimal, leaveOpen: true))
            {
                deflate.Write(rawScanlines, 0, rawScanlines.Length);
                deflate.Flush();
            }

            // Adler-32 checksum
            uint adler = ComputeAdler32(rawScanlines);
            compMs.WriteByte((byte)((adler >> 24) & 0xFF));
            compMs.WriteByte((byte)((adler >> 16) & 0xFF));
            compMs.WriteByte((byte)((adler >> 8) & 0xFF));
            compMs.WriteByte((byte)(adler & 0xFF));

            compressedData = compMs.ToArray();
        }

        WriteChunk(ms, "IDAT"u8, compressedData);

        // 3. IEND Chunk
        WriteChunk(ms, "IEND"u8, Array.Empty<byte>());

        return ms.ToArray();
    }

    private static void WriteChunk(Stream stream, ReadOnlySpan<byte> type, byte[] data)
    {
        byte[] lenBytes = new byte[4];
        WriteBigEndianInt(lenBytes, 0, data.Length);
        stream.Write(lenBytes);
        stream.Write(type);
        if (data.Length > 0)
        {
            stream.Write(data);
        }

        // CRC-32 over chunk type and data
        uint crc = ComputeCrc32(type, data);
        byte[] crcBytes = new byte[4];
        WriteBigEndianInt(crcBytes, 0, (int)crc);
        stream.Write(crcBytes);
    }

    private static void WriteBigEndianInt(byte[] buffer, int offset, int value)
    {
        buffer[offset] = (byte)((value >> 24) & 0xFF);
        buffer[offset + 1] = (byte)((value >> 16) & 0xFF);
        buffer[offset + 2] = (byte)((value >> 8) & 0xFF);
        buffer[offset + 3] = (byte)(value & 0xFF);
    }

    private static uint ComputeCrc32(ReadOnlySpan<byte> type, byte[] data)
    {
        uint crc = 0xFFFFFFFF;
        foreach (byte b in type)
        {
            crc = CrcTable[(crc ^ b) & 0xFF] ^ (crc >> 8);
        }
        foreach (byte b in data)
        {
            crc = CrcTable[(crc ^ b) & 0xFF] ^ (crc >> 8);
        }
        return crc ^ 0xFFFFFFFF;
    }

    private static uint ComputeAdler32(byte[] data)
    {
        const uint modAdler = 65521;
        uint a = 1, b = 0;
        foreach (byte byteVal in data)
        {
            a = (a + byteVal) % modAdler;
            b = (b + a) % modAdler;
        }
        return (b << 16) | a;
    }

    private static readonly uint[] CrcTable = InitializeCrcTable();

    private static uint[] InitializeCrcTable()
    {
        var table = new uint[256];
        for (uint i = 0; i < 256; i++)
        {
            uint c = i;
            for (int k = 0; k < 8; k++)
            {
                c = (c & 1) != 0 ? 0xEDB88320 ^ (c >> 1) : c >> 1;
            }
            table[i] = c;
        }
        return table;
    }
}
