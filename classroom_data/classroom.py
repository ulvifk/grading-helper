import json
import os
import zipfile
from collections import namedtuple
from dataclasses import dataclass
from typing import Callable, Self, List

from classroom_data import StudentQuestionInfo, Question, settings_loader
from classroom_data.student_data.student import Student


@dataclass
class Classroom:
    students: list[Student]

    def to_json(self):
        return [student.to_json() for student in self.students]


StudentInformation = namedtuple("StudentInformation", ["name", "surname", "student_number", "submission_directory"])
NameFormatter = Callable[[str], StudentInformation]


def _default_name_formatter(path: str) -> StudentInformation:
    dir_name = path.split("/")[-1]
    name = dir_name.split("_")[0].split(" ")[0]
    surname = dir_name.split("_")[0].split(" ")[1]
    student_number = int(dir_name.split("_")[1])
    return StudentInformation(name=name, surname=surname, student_number=student_number, submission_directory=path)


class ClassroomBuilder:
    directory: str
    _name_formatter: NameFormatter
    _questions: list[Question]

    def __init__(self, directory: str):
        self.directory = directory
        self._name_formatter = _default_name_formatter
        self._questions = settings_loader.questions

    def set_name_formatter(self, name_formatter: NameFormatter) -> Self:
        self._name_formatter = name_formatter
        return self

    def unzip(self) -> Self:
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                try:
                    if file.endswith(".zip"):
                        zip_path = os.path.join(root, file)
                        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                            zip_ref.extractall(root)
                except Exception as e:
                    print(f"Failed to unzip {file}. Reason: {e}")

        return self

    def build(self) -> Classroom:
        def get_all_student_submission_paths() -> list[str]:
            student_submission_paths = []
            for name in os.listdir(self.directory):
                full_path = os.path.join(self.directory, name)
                if os.path.isdir(full_path):
                    student_submission_paths.append(full_path)

            return student_submission_paths

        student_submission_dirs = get_all_student_submission_paths()

        students = []
        for student_submission_dir in student_submission_dirs:
            student_information = self._name_formatter(student_submission_dir)

            q_info = self._get_student_question_info_list(student_submission_dir)
            students.append(Student(
                name=student_information.name,
                surname=student_information.surname,
                student_number=student_information.student_number,
                submission_directory=student_information.submission_directory,
                question_info=q_info,
                is_graded={q_info.question.question: False for q_info in q_info}
            ))

        for student in students:
            for q_info in student.question_info:
                if q_info.code == "":
                    print(f"Student {student.name} {student.surname} did not submit a file for question {q_info.question.question}")

        return Classroom(students=students)

    def _get_student_question_info_list(self, submission_directory: str) -> list[StudentQuestionInfo]:
        def get_submission_files() -> List[str]:
            submission_files = []
            for root, dirs, files in os.walk(submission_directory):
                for file in files:

                    if "macos" in root.lower():
                        continue

                    if file.endswith(".py"):
                        submission_files.append(os.path.join(root, file))

            return submission_files

        submission_files = get_submission_files()
        question_info_list = []

        for question in self._questions:
            respective_submission_file = next((file for file in submission_files
                                               if any(key in file.lower() for key in question.keys)), None)

            if respective_submission_file is None:
                code = ""
            else:
                with open(respective_submission_file, "r") as f:
                    code = f.read()

            question_info = StudentQuestionInfo(
                question=question,
                code=code,
                file_path=respective_submission_file,
                grade=0
            )
            question_info_list.append(question_info)

        return question_info_list


def save_classroom_to_json(classroom: Classroom, file_name: str):
    data = [student.to_json() for student in classroom.students]
    with open(file_name, "w") as f:
        # noinspection PyTypeChecker
        json.dump(data, f, indent=4)


def load_classroom_from_json(file_name: str) -> Classroom:
    def get_student_q_info_json(student_json: dict, question: Question) -> dict:
        return next(
            (info for info in student_json["question_info"] if info["question"]["question"] == question.question), None)

    with open(file_name, "r") as f:
        data = json.load(f)

    students = []
    for student_json in data:
        question_info = []
        for question in settings_loader.questions:
            q_info_json = get_student_q_info_json(student_json, question)

            question_info.append(StudentQuestionInfo(
                question=question,
                code=q_info_json["code"],
                grade=q_info_json["grade"],
                file_path=q_info_json["file_path"]
            ))

        student = Student(
            name=student_json["name"],
            surname=student_json["surname"],
            student_number=student_json["student_number"],
            submission_directory=student_json["submission_directory"],
            question_info=question_info,
            is_graded=student_json["is_graded"]
        )
        students.append(student)

    return Classroom(students=students)

def write_grades_to_excel(classroom: Classroom, file_name: str):
    import pandas as pd

    datas = {
    }
    for question in settings_loader.questions:
        data = []
        for student in classroom.students:
            q_info = next(info for info in student.question_info if info.question.question == question.question)
            data.append([student.name, student.surname, student.student_number, q_info.grade, student.is_graded[question.question]])

        df = pd.DataFrame(data, columns=["Name", "Surname", "Student Number", "Grade", "Is Graded"])
        datas[question.question] = df

    with pd.ExcelWriter(file_name) as writer:
        for key in datas:
            datas[key].to_excel(writer, sheet_name=key, index=False)

