import os
import subprocess
import concurrent.futures


def get_projects():
    result = subprocess.run(["defects4j", "pids"], capture_output=True, text=True)
    return ["Jsoup"]
    return result.stdout.splitlines()


def get_bugs(project_name):
    result = subprocess.run(
        ["defects4j", "bids", "-p", project_name], capture_output=True, text=True
    )
    bugs = [f"{bug_id}b" for bug_id in result.stdout.splitlines()]
    return bugs


def checkout_defects4j(project_name, bug_id, workspace_path):
    buggy_workspace = os.path.join(workspace_path, "buggy")
    fixed_workspace = os.path.join(workspace_path, "fixed")

    subprocess.run(
        [
            "defects4j",
            "checkout",
            "-p",
            project_name,
            "-v",
            bug_id,
            "-w",
            buggy_workspace,
        ]
    )
    fix_id = bug_id.replace("b", "f") if "b" in bug_id else bug_id.replace("f", "b")
    subprocess.run(
        [
            "defects4j",
            "checkout",
            "-p",
            project_name,
            "-v",
            fix_id,
            "-w",
            fixed_workspace,
        ]
    )

    return buggy_workspace, fixed_workspace


def process_bug(project_name, bug_id, project_folder):
    workspace_path = os.path.join(project_folder, bug_id)
    checkout_defects4j(project_name, bug_id, workspace_path)
    return f"Processed bug {bug_id} in {project_name}"


def main(output_folder):
    projects = get_projects()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []

        for project in projects:
            bugs = get_bugs(project)
            project_folder = os.path.join(output_folder, project)

            for bug_id in bugs:
                print(f"Submitting bug {bug_id} in project {project} for processing")
                future = executor.submit(process_bug, project, bug_id, project_folder)
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            print(future.result())


if __name__ == "__main__":
    output_folder = os.path.join(os.path.expanduser("~"), "defects4j_data")
    main(output_folder)
