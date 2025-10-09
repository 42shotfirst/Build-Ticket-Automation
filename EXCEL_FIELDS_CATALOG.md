# Excel Fields Catalog - LLDtest.xlsm

**Generated:** 2025-10-01  
**Source File:** LLDtest.xlsm  
**Total Sheets:** 7  
**Total Key-Value Pairs:** 296  
**Total Tables:** 30  

---

## Overview

This document catalogs all fields extracted from the Excel spreadsheet used for Azure infrastructure automation. The data is organized by sheet and includes both key-value pairs and table structures.

---

## Sheet 1: Build_ENV

**Purpose:** Build environment configuration and resource group settings

### Key-Value Pairs (5)

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Resource Group | Resource group identifier | `var.resource_group_key` |
| Key | Resource group key | `var.resource_group_key` |
| Name | Resource group name | Resource naming |
| Subscription | Azure subscription | `var.subscription` |
| Location | Azure region | Resource location |

### Tables (5)

- **Table 0:** Resource group template configuration
- **Table 1:** Terraform variable mappings
- **Table 2-4:** Build environment values and validation

---

## Sheet 2: Resources

**Purpose:** Main resource configuration including VMs, networking, storage, and application services

### Key-Value Pairs (203)

#### Project Information

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Overview | Project overview | Documentation |
| Application Name | Application identifier | `var.application_name` |
| Service Now Ticket | ServiceNow ticket reference | Tags |
| Environment | Deployment environment | `var.environment` |
| App Tier | Application tier | Tags |
| Shared Service Name | Shared service identifier | Tags |
| IT Cost Center ID | IT cost center | Tags |
| IT Domain | IT domain | Tags |
| Notes | Additional notes | Documentation |
| Segment | Business segment | Tags |
| Line of Business | Line of business | Tags |
| Department | Department | Tags |
| Cost Center ID | Cost center | Tags |

#### Resource Group Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Resource Group | Resource group name | `azurerm_resource_group.main.name` |
| Key | Resource group key | Naming |
| Name | Resource name | Resource identification |
| Subscription | Azure subscription | Provider configuration |
| Location | Azure region | `var.location` |

#### Networking Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Subnet | Subnet name | `azurerm_subnet` |
| VNET Resource Group | VNet resource group | Cross-resource references |
| VNet Name | Virtual network name | `azurerm_virtual_network` |
| NSG Name | Network security group name | `azurerm_network_security_group` |
| Route Table Name | Route table name | Routing configuration |
| Address Prefixes | CIDR blocks | `var.subnet_address_prefixes` |
| Service Endpoints | Service endpoints | Subnet configuration |
| Application Security Group | ASG identifier | Security configuration |
| Network Security Rule | NSG rule | Security rules |
| NSG Resource Group | NSG resource group | Cross-resource references |
| Rules | Security rules | NSG rules |

#### Identity and Security

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| User Assigned Identity | Managed identity | Identity configuration |
| Resource Group Key | Resource group key | Cross-resource references |
| Private Endpoint | Private endpoint config | Network isolation |
| Subresource Names | Subresource identifiers | Private endpoint config |
| Private Connection Resource | Private connection | Network configuration |
| Subnet Key | Subnet identifier | Networking |
| ASG Key | ASG identifier | Security configuration |

#### Key Vault Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Key Vault | Key vault name | `azurerm_key_vault` |
| SKU | Key vault SKU | Pricing tier |
| Soft Delete Retention Days | Retention period | Data protection |
| Public Network Access Enabled | Public access | Security configuration |
| Enabled for RBAC | RBAC status | Access control |
| Enabled for Deployment | Deployment flag | VM deployment |
| Enabled for Disk Encryption | Disk encryption flag | Encryption |
| Enabled for template deployment | Template deployment flag | ARM templates |
| Enable Purge Protection | Purge protection | Data protection |
| Key Vault Key | Key vault key name | Encryption keys |
| Key Type | Key type (RSA/EC) | Key configuration |
| Key Size | Key size (bits) | Key configuration |
| Key Opts | Key operations | Key permissions |
| Disk Encryption Set | Disk encryption set | VM disk encryption |
| Idenity Type | Identity type | Managed identity |

#### Virtual Machine Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Virtual Machine | VM name | `azurerm_linux_virtual_machine` |
| OS | Operating system | `var.os_image` |
| OS URN | OS image URN | Image reference |
| Packer Image ID | Custom Packer image | Custom images |
| OS disk size | OS disk size (GB) | Disk configuration |
| OS disk type | OS disk type | Storage tier |
| Private IP Address Allocation | IP allocation method | Network configuration |
| IP Address | Static IP address | Network configuration |
| Role | VM role/function | Tags and configuration |
| Patch Optin | Patch management | Update management |
| Admin Username | Admin username | `var.admin_username` |
| Data Disk(s) | Data disks | Additional storage |
| vm_key | VM key | Resource identification |
| Data disk sizes | Data disk sizes | Storage configuration |
| Data disk type | Data disk type | Storage tier |

#### Storage Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Storage Account | Storage account flag | `azurerm_storage_account` |
| Storage Account Name | Storage account name | `var.storage_account_tier` |
| Performance | Performance tier | Storage configuration |
| Redundancy | Replication type | `var.storage_replication_type` |
| Storage Share | File share flag | File storage |
| Quota | Share quota (GB) | File share size |
| Protocol | Storage protocol | SMB/NFS |
| Access Tier | Access tier | Hot/Cool storage |

#### Kubernetes (AKS) Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Kubernetes Cluster | AKS cluster flag | `azurerm_kubernetes_cluster` |
| Kubernetes Cluster Name | Cluster name | AKS naming |
| Region | Cluster region | Location |
| AKS Pricing Tier | Pricing tier | SKU configuration |
| Kubernetes Version | K8s version | Cluster version |
| Maintenance Window | Maintenance schedule | Update management |
| Automatic Upgrade | Auto-upgrade flag | Update policy |
| Automatic Upgrade Scheduler | Upgrade schedule | Maintenance windows |
| Node Security Channel Type | Security channel | Node updates |
| Security Channel Scheduler | Security schedule | Update policy |
| Authentication and Authorization | Auth config | RBAC configuration |
| Private Access - Enable private cluster | Private cluster flag | Network isolation |
| Public Access - Set authorized IP ranges | IP whitelist | Network security |
| Kubernetes Service Addresses | Service CIDR | Network configuration |
| Kubernetes Service IP address | Service IP | Network configuration |
| DNS Name Prefix | DNS prefix | `var.dns_prefix` |
| Network Policy | Network policy | Calico/Azure |
| Load Balancer | Load balancer config | Service exposure |
| Microsoft Defender for Cloud | Defender flag | Security |
| Azure Container Registry | ACR integration | Container registry |
| Service Mesh – Enable Istio | Istio flag | Service mesh |
| Azure Policy | Azure Policy flag | Governance |
| Container Insights – Log Analytics workspace | Log workspace | Monitoring |
| Container Insights – Cost Preset | Cost preset | Monitoring tier |
| Infrastructure Resource Group | Infra RG | AKS infrastructure |

#### AKS Node Pool Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Kubernetes Default Node Pool | Default pool flag | Node pool config |
| Node Pool Name | Node pool name | Pool identification |
| Mode | Node pool mode | System/User |
| Availability Zone | Availability zones | High availability |
| OS SKU | OS SKU | Node OS |
| OS Disk Type | Disk type | Storage configuration |
| OS Disk Size | Disk size (GB) | Node storage |
| Choose Node Size | VM size | `var.vm_size` |
| Orchestrator Version | K8s version | Node version |
| Node Count | Node count | Capacity |
| Minimum Node Count | Min nodes | Auto-scaling |
| Max Node Count | Max nodes | Auto-scaling |
| Max Pods P/Node | Max pods per node | Pod density |
| Labels | Node labels | Workload placement |
| Taints | Node taints | Workload placement |
| Enable Azure Spot Instance | Spot instances | Cost optimization |
| Scale Method | Scaling method | Auto-scaling |
| Enable Public IP per Node | Public IP flag | Network configuration |
| Kubernetes Cluster Node Pools | Additional pools | Multi-pool clusters |

#### Container Registry Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Admin Enabled | Admin account | `azurerm_container_registry` |
| Data Endpoint Enabled | Data endpoint | Network configuration |
| Zone Redundancy Enabled | Zone redundancy | High availability |
| Public Network Access | Public access | Network security |
| Network Rule Sets | Network rules | Firewall configuration |

#### Application Gateway Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Application Gateway | App gateway flag | `azurerm_application_gateway` |
| SKU name | SKU name | `var.app_gateway_sku` |
| SKU tier | SKU tier | Performance tier |
| SKU Capacity | Capacity | `var.app_gateway_capacity` |
| Min Capacity | Min capacity | Auto-scaling |
| Max Capacity | Max capacity | Auto-scaling |
| Availability Zones | Availability zones | High availability |

#### App Service Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| App Service Environment | ASE flag | `azurerm_app_service_environment` |
| Virtual IP | Virtual IP | Network configuration |
| Physical hardware isolation | Isolation flag | Security |
| Zone redundancy | Zone redundancy | High availability |
| App Service Plan | App service plan | `azurerm_app_service_plan` |
| Operating System | OS type | Windows/Linux |
| Pricing plan | Pricing tier | SKU |
| Windows Web App | Web app flag | `azurerm_windows_web_app` |
| Runtime stack | Runtime version | Application runtime |
| Plan | Service plan | Configuration |

#### Redis Cache Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Azure Cache for Redis | Redis flag | `azurerm_redis_cache` |
| Cache SKU | Cache SKU | Pricing tier |
| Cache size | Cache size | Memory capacity |
| Connectivity method | Connection type | Network configuration |
| Redis version | Redis version | Version selection |
| Non-TLS port | Non-TLS flag | Security |
| Availability zones | Availability zones | High availability |
| Microsoft Entra Authentication | Entra auth | Authentication |
| Access Keys Authentication | Key auth | Authentication |

#### Monitoring and Logging

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Application Insights | App Insights flag | `azurerm_application_insights` |
| Log Analytics Workspace | Log workspace | Monitoring |
| Data Collection Rule | DCR flag | Data collection |
| Platform Type | Platform type | OS type |
| Data Collection Endpoint | DCE | Data ingestion |
| Destinations | Destinations | Data routing |
| Azure Monitor workspace | Monitor workspace | Metrics |
| Public Access | Public access | Network configuration |
| Azure Managed Grafana | Grafana flag | Visualization |
| Pricing Plan | Pricing tier | SKU |
| Grafana Version | Grafana version | Version selection |
| Enable API key creation | API key flag | API access |
| Deterministic outbound IP | Deterministic IP | Network configuration |

#### Public IP Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| Public IP Address | Public IP flag | `azurerm_public_ip` |
| IP address assignment | Allocation method | Static/Dynamic |
| Tier | IP tier | Basic/Standard |
| IP Version | IP version | IPv4/IPv6 |
| Idle timeout (minutes) | Timeout | Connection settings |
| Availability zone | Availability zone | Zone redundancy |

#### SQL Server Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| MS SQL Server | SQL Server flag | `azurerm_mssql_server` |
| Version | SQL version | Version selection |
| Connection Policy | Connection policy | Security |
| Minimum TLS Version | TLS version | Security |
| Administrator Login | Admin username | Authentication |
| Outbound Network Restriction Enabled | Network restrictions | Security |
| Azuread AUTHENTICATION Only | Entra-only auth | Authentication |
| Login Username | Login username | Authentication |
| Identity Type | Identity type | Managed identity |

#### SQL Database Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| MS SQL Database | SQL DB flag | `azurerm_mssql_database` |
| Collation | Database collation | Character set |
| Create Mode | Creation mode | Database creation |
| License Type | License type | Licensing |
| Storage Account Type | Storage type | Performance tier |
| Maintenance Configuration Type | Maintenance config | Update management |
| Max Size (GB) | Max size | Database size |
| Read Replica Count | Replica count | High availability |
| Auto Pause Delay (Minutes) | Auto-pause delay | Cost optimization |
| Ledger Enabled | Ledger flag | Immutable ledger |
| Read Scale | Read scale-out | Performance |
| Zone Redundant | Zone redundancy | High availability |
| Geo Backup Enabled | Geo backup | Disaster recovery |
| Transparent Data Encryption Enabled | TDE flag | Encryption |
| Monthly Retention | Monthly retention | Backup policy |
| Weekly Retention | Weekly retention | Backup policy |
| Yearly Retention | Yearly retention | Backup policy |
| Week Of Year | Week of year | Yearly backup |
| Backup Interval In Hours | Backup interval | Short-term retention |
| Retention Days | Retention days | Backup retention |

#### SQL Managed Instance Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| MS SQL Managed Instance | SQL MI flag | `azurerm_mssql_managed_instance` |
| Virtual Cores | vCore count | Compute capacity |
| Storage Size (GB) | Storage size | Storage capacity |

#### Access and Post-Deployment

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| RDP/SSH Access | Remote access | Network security |
| Post Deployment | Post-deployment scripts | Automation |
| Domain join | Domain join flag | AD integration |

### Tables (19)

- **Table 0:** Template version information
- **Tables 1-18:** Resource configuration tables with various resource types and settings

---

## Sheet 3: NSG

**Purpose:** Network Security Group rules configuration

### Key-Value Pairs (1)

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| name | NSG rule name | `azurerm_network_security_rule` |

### Tables (5)

Security rule tables with the following structure:

| Field | Description | Example |
|-------|-------------|---------|
| name | Rule name | "one", "two", "three" |
| priority | Rule priority (100-4096) | 100, 110, 120 |
| direction | Traffic direction | Inbound, Outbound |
| access | Allow or Deny | Allow, Deny |
| protocol | Network protocol | Tcp, Udp, * |
| source_port_range | Source port | *, 80, 443 |
| destination_port_ranges | Destination ports | *, 3389, 22 |
| source_asg | Source ASG | ASG identifier |
| destination_asg | Destination ASG | ASG identifier |
| source_address_prefixes | Source IP ranges | CIDR blocks |
| destination_address_prefixes | Destination IP ranges | CIDR blocks |
| description | Rule description | Text description |

**Total Rules Extracted:** 13 security rules

---

## Sheet 4: APGW

**Purpose:** Application Gateway configuration

### Key-Value Pairs (42)

#### Backend Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| backend_address_pool | Backend pool name | Backend pools |
| name | Pool name | Identification |
| fqdns | Backend FQDNs | Target addresses |

#### HTTP Settings

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| backend_http_settings | HTTP settings name | Backend settings |
| cookie_based_affinity | Cookie affinity | Session management |
| pick_host_name_from_backend_address | Host header | Request routing |
| port | Backend port | `var.app_gateway_port` |
| probe_name | Health probe | Health monitoring |
| protocol | Protocol (HTTP/HTTPS) | `var.app_gateway_protocol` |
| request_timeout | Request timeout | Timeout settings |
| trusted_root_certificate_names | Root certs | Certificate validation |

#### Frontend Configuration

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| frontend_ip_configuration | Frontend IP config | Public/Private IP |
| private_ip_address_allocation | IP allocation | Static/Dynamic |
| snet_key | Subnet key | Network configuration |
| frontend_port | Frontend port | Listener port |

#### HTTP Listener

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| http_listener | Listener name | Request listeners |
| frontend_ip_configuration_name | Frontend IP name | IP configuration |
| frontend_port_name | Port name | Port reference |
| require_sni | SNI requirement | SSL configuration |

#### Health Probes

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| probe | Probe name | Health monitoring |
| host | Probe host | Target host |
| interval | Probe interval | Monitoring frequency |
| minimum_servers | Min healthy servers | Availability |
| path | Probe path | Health endpoint |
| pick_host_name_from_backend_http_settings | Host header | Request routing |
| timeout | Probe timeout | Timeout settings |
| unhealthy_threshold | Unhealthy threshold | Failure detection |
| match status_code | Expected status code | Success criteria |

#### Routing Rules

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| request_routing_rule | Routing rule name | Request routing |
| backend_address_pool_name | Backend pool | Target pool |
| backend_http_settings_name | HTTP settings | Settings reference |
| http_listener_name | Listener name | Listener reference |
| priority | Rule priority | `var.priority` |
| rule_type | Rule type | Basic/PathBased |

#### Rewrite Rules

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| rewrite_rule_set | Rewrite set name | URL rewriting |

#### URL Path Maps

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| url_path_map | Path map name | Path-based routing |
| default_backend_address_pool_name | Default pool | Default routing |
| default_backend_http_settings_name | Default settings | Default configuration |
| default_rewrite_rule_set_name | Default rewrite | Default URL rewriting |
| path_rule | Path rule name | Path matching |
| paths | URL paths | Path patterns |
| rewrite_rule_set_name | Rewrite set | URL rewriting |

---

## Sheet 5: ACR NRS

**Purpose:** Azure Container Registry Network Rule Set configuration

### Key-Value Pairs (7)

| Field Name | Description | Usage in Terraform |
|------------|-------------|-------------------|
| action | Rule action | Allow/Deny |
| 1, 3, 5, 7, 9, 11 | IP range identifiers | Network rules |

**Note:** This sheet appears to contain IP range configurations for ACR firewall rules.

---

## Sheet 6: Resource Options

**Purpose:** Resource naming patterns and prefixes

### Key-Value Pairs (38)

Resource naming patterns for consistent naming across all Azure resources:

| Resource Type | Field Name | Usage in Terraform |
|--------------|------------|-------------------|
| Overview | Overview | Documentation |
| Resource Group | Resource_Group | `var.resource_naming_patterns["Resource_Group"]` |
| Application Security Group | Application_Security_Group | ASG naming |
| Subnet | Subnet | `var.resource_naming_patterns["Subnet"]` |
| Network Security Group | Network_Security_Group | `var.resource_naming_patterns["Network_Security_Group"]` |
| User Assigned Identity | User_Assigned_Identity | Identity naming |
| Private Endpoint | Private_Endpoint | Private endpoint naming |
| Key Vault | Key_Vault | Key vault naming |
| Key Vault Key | Key_Vault_Key | Key naming |
| Disk Encryption Set | Disk_Encryption_Set | Encryption naming |
| Virtual Machine | Virtual_Machine | VM naming |
| Data Disk | Data_Disk | Disk naming |
| Storage Account | Storage_Account | `var.resource_naming_patterns["Storage_Account"]` |
| Storage Share | Storage_Share | Share naming |
| Kubernetes Cluster | AKS | AKS naming |
| AKS Default Node | AKS_Default_Node | Node pool naming |
| AKS Cluster Node | AKS_Cluster_Node | Node pool naming |
| Container Registry | Azure_Container_Registry | `var.resource_naming_patterns["Azure_Container_Registry"]` |
| Application Gateway | Application_Gateway | `var.resource_naming_patterns["Application_Gateway"]` |
| App Service Plan | App_Service_Plan | Plan naming |
| App Service Environment | App_Service_Environment | ASE naming |
| Windows Web App | Windows_Web_App | Web app naming |
| Redis Cache | Azure_Cache_for_Redis | Redis naming |
| Application Insights | Application_Insights | Insights naming |
| Data Collection Rule | Data_Collection_Rule | DCR naming |
| Log Analytics Workspace | Log_Analytics_Workspace | Workspace naming |
| Azure Monitor Workspace | Azure_Monitor_Workspace | Monitor naming |
| Azure Managed Grafana | Azure_Managed_Grafana | Grafana naming |
| Public IP Address | Public_IP_Address | IP naming |
| Load Balancer | Load_Balancer | LB naming |
| SQL Server | MS_SQL_Server | SQL naming |
| SQL Database | MS_SQL_Database | Database naming |
| SQL Managed Instance | MS_SQL_Managed_Instance | MI naming |
| RDP/SSH Access | RDP_SSH_Access | Access naming |
| Post Deployment | Post_Deployment | Script naming |
| Route Table | Route_Table | Route table naming |
| Virtual Network | VNET | VNet naming |
| Subscription | Subscription | Subscription reference |

### Tables (1)

**Table 0:** Resource naming patterns with Prefix and Suffix columns

---

## Sheet 7: Issue and blockers

**Purpose:** Issue tracking and blockers

### Status

- No key-value pairs
- No tables
- Currently empty

---

## Data Usage in Terraform

### Variables Created (22)

1. **Project Configuration**
   - `project_name`
   - `application_name`
   - `environment`
   - `location`

2. **Build Environment**
   - `subscription`
   - `resource_group_key`

3. **Application Details**
   - `app_owner`
   - `business_owner`
   - `admin_username`

4. **Infrastructure**
   - `vm_count`
   - `vm_size`

5. **Network Configuration**
   - `vnet_address_space`
   - `subnet_address_prefixes`

6. **Application Gateway**
   - `app_gateway_sku`
   - `app_gateway_capacity`
   - `app_gateway_port`
   - `app_gateway_protocol`

7. **Container Registry**
   - `acr_sku`

8. **Storage**
   - `storage_account_tier`
   - `storage_replication_type`

9. **Resource Naming**
   - `resource_naming_patterns`
   - `tags`

### Resources Generated (15)

1. `azurerm_resource_group.main`
2. `azurerm_virtual_network.main`
3. `azurerm_subnet.main`
4. `azurerm_network_security_group.main`
5. `azurerm_network_security_rule.rule_*` (13 rules)
6. `azurerm_public_ip.appgw`
7. `azurerm_application_gateway.main`
8. `azurerm_container_registry.main`
9. `azurerm_storage_account.main`
10. `azurerm_storage_container.main`
11. `azurerm_linux_virtual_machine.*` (2 VMs)
12. `azurerm_network_interface.*` (2 NICs)

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Sheets** | 7 |
| **Total Key-Value Pairs** | 296 |
| **Total Tables** | 30 |
| **Total Fields Extracted** | 296+ |
| **Terraform Variables** | 22 |
| **Terraform Resources** | 15 |
| **NSG Rules** | 13 |
| **VM Instances** | 2 |

---

## Notes

1. **Terraform Variables:** All fields starting with `wab:` or containing `Terraform Variable` are variable references in the Excel template
2. **Resource Naming:** The Resource Options sheet provides standardized naming patterns for all Azure resources
3. **Extensibility:** The structure supports adding more sheets for additional Azure resources
4. **Validation:** Each sheet includes validation columns to ensure data integrity
5. **Empty Fields:** Some fields may be empty or contain placeholder values in the template

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-10-01 | 1.0 | Initial catalog creation |

---

**End of Excel Fields Catalog**

