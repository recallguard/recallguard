from ai.summarizer import summarize


def test_summarize():
    text = "Important recall notice"
    assert summarize(text).startswith("Summarize")

