# Lacuna

Lacuna is a character-level n-gram language model for restoring missing
characters in text. Train it on a corpus, mark each one-character gap with
`?`, and it ranks likely completions with beam search.

The repository also includes utilities for preparing Greek text, including a
processed form of the [SBL Greek New Testament](data/sblgnt.txt).

## Requirements

- Python 3.11 or later
- [Poetry](https://python-poetry.org/)

## Install

Clone the repository and install its locked dependencies:

```bash
poetry install
```

To work without Poetry, install the project dependencies listed in
[`pyproject.toml`](pyproject.toml) in a Python 3.11+ virtual environment.

## Quick start

Train a model on an iterable of strings, then use `?` for each character to
restore. The model works at the character level; spaces and punctuation are
characters too unless they have been removed during corpus preparation.

```python
from lacuna.lacuna import Lacuna

lacuna = Lacuna(3)  # trigram model
lacuna.train(["banana", "bandana"])

for result in lacuna.fill("ba?a", beam_width=10, top_k=3):
    print(result.prefix, result.score)
```

Each result is a `LacunaResult(prefix, item, suffixes, score)`. `prefix` is
the completed text and `score` is the model's accumulated ranking score.
Higher scores are ranked first.

For a corpus stored one example per line:

```python
from lacuna.lacuna import Lacuna

lacuna = Lacuna(4)
lacuna.train_from_file("data/sblgnt_processed.txt")

for result in lacuna.fill("λογ?ς", top_k=5):
    print(result.prefix, result.score)
```

## How masking works

- `?` is the default mask and represents exactly one missing character.
- Multiple masks represent multiple gaps, e.g. `"λογ??"` restores two
  characters.
- Change the mask when constructing the model: `Lacuna(4, mask="_")`.
- `beam_width` controls how many partial candidates are retained while filling
  multi-character gaps; `top_k` controls how many final candidates are
  returned.

The model uses NLTK's interpolated Kneser–Ney language model. The order passed
to `Lacuna(n)` is the largest character n-gram it considers. Text is padded
with begin/end markers by default so the model can learn start and end context.

## Corpus preparation

`data/sblgnt.txt` contains the source text with book/chapter/verse prefixes,
diacritics, punctuation, and spaces. `data/sblgnt_processed.txt` is its
normalized character stream, one verse per line, suitable for training.

Regenerate the processed file with:

```bash
poetry run python script/sblgnt_to_uc.py < data/sblgnt.txt > data/sblgnt_processed.txt
```

Other supplied scripts:

| Script | Purpose |
| --- | --- |
| `script/remove_diacritics.py` | Remove Greek diacritics, normalize sigma, and retain iota subscripts as `ι`. |
| `script/normalize.py` | Inspect Unicode normalization of polytonic Greek input. |
| `script/tei_to_text.py SOURCE_DIR TARGET_DIR` | Convert TEI XML files with Beta Code forms into UTF-8 text files. |
| `script/letter_count.py N` | Read standard input and emit tab-separated counts for character n-grams. |

For example, to produce bigram counts from the processed corpus:

```bash
poetry run python script/letter_count.py 2 < data/sblgnt_processed.txt > 2grams.tsv
```

## Development

Run the test suite with:

```bash
poetry run pytest
```

Format and lint using the included development dependencies:

```bash
poetry run black lacuna script tests
poetry run isort lacuna script tests
poetry run flake8 lacuna script tests
```
