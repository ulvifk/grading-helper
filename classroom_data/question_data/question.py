from dataclasses import dataclass


@dataclass
class Question:
    question: str
    keys: list[str]
    possible_grades: list[float]
    grade: float

    def __post_init__(self):
        if self.grade not in self.possible_grades:
            raise ValueError(f"Grade {self.grade} is not in possible grades {self.possible_grades}")

    def to_json(self):
        return {
            "question": self.question,
            "keys": self.keys,
            "grade": self.grade
        }
