import pytest

from bano import helpers


def test_is_valid_housenumber():
    assert helpers.is_valid_housenumber('1234') is True
    assert helpers.is_valid_housenumber('012345678910') is False


@pytest.mark.parametrize('input,output', [
    ({}, ''),
    ({'addr:postcode': '75001'}, '75001'),
    ({'postal_code': '75001'}, '75001'),
    ({'addr:postcode': '75001', 'postal_code': '77999'}, '75001'),
    ({'addr:postcode': '', 'postal_code': '77999'}, '77999'),
    ({'addr:postcode': '', 'postal_code': ''}, '')
])
def test_find_cp_in_tags(input, output):
    assert helpers.find_cp_in_tags(input) == output


@pytest.mark.parametrize('input,output', [
    ('Boulevard de Sébastopol', 'BD SEBASTOPOL')
])
def test_normalize(input, output):
    assert helpers.normalize(input) == output

def test_is_valid_fantoir():
    assert helpers.is_valid_fantoir('', '12345') is False
    assert helpers.is_valid_fantoir('123456789', '12345') is False
    assert helpers.is_valid_fantoir('1234567890', '12346') is False
    assert helpers.is_valid_fantoir('1234567890', '12345') is True
