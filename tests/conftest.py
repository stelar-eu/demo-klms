import pytest
from stelar.etl.base import Catalog, Module

@pytest.fixture()
def simple_catalog():

    cat = Catalog()

    # Add a product to the catalog
    m1 = Module("m1")
    m2 = Module("m2")
    m3 = Module("m3")
    m4 = Module("m4")
    m5 = Module("m5")
    m6 = Module("m6")

    m2.require(m1)
    m2.require(m3)
    m2.require(m5)
    m3.require(m1)
    m4.require(m2)
    m5.require(m4)
    m6.require(m3)
    m6.require(m5)


    M = [m1, m2, m3, m4, m5, m6]

    cat.add(M)

    return cat