
from sample_error_fixed import greet


def test_greet_prints_hello(capsys):
    greet()
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"
