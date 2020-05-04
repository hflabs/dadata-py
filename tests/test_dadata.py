import dadata


def test_clean():
    source = "source"
    result = dadata.clean(source)
    assert result == source
