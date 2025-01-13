#!/usr/bin/env python3

import csv
import subprocess
import argparse
from tabulate import tabulate
from collections import defaultdict

def run_ocp_insights(cluster_id):
    result = subprocess.run(["ocp_insights.sh", "--id", cluster_id], capture_output=True, text=True)
    return result.stdout

def extract_operators(output):
    operators = defaultdict(list)
    lines = output.split('\n')
    capture = False
    for line in lines:
        if line.startswith("DISPLAY NAME"):
            capture = True
            continue
        if capture:
            if not line.strip():
                break
            parts = line.strip().split()
            if len(parts) >= 2:
                # Remove the version number (last part) from the operator name
                operator_name = " ".join(parts[:-2])  # Join all parts except the last two
                operator_version = parts[-2]  # The second-to-last part is the version
                operators[operator_name].append(operator_version)
    return operators

def extract_cluster_version(output):
    lines = output.split('\n')
    for line in lines:
        if line.startswith("Cluster Version:"):
            return line.split(":")[1].strip()  # Extract and return the version
    return "Unknown"  # Default if version is not found

def read_csv(file_path):
    clusters = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            clusters.append((row[0], row[1]))  # (cluster_id, cluster_name)
    return clusters

def generate_output(clusters, output_type, output_file=None):
    all_operators = defaultdict(set)

    # First pass: Collect all unique operators across all clusters and their versions
    for cluster_id, cluster_name in clusters:
        output = run_ocp_insights(cluster_id)
        operators = extract_operators(output)
        for operator_name, versions in operators.items():
            all_operators[operator_name].update(versions)

    # Sort operators to make the table columns predictable
    sorted_operators = sorted(all_operators.keys())

    # Second pass: Collect operator data and cluster version for each cluster
    table_data = []
    for cluster_id, cluster_name in clusters:
        output = run_ocp_insights(cluster_id)
        operators = extract_operators(output)
        cluster_version = extract_cluster_version(output)
        row = [cluster_name, cluster_id, cluster_version]
        for operator in sorted_operators:
            # Join the versions with a delimiter (e.g., comma) for each operator
            row.append(", ".join(sorted(set(operators.get(operator, [])))))
        table_data.append(row)

    headers = ["Cluster Name", "Cluster ID", "OpenShift Version"] + sorted_operators

    if output_type == "table":
        # Formatted table output
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    elif output_type == "csv":
        if output_file:
            with open(output_file, mode='w', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(headers)
                csv_writer.writerows(table_data)
        else:
            raise ValueError("Output file must be specified for CSV output.")

def main():
    parser = argparse.ArgumentParser(description="Process cluster data and output as table or CSV.")
    parser.add_argument('file_path', help="Path to the input CSV file.")
    parser.add_argument('--output', choices=['table', 'csv'], required=True, help="Output format: 'table' or 'csv'.")
    parser.add_argument('--output-file', help="Path to the output CSV file (required if output is 'csv').")

    args = parser.parse_args()

    clusters = read_csv(args.file_path)
    generate_output(clusters, args.output, args.output_file)

if __name__ == "__main__":
    main()

