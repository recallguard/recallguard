from backend.utils.priority import classify_recall

class Obj:
    def __init__(self, classification=None, hazard=None):
        self.classification = classification
        self.hazard = hazard


def test_classify_recall_keyword():
    r = Obj(classification="Class II", hazard="Risk of fire and burns")
    assert classify_recall(r) == "urgent"


def test_classify_recall_default():
    r = Obj(classification="Class III", hazard="minor defect")
    assert classify_recall(r) == "digest"
