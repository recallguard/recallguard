from backend.api.alerts.check_user_items import check_user_items


def test_check_user_items():
    items = ["widget", "Gadget"]
    recalls = [{"product": "Widget"}]
    assert check_user_items(items, recalls) == ["widget"]

    items = ["Widget", "Gadget"]
    recalls = [{"product": "Widget"}]
    assert check_user_items(items, recalls) == ["Widget"]
