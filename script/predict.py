"""Train a character n-gram model from a file and predict text from stdin."""

import argparse
import sys

from lacuna.lacuna import Lacuna


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="Train from a processed text file and fill masked text from stdin."
    )
    parser.add_argument(
        "training_file",
        help="processed text file used to train the character n-gram model",
    )
    parser.add_argument(
        "-n",
        "--order",
        type=positive_int,
        default=3,
        help="largest character n-gram order (default: 3)",
    )
    parser.add_argument(
        "--beam-width",
        type=positive_int,
        default=10,
        help="number of partial results retained during search (default: 10)",
    )
    parser.add_argument(
        "--top-k",
        type=positive_int,
        default=5,
        help="number of completed results to print (default: 5)",
    )
    parser.add_argument(
        "--mask",
        default="?",
        help="character marking a missing character (default: ?)",
    )
    return parser.parse_args(args)


def main(args=None):
    options = parse_args(args)
    model = Lacuna(options.order, mask=options.mask)
    model.train_from_file(options.training_file)

    for query in sys.stdin.read().splitlines():
        for result in model.fill(
            query,
            beam_width=options.beam_width,
            top_k=options.top_k,
        ):
            print(f"{result.prefix}\t{result.score}")


if __name__ == "__main__":
    main()
