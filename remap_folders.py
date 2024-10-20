import os
import shutil
from concurrent.futures import ThreadPoolExecutor

def process_folder(folder):
    # Split the folder name
    parts = folder.split('_')
    if len(parts) != 2:
        return  # Skip if not in the expected format

    project_name = parts[0]
    bug_identifier = parts[1]

    # Define the new project folder path
    new_project_folder = os.path.join(base_dir, project_name)

    # Create the project folder if it does not exist
    if not os.path.exists(new_project_folder):
        os.makedirs(new_project_folder)

    # Define the new folder name for the bug
    new_bug_folder = os.path.join(new_project_folder, f"{bug_identifier}")

    # Copy the contents of the original folder to the new folder with the renamed bug identifier
    if not os.path.exists(new_bug_folder):
        shutil.copytree(os.path.join(base_dir, folder), new_bug_folder)

def main(base_dir):
    # List all subfolders in the base directory
    subfolders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    # Process each folder concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(process_folder, subfolders)

if __name__ == "__main__":
    # Specify the path to your base directory containing the defects4j bugs
    base_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    main(base_dir)
