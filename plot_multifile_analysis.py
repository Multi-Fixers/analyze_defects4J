import os
import json
import matplotlib.pyplot as plt
import numpy as np


def draw_summary_graph(project_summaries, base_dir):
    projects = list(project_summaries.keys())
    single_file = [project_summaries[proj]["single_file"] for proj in projects]
    multi_file = [project_summaries[proj]["multi_file"] for proj in projects]

    # Set up bar width and x locations
    bar_width = 0.25  # Width of each bar
    x = np.arange(len(projects))  # X locations for the bars

    # Create summary graph for all projects
    plt.figure(figsize=(12, 6))

    # Plot each category of bugs
    plt.bar(
        x - bar_width, single_file, width=bar_width, label="Single File Bugs", color="b"
    )
    plt.bar(
        x,
        multi_file,
        width=bar_width,
        label="Multi File Bugs",
        color="r",
    )

    # Customize the x-axis
    plt.xticks(x, projects, rotation=45, ha="right")
    plt.xlabel("Project")
    plt.ylabel("Bug Count")
    plt.title("Multi-Line Bug Classification Across Projects")
    plt.legend()
    plt.tight_layout()

    # Save the summary graph in the base directory
    output_path = os.path.join(base_dir, "multi_file_analysis.png")
    plt.savefig(output_path)
    plt.close()


def main(base_dir):
    # Dictionary to hold the overall summary across projects
    overall_summary = {
        "single_line_bugs": 0,
        "single_file_multi_line_bugs": 0,
        "multi_file_bugs": 0,
    }

    # Dictionary to hold the classification counts across all projects
    # analyzed_summary = {}

    # Dictionary to hold project-specific summaries
    project_summaries = {}

    # Traverse through each project directory
    projects = [
        f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))
    ]
    for project in projects:
        print(project)
        project_dir = os.path.join(base_dir, project)
        data_file = os.path.join(project_dir, "multi_file_analysis.json")

        if not os.path.isfile(data_file):
            continue

        with open(data_file, "r") as f:
            metaData = json.load(f)

        # Draw individual project graphs
        # draw_project_graph(project, metaData, project_dir)

        # Collect project summary
        summary = metaData.get("summary", {})
        print(summary)
        project_summaries[project] = {
            "single_file": summary.get("single_file_multi_line_bugs", 0),
            "multi_file": summary.get("multi_file_bugs", 0),
        }

        # Update overall summary
        overall_summary["single_line_bugs"] += summary.get("single_line_bugs", 0)
        overall_summary["single_file_multi_line_bugs"] += summary.get(
            "single_file_multi_line_bugs", 0
        )
        overall_summary["multi_file_bugs"] += summary.get("multi_file_bugs", 0)

        # Update classification summary
        # for classification, count in summary.items():
        #     if "-" in classification:  # classification like "1-hunk_1-line"
        #         if classification not in analyzed_summary:
        #             analyzed_summary[classification] = 0
        #         analyzed_summary[classification] += count

    # Draw summary graph across projects in base directory
    draw_summary_graph(project_summaries, base_dir)

    # Draw classification graph in base directory
    # draw_analyzed_graph(analyzed_summary, base_dir)

    # Save the overall summary to a JSON file in base directory
    multifile_summary_file = os.path.join(base_dir, "multifile_summary.json")

    with open(multifile_summary_file, "w") as f:
        json.dump(
            overall_summary,
            f,
            indent=4,
        )


if __name__ == "__main__":
    # Specify your base directory
    base_dir = os.path.join(os.path.dirname(__file__), "tmp")
    main(base_dir)
