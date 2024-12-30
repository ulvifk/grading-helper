import logging
import os
import shutil
from dataclasses import dataclass
from typing import List

import mosspy

from classroom_data import Classroom, settings_loader


@dataclass
class StudentSubmission:
    name: str
    surname: str
    student_number: str
    submission_code: str

    def get_temp_submission_file_name(self) -> str:
        return f"{self.name}_{self.surname}_{self.student_number}.py"


class MossAPI:
    _api_key: str
    _classroom: Classroom
    _moss: mosspy.Moss
    _temp_dir: str = "temp/"

    def __init__(self, classroom: Classroom):
        self._api_key = os.getenv("MOSS_API_KEY")
        if self._api_key is None:
            raise ValueError("MOSS_API_KEY environment variable is not set")

        self._classroom = classroom

        if not os.path.exists(self._temp_dir):
            os.makedirs(self._temp_dir)

    def run_moss(self, question_name: str, save_dir: str):
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        self._moss = mosspy.Moss(self._api_key, "python")
        logging.basicConfig(level=logging.ERROR)

        student_submissions = self._get_student_submissions(question_name)
        question = next((q for q in settings_loader.questions if q.question == question_name), None)
        if question is None:
            raise ValueError(f"Cannot find question {question_name}")

        if question.base_code != "":
            self._add_base_code(question.base_code)

        for submission in student_submissions:
            self._add_submission(submission)

        url = self._moss.send(lambda file_path, display_name: print('*', end='', flush=True))

        print()
        print("Report Url: " + url)

        dest_dir = f"submission/{question_name}"
        os.makedirs(dest_dir, exist_ok=True)

        # Save report file
        self._moss.saveWebPage(url, f"{save_dir}/report.html")

        # Download whole report locally including code diff links
        # mosspy.download_report(url, f"{save_dir}/report/", connections=8, log_level=10,
        #                        on_read=lambda url: print('*', end='', flush=True))

        shutil.rmtree(self._temp_dir)

    def _add_submission(self, submission: StudentSubmission):
        code = submission.submission_code
        temp_file_name = self._temp_dir + submission.get_temp_submission_file_name()

        with open(temp_file_name, "w") as f:
            f.write(code)

        self._moss.addFile(temp_file_name)

    def _add_base_code(self, base_code: str):
        base_code_file = self._temp_dir + "base_code.py"
        with open(base_code_file, "w") as f:
            f.write(base_code)
        self._moss.addBaseFile(base_code_file)

    def _get_student_submissions(self, question_name: str) -> List[StudentSubmission]:
        submissions = []
        for student in self._classroom.students:
            question_info = student.get_question_info(question_name)

            if question_info is None:
                student_submission = None
            else:
                student_submission = StudentSubmission(name=student.name,
                                                       surname=student.surname,
                                                       student_number=student.student_number,
                                                       submission_code=question_info.code)

            if student_submission is None:
                print(
                    f"Cannot find submission for student {student.name} {student.surname} "
                    f"for questions {question_name}")
                continue

            if student_submission.submission_code == "":
                print(f"Submission for student {student.name} {student.surname} is empty")
                continue

            submissions.append(student_submission)

        return submissions
