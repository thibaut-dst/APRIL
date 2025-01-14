#!/bin/bash

# Define container names
CONTAINER1="april-web-1"
CONTAINER2="mongo"

# Define log files
LOGFILE1="container_${CONTAINER1}_usage.log"
LOGFILE2="container_${CONTAINER2}_usage.log"

# Initialize log files with headers
echo "Timestamp, Memory_Usage(MB), Memory_Usage(%), CPU_Usage(%), Network_In, Network_Out" > "$LOGFILE1"
echo "Timestamp, Memory_Usage(MB), Memory_Usage(%), CPU_Usage(%), Network_In, Network_Out" > "$LOGFILE2"

# Function to capture Memory usage in MB
capture_memory_usage_mb() {
    local container_name=$1
    docker stats --no-stream --format "{{.MemUsage}}" "$container_name" | \
    awk -F' / ' '{print $1}' | sed 's/[^0-9.]//g'
}

# Function to capture Memory usage in %
capture_memory_usage_percent() {
    local container_name=$1
    docker stats --no-stream --format "{{.MemPerc}}" "$container_name" | \
    sed 's/%//g'
}

# Function to capture CPU usage in %
capture_cpu_usage() {
    local container_name=$1
    docker stats --no-stream --format "{{.CPUPerc}}" "$container_name" | \
    sed 's/%//g'
}

# Function to capture Network In and Out (with units)
capture_network_usage() {
    local container_name=$1
    docker stats --no-stream --format "{{.NetIO}}" "$container_name" | \
    awk -F' / ' '{print $1, $2}'
}

# Monitor function
monitor_containers() {
    while true; do
        # Check if containers are running
        RUNNING1=$(docker ps -q -f name="$CONTAINER1")
        RUNNING2=$(docker ps -q -f name="$CONTAINER2")

        # Stop monitoring if either container stops running
        if [[ -z "$RUNNING1" || -z "$RUNNING2" ]]; then
            echo "One of the containers has stopped. Monitoring ended."
            break
        fi

        TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

        # Capture metrics for CONTAINER1
        MEM_USAGE_MB1=$(capture_memory_usage_mb "$CONTAINER1")
        MEM_USAGE_PERCENT1=$(capture_memory_usage_percent "$CONTAINER1")
        CPU_USAGE1=$(capture_cpu_usage "$CONTAINER1")
        NET_USAGE1=$(capture_network_usage "$CONTAINER1")
        NETWORK_IN1=$(echo "$NET_USAGE1" | awk '{print $1}')
        NETWORK_OUT1=$(echo "$NET_USAGE1" | awk '{print $2}')

        # Capture metrics for CONTAINER2
        MEM_USAGE_MB2=$(capture_memory_usage_mb "$CONTAINER2")
        MEM_USAGE_PERCENT2=$(capture_memory_usage_percent "$CONTAINER2")
        CPU_USAGE2=$(capture_cpu_usage "$CONTAINER2")
        NET_USAGE2=$(capture_network_usage "$CONTAINER2")
        NETWORK_IN2=$(echo "$NET_USAGE2" | awk '{print $1}')
        NETWORK_OUT2=$(echo "$NET_USAGE2" | awk '{print $2}')

        # Log data for CONTAINER1
        if [[ -n "$MEM_USAGE_MB1" && -n "$MEM_USAGE_PERCENT1" && -n "$CPU_USAGE1" && -n "$NETWORK_IN1" && -n "$NETWORK_OUT1" ]]; then
            echo "$TIMESTAMP, $MEM_USAGE_MB1, $MEM_USAGE_PERCENT1, $CPU_USAGE1, $NETWORK_IN1, $NETWORK_OUT1" >> "$LOGFILE1"
        fi

        # Log data for CONTAINER2
        if [[ -n "$MEM_USAGE_MB2" && -n "$MEM_USAGE_PERCENT2" && -n "$CPU_USAGE2" && -n "$NETWORK_IN2" && -n "$NETWORK_OUT2" ]]; then
            echo "$TIMESTAMP, $MEM_USAGE_MB2, $MEM_USAGE_PERCENT2, $CPU_USAGE2, $NETWORK_IN2, $NETWORK_OUT2" >> "$LOGFILE2"
        fi

        # Wait for 5 seconds before the next check
        #sleep 5
    done
}

# Start monitoring
monitor_containers