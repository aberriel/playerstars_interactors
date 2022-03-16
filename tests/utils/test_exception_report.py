from playerstars_interactors.utils.report_exception import exception_str


def test_exception_report():
    exc = ValueError('oops')
    assert exception_str(exc) == 'ValueError(oops)'

    exc = IndexError('oops')
    assert exception_str(exc) == 'IndexError(oops)'
