from backend.api.products.vin_lookup import vin_lookup


def test_vin_lookup():
    result = vin_lookup("123")
    assert result["vin"] == "123"

