from stelar.etl.base import Catalog, Module


def test_create_catalog():

    # Create a catalog
    cat = Catalog()

    # Add a product to the catalog
    m1 = Module("m1")
    m2 = Module("m2")
    m3 = Module("m3")
    m4 = Module("m4")
    m5 = Module("m5")
    m6 = Module("m6")

    m2.require(m1)
    m3.require(m1)
    m4.require(m2)
    m5.require([m4, m2])
    m6.require(m3)
    m6.require(m5)


    M = [m1, m2, m3, m4, m5, m6]

    cat.add(M)

    assert len(cat.root) == 6
    assert len(list(cat.modules())) == 6
    assert set(cat.modules()) == set(M)

    assert cat.get("m1") is m1
    assert cat.get("m2") is m2
    assert cat.get("m3") is m3
    assert cat.get("m4") is m4
    assert cat.get("m5") is m5
    assert cat.get("m6") is m6

