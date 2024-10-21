import os
import subprocess
import difflib
import concurrent.futures
from functools import partial

def get_projects():
    result = subprocess.run(['defects4j', 'pids'], capture_output=True, text=True)
    return result.stdout.splitlines()

def get_bugs(project_name):
    result = subprocess.run(['defects4j', 'bids', '-p', project_name], capture_output=True, text=True)
    bugs = [f"{bug_id}b" for bug_id in result.stdout.splitlines()]
    return bugs

def checkout_defects4j(project_name, bug_id, workspace_path):
    buggy_workspace = os.path.join(workspace_path, 'buggy')
    fixed_workspace = os.path.join(workspace_path, 'fixed')
    
    subprocess.run(['defects4j', 'checkout', '-p', project_name, '-v', bug_id, '-w', buggy_workspace])
    fix_id = bug_id.replace('b', 'f') if 'b' in bug_id else bug_id.replace('f', 'b')
    subprocess.run(['defects4j', 'checkout', '-p', project_name, '-v', fix_id, '-w', fixed_workspace])
    
    return buggy_workspace, fixed_workspace

def generate_diff(buggy_workspace, fixed_workspace):
    diff_command = f'diff -ur {buggy_workspace} {fixed_workspace}'
    result = subprocess.run(diff_command, shell=True, capture_output=True)
    diff_output = result.stdout.decode('utf-8', errors='ignore')
    return diff_output

def find_multiline_diffs(diff_output):
    lines = diff_output.splitlines()
    buggy_lines = []
    inside_code_file = False
    
    for line in lines:
        if line.startswith('---') or line.startswith('+++'):
            if '.java' in line:
                inside_code_file = True
            else:
                inside_code_file = False
            continue
        if inside_code_file:
            buggy_lines.append(line)
            
    return buggy_lines

def save_diffs_to_folder(workspace_path, diff):
    with open(os.path.join(workspace_path, f'diff.txt'), 'w') as f:
        for line in diff:
            f.write(line + '\n')

def process_bug(project_name, bug_id, project_folder):
    workspace_path = os.path.join(project_folder, bug_id)
    buggy_workspace, fixed_workspace = checkout_defects4j(project_name, bug_id, workspace_path)
    diff_output = generate_diff(buggy_workspace, fixed_workspace)
    multiline_diffs = find_multiline_diffs(diff_output)
    save_diffs_to_folder(workspace_path, multiline_diffs)
    return f'Processed bug {bug_id} in {project_name}'

def main(output_folder):
    projects = get_projects()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        
        for project in projects:
            bugs = get_bugs(project)
            project_folder = os.path.join(output_folder, project)
            
            for bug_id in bugs:
                print(f'Submitting bug {bug_id} in project {project} for processing')
                future = executor.submit(process_bug, project, bug_id, project_folder)
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            print(future.result())

if __name__ == "__main__":
    output_folder =  os.path.join(os.path.dirname(__file__), 'tmp')  # Specify your output folder
    main(output_folder)
