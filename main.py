from classroom_data import *

QUESTION_NAMES = [
    "Question3",
    "Question4"
]


def load_classroom() -> Classroom:
    classroom = ClassroomBuilder("submissions").unzip().build()
    return classroom

def main():
    classroom = load_classroom()
    classroom.students[0].question_is_graded("Question3")
    save_classroom_to_json(classroom, "classroom.json")
    classroom = load_classroom_from_json("classroom.json")
    asd = 0

if __name__ == "__main__":
    main()
