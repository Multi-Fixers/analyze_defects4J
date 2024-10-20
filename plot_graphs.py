import os
import json
import matplotlib.pyplot as plt
import numpy as np

def draw_project_graph(project_name, metaData, project_dir):
    bug_ids = []
    buggy_lines = []
    hunk_counts = []

    for bug_id, data in metaData.items():
        if bug_id != "summary":
            bug_ids.append(bug_id)
            buggy_lines.append(data["buggy_lines"])
            hunk_counts.append(data["hunk_count"])

    x = np.arange(len(bug_ids))  # Create x positions for the bars
    width = 0.35  # Width of the bars

    fig, ax = plt.subplots(figsize=(10, 6))  # Adjust figure size for better readability

    # Create bar for Buggy Lines
    ax.bar(x - width/2, buggy_lines, width, label='Buggy Lines', color='tab:blue')

    # Create bar for Hunk Count
    ax.bar(x + width/2, hunk_counts, width, label='Hunk Count', color='tab:orange')

    # Add labels, title, and custom x-axis tick labels
    ax.set_xlabel('Bug ID')
    ax.set_ylabel('Count')
    ax.set_title(f'{project_name} - Bug Analysis')
    ax.set_xticks(x)
    ax.set_xticklabels(bug_ids, rotation=45, ha="right")  # Rotate labels for better readability
    ax.legend()

    fig.tight_layout()

    # Save the graph inside the project directory
    output_path = os.path.join(project_dir, f'{project_name}_bug_analysis.png')
    plt.savefig(output_path)
    plt.close()

def draw_summary_graph(project_summaries, base_dir):
    projects = list(project_summaries.keys())
    single_line = [project_summaries[proj]['single_line'] for proj in projects]
    single_hunk_multi_line = [project_summaries[proj]['single_hunk_multi_line'] for proj in projects]
    multi_hunk = [project_summaries[proj]['multi_hunk'] for proj in projects]

    # Set up bar width and x locations
    bar_width = 0.25  # Width of each bar
    x = np.arange(len(projects))  # X locations for the bars

    # Create summary graph for all projects
    plt.figure(figsize=(12, 6))
    
    # Plot each category of bugs
    plt.bar(x - bar_width, single_line, width=bar_width, label='Single Line Bugs', color='b')
    plt.bar(x, single_hunk_multi_line, width=bar_width, label='Single Hunk Multi Line Bugs', color='g')
    plt.bar(x + bar_width, multi_hunk, width=bar_width, label='Multi Hunk Bugs', color='r')

    # Customize the x-axis
    plt.xticks(x, projects, rotation=45, ha='right')
    plt.xlabel('Project')
    plt.ylabel('Bug Count')
    plt.title('Bug Summary Across Projects')
    plt.legend()
    plt.tight_layout()

    # Save the summary graph in the base directory
    output_path = os.path.join(base_dir, 'summary_bug_analysis.png')
    plt.savefig(output_path)
    plt.close()

def draw_classification_graph(classification_summary, base_dir):
    classifications = list(classification_summary.keys())
    counts = list(classification_summary.values())

    # Create classification graph (horizontal bars)
    plt.figure(figsize=(10, 10))  # Increase the figure height for more spacing
    bars = plt.barh(classifications, counts, color='purple', height=0.5)  # Increase bar height for more space

    plt.xlabel('Count')
    plt.ylabel('Classification')
    plt.title('Classification of Bugs Across All Projects')
    
    # Increase space between rows by adjusting y-axis limits
    plt.ylim(-1, len(classifications))  # Adjust y-limits for even more space

    # Optionally, add padding to the bars for better visibility
    for bar in bars:
        bar.set_edgecolor('black')  # Add edges to bars for better visibility
        bar.set_linewidth(1)

    plt.tight_layout()

    # Save the classification graph in the base directory
    output_path = os.path.join(base_dir, 'classification_summary.png')
    plt.savefig(output_path)
    plt.close()

def main(base_dir):
    # Dictionary to hold the overall summary across projects
    overall_summary = {
        "single_line": 0,
        "single_hunk_multi_line": 0,
        "multi_hunk": 0
    }
    
    # Dictionary to hold the classification counts across all projects
    classification_summary = {}

    # Dictionary to hold project-specific summaries
    project_summaries = {}

    # Traverse through each project directory
    for project in os.listdir(base_dir):
        project_dir = os.path.join(base_dir, project)
        meta_file = os.path.join(project_dir, "metaData.json")
        
        if not os.path.isfile(meta_file):
            continue

        with open(meta_file, 'r') as f:
            metaData = json.load(f)

        # Draw individual project graphs
        draw_project_graph(project, metaData, project_dir)

        # Collect project summary
        summary = metaData.get("summary", {})
        project_summaries[project] = {
            "single_line": summary.get("single_line", 0),
            "single_hunk_multi_line": summary.get("single_hunk_multi_line", 0),
            "multi_hunk": summary.get("multi_hunk", 0)
        }

        # Update overall summary
        overall_summary["single_line"] += summary.get("single_line", 0)
        overall_summary["single_hunk_multi_line"] += summary.get("single_hunk_multi_line", 0)
        overall_summary["multi_hunk"] += summary.get("multi_hunk", 0)

        # Update classification summary
        for classification, count in summary.items():
            if "-" in classification:  # classification like "1-hunk_1-line"
                if classification not in classification_summary:
                    classification_summary[classification] = 0
                classification_summary[classification] += count

    # Draw summary graph across projects in base directory
    draw_summary_graph(project_summaries, base_dir)

    # Draw classification graph in base directory
    draw_classification_graph(classification_summary, base_dir)

    # Save the overall summary to a JSON file in base directory
    output_summary_file = os.path.join(base_dir, "overall_summary.json")
    with open(output_summary_file, 'w') as f:
        json.dump({
            "overall_summary": overall_summary,
            "classification_summary": classification_summary
        }, f, indent=4)

if __name__ == "__main__":
    # Specify your base directory
    base_dir = os.path.join(os.path.dirname(__file__), 'tmp')
    main(base_dir)
