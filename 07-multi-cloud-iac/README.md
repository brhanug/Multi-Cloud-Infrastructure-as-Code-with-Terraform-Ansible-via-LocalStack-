# Project 7: Multi-Cloud Infrastructure as Code with Terraform & Ansible (via LocalStack)

This project demonstrates a local cloud engineering and configuration management workflow using **Terraform** for declarative infrastructure provisioning and **Ansible** for configuration management, all executed against **LocalStack** to emulate AWS cloud services locally.

## Project Structure

```
07-multi-cloud-iac/
├── docker-compose.yml       # LocalStack container and test target VM setup
├── terraform/
│   ├── providers.tf         # Configures AWS provider to route requests to LocalStack
│   ├── main.tf              # Defines VPC, Subnet, Security Group, EC2 instance, and S3 bucket
│   ├── variables.tf         # Project input variables
│   └── outputs.tf           # Terraform output configuration
└── ansible/
    ├── ansible.cfg          # Default Ansible config (SSH key, inventory location)
    ├── inventory.ini        # Ansible target inventory
    ├── playbook.yml         # System hardening and Docker CE installation instructions
    └── target/
        └── Dockerfile       # SSH-enabled Ubuntu container representing the EC2 instance
```

---

## Architecture Overview

1. **LocalStack Emulation**: Mock AWS environment providing API endpoints for EC2, S3, and VPC.
2. **Infrastructure-as-Code (Terraform)**:
   - Sets up a Virtual Private Cloud (VPC) with a public subnet, internet gateway, and route table.
   - Configures a Security Group allowing SSH (22), HTTP (80), and custom ports.
   - Provisions an S3 bucket for data/backup storage.
   - Provisions a mock EC2 instance.
3. **Configuration Management (Ansible)**:
   - Since LocalStack does not run a hypervisor, we spin up an SSH-enabled Docker container (`target-vm`) simulating our EC2 server.
   - The Ansible playbook dynamically configures the container over SSH:
     - Installs Docker CE.
     - Upgrades security packages.
     - Hardens SSH access (disabling password authentication, enforcing SSH key-based access).

---

## Getting Started

### 1. Prerequisites
- Docker & Docker Compose
- Terraform (v1.0+)
- Ansible (v2.15+)

### 2. Start LocalStack and Target VM
Initialize the local cloud and target containers:
```bash
docker-compose up -d --build
```

### 3. Provision Infrastructure (Terraform)
Initialize and apply the Terraform configuration:
```bash
cd terraform
terraform init
terraform apply -auto-approve
```

### 4. Configure Server (Ansible)
Execute the Ansible playbook:
```bash
cd ../ansible
ansible-playbook -i inventory.ini playbook.yml
```

---

## Verification & Hardening Validation

1. **Verify S3 Bucket and EC2 Provisioning**:
   Confirm S3 bucket exists inside LocalStack:
   ```bash
   aws --endpoint-url=http://localhost:4566 s3 ls
   ```

2. **Verify Docker Installation in VM**:
   Check if Docker CE was successfully deployed on the target machine:
   ```bash
   docker exec target-vm docker --version
   ```

3. **Verify SSH Key Authorization**:
   Test direct SSH connection to the server without password prompting:
   ```bash
   ssh -i ansible/id_rsa -p 2223 root@localhost "echo Connection Verified"
   ```
