#!/usr/bin/env bash
set -e

# ANSI Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}               STARTING PROJECT 7 DEMONSTRATION                ${NC}"
echo -e "${BLUE}================================================================${NC}"

# Navigate to Project 7 root directory
cd "$(dirname "$0")"

echo -e "\n${YELLOW}[Step 1/4] Starting LocalStack and Target VM Containers...${NC}"
docker-compose up -d --build

echo -e "\n${YELLOW}[Step 2/4] Initializing and Applying Terraform Config...${NC}"
cd terraform
/Users/brhanu/Documents/Projects/bin/terraform init
/Users/brhanu/Documents/Projects/bin/terraform apply -auto-approve

echo -e "\n${YELLOW}[Step 3/4] Verifying SSH Connection to Target VM...${NC}"
cd ../ansible
ssh -i id_rsa -p 2223 -o StrictHostKeyChecking=no -o ConnectTimeout=5 root@localhost "echo 'SSH Connection: OK'"

echo -e "\n${YELLOW}[Step 4/4] Executing Ansible Provisioning & Hardening Playbook...${NC}"
/Users/brhanu/Library/Python/3.9/bin/ansible-playbook -i inventory.ini playbook.yml

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}            PROJECT 7 DEMO COMPLETED SUCCESSFULLY!             ${NC}"
echo -e "${GREEN}================================================================${NC}"
