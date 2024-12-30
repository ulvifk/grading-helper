from classroom_data import *
from moss_plag_checker import MossAPI


QUESTION_NAMES = [
     "Question1",
    "Question2",
    "Question3",
    "Question4",
]

def load_classroom() -> Classroom:
    classroom = ClassroomBuilder("submissions").unzip().build()
    return classroom

if __name__ == "__main__":
    classroom = load_classroom()

    for question_name in QUESTION_NAMES:
        moss_api = MossAPI(classroom)
        moss_api.run_moss(question_name, f"plag_report/{question_name}")
