# LZW
LZW encoder implemented in 3 different ways, both of which can receive any type of file

#To execute:

  python3 lzw_codificador1 (file to be compressed) (max number of bytes in the dictionary)
  python3 lzw_codificador2 (file to be compressed) (max number of bytes in the dictionary)
  python3 lzw_codificador3 (file to be compressed) (max number of bytes in the dictionary)

Warming = The maximum number of bytes will be used in the code as 2^this number

# The difference in the codes:

1 - Filling the dictionary with the maximum number of bytes = Keeps it static until the end of compression and decompression.

2 - Filling the dictionary with the maximum number of bytes = Resets it to the initial state

3 - When filling the dictionary with the maximum number of bytes = Keep it static and observe the average length of the compressed file. If it goes too high, it resets the dictionary to the initial state (Only works for dictionaries with a size of 4K, 32K and 256KB)

# How it works:

It works on top of an input sequence, be it made up of bytes. The compression process involves replacing repeated sequences of data with codes that represent these sequences in a more compact way.
The LZW algorithm is based on building and dynamically updating a dictionary of codes during the compression process. Initially, the dictionary contains all the possible characters or symbols that could appear in the input sequence. As the algorithm goes through the input sequence, it identifies repeating patterns and replaces them with corresponding codes in the dictionary, thus reducing the total file size.

When decompressing a file compressed with the LZW algorithm, the process is reversed: the codes are translated back into the original sequence using the dictionary. As the LZW algorithm is lossless, the decompressed output is an exact copy of the original input.
