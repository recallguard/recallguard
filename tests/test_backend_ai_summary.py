from backend.utils.ai_summary import summarize_recall


class DummyClient:
    class Chat:
        class Completions:
            @staticmethod
            def create(*args, **kwargs):
                class Msg:
                    content = "This is a hazard summary. Next: Take action."

                class Choice:
                    message = Msg()

                class Resp:
                    choices = [Choice()]

                return Resp()

        def __init__(self):
            self.completions = self.Completions()

    def __init__(self, *args, **kwargs):
        self.chat = self.Chat()


def test_summarize_recall(monkeypatch):
    import openai

    monkeypatch.setattr(openai, "OpenAI", DummyClient)
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    summary, next_steps = summarize_recall("Widget", "fire", "Class I")
    assert summary.startswith("This is")
    assert next_steps.startswith("Next:")

