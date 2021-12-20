import pytest

from bano.sources import bal


def test_process_should_validate_departements():
    with pytest.raises(ValueError):
        bal.process('BAL', ['123'])