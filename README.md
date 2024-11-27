# OpenShift Cluster Scripts

## Scripts

#### Input CSV Format:
The input CSV file should have the following format:

```
<cluster_id>,<cluster_name>
<cluster_id_1>,<cluster_name_1>
<cluster_id_2>,<cluster_name_2>
...
```

### 1. `clustersoperators.py`

#### Description:
`clustersoperators.py` processes OpenShift cluster data, extracting information about operators and their versions, and then displaying it either as a formatted table or saving it to a CSV file.

#### Usage:
./clustersoperators.py <input_csv_file> --output <output_format> [--output-file <output_csv_file>]

#### Arguments:
- `<input_csv_file>`: (Mandatory) Path to the input CSV file containing cluster IDs and names.
- `--output`: (Mandatory) Specifies the output format. Accepted values are `table` or `csv`.
- `--output-file`: (Mandatory if `--output` is `csv`) Path to the output CSV file. This argument is only required when the output format is `csv`.

#### Example:
To display the operator information in a table:
./clustersoperators.py clusters.csv --output table

To save the operator information to a CSV file:
./clustersoperators.py clusters.csv --output csv --output-file operators_output.csv

### 2. `clustersalerts.py`

#### Description:
`clustersalerts.py` processes OpenShift cluster data, extracting alert information for each cluster and printing it to the console.

#### Usage:
./clustersalerts.py <input_csv_file>

#### Arguments:
- `<input_csv_file>`: (Mandatory) Path to the input CSV file containing cluster IDs and names.

#### Example:
To display the alert information:
./clustersalerts.py clusters.csv

