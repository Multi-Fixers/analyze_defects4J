import os
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from concurrent.futures import ProcessPoolExecutor, as_completed

def calculate_summary(metaData):
    classification = {
        "control_dep": 0,
        "data_dep": 0,
        "evolutionary": 0,
        "single": 0,
        "multi": 0,
        "total": 0
    }

    for bug in metaData:
        if bug in ["summary", "classification"]:
            continue

        for t in metaData[bug]["type"]:
            classification[t] += 1
            classification["total"] += 1

    metaData["classification"] = classification
    return classification

def save_json(output_path, data):
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)

def read_json(input_path):
    if not os.path.isfile(input_path):
        return {}

    with open(input_path, 'r') as file:
        return json.load(file)

def draw_classification_graph(heading, classification, output_file_path):
    # Filter classification data to exclude 'total' and any categories with a value of 0
    labels = [k for k, v in classification.items() if k != 'total' and v > 0]
    sizes = [v for k, v in classification.items() if k != 'total' and v > 0]

    # Generate a color list with a unique color for each section
    colors = list(mcolors.TABLEAU_COLORS.values())[:len(sizes)]

    # Create a pie chart with only percentage shown
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)

    ax.axis('equal')  # Draw the pie chart as a circle
    plt.title(heading)
    plt.savefig(output_file_path)
    plt.close(fig)

def process_project(base_dir, project):
    print("Started project", project)
    project_dir = os.path.join(base_dir, project)
    metaData_path = os.path.join(project_dir, "metaData.json")
    metaData = read_json(metaData_path)

    project_summary = {
        "control_dep": 0,
        "data_dep": 0,
        "evolutionary": 0,
        "multi": 0,
        "single": 0,
        "total": 0
    }

    if "type" in next(iter(metaData.values())):
        project_summary = calculate_summary(metaData)
        save_json(metaData_path, metaData)

        # Draw individual project graphs
        graph_path = os.path.join(project_dir, f'{project}_bug_classification.png')
        draw_classification_graph(f'{project} - Bug classification', metaData["classification"], graph_path)

    print(f'Processed project {project}.')
    return project_summary

def aggregate_summaries(summaries):
    overall_summary = {
        "control_dep": 0,
        "data_dep": 0,
        "evolutionary": 0,
        "multi": 0,
        "single": 0,
        "total": 0,
    }

    for summary in summaries:
        for key in overall_summary:
            overall_summary[key] += summary.get(key, 0)

    return overall_summary

def main(base_dir):
    # Traverse through each project directory
    projects = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    summaries = []
    with ProcessPoolExecutor() as executor:
        # Submit all projects for parallel processing
        futures = {executor.submit(process_project, base_dir, project): project for project in projects}
        for future in as_completed(futures):
            project_summary = future.result()
            summaries.append(project_summary)

    # Aggregate project summaries into an overall summary
    classification_summary = aggregate_summaries(summaries)

    # Draw classification graph across all projects in base directory
    graph_path = os.path.join(base_dir, "classification_summary.png")
    draw_classification_graph("Classification of Bugs Across All Projects", classification_summary, graph_path)

    # Update and save the summary file
    summary_path = os.path.join(base_dir, 'overall_summary.json')
    summaryfile = read_json(summary_path)
    summaryfile["classification_summary"] = classification_summary
    save_json(summary_path, summaryfile)

if __name__ == "__main__":
    # Specify your base directory
    base_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    main(base_dir)
