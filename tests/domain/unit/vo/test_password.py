import pytest
from dataclasses import FrozenInstanceError

from domain.vo.password import Password

# happy path test
def test_successful_password():

    password = Password("StrongPassword123@")
    assert password.value == "StrongPassword123@"

def test_pass_is_immutable():

    password = Password("StrongPassword123@")
    with pytest.raises(FrozenInstanceError):
        password.value = "StrongPassword123@11"

# failures test
@pytest.mark.parametrize(
    "invalid_input, error_type",
    [
        ("sTrong1!", ValueError),
        ("Strongpassword#####", ValueError),
        ("biiisatoo123!!!!!!", ValueError),
        ("BIISTOO123123123!", ValueError),
        ("BIstoooo1231241sf", ValueError),
        ("", ValueError),
        (" ", ValueError),
        (None, TypeError),
        (123414, TypeError)
    ]
)
def test_invalid_password(invalid_input, error_type):

    with pytest.raises(error_type):
        Password(invalid_input)