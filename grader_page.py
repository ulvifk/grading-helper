import contextlib
import io
import os.path
import sys
from time import sleep

import streamlit as st

print(st.__file__)

from classroom_data import *

if not os.path.exists("classroom.json"):
    classroom = ClassroomBuilder("submissions").unzip().build()
    save_classroom_to_json(classroom, "classroom.json")
else:
    classroom = load_classroom_from_json("classroom.json")

_students = classroom.students
questions = settings_loader.questions

if "selected_question" not in st.session_state:
    st.session_state["selected_question"] = questions[0].question

if "selected_student_name" not in st.session_state:
    student = next((student for student in _students), None)
    st.session_state.selected_student_name = f"{student.name} {student.surname}"

if "student_names" not in st.session_state:
    st.session_state["student_names"] = [f"{student.name} {student.surname}" for student in _students]

if "show_only_ungraded_students" not in st.session_state:
    st.session_state["show_only_ungraded_students"] = False


@contextlib.contextmanager
def capture_stdout():
    new_stdout = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield new_stdout
    finally:
        sys.stdout = old_stdout


def reload_page():
    js = '''
        <script>
            var body = window.parent.document.querySelector(".main");
            console.log(body);
            body.scrollTop = 0;
        </script>
        '''

    st.components.v1.html(js)
    sleep(0.1)
    st.rerun()

def grader_page():
    question_names = [question.question for question in questions]

    info_col, student_select_col = st.columns(2)

    with student_select_col:
        st.session_state["show_only_ungraded_students"] = st.checkbox("Only Show Ungraded Students",
                                                                      value=st.session_state[
                                                                          "show_only_ungraded_students"],
                                                                      key="show_only_ungraded_students_check_box")

        selected_question_name = st.selectbox(label="Questions", options=question_names)
        selected_question = questions[question_names.index(selected_question_name)]
        st.session_state["selected_question_name"] = selected_question.question

        if not st.session_state["show_only_ungraded_students"]:
            student_names = [f"{student.name} {student.surname}" for student in _students]
        else:
            student_names = [f"{student.name} {student.surname}" for student in _students if
                             not student.is_graded[selected_question_name]]

        students = [student for student in _students if f"{student.name} {student.surname}" in student_names]

        st.session_state.selected_student_name = st.selectbox(label="Students", options=student_names, index=0)
        selected_student = students[student_names.index(st.session_state.selected_student_name)]

        question_info = next((info for info in selected_student.question_info if
                              info.question.question == st.session_state["selected_question_name"]),
                             None)

        question = question_info.question

    with info_col:
        st.write(f"**Name:** {selected_student.name} {selected_student.surname}")
        total_grade_placeholder = st.empty()
        if selected_student.is_graded[st.session_state["selected_question"]]:
            st.write(f"**Graded**")
        else:
            st.write(f"**Not Graded**")

        full_grade_button = st.button("Full Grade")
        if full_grade_button:
            question_info.grade = question.possible_grades[-1]
            selected_student.is_graded[selected_question_name] = True
            save_classroom_to_json(classroom, "classroom.json")
            reload_page()

    with open("dummy.py", "w", encoding="utf-8") as f:
        f.write(question_info.code)

    st.divider()

    # st.write(f"**{partial_question.partial_question}**")
    # st.write(f"**Description:** {partial_question.description}")

    init_index = question.possible_grades.index(question_info.grade)

    chosen_grade = st.radio("Grade", options=question.possible_grades, index=init_index,
                            key=f"Grade {selected_question.question} {selected_student.name} {selected_student.surname}")

    question_info.grade = chosen_grade

    is_graded_init_index = 0 if selected_student.is_graded[selected_question_name] else 1
    is_graded = st.radio("Is Graded", options=["Yes", "No"], index=is_graded_init_index,
                         key=f"is_graded {selected_question.question} {selected_student.name} {selected_student.surname}")

    if is_graded == "Yes":
        selected_student.is_graded[selected_question_name] = True
    else:
        selected_student.is_graded[selected_question_name] = False
    save_classroom_to_json(classroom, "classroom.json")

    next_student_button = st.button("Next Student")
    if next_student_button:
        reload_page()


if __name__ == "__main__":
    grader_page()
