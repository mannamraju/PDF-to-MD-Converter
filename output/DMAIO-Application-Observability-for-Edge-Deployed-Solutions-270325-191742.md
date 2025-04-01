```markdown
# Application Observability for Edge-Deployed Solutions

## Overview
### Background
In modern distributed systems, observability is crucial for maintaining the health, performance, and reliability of edge-deployed solutions. This document outlines design choices for implementing observability at the edge, addressing the following business objectives:

- **Proactive Issue Detection and Easier Root Cause Analysis**: The observability platform will enable the identification and resolution of potential issues before they impact users. Downtime can be minimized, ensuring SLOs and SLIs are consistently met for edge-deployed solutions.
- **Informed Decision-Making**: By leveraging metrics, logs, and traces collected from edge devices, stakeholders can make data-driven decisions regarding system improvements and resource allocation.
- **Improved Operational Efficiency**: Centralize monitoring for all HCI clusters and applications in a single unified platform to enhance operational efficiency.
- **Integration of Deployment Components**: Seamlessly integrate deployment components such as GitOps and CI/CD with the central observability platform.
- **Compatibility with Key Technologies**: Ensure compatibility with Stack HCI, Kubernetes, GitOps-based fleet management, and alignment with Microsoft's observability tech stack strategy.
- **Optimal Data Flow from Edge to Cloud**: Optimize telemetry flow from edge to the observability platform, considering bandwidth constraints.
- **Offline Capabilities**: Ensure resilience to network outages, with automatic data collection resumption post-network restoration.

---

## Pillars of Observability
The purpose of an observability system is to collect, process, and export signals. These signals typically encompass three main components:

- **Metrics**: Quantitative data measuring aspects like CPU usage, memory consumption, request rates, and error rates.
- **Logs**: Detailed, timestamped records of events and actions providing insights into application and infrastructure behavior.
- **Traces**: End-to-end records of requests or transactions identifying performance bottlenecks and dependencies.

For more details, refer to the [Observability - Engineering Fundamentals Playbook](https://learn.microsoft.com/en-us/azure/azure-monitor/overview).

---

## Edge Observability Design
In an edge system, telemetry transmission to the cloud requires:
1. Instrumented systems.
2. An agent to gather and transmit telemetry data.

### Data Sources
Options evaluated for telemetry transmission:
1. **Azure Monitor Container Insights**: Microsoft solution for collecting telemetry from edge container systems.
2. **OpenTelemetry Collector**: Vendor-agnostic open-source tool for telemetry data collection, processing, and export.
3. **Azure Monitor Edge Pipeline (Preview)**: Similar to OpenTelemetry but not recommended due to preview status.

| Feature                  | Azure Monitor Container Insights | OpenTelemetry Collector |
|--------------------------|-----------------------------------|--------------------------|
| Deployment Ease          | Easy: Enabled as an extension.   | Medium: Requires YAML configuration. |
| Multi-cloud, On-premise  | Supported in Azure only.         | Supported.              |
| Storage                  | Azure Monitor.                  | Multiple backends including Application Insights, Prometheus, etc. |
| Offline Storage          | Not supported.                  | Disk-based queuing supported. |
| Instrumentation          | Azure SDK.                      | OpenTelemetry SDK with flexibility. |
| Managed Identity Support | Natively supported.             | Limited. Requires AAD Proxy. |

**Recommendation**: OpenTelemetry is preferred for its reliability, flexibility, and alignment with Microsoft's long-term strategy.

---

## Data Platform
A data platform aggregates, analyzes, and visualizes telemetry data. Key Azure Monitor components include:
- **Azure Monitor Metrics**: Time-series database.
- **Azure Managed Prometheus**: PromQL interface.
- **Log Analytics**: Powered by Azure Data Explorer.
- **Application Insights**: Correlation capabilities.

---

## Visualization
Visualization platforms translate telemetry data into actionable insights. Platforms considered include Azure Monitor Workbooks, Grafana, and Power BI.

For detailed comparisons, refer to [Azure Monitor best practices](https://learn.microsoft.com/en-us/azure/azure-monitor/overview).

---

## Proposed Development Plan

### Architecture
1. Deploy an OpenTelemetry Collector instance per SDLC environment.
2. Configure Azure Monitor Agent (AMA) to pull telemetry from OpenTelemetry Collector’s Prometheus.
3. Deploy Kubernetes services to enable OTLP instrumented workloads.

---

## OpenTelemetry Collector Pipeline
The OpenTelemetry pipeline consists of:
- **Receivers**: Collect telemetry data (e.g., OTLP Receiver, Kubelet Stats Receiver).
- **Processors**: Transform and batch telemetry data (e.g., Batch Processor).
- **Exporters**: Export telemetry to backends (e.g., Azure Monitor Exporter, Prometheus Exporter).

### Extensions
- **File Storage**: Persist state to the local file system for reliability.

---

## Estimating Storage Requirements

### Metrics
Kubelet Stats Receiver broadcasts a payload every 20 seconds. Approximate storage:
- 1 KB per payload.
- 5 MB of data/day/workload.

### Logs and Traces
Estimated at 1 GB/day.

### Configuration
Recommended:
- Max outage = 1 day.
- PVC storage minimum = 10 GB/day.
- Retry configurations to handle failures.

---

## Deployment and Deployment Artifacts
OpenTelemetry Collector will be deployed using GitOps-based workflow. Deployment requirements:
1. Attach PersistentVolumeClaim to each instance.
2. Ensure service reachability via HTTP/gRPC.

---

## Data Retention

| Data Type | Retention Period | Notes                     |
|-----------|------------------|---------------------------|
| Metrics   | 93 days          | Prometheus metrics stored for 18 months. |
| Logs & Traces | 93 days       | Configurable retention. |

---

## Alerting
Azure Monitor Alerts will notify users based on predefined rules. Types of alerts:
- Metric alerts.
- Log search alerts.
- Prometheus alerts.

---

## Communication Mechanism
Alerts will be sent via SMS and email to designated recipients.

---

## Instrumentation in Workloads
Workloads will be identified using:
- `plant_id-environment-application_name`
- `service.version`

Environment variables:
- `OTEL_SERVICE_NAME`
- `OTEL_RESOURCE_ATTRIBUTES`

---

## Control Tower
Control Tower uses Azure Table Storage for checkpointing. Proposed enhancement:
- Publish a custom metric `finished_execution` to track successful uploads.

---

## Service-level Indicators
A Grafana dashboard will provide fleet-wide visibility into operations, with filtering options for location and environment.

---

## Capacity Requirements

| Application | Min CPU | Min Memory | Max CPU | Max Memory |
|-------------|---------|------------|---------|------------|
| OpenTelemetry Collector | 500m     | 1024Mi   | 2000m     | 2048Mi   |
| Azure Monitoring Agent  | 405m     | 1100Mi   | 14100m    | 29700Mi  |

---

## Disk Space
Each OpenTelemetry instance requires 10 GB of disk space for telemetry data storage in case of disconnection.

---

## Images
![Page 1](page_1.png)
![Page 2](page_2.png)
![Page 3](page_3.png)
![Page 4](page_4.png)
![Page 5](page_5.png)
![Page 6](page_6.png)
![Page 7](page_7.png)
![Page 8](page_8.png)
![Page 9](page_9.png)
![Page 10](page_10.png)
![Page 11](page_11.png)
```
This markdown format preserves the structure and formatting of the content while integrating extracted text and images.