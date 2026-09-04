import sys
import unicodedata

# read from standard in
for line in sys.stdin:
    # for each character in the line
    for char in line:
        # if the character is a polytonic Greek letter
        if "\u1f00" <= char <= "\u1ffe":
            for c in unicodedata.normalize("NFD", char):
                print(c, hex(ord(c)), unicodedata.name(c))
            # remove the diacritics from the character
            char = "".join(c for c in unicodedata.normalize("NFD", char))
        # print the character
        print(char, end="")
