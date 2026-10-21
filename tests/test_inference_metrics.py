from tuneforge.inference import response_repetition_ratio


def test_empty_response_has_zero_repetition():
    assert response_repetition_ratio("") == 0.0


def test_unique_words_have_zero_repetition():
    assert response_repetition_ratio("one two three") == 0.0


def test_repeated_words_raise_repetition_ratio():
    ratio = response_repetition_ratio("one one two two")
    assert ratio == 0.5
