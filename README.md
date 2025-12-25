# Grading Helper

Grading Helper is a tool designed to streamline the process of grading programming assignments. It provides a user-friendly interface for reviewing code, assigning grades, and managing student submissions. Additionally, it integrates with MOSS (Measure Of Software Similarity) for plagiarism detection.

## Features

- **Interactive Grading UI**: A Streamlit-based web interface to view student code, assign grades, and mark submissions as graded.
- **Configurable Settings**: Easily define questions, maximum scores, and reference code via `settings.yml`.
- **Submission Processing**: Automatically processes and unzips student submissions.
- **Progress Saving**: Grades and status are saved to `classroom.json` to prevent data loss.
- **Plagiarism Detection**: Automated MOSS script to generate plagiarism reports for each question.

## Prerequisites

- Python 3.x
- [Streamlit](https://streamlit.io/)
- [PyYAML](https://pyyaml.org/)
- [mosspy](https://github.com/soachishti/moss.py) (for plagiarism detection)

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd grading-helper
    ```

2.  Install the required Python packages:
    ```bash
    pip install streamlit pyyaml mosspy
    ```

## Configuration

1.  **Environment Variables**:
    For plagiarism detection using MOSS, you need to set the `MOSS_API_KEY` environment variable.
    ```bash
    export MOSS_API_KEY="your_moss_user_id"
    ```

2.  **Settings**: Edit the `settings.yml` file to configure your assignment questions.
    ```yaml
    Questions:
      - question: "Question1"
        keys: [ "q1", "q01"]       # Keys to identify the question file in submissions
        grade: 25                  # Default/Max grade
        possible_grades: [0, 25]   # discrete grade options
    
        # Used in moss to identify shared code
        base_code_file: "base_code/q01.py" # Path to the base/solution code
    ```

3.  **Submissions**: Ensure your student submissions (e.g., a zip file or directory named `submissions`) are placed in the project root or where the tool expects them.

## Usage

### Grading Interface

To start the grading interface:

```bash
./grading_ui.sh
```

Or run directly with Streamlit:

```bash
streamlit run grader_page.py
```

The web interface will open in your browser, allowing you to:
- Select students and questions.
- View student code side-by-side or in a dedicated view.
- Assign grades and mark as "Graded".
- Save progress automatically to `classroom.json`.

### Plagiarism Check

To run the plagiarism checker:

1.  Ensure you have set the `MOSS_API_KEY`.
2.  Run the script:
    ```bash
    python moss_script.py
    ```
3.  Reports will be generated in the `plag_report/` directory.

## Project Structure

- `grader_page.py`: The main Streamlit application for grading.
- `settings.yml`: Configuration file for questions and grading rules.
- `classroom_data/`: Logic for handling classroom interactions (loading students, submissions).
- `moss_script.py`: Script to invoke the MOSS plagiarism checker.
- `moss_plag_checker/`: Contains the MOSS API wrapper logic.
- `main.py`: Entry point for testing classroom loading logic.
