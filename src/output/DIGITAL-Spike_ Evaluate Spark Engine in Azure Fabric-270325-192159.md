# Spike: Evaluate Spark Engine in Azure Fabric

## Description

As a data engineer, I want to run transformation jobs in the Spark Engine in Fabric to evaluate the
following:

- Integrate with MVE Data Generator
- Flexibility of Job Scheduling
- Integration with ADLS/OneLake
- Performance of Spark Engine
- CI/CD of Spark Notebooks
- Data Observability
- Integration of Great Expectations
- KeyVault Integration
- Cost Estimation

## Summary

### Feature Support Summary

| Feature | Support Status |
|---------|---------------|
| Flexibility of Job Scheduling | Partial |
| Integration with ADLS/OneLake | Yes |
| Performance of Spark Engine | Yes |
| CI/CD of Spark Notebooks | Limited |
| Data Observability | Limited |
| Integration of Great Expectations for Data Validation | Yes |
| KeyVault Integration in Spark Engine | Yes |
| Cost Estimation for Workloads | Needs Review |

### Findings

#### Flexibility of Job Scheduling

In short, Apache Spark job scheduling can be done at the Cluster level or at the Spark Application level:

- **Cluster Level:**
  Here, a job refers to multiple Spark applications. This refers to scheduling jobs on the same cluster
  based on the resources available in the cluster. Each job requests resources from the cluster manager
  for processing the job. Once the request is approved, these resources are locked and won't be
  available for subsequent jobs until they are released.

- **Application Level:**
  In Spark, an action triggers a job. There might be cases where multiple job requests come in;
  job scheduling refers to scheduling these jobs accordingly.

#### Spark Job Definition Comparison

| Feature | Support Status |
|---------|---------------|
| Concurrency Throttling and Queueing | Partial |
| Integration with ADLS/OneLake | Yes |
| Performance of Spark Engine | Yes |
| CI/CD of Spark Notebooks | Limited |
| Data Observability | Limited |
| Integration of Great Expectations | Yes |
| KeyVault Integration | Yes |
| Cost Estimation | Needs Review |

### Key Details

#### Microsoft Fabric Spark Job Submission

- Job submission is based on purchased Fabric capacity SKUs
- The queueing mechanism operates as a **FIFO-based queue**, allowing jobs to be submitted once
  capacity becomes available
- When the capacity is fully utilized due to concurrent running jobs, new submissions are throttled
  with the message:

> "Unable to submit this request because all the available capacity is currently being used.
> Cancel a currently running job, increase your available capacity, or try again later."

Notebook jobs and Spark job definitions are automatically retried when capacity becomes available.
The queue expiration is set to **24 hours** from the job submission time.

#### Bursting

- Fabric capacities support **bursting**, enabling extra compute cores beyond what you've purchased
- For Spark workloads, bursting allows users to submit jobs with a total of **3X the Spark VCores
  purchased**
- Bursting increases the total number of Spark VCores for concurrency but doesn't increase the
  maximum cores per job
- Users cannot submit a job that requires more cores than what their Fabric capacity offers

#### Optimistic Job Admission

- Introduced for more **flexibility in concurrency usage**
- Users can run up to ~24 jobs concurrently with the same configuration when submitted concurrently
- Prevents job starvation and significantly improves concurrency (up to ~12X in some cases)

### Custom Apache Spark Pools

- **Custom Spark Pools** can be created in Fabric
- Enable or disable **autoscaling** for custom Spark pools
- With autoscaling, the pool dynamically acquires nodes up to a maximum limit specified by the user,
  retiring them after job execution. This dynamic resource adjustment ensures better performance based
  on job requirements.

### Additional Considerations and Limitations

- **Livy API:** In the roadmap but not yet exposed in Fabric. Users must create notebooks and Spark
  job definitions with the Fabric UI
- **Managed Identity:** Currently, Fabric doesn't support running notebooks and Spark job definitions
  using workspace identity or managed identity for Azure KeyVault within notebooks

## Performance of Spark Engine

- Spark engine in Fabric spins up significantly faster than Synapse Engine: **2 to 4 seconds vs
  ~2 minutes**

## Integration with ADLS/OneLake

### OneLake: To Rule Them All

#### Overview

OneLake is a single, unified, logical data lake for the entire organization, akin to OneDrive.
OneLake comes automatically with every Microsoft Fabric tenant and is designed to be the **single
place for all analytics data**. OneLake offers:

- One data lake for the entire organization
- One copy of data for use with multiple analytical engines

#### Key Features of OneLake

- Built on **Azure Data Lake Storage (ADLS) Gen2**, supporting all file types (structured or
  unstructured)
- Stores all Fabric data items like data warehouses and lakehouses in **Delta Parquet format**
- Compatible with existing ADLS Gen2 applications, including Azure Databricks using the same APIs
  and SDKs
- Allows addressing data as if it's one big ADLS storage account for the organization
- Each workspace corresponds to a container; different data items appear as folders within those
  containers

#### OneLake File Explorer for Windows

OneLake is the "OneDrive for data," enabling:

- Easy exploration of OneLake data from Windows
- Navigation across workspaces and data items
- Uploading, downloading, and modifying files

Even **nontechnical users** can work with data lakes through OneLake File Explorer.

#### Shortcuts Connect Data Across Domains Without Movement

Shortcuts allow users and applications to share data without moving or duplicating it:

- Represent references to data stored in file locations within OneLake, ADLS, S3, Dataverse,
  or external sources
- Shortcuts mimic local storage behavior for files and folders

## CI/CD of Spark Notebooks

### Source Control Integration

#### Git Integration Features

- **In Preview:** Supports Git integration with Azure DevOps and Azure Repos
- Each team member creates isolated workspaces during collaboration
- Version control for entire analytics projects
- Branch protection and review policies support
- Conflict resolution with automatic merging when possible

#### Git Workflow Support

- Feature branch development
- Pull request-based reviews
- Automatic conflict detection
- History tracking and rollback capabilities
- Parallel development support

### Deployment Pipeline Features

#### Environment Management

- Support for multiple environments (Dev/Test/Prod)
- Environment-specific configurations
- Selective deployment of artifacts
- Automated validation between stages

#### Deployment Rules

- **Validation Rules:** Ensure code quality and standards
- **Dependencies:** Automatic dependency resolution
- **Rollback:** Automated rollback on failure
- **Versioning:** Automatic version management

### Supported Artifacts

#### Primary Artifacts

- Spark Notebooks
- Data Pipelines
- Dataflows Gen1
- Datamarts
- Lakehouse configurations
- Reports
- Semantic models

#### Configuration Items

- Connection strings
- Environment variables
- Security configurations
- Resource allocations

### Integration Features

#### Azure DevOps Integration

- Built-in CI/CD pipelines
- Work item tracking
- Release management
- Automated testing support

#### Automated Testing Support

- Notebook validation
- Data quality checks
- Performance testing
- Security compliance verification

### Security and Compliance

#### Access Control

- Role-based access control (RBAC)
- Environment-specific permissions
- Secret management integration
- Audit logging

#### Compliance Features

- Change tracking
- Deployment approvals
- Audit history
- Regulatory compliance support

### Best Practices

#### Development Workflow

1. **Workspace Creation:**
   - Create isolated development workspaces
   - Configure source control integration
   - Set up branch policies

2. **Development Process:**
   - Work in feature branches
   - Regular commits with meaningful messages
   - Automated testing before merges

3. **Review Process:**
   - Pull request-based reviews
   - Automated validation checks
   - Documentation updates

4. **Deployment Strategy:**
   - Progressive deployment through environments
   - Automated validation between stages
   - Rollback procedures in place

### Known Limitations

#### Current Limitations

- **Azure DevOps On-Prem:** Not supported
- **Sovereign Clouds:** Not supported
- **DirectQuery Models:** No support for DirectQuery and composite models on Power BI datasets
- **Analysis Services:** Limited integration with Analysis Services
- **DirectLake:** DirectLake semantic models not supported

#### Workarounds

- Use Azure DevOps Services instead of on-premises
- Implement custom validation for unsupported scenarios
- Use alternative deployment methods for unsupported artifacts
- Manual intervention for complex scenarios

### Future Roadmap

#### Planned Improvements

- Enhanced merge conflict resolution
- Expanded testing capabilities
- Additional source control providers
- Improved semantic model support

#### Migration Considerations

- Plan for future feature adoption
- Document current workarounds
- Track feature availability
- Maintain upgrade readiness

## Data Observability

### Features

- **Spark Advisor:** Built-in monitoring of pools and jobs via the Monitoring Hub
- **Spark history server:** Provides basic observability

#### Unsupported Integrations

- Prometheus/Grafana
- Log Analytics
- Storage Account
- Event Hubs

## Integration of Great Expectations

Tutorial: **Validate data using SemPy and Great Expectations (GX)**

## KeyVault Integration

Key Vault integration is supported via Microsoft Spark Utilities (MSSparkUtils):

- Credential utilities manage secrets and access tokens stored in Azure Key Vault

## Cost Estimation

### Fabric SKU Types and Pricing Models

1. **Azure Model**
   - **Billing:** Per-second granularity with no upfront commitment
   - **Management:** Pay-as-you-go model, scalable through Azure portal
   - **Cost Optimization:** Capacity can be paused during idle periods
   - **Best For:** Variable workloads, development/testing environments
   - **Key Benefit:** Maximum flexibility and cost control

2. **Microsoft 365 Model**
   - **Billing:** Monthly or yearly commitment required
   - **Management:** Fixed capacity with predictable costs
   - **Cost Optimization:** Better rates for long-term commitments
   - **Best For:** Production workloads with steady utilization
   - **Key Benefit:** Predictable spending and potential cost savings

### Capacity Units (CUs) and Pricing Structure

#### Base Pricing

- **Standard Rate:** $0.18/CU/hour (USD) for EAST US 2
- **Minimum Purchase:** F4 (4 CUs)
- **Maximum Single Instance:** F2048 (2048 CUs)

#### Available SKU Sizes

| SKU Size | CUs | Ideal For |
|----------|-----|-----------|
| F4 | 4 | Development and testing |
| F8 | 8 | Small production workloads |
| F16 | 16 | Medium production workloads |
| F32 | 32 | Large production workloads |
| F64 | 64 | Enterprise workloads |
| F128+ | 128+ | Large enterprise deployments |

#### Bursting Capabilities

- **Limit:** Up to 3X purchased Spark VCores
- **Use Case:** Handle temporary spikes in demand
- **Cost:** Included in base price
- **Restrictions:** Cannot exceed maximum cores per job limit
- **Duration:** Available for short bursts, not sustained usage

### Cost Components Breakdown

#### 1. Compute Costs

- **Formula:** CUs × Hours × Rate
- **Example:**
  - F64 SKU running 24/7:
    - 64 CUs × 730 hours × $0.18 = $8,409.60/month
  - F32 SKU running 12 hours/day:
    - 32 CUs × 365 hours × $0.18 = $2,102.40/month

#### 2. Storage Costs

- **OneLake Storage:** $0.023/GB/month
- **Includes:**
  - Raw data storage
  - Delta tables
  - Notebook outputs
  - Query results
  - Temporary processing files

#### 3. Network Costs

- **Inter-region Transfer:** Variable based on source/destination
- **Inbound Data:** Usually free
- **Outbound Data:** Charged based on volume tiers
- **VNet Integration:** May incur additional costs

#### 4. Additional Costs

- **Power BI Pro Licenses:** $10/user/month
- **Premium Features:** Varied based on requirements
- **Support Plans:** Different tiers available

### Optimization Strategies

#### 1. Compute Optimization

- Schedule jobs during off-peak hours
- Implement auto-scaling for variable workloads
- Use bursting capabilities strategically
- Right-size CUs based on actual usage patterns

#### 2. Storage Optimization

- Implement data lifecycle management
- Use compression for stored data
- Regular cleanup of temporary files
- Monitor storage metrics

#### 3. Cost Management Tools

- **Azure Cost Management:** Track spending patterns
- **Budget Alerts:** Set up notifications
- **Usage Reports:** Monitor resource utilization
- **Optimization Recommendations:** AI-driven insights

### Concrete Example: Enterprise Implementation

A mid-sized enterprise implementing Microsoft Fabric with mixed workload patterns:

| Component | Configuration | Monthly Cost |
|-----------|---------------|--------------|
| **Primary Compute** | F64 × 365h (12h/day) | $4,204.80 |
| **Development Environment** | F32 × 365h (12h/day) | $2,102.40 |
| **Data Storage** | 1000GB OneLake | $23.00 |
| **User Licenses** | 100 Power BI Pro users | $1,000.00 |
| **Support** | Standard tier | $100.00 |
| **Network Transfer** | 500GB/month | $45.00 |
| **Total Monthly Cost** | | $7,475.20 |

#### Annual Cost Projection

- **Monthly Cost:** $7,475.20
- **Annual Total:** $89,702.40
- **Potential Savings:**
  - Reserved Instances: Up to 20%
  - Optimized Storage: ~5-10%
  - Workload Scheduling: ~15%

### Comparison with Alternative Solutions

#### vs. Azure Synapse Analytics

- **Initial Setup:** Lower in Fabric
- **Operational Costs:** Generally lower for similar workloads
- **Management Overhead:** Reduced in Fabric
- **Integration Costs:** Better in Fabric for Microsoft ecosystem

#### vs. Self-Managed Spark

- **TCO:** Higher in Fabric but includes managed services
- **Operational Efficiency:** Better in Fabric
- **Resource Utilization:** More efficient in Fabric
- **Maintenance Costs:** Significantly lower in Fabric

### Cost Monitoring and Governance

1. **Built-in Tools**
   - Resource utilization dashboards
   - Cost allocation reports
   - Usage metrics
   - Performance insights

2. **Best Practices**
   - Regular cost reviews
   - Automated shutdown of idle resources
   - Resource tagging for cost allocation
   - Budget thresholds and alerts

### Additional Resources

- [Fabric Pricing Calculator](https://learn.microsoft.com/en-us/fabric/enterprise/microsoft-fabric-pricing)
- [Capacity Planning Guide](https://learn.microsoft.com/en-us/fabric/enterprise/capacity-planning)
- [Cost Optimization Best Practices](https://learn.microsoft.com/en-us/fabric/enterprise/fabric-skus#fabric-capacity-units-cu)
- [Enterprise Deployment Guide](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-deployment-process)

## Resources

1. [Microsoft Fabric vs Synapse: A Comparative Study](https://learn.microsoft.com/en-us/fabric/get-started/fabric-vs-synapse)
2. [Fabric and Azure Synapse Spark Comparison](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-compute#compare-fabric-data-engineering-and-azure-synapse-spark)
3. [Overview of Fabric Git Integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-overview)
4. [Get Started with Git Integration](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/add-git-repository)
5. [Git Integration Process](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-integration-process)
6. [Apache Spark Monitoring Overview](https://learn.microsoft.com/en-us/fabric/data-engineering/monitor-spark-applications)
7. [Deployment Pipelines Process](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/understand-deployment-process)
8. [Buy a Microsoft Fabric Subscription](https://learn.microsoft.com/en-us/fabric/enterprise/buy-subscription)
9. [Capacity Planning Guide](https://learn.microsoft.com/en-us/fabric/enterprise/capacity-planning)

## Images

![Diagram showing the execution flow of Spark jobs in Azure Fabric](../output/images/image_1_1.png)

![Dashboard interface displaying real-time performance metrics for Spark clusters](../output/images/image_3_1.png)
