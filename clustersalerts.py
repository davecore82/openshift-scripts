import csv
import subprocess

def run_ocp_insights(cluster_id):
    result = subprocess.run(["ocp_insights.sh", "--id", cluster_id], capture_output=True, text=True)
    return result.stdout

def extract_alerts(output):
    alerts = []
    lines = output.split('\n')
    capture = False
    for line in lines:
        if line.startswith("ALERT NAME"):
            capture = True
            continue
        if capture:
            if not line.strip():
                break
            alerts.append(line.strip())
    return alerts

def read_csv(file_path):
    clusters = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            clusters.append((row[0], row[1]))  # (cluster_id, cluster_name)
    return clusters

def main(file_path):
    clusters = read_csv(file_path)
    for cluster_id, cluster_name in clusters:
        output = run_ocp_insights(cluster_id)
        alerts = extract_alerts(output)
        print(f"\nCluster Name: {cluster_name}\nCluster ID: {cluster_id}")
        print("Alerts:")
        for alert in alerts:
            print(f"  {alert}")

if __name__ == "__main__":
    file_path = 'clusters.csv'  # replace with your CSV file path
    main(file_path)

