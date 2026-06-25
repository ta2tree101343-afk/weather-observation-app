import pytest
import wards
from schemas import Ward


def test_is_valid_known_ward():
    assert wards.is_valid("13101") is True


def test_is_valid_unknown_ward():
    assert wards.is_valid("99999") is False


def test_is_valid_empty_string():
    assert wards.is_valid("") is False


def test_get_name_known_ward():
    assert wards.get_name("13101") == "千代田区"


def test_get_name_unknown_ward_raises():
    with pytest.raises(KeyError, match="Unknown ward code"):
        wards.get_name("99999")


def test_list_all_returns_23_wards():
    result = wards.list_all()
    assert len(result) == 23


def test_list_all_returns_ward_instances():
    result = wards.list_all()
    assert all(isinstance(w, Ward) for w in result)
    assert result[0] == Ward(code="13101", name="千代田区")
    assert result[-1] == Ward(code="13123", name="江戸川区")
