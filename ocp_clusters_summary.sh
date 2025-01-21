#!/bin/bash

# Check if argument is passed
if [ -z "$1" ]; then
    echo "Usage: $0 <directory|cluster-id>"
    echo ""
    echo "You can either pass in the directory where the cluster insights data for that customer is located, or just a cluster ID from that customer."
    echo ""
    echo "If you pass a cluster ID, the script will determine the directory using the following command:"
    echo ""
    echo "  ls -d -1 /ocp/*/<cluster-id>"
    echo ""
    echo "The correct directory will be extracted and used automatically."
    exit 1
fi

INPUT="$1"

# Determine if input is a directory or a cluster ID
if [ -d "$INPUT" ]; then
    DIRECTORY="$INPUT"
elif [[ "$INPUT" =~ ^[a-z0-9\-]+$ ]]; then
    # Try to find the directory using the cluster ID
    DIRECTORY=$(ls -d -1 /ocp/*/"$INPUT" 2>/dev/null | head -n 1 | xargs dirname)
    if [ -z "$DIRECTORY" ]; then
        echo "Error: Could not determine the directory for cluster ID $INPUT."
        exit 1
    fi
else
    echo "Error: $INPUT is neither a valid directory nor a cluster ID."
    exit 1
fi

# Arrays to store data
cluster_ids=()
cluster_versions=()
platforms=()
install_types=()
network_types=()
checkins=()

# Function to parse the output of ocp_insights.sh
parse_output() {
    local output="$1"
    local cluster_id="$2"

    local checkin=$(echo "$output" | grep -i "Checkin:" | cut -d":" -f2- | xargs)
    local cluster_version=$(echo "$output" | grep -i "Cluster Version:" | cut -d":" -f2- | xargs)
    local platform=$(echo "$output" | grep -i "Platform:" | cut -d":" -f2- | xargs)
    local install_type=$(echo "$output" | grep -i "Install Type:" | cut -d":" -f2- | xargs)
    local network_type=$(echo "$output" | grep -i "NetworkType:" | cut -d":" -f2- | xargs)

    # Append data to arrays
    cluster_ids+=("$cluster_id")
    cluster_versions+=("$cluster_version")
    platforms+=("$platform")
    install_types+=("$install_type")
    network_types+=("$network_type")
    checkins+=("$checkin")
}

# Iterate through the files in the directory
for file in "$DIRECTORY"/*; do
    # Get the base filename
    base_filename=$(basename "$file")

    # Run the ocp_insights.sh command
    output=$(ocp_insights.sh --id "$base_filename")

    # Parse and store the output
    parse_output "$output" "$base_filename"
done

# Determine column widths
max_id_length=$(printf "%s\n" "Cluster ID" "${cluster_ids[@]}" | awk '{ if (length > max) max = length } END { print max }')
max_version_length=$(printf "%s\n" "Cluster Version" "${cluster_versions[@]}" | awk '{ if (length > max) max = length } END { print max }')
max_platform_length=$(printf "%s\n" "Platform" "${platforms[@]}" | awk '{ if (length > max) max = length } END { print max }')
max_install_length=$(printf "%s\n" "Install Type" "${install_types[@]}" | awk '{ if (length > max) max = length } END { print max }')
max_network_length=$(printf "%s\n" "Network Type" "${network_types[@]}" | awk '{ if (length > max) max = length } END { print max }')
max_checkin_length=$(printf "%s\n" "Checkin" "${checkins[@]}" | awk '{ if (length > max) max = length } END { print max }')

# Print header
printf "%-${max_id_length}s %-${max_version_length}s %-${max_platform_length}s %-${max_install_length}s %-${max_network_length}s %-${max_checkin_length}s\n" \
       "Cluster ID" "Cluster Version" "Platform" "Install Type" "Network Type" "Checkin"
printf "%-${max_id_length}s %-${max_version_length}s %-${max_platform_length}s %-${max_install_length}s %-${max_network_length}s %-${max_checkin_length}s\n" \
       "$(printf -- '-%.0s' $(seq 1 $max_id_length))" \
       "$(printf -- '-%.0s' $(seq 1 $max_version_length))" \
       "$(printf -- '-%.0s' $(seq 1 $max_platform_length))" \
       "$(printf -- '-%.0s' $(seq 1 $max_install_length))" \
       "$(printf -- '-%.0s' $(seq 1 $max_network_length))" \
       "$(printf -- '-%.0s' $(seq 1 $max_checkin_length))"

# Print data
for i in "${!cluster_ids[@]}"; do
    printf "%-${max_id_length}s %-${max_version_length}s %-${max_platform_length}s %-${max_install_length}s %-${max_network_length}s %-${max_checkin_length}s\n" \
           "${cluster_ids[i]}" "${cluster_versions[i]}" "${platforms[i]}" "${install_types[i]}" "${network_types[i]}" "${checkins[i]}"
done

