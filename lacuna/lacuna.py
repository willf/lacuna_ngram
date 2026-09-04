from collections import namedtuple
from functools import partial
from itertools import chain

from nltk.lm import KneserNeyInterpolated
from nltk.lm.preprocessing import padded_everygram_pipeline
from nltk.util import everygrams, pad_sequence

flatten = chain.from_iterable


def sliding_window(s, k=1):
    for i in range(len(s) - k + 1):
        yield s[i : i + k]


def split_on_mask(text, mask="?"):
    splits = [prefix + mask for prefix in text.split(mask)]
    if not text.endswith(mask):
        splits[-1] = splits[-1][: -len(mask)]
    else:
        splits = splits[:-1]
    return splits


def make_result(sequence, token, score):
    return {"sequence": sequence, "token_str": token, "score": score}


# Result = namedtuple("Result", ["sequence", "log_probability"])
# # (prefix, score, item) -> (prefix + item, score + logscore(item)) for item in expansion(item)

LacunaResult = namedtuple("LacunaResult", ["prefix", "item", "suffixes", "score"])


class Lacuna:
    def __init__(self, n, BOS="␂", EOS="␃", pad_left=True, pad_right=True, mask="?"):
        self.n = n
        self.ngrams = {}
        self.n
        self.BOS = BOS
        self.EOS = EOS
        self.pad_left = pad_left
        self.pad_right = pad_right
        self.lm = KneserNeyInterpolated(self.n)
        self.mask = mask

    def padder(self):
        return partial(
            pad_sequence,
            pad_left=self.pad_left,
            pad_right=self.pad_right,
            left_pad_symbol=self.BOS,
            right_pad_symbol=self.EOS,
            n=self.n,
        )

    def create_training_data(self, strings):
        texts = [list(s) for s in strings]
        return (
            (everygrams(list(self.padder()(text)), max_len=self.n) for text in texts),
            flatten(map(self.padder(), texts)),
        )

    def _create_training_data(self, strings):
        texts = [list(s) for s in strings]
        return padded_everygram_pipeline(self.n, texts)

    def train(self, strings):
        train, vocab = self.create_training_data(strings)
        self.lm.fit(train, vocab)

    def logscore(self, char, context=[]):
        return self.lm.logscore(char, context)

    def score(self, char, context=[]):
        return self.lm.score(char, context)

    def logscore_sequence(self, sequence):
        return self.lm.logscore(sequence[-1], sequence[:-1])

    def score_sequence(self, sequence):
        return self.lm.score(sequence[-1], sequence[:-1])

    def logscore_string(self, string):
        return self.lm.score(string[-1], list(string[:-1]))

    def score_string(self, string):
        return self.lm.score(string[-1], list(string[:-1]))

    def vocabulary(self):
        return set(self.lm.vocab) - {"<UNK>", self.BOS, self.EOS}

    def vocabulary_string(self):
        return "".join(sorted(self.vocabulary()))

    def generate(
        self,
        n_letters,
        text_seed=[],
        random_seed=None,
    ):
        return self.lm.generate(n_letters, text_seed=text_seed, random_seed=random_seed)

    def train_from_file(self, filename):
        with open(filename, "r") as f:
            self.train(f.read().split("\n"))

    def expansion(self, item):
        if item.endswith(self.mask):
            for c in self.vocabulary():
                yield item.replace(self.mask, c)
        else:
            yield item

    # "prefix", "item" "suffixes", "score"

    def initial_state(self, query):
        suffixes = split_on_mask(query, self.mask)
        expansion = self.expansion(suffixes[0])
        remaining = suffixes[1:]
        for item in expansion:
            yield LacunaResult(
                prefix=item,
                item=item,
                suffixes=remaining,
                score=self.logscore_string(item),
            )

    def beam_search(self, query, beam_width=10):
        beam = self.initial_state(query)
        beam = sorted(beam, key=lambda x: x.score, reverse=True)[0:beam_width]
        while beam[0].suffixes:
            new_beam = []
            for partial_result in beam:
                expansion = self.expansion(partial_result.suffixes[0])
                for item in expansion:
                    full_expansion = partial_result.prefix + item
                    new_beam.append(
                        LacunaResult(
                            prefix=full_expansion,
                            item=item,
                            suffixes=partial_result.suffixes[1:],
                            score=partial_result.score
                            + self.logscore_string(full_expansion),
                        )
                    )
            beam = sorted(new_beam, key=lambda x: x.score, reverse=True)[0:beam_width]
        return beam

    def fill(self, text, beam_width=10, top_k=5):
        results = self.beam_search(text, beam_width=beam_width)
        return results[0:top_k]


if __name__ == "__main__":
    lac = Lacuna(4)
    lac.train_from_file("/Users/willf/Downloads/gutenberg/austen-sense.txt")
    result = [
        ch
        for ch in lac.generate(250, text_seed=list("Replied Elinor"))
        if ch not in ["␂", "␃"]
    ]
    print("Elinor says" + "".join(result))
    # query = "very pretty"
    # top_results = lac.max_probable_sequence(query)
    # print(f"Top results for {query}:")
    # for r in top_results:
    #    print(f"{''.join(r.sequence)} with log probability {r.log_probability}")
    query = "lovely day"
    top_results = lac.max_probable_sequence(query, use_padding=False)
    print(f"Top results for {query}:")
    for r in top_results:
        print(f"{''.join(r.sequence)} with log probability {r.log_probability}")
    print("Done!")
