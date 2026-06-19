#!/usr/bin/env bash
set -e

# ANSI Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}               STARTING CHAOS ENGINEERING DEMO                 ${NC}"
echo -e "${BLUE}================================================================${NC}"

# Navigate to 09-chaos-engineering directory
cd "$(dirname "$0")"

# -------------------------------------------------------------------------
# Part 1: Pod Failure (Pod Kill) Experiment
# -------------------------------------------------------------------------
echo -e "\n${YELLOW}[Step 1/2] Executing Pod Failure (Kill) Experiment...${NC}"

# Get current pod names for data-api
OLD_POD=$(kubectl get pods -l app.kubernetes.io/name=data-api -o jsonpath='{.items[0].metadata.name}')
echo -e "Current active data-api pod: ${BLUE}${OLD_POD}${NC}"

echo -e "Injecting Pod Kill Chaos experiment..."
kubectl apply -f pod-failure.yaml

# Wait a brief moment for Chaos Mesh to intercept and terminate the pod
echo "Waiting for pod replacement..."
NEW_POD=""
for i in {1..10}; do
    NEW_POD=$(kubectl get pods -l app.kubernetes.io/name=data-api --field-selector status.phase=Running -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
    if [ -n "$NEW_POD" ] && [ "$OLD_POD" != "$NEW_POD" ]; then
        break
    fi
    sleep 1
done

# Check if pod has changed and if replicaset healed
if [ "$OLD_POD" != "$NEW_POD" ] && [ -n "$NEW_POD" ]; then
    echo -e "${GREEN}✓ Success! Pod ${OLD_POD} was terminated, and Kubernetes spawned new pod ${NEW_POD} automatically!${NC}"
else
    echo -e "${RED}✗ Error: Pod was not replaced. Checking pod status...${NC}"
    kubectl get pods -l app.kubernetes.io/name=data-api
fi

# Clean up pod chaos
kubectl delete -f pod-failure.yaml --ignore-not-found=true

# -------------------------------------------------------------------------
# Part 2: Network Latency Delay Experiment
# -------------------------------------------------------------------------
echo -e "\n${YELLOW}[Step 2/2] Executing Network Latency Injection Experiment...${NC}"

# Define the target endpoint
URL="http://localhost:8081/items/sentiment?text=ChaosEngineeringTesting"

echo -e "Measuring baseline latency..."
BASELINE_TIME=$(curl -o /dev/null -s -w "%{time_total}\n" "$URL")
echo -e "Baseline response time: ${BLUE}${BASELINE_TIME}s${NC}"

echo -e "Injecting 250ms Network Latency Chaos experiment..."
kubectl apply -f network-latency.yaml

# Wait a brief moment for rules to apply
echo "Waiting 5 seconds for network delay enforcement..."
sleep 5

echo -e "Measuring response time during Network Latency Chaos..."
CHAOS_TIME=$(curl -o /dev/null -s -w "%{time_total}\n" "$URL")
echo -e "Response time during chaos: ${RED}${CHAOS_TIME}s${NC}"

# Clean up network chaos
echo -e "\nCleaning up network latency experiments..."
kubectl delete -f network-latency.yaml --ignore-not-found=true

# Analyze result
DIFF=$(echo "$CHAOS_TIME - $BASELINE_TIME" | bc)
echo -e "\nAdded latency: ${YELLOW}${DIFF}s${NC}"
if (( $(echo "$DIFF > 0.2" | bc -l) )); then
    echo -e "${GREEN}✓ Success! Network latency was successfully injected (+250ms delay detected).${NC}"
else
    echo -e "${RED}✗ Error: Latency delay was not detected or below threshold.${NC}"
fi

echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}          CHAOS ENGINEERING DEMO COMPLETED SUCCESSFULLY!        ${NC}"
echo -e "${GREEN}================================================================${NC}"
