import csv
import subprocess
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

def read_csv(file_path):
    clusters = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            clusters.append((row[0], row[1]))  # (cluster_id, cluster_name)
    return clusters

def main(file_path, output_file):
    clusters = read_csv(file_path)
    all_operators = defaultdict(set)

    # First pass: Collect all unique operators across all clusters and their versions
    for cluster_id, cluster_name in clusters:
        output = run_ocp_insights(cluster_id)
        operators = extract_operators(output)
        for operator_name, versions in operators.items():
            all_operators[operator_name].update(versions)

    # Sort operators to make the table columns predictable
    sorted_operators = sorted(all_operators.keys())

    # Second pass: Collect operator data for each cluster
    table_data = []
    for cluster_id, cluster_name in clusters:
        output = run_ocp_insights(cluster_id)
        operators = extract_operators(output)
        row = [cluster_name, cluster_id]
        for operator in sorted_operators:
            # Join the versions with a delimiter (e.g., comma) for each operator
            row.append(", ".join(sorted(set(operators.get(operator, [])))))
        table_data.append(row)

    # Write the data to a CSV file
    headers = ["Cluster Name", "Cluster ID"] + sorted_operators
    with open(output_file, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(headers)
        csv_writer.writerows(table_data)

if __name__ == "__main__":
    file_path = 'clusters.csv'  # replace with your input CSV file path
    output_file = 'output.csv'  # replace with your desired output CSV file path
    main(file_path, output_file)

