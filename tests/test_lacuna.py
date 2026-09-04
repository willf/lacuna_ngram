import pytest

from lacuna.lacuna import Lacuna, split_on_mask, sliding_window
from lacuna.utils import beam_search, create_prompts, fill


def test_sliding_window_returns_overlapping_windows():
    assert list(sliding_window("abcd", 2)) == ["ab", "bc", "cd"]


def test_split_on_mask_preserves_masked_segments():
    assert split_on_mask("ba?a") == ["ba?", "a"]
    assert split_on_mask("ba??") == ["ba?", "?"]
    assert split_on_mask("banana") == ["banana"]


def test_utils_beam_search_keeps_highest_scoring_sequences():
    results = [
        [
            {"sequence": "a[MASK]", "token_str": "x", "score": 0.8},
            {"sequence": "b[MASK]", "token_str": "y", "score": 0.7},
        ],
        [
            {"sequence": "[MASK]", "token_str": "m", "score": 0.9},
            {"sequence": "[MASK]", "token_str": "n", "score": 0.1},
        ],
    ]

    ranked = beam_search(results, k=2, mask="[MASK]")

    assert [result.sequence for result in ranked] == ["am", "bm"]
    assert ranked[0].score == pytest.approx(0.72)


def test_utils_fill_returns_input_when_no_mask_is_present():
    assert fill("plain text", pipe=None) == [("plain text", 1)]


def test_create_prompts_masks_each_token_position():
    assert create_prompts(["one", "two", "three"]) == [
        "[MASK] two three",
        "one [MASK] three",
        "one two [MASK]",
    ]


def test_lacuna_trains_and_fills_a_character_gap():
    model = Lacuna(3)
    model.train(["banana", "bandana"])

    assert model.vocabulary() == {"a", "b", "d", "n"}
    assert model.vocabulary_string() == "abdn"
    assert {result.prefix for result in model.fill("ba?a", top_k=3)} >= {"bana"}


def test_lacuna_train_from_file(tmp_path):
    corpus = tmp_path / "corpus.txt"
    corpus.write_text("cat\ndog\n", encoding="utf-8")

    model = Lacuna(2)
    model.train_from_file(corpus)

    assert model.vocabulary() == {"a", "c", "d", "g", "o", "t"}
