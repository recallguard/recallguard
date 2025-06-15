from backend.api.products.email_import import parse_email


def test_parse_email():
    content = "Widget\nGadget"
    assert parse_email(content) == ["Widget", "Gadget"]

