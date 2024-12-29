from dataclasses import dataclass

from .student_question_info import StudentQuestionInfo


@dataclass
class Student:
    name: str
    surname: str
    student_number: str
    submission_directory: str
    question_info: list[StudentQuestionInfo]
    is_graded: dict[str, bool]

    def to_json(self):
        return {
            "name": self.name,
            "surname": self.surname,
            "student_number": self.student_number,
            "submission_directory": self.submission_directory,
            "question_info": [info.to_json() for info in self.question_info],
            "is_graded": self.is_graded
        }

    def get_question_info(self, question_name):
        return next((info for info in self.question_info if info.question.question == question_name), None)

    def __hash__(self):
        return hash(self.name + self.surname)

    def question_is_graded(self, question_name: str):
        self.is_graded[question_name] = True
