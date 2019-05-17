from bano import models


def test_register_should_set_new_item():
    adresses = models.Adresses()
    adresses.register("Boulevard de Sébastopol")
    assert "BD SEBASTOPOL" in adresses