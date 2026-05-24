def test_import_core_modules():
    import numpy
    import scipy
    import deap

    assert numpy is not None
    assert scipy is not None
    assert deap is not None