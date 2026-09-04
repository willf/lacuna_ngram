# remove all diacritics from polytonic Greek text
# usage: python remove_diacritics.py < input.txt > output.txt

import sys
import unicodedata

# read from standard in
for line in sys.stdin:
    # for each character in the line
    for char in line:
        # if the character is a polytonic Greek letter
        # remove the diacritics from the character
        chars = []
        normed = unicodedata.normalize("NFD", char)
        if 0x0314 in [ord(c) for c in normed]:
            extra = chr(0x1FFE)
        else:
            extra = ""
        for c in extra + normed:
            if c == "ς" or c == "ϲ" or c == "Ϲ" or c == "Σ":
                chars.append("σ")
            elif (
                unicodedata.category(c) == "Mn"
                and unicodedata.name(c) == "COMBINING GREEK YPOGEGRAMMENI"
            ):
                chars.append("ι")
            elif ord(c) == 0x0314:  # rough breathing
                pass  # chars.append("h")
            elif unicodedata.category(c) != "Mn":
                chars.append(c)
        print("".join(chars), end="")
