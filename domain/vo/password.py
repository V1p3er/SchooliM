import re
from dataclasses import dataclass, field

LOWERCASE_PATTERN = re.compile(r"[a-z]")
UPPERCASE_PATTERN = re.compile(r"[A-Z]")
DIGIT_PATTERN = re.compile(r"[0-9]")
SPECIAL_PATTERN = re.compile(r"[^a-zA-Z0-9]")

# immutable class using frozen=True parameter from dataclass
@dataclass(frozen=True, slots=True)
class Password:
    
    _value: str = field(repr=False)

    # post init validations
    def __post_init__(self):
        

        normalized = str(self._value).strip()

        if len(normalized) < 12:
            raise ValueError("password should be at least 12 characters")
        
        if not DIGIT_PATTERN.search(normalized):
            raise ValueError("password should contain at least one number")

        if not LOWERCASE_PATTERN.search(normalized):
            raise ValueError("password should contain at least one lowercase character")

        if not UPPERCASE_PATTERN.search(normalized):
            raise ValueError("password should contain at least one uppercase character")
        
        if not SPECIAL_PATTERN.search(normalized):
            raise ValueError("password should contain at least one special character")
        
        object.__setattr__(self, "_value", normalized)