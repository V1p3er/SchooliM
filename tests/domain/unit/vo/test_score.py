import pytest

from domain.vo.score import Score


# happy path
def test_correct_input_and_int_to_float():

    score = Score(12)
    assert score._value == 12.0

def test_float_input():

    score = Score(15.5)
    assert score._value == 15.5

def test_string_numeric_input():

    score = Score("18.5")
    assert score._value == 18.5

# failure tests
@pytest.mark.parametrize(
    "invalid_inputs, error_type",
    [
        (None, TypeError),
        ("", TypeError),
        ("hello", TypeError),
        (-0.1, ValueError),
        (20.1, ValueError),
        (-1, ValueError),
        (21, ValueError),
        ([], TypeError),
        ({}, TypeError),
    ]
)
def test_invalid_inputs(invalid_inputs, error_type):
    
    with pytest.raises(error_type):
        Score(invalid_inputs)
