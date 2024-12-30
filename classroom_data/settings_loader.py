import yaml

from classroom_data.question_data.question import Question

with open("settings.yml") as f:
    data = yaml.safe_load(f)

questions = []
for question_data in data["Questions"]:

    if "base_code_file" in question_data:
        base_code_file = open(question_data["base_code_file"], "r").read()
    else:
        base_code_file = ""

    questions.append(
        Question(
            question=question_data["question"],
            keys=question_data["keys"],
            grade=int(question_data["grade"]),
            possible_grades=[int(grade) for grade in question_data["possible_grades"]],
            base_code=base_code_file
        )
    )
