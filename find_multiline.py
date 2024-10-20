import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

def analyze_diffs(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    hunk_count = 0
    buggy_line_count = 0
    in_addition_block = False
    after_deletion = False
    bugs_in_hunk = 0

    for line in lines:
        # Check for a hunk
        if line.startswith('@@'):
            hunk_count += 1
            in_addition_block = False  # Reset the addition block flag
            after_deletion = False
            bugs_in_hunk = 0
        
        # Analyze lines for additions (+) and deletions (-)
        if line[1:].strip() == '}' and bugs_in_hunk != 0:
            continue  # Skip counting this line
            
        if line.startswith('+'):
            if in_addition_block or after_deletion:
                continue
            else:
                buggy_line_count += 1  # Count as a new addition
                in_addition_block = True
                after_deletion = False
                bugs_in_hunk += 1
        
        elif line.startswith('-'):
            buggy_line_count += 1  # This is a replacement, reduce count
            after_deletion = True
            in_addition_block = False
            bugs_in_hunk += 1
            
        else:   
            in_addition_block = False  # Exit addition block
            after_deletion = False
    
    return hunk_count, buggy_line_count
    
def calculate_summary(metaData):
    summary = {"single_line" : 0,
               "single_hunk_multi_line" :0,
               "multi_hunk": 0}

    for bug in metaData:
        hunk_count =metaData[bug]["hunk_count"]
        buggy_lines = metaData[bug]["buggy_lines"]
        if hunk_count > 1:
            summary["multi_hunk"] += 1
        elif buggy_lines > 1:
            summary["single_hunk_multi_line"] += 1
        else:
            summary["single_line"] += 1
            
        type = f'{hunk_count}-hunk_{buggy_lines}-line'
        if type not in summary:
            summary[type] = 1
        else:
            summary[type] += 1
            
    metaData["summary"] = summary
    
def save_metaData_json(project_dir, metaData):
    output_file_path = os.path.join(project_dir, "metaData.json")
    
    with open(output_file_path, 'w') as file:
        json.dump(metaData, file, indent=4)

def process_bug(bug_dir, bug):
    file_path = os.path.join(bug_dir, "diff.txt")
    hunks, buggy_lines = analyze_diffs(file_path)
    return bug, {"hunk_count": hunks, "buggy_lines": buggy_lines}

def process_project(base_dir, project):
    project_dir = os.path.join(base_dir, project)
    
    metaData = {}
    bugs = [b for b in os.listdir(project_dir) if os.path.isdir(os.path.join(project_dir, b))]
    
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_bug, os.path.join(project_dir, bug), bug) for bug in bugs]
        
        for future in as_completed(futures):
            bug, data = future.result()
            metaData[bug] = data
            print(f'Hunk Count: {data["hunk_count"]}, Total Buggy Lines: {data["buggy_lines"]} in {project}_{bug}')
    
    calculate_summary(metaData)
    save_metaData_json(project_dir, metaData)

def main(base_dir):
    # List all subfolders in the base directory
    projects = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
    
    # Process each project concurrently
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_project, base_dir, project) for project in projects]

        for future in as_completed(futures):
            future.result()  # Process the future to handle exceptions if any

if __name__ == "__main__":
    # Specify the path to your base directory containing the defects4j bugs
    base_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    main(base_dir)
