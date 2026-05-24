import pytest

from domain.vo.username import UserName


# happy paths
def test_valid_username_and_normalization_functionality():
    
    username = UserName(" Arman ")

    assert username._value == "arman"

# failure tests using pytest parametrize decorator for each invalid inputs with their error types
@pytest.mark.parametrize(
    "invalid_inputs, error_type",
    [
        ("", ValueError),
        ("  ", ValueError),
        ("s", ValueError),
        ("longggggggggggggggggggggggggggggggggggggggggggggggggggg", ValueError),
        ("Spe@ial", ValueError),
    ]
)
def test_invalid_usernames(invalid_inputs, error_type):

    with pytest.raises(error_type):
        UserName(invalid_inputs)