import csv
import subprocess
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

def read_csv(file_path):
    clusters = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            clusters.append((row[0], row[1]))  # (cluster_id, cluster_name)
    return clusters

def main(file_path):
    clusters = read_csv(file_path)
    all_operators = defaultdict(set)

    # First pass: Collect all unique operators across all clusters and their versions
    for cluster_id, cluster_name in clusters:
        output = run_ocp_insights(cluster_id)
        operators = extract_operators(output)
        for operator_name, versions in operators.items():
            all_operators[operator_name].update(versions)

    # Debug: Print the collected operators and their versions (without versions in operator names)
    print("Collected Operators and Versions:")
    for operator_name, versions in all_operators.items():
        print(f"{operator_name}: {', '.join(sorted(versions))}")

    # Sort operators to make the table columns predictable
    sorted_operators = sorted(all_operators.keys())

    # Debug: Print the sorted operator names (column headers)
    print("\nSorted Operator Names (Columns):")
    for operator in sorted_operators:
        print(operator)

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

    # Debug output: Print the CSV data being built
    print("\nCSV Data (in memory):")
    headers = ["Cluster Name", "Cluster ID"] + sorted_operators
    print(f"Headers: {headers}")
    for row in table_data:
        print(row)

    # Formatted table output
    print("\nFormatted Table:")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    file_path = 'clusters.csv'  # replace with your CSV file path
    main(file_path)

