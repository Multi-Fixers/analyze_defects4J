import os
import subprocess
import concurrent.futures
import json


def get_projects():
    result = subprocess.run(["defects4j", "pids"], capture_output=True, text=True)
    return result.stdout.splitlines()


def get_bugs(project_name):
    result = subprocess.run(
        ["defects4j", "bids", "-p", project_name], capture_output=True, text=True
    )
    bugs = [f"{bug_id}b" for bug_id in result.stdout.splitlines()]
    return bugs


def save_data_to_json(project_dir, data):
    output_file_path = os.path.join(project_dir, "multi_file_analysis.json")

    with open(output_file_path, "w") as file:
        json.dump(data, file, indent=4)


def process_project(project, fl_folder, output_folder):
    project_output_folder = os.path.join(output_folder, project)
    project_fl_folder = os.path.join(fl_folder, project)
    bugs = get_bugs(project)
    output = {}

    multi_line_bugs = 0
    multi_file_bugs = 0
    single_line_bugs = 0

    for bug in bugs:
        bug_fl_file = os.path.join(project_fl_folder, f"fl_{bug}.json")
        multi_file = False

        with open(bug_fl_file, "r") as f:
            bug_fl_data = json.load(f)

        if len(bug_fl_data) > 1:
            file1 = bug_fl_data[0]["file_path"]

            for loc in bug_fl_data[1:]:
                if loc["file_path"] != file1:
                    multi_file_bugs += 1
                    output[bug] = "multi_file"
                    multi_file = True
                    break

            if not multi_file:
                output[bug] = "single_file-multi_line"
                multi_line_bugs += 1

        else:
            output[bug] = "single_line"
            single_line_bugs += 1

    output["summary"] = {
        "single_line_bugs": single_line_bugs,
        "single_file_multi_line_bugs": multi_line_bugs,
        "multi_file_bugs": multi_file_bugs,
    }

    save_data_to_json(project_output_folder, output)


def main(fl_folder, output_folder):
    projects = get_projects()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []

        for project in projects:
            print(f"Submitting project {project} for processing")
            future = executor.submit(process_project, project, fl_folder, output_folder)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    fl_folder = os.path.join(os.path.expanduser("~/InsightRepair/fault_locations"))
    output_folder = os.path.join(os.path.dirname(__file__), "tmp")

    main(fl_folder, output_folder)
