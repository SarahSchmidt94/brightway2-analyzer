import pytest
from bw2data.tests import bw2test
from bw2data import Database, Method, get_activity
from bw2calc import LCA
from bw2analyzer import perturbation_analysis as pa



@pytest.fixture
@bw2test
def pa_fixture():
    Database("biosphere3").write(
        {
            ("biosphere3", "bio-exc1"): {
                "name": "bio-exc1",
                "type": "emission",
                "categories": ("cat1", "cat2"),
            },
            ("biosphere3", "bio-exc2"): {
                "name": "bio-exc2",
                "type": "emission",
                "categories": ("cat1", "cat2"),
            },
            ("biosphere3", "bio-exc3"): {
                "name": "bio-exc3",
                "type": "emission",
                "categories": ("cat1", "cat2"),
            },
            ("biosphere3", "bio-exc4"): {
                "name": "bio-exc4",
                "type": "emission",
                "categories": ("cat1", "cat2"),
            },
            ("biosphere3", "bio-exc5"): {
                "name": "bio-exc5",
                "type": "emission",
                "categories": ("cat1", "cat2"),
            },
        }
    )

    method = Method(("test method",))
    method.register()
    method.write(
        [
            (("biosphere3", "bio-exc1"), 1),
            (("biosphere3", "bio-exc2"), 2),
            (("biosphere3", "bio-exc3"), 3),
            (("biosphere3", "bio-exc4"), 4),
            (("biosphere3", "bio-exc5"), 5),
        ]
    )

    Database("foreground").write(
        {
            ("foreground", "act 1"): {
                "name": "act1",
                "location": "GLO",
                "exchanges": [
                    {
                        "input": ("foreground", "act 1"),
                        "amount": 1,
                        "type": "production",
                    },
                    {
                        "input": ("biosphere3", "bio-exc1"),
                        "amount": 1,
                        "type": "biosphere",
                    },
                    {
                        "input": ("biosphere3", "bio-exc2"),
                        "amount": 1,
                        "type": "biosphere",
                    },
                    {
                        "input": ("foreground", "act 2"),
                        "amount": 1,
                        "type": "technosphere",
                    },
                    {
                        "input": ("foreground", "act 3"),
                        "amount": 1,
                        "type": "technosphere",
                    },
                    {
                        "input": ("foreground", "act 3"),
                        "amount": 2,
                        "type": "technosphere",
                    },
                    {
                        "input": ("foreground", "act 4"),
                        "amount": 1,
                        "type": "technosphere",
                    },
                ],
            },
            ("foreground", "act 2"): {
                "name": "act2",
                "location": "GLO",
                "exchanges": [
                    {
                        "input": ("foreground", "act 2"),
                        "amount": 1,
                        "type": "production",
                    },
                    {
                        "input": ("biosphere3", "bio-exc3"),
                        "amount": 1,
                        "type": "biosphere",
                    },
                ]
            },
            ("foreground", "act 3"): {
                "name": "act3",
                "location": "GLO",
                "exchanges": [
                    {
                        "input": ("foreground", "act 3"),
                        "amount": 1,
                        "type": "technosphere",
                    },
                    {
                        "input": ("biosphere3", "bio-exc4"),
                        "amount": 1,
                        "type": "biosphere",
                    },
                ]
            },
            ("foreground", "act 4"): {
                "name": "act4",
                "location": "GLO",
                "exchanges": [
                    {
                        "input": ("foreground", "act 4"),
                        "amount": 1,
                        "type": "production",
                    },
                    {
                        "input": ("biosphere3", "bio-exc5"),
                        "amount": 1,
                        "type": "biosphere",
                    },
                    {
                        "input": ("biosphere3", "bio-exc4"),
                        "amount": 0,
                        "type": "biosphere",
                    },
                    {
                        "input": ("foreground", "act 2"),
                        "amount": 1,
                        "type": "technosphere",
                    },
                ]
            },
        }
    )

def test_fixture_no_errors(pa_fixture):
    bio = Database("biosphere")
    db = Database("foreground")
    act2 = get_activity(("foreground", "act 2"))
    method = ("test method",)
    lca = LCA({act2:1}, method)
    lca.lci()
    lca.lcia()
    assert lca.score == 3

def test_select_parameters_by_activity_list(pa_fixture):
    act1= get_activity(('foreground', 'act 1'))
    act2 = get_activity(('foreground', 'act 2'))
    act_list=[act1,act2]
    exc_types=['technosphere', 'biosphere', 'all', 'xyz']

    for exc_type in exc_types:
        if exc_type == 'technosphere':
            expected_exclist=[*act1.technosphere(), *act2.technosphere()]
            expected_exclist=[e._data for e in expected_exclist]
            exclist=pa.select_parameters_by_activity_list(act_list,exc_type=exc_type)
            exclist = [e._data for e in exclist]
            assert exclist == expected_exclist
        elif exc_type == 'biosphere':
            expected_exclist=[*act1.biosphere(), *act2.biosphere()]
            expected_exclist=[e._data for e in expected_exclist]
            exclist=pa.select_parameters_by_activity_list(act_list,exc_type=exc_type)
            exclist = [e._data for e in exclist]
            assert exclist == expected_exclist
        elif exc_type == 'all':
            expected_exclist=[*act1.technosphere(),*act1.biosphere(), *act2.technosphere(),*act2.biosphere()]
            expected_exclist = [e._data for e in expected_exclist]
            exclist=pa.select_parameters_by_activity_list(act_list,exc_type=exc_type)
            exclist = [e._data for e in exclist]
            assert exclist == expected_exclist
        else:
            expected_exclist=[]
            exclist=pa.select_parameters_by_activity_list(act_list,exc_type=exc_type)
            assert exclist == expected_exclist


def test_select_parameters_by_supply_chain_level(pa_fixture):
   act1 = get_activity(('foreground', 'act 1'))
   supply_chain_levels=[1,2,5]
   for s in supply_chain_levels:
        exclist = pa.select_parameters_by_supply_chain_level(act1,max_level=s)
        exclist = [e._data for e in exclist]
        len_exclist = len(exclist)
        if s == 1:
            expected_exclist = [*act1.biosphere(), *act1.technosphere()]
            expected_exclist = [e._data for e in expected_exclist]
            len_expected_exclist = len(expected_exclist)
        if s == 2:
            len_expected_exclist = 13
        if s == 5:
            len_expected_exclist = 26
        assert len_exclist == len_expected_exclist


def test_check_for_duplicates(pa_fixture):
    act3 = get_activity(('foreground', 'act 3'))
    act3_excs=[exc for exc in act3.exchanges()]
    elem=pa.check_for_duplicates(act3_excs)
    expected_elem = ('bio-exc4', 'act 3')
    assert elem == expected_elem

def test_check_for_loops(pa_fixture):
    act3 = get_activity(('foreground', 'act 3'))
    act3_excs = [exc for exc in act3.exchanges()]
    exclist = pa.check_for_loops(act3_excs)
    exclist = [e._data for e in exclist]
    expected_exclist = [*act3.biosphere()]
    expected_exclist = [e._data for e in expected_exclist]
    assert exclist == expected_exclist

def test_check_for_zeros(pa_fixture):
    act4 = get_activity(('foreground', 'act 4'))
    act4_excs = [exc for exc in act4.biosphere()]
    exclist = pa.check_for_zeros(act4_excs)
    exclist = [e._data for e in exclist]
    expected_exclist = [exc for exc in act4.biosphere() if exc.amount != 0]
    expected_exclist = [e._data for e in expected_exclist]
    assert expected_exclist == exclist

def test_parameters_to_dataframe(pa_fixture):
    act1 = get_activity(('foreground', 'act 1'))
    exclist = pa.select_parameters_by_supply_chain_level(act1)
    param_df = pa.parameters_to_dataframe(exclist, category_type='type')
    actual_param_tuple=(len(param_df), {'biosphere':param_df['type'].value_counts()['biosphere'],
                                        'technosphere':param_df['type'].value_counts()['technosphere'],})
    expected_param_tuple=(6, {'biosphere' : 2, 'technosphere': 4})
    assert expected_param_tuple == actual_param_tuple

def test_create_presamples(pa_fixture):
    act1 = get_activity(('foreground', 'act 1'))
    exclist = pa.select_parameters_by_supply_chain_level(act1)
    param_df = pa.parameters_to_dataframe(exclist, category_type='type')
    pa.create_presamples(param_df, 'foreground')
    #assert

#def test_perform_perturbation_analysis():
   # assert

#def test_calculate_sensitivity_ratios():
   # assert

#def test_calculate_sensitivity_coefficients():
  #  assert





if __name__ == "__main__":
    pa_fixture()
    test_fixture_no_errors(None)
    test_select_parameters_by_activity_list()
    test_select_parameters_by_supply_chain_level()
    test_check_for_duplicates()
