from classroom_data import *
from moss_plag_checker import MossAPI


QUESTION_NAMES = [
    "Question1"
]

def load_classroom() -> Classroom:
    classroom = ClassroomBuilder("submissions").unzip().build()
    return classroom

if __name__ == "__main__":
    classroom = load_classroom()

    moss_api = MossAPI(classroom)
    moss_api.run_moss(QUESTION_NAMES, "plag_report")