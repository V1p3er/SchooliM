from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Score:
    
    _value: float

    # post init validations and normalization
    def __post_init__(self):
        
        try:
            normalized = float(self._value)
        except(TypeError, ValueError):
            raise TypeError("Score must be a number!")

        if not 0.0 <= normalized <= 20.0:
            raise ValueError("Score should be between 0 to 20")

        object.__setattr__(self, "_value", normalized)