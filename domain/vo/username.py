import re
from dataclasses import dataclass

# valid username pattern to match username with this re compiled pattern
_VALID_USERNAME_PATTERN = re.compile(r"^[a-z0-9_-]+$")


@dataclass(frozen=True, slots=True)
class UserName:

    _value: str

    # post init validation for ensuring correct object would be created
    def __post_init__(self):
        
        try:
            normalize = str(self._value).strip().lower()
        except(TypeError, ValueError):
            raise TypeError("Username must be a string!")

        length = len(normalize)

        if not normalize:
            raise ValueError("Username cannot be empty")
        
        if not 3 <= length <= 20:
            raise ValueError("Username must be between 3 to 20 characters")
        
        if not re.fullmatch(_VALID_USERNAME_PATTERN, normalize):
            raise ValueError("Username cannot have special characters like (@ $ # etc) in it. Correct username example: arman_test-1_")

        # cause our class set to immutable forcfully changing self._value = normalized
        object.__setattr__(self, "_value", normalize)