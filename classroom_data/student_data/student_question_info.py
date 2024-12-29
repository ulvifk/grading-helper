from dataclasses import dataclass

from classroom_data.question_data.question import Question


@dataclass
class StudentQuestionInfo:
    question: Question
    code: str
    file_path: str
    grade: float

    def to_json(self):
        return {
            "question": self.question.to_json(),
            "code": self.code,
            "file_path": self.file_path,
            "grade": self.grade
        }