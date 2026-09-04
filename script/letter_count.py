# from standard in,
# count how many times each letter appears in the input
# and print the counts in alphabetical order
# with a tab between the letter and the count
# and a newline at the end

import sys


def ngrams(line, n):
    for i in range(len(line) - n + 1):
        yield line[i : i + n]


n = sys.argv[1] or 1
n = int(n)
# create a dictionary to store the counts
counts = {}
# read from standard in
for line in sys.stdin:
    tokens = line.split(" ")
    tokens = [t for t in tokens if t != ""]
    tokens = ["^" + token + "$" for token in tokens]
    line = "".join(tokens)
    # for each letter in the line
    for ngram in ngrams(line, n):
        # if the letter is not in the dictionary
        if ngram not in counts:
            # add the letter to the dictionary with a count of 1
            counts[ngram] = 1
        # if the letter is in the dictionary
        else:
            # increment the count for the letter
            counts[ngram] += 1

# sort the dictionary by the keys
sorted_counts = sorted(counts.items())
# for each letter and count in the sorted dictionary
for ngram, count in sorted_counts:
    # print the letter and count with a tab between them
    print(ngram + "\t" + str(count))
