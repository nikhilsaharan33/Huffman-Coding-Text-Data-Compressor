import os
import heapq
import collections
import csv


class HuffNode:

    def __init__(self, value, freq):
        self.value = value
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

    def __eq__(self, other):
        return self.freq == other.freq


class HuffmanCoding:

    def __init__(self, path=None):
        self.path = path
        self.__heap = []
        self.__codes = {}
        self.__reverseCodes = {}

    @staticmethod
    def __make_frequency_dict(text):
        return collections.Counter(text)

    def __buildHeap(self, freq_dict):
        for char in freq_dict:
            newNode = HuffNode(char, freq_dict[char])
            heapq.heappush(self.__heap, newNode)

    def __buildTree(self):
        while len(self.__heap) > 1:
            node1 = heapq.heappop(self.__heap)
            node2 = heapq.heappop(self.__heap)
            newNode = HuffNode(None, node1.freq + node2.freq)
            newNode.left = node1
            newNode.right = node2
            heapq.heappush(self.__heap, newNode)

    def __buildCodesHelper(self, root, curr_bits):
        if root is None:
            return
        if root.value is not None:
            self.__codes[root.value] = curr_bits
            self.__reverseCodes[curr_bits] = root.value
            return
        self.__buildCodesHelper(root.left, curr_bits + "0")
        self.__buildCodesHelper(root.right, curr_bits + "1")

    def __buildCodes(self):
        root = heapq.heappop(self.__heap) if self.__heap else None
        self.__buildCodesHelper(root, "")

    def __getEncodedText(self, text):
        encoded_text = ""
        for char in text:
            encoded_text += self.__codes[char]
        return encoded_text

    @staticmethod
    def __getPaddedEncodedText(encoded_text):
        padded_amount = 8 - (len(encoded_text) % 8)

        for i in range(padded_amount):
            encoded_text += '0'
        padded_info = "{0:08b}".format(padded_amount)
        encoded_text = padded_info + encoded_text
        return encoded_text

    @staticmethod
    def __getBytesArray(padded_encoded_text):
        array = []
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i + 8]
            array.append(int(byte, 2))
        return array

    def compress(self):
        file_name, file_extension = os.path.splitext(self.path)  # get the file name and the file extension separately
        output_path = file_name + ".bin"
        with open(self.path, 'r+') as file, open(output_path, 'wb') as output:
            text = file.read()
            text = text.rstrip()  # remove any trailing spaces in the end
            # make frequency dictionary using the text
            freq_dict = self.__make_frequency_dict(text)
            # construct the heap from the frequency_dict
            self.__buildHeap(freq_dict)
            # construct the Huffman tree from the heap
            self.__buildTree()
            self.__buildCodes()
            # creating the encoded text using the codes
            encoded_text = self.__getEncodedText(text)
            padded_encoded_text = self.__getPaddedEncodedText(encoded_text)
            # convert the encoded text into actual binary from
            bytes_array = self.__getBytesArray(padded_encoded_text)
            final_bytes = bytes(bytes_array)
            # write the final bytes in the output file
            my_dictionary = self.__reverseCodes
            with open(f'decoded.csv', 'w') as f:
                for key in my_dictionary.keys():
                    f.write("%s, %s\n" % (key, my_dictionary[key]))
            output.write(final_bytes)
            print(f'File Compressed. Compressed file Path: {output_path}\nDecode_CSV file: decoded.csv')
        return output_path

    @staticmethod
    def __removePadding(text):
        padded_info = text[:8]
        padding_amount = int(padded_info, 2)

        text_padding_removed = text[8:-1 * padding_amount]
        return text_padding_removed

    @staticmethod
    def __decodeText(text, reversedCodes):
        decoded_text = ""
        current_bits = ""
        for bit in text:
            current_bits += bit
            if current_bits in reversedCodes:
                decoded_text += reversedCodes[current_bits]
                current_bits = ""
        return decoded_text

    def decompress(self, input_path):
        csv_name = input('Enter the decode csv name: ')
        file_name, file_extension = os.path.splitext(input_path)
        output_path = file_name + "_decompressed" + ".txt"
        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            bit_string = ''
            byte = file.read(1)
            while byte:
                byte = ord(byte)
                bits = bin(byte)[2:].rjust(8, '0')
                bit_string += bits
                byte = file.read(1)

            actual_text = self.__removePadding(bit_string)
            with open(csv_name, mode='r') as infile:
                reader = csv.reader(infile)
                reversedCodes = {rows[0]: rows[1][1:] for rows in reader}

            decompressed_text = self.__decodeText(actual_text, reversedCodes)
            output.write(decompressed_text)
            print(f"File decompressed. Path: {output_path}")


s = input("Press 1 to compress a file. Press 0 to decompress a file.")
if s == "1":
    original_file_path = input("Enter the text file location: ")
    h = HuffmanCoding(original_file_path)
    h.compress()
else:
    inputFilePath = input("Enter location of the file to be decompressed: ")
    h = HuffmanCoding()
    h.decompress(inputFilePath)
