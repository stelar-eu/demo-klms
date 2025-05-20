from stelar.etl import Catalog


def test_sci(simple_catalog):

    simple_catalog.strongly_connected_index()

    mlist = list(simple_catalog.modules())

    mlist.sort(key=lambda x: x.scc_index)

    for m in mlist:
        print(m.name, m.scc_index)

    assert simple_catalog.get("m1").scc_index == 0
    assert simple_catalog.get("m2").scc_index == 2
    assert simple_catalog.get("m3").scc_index == 1
    assert simple_catalog.get("m4").scc_index == 2
    assert simple_catalog.get("m5").scc_index == 2
    assert simple_catalog.get("m6").scc_index == 3

