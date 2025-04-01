# Application Observability for Edge-Deployed Solutions

## Overview

### Background
In modern distributed systems, observability is crucial for maintaining the health, performance, and reliability of edge-deployed solutions. This document outlines design choices for implementing observability at the edge, addressing the following business objectives:

- **Proactive Issue Detection and Easier Root Cause Analysis**: The observability platform will enable the identification and resolution of potential issues before they impact users. By quickly pinpointing the root cause of problems, downtime can be minimized, ensuring that service level objectives (SLOs) and service level indicators (SLIs) are consistently met for edge-deployed solutions.
- **Informed Decision-Making**: By leveraging metrics, logs, and traces collected from edge devices, stakeholders can make data-driven decisions regarding system improvements and resource allocation.
- **Improved Operational Efficiency**: Centralize monitoring for all HCI clusters and applications in a single unified platform to enhance operational efficiency.
- **Integration of Deployment Components**: Seamlessly integrate deployment components such as GitOps and CI/CD with the central observability platform.
- **Compatibility with Key Technologies**: Ensure compatibility with Stack HCI, Kubernetes, GitOps-based fleet management, and alignment with Microsoft's observability tech stack strategy.
- **Optimal Data Flow from Edge to Cloud**: Optimize telemetry flow from edge to observability platform considering bandwidth constraints.
- **Offline Capabilities**: The observability platform should be resilient to network outages, automatically resuming data collection and transmission once connectivity is restored to prevent data loss during downtime.

---

## Pillars of Observability
The purpose of an observability system is to collect, process, and export signals. These signals typically encompass three main components:
- **Metrics**: Quantitative data measuring system performance and health, such as CPU usage, memory consumption, request rates, and error rates.
- **Logs**: Detailed, timestamped records of events and actions within a system, providing insights into behavior and application state.
- **Traces**: End-to-end records of requests or transactions propagating through different services and components in a distributed system, identifying performance bottlenecks and dependencies.

For detailed differences between metrics, logs, and traces, refer to the [Observability - Engineering Fundamentals Playbook](https://learn.microsoft.com/).

---

## Edge Observability Design

In an edge system, the ability to send telemetry to the cloud for analysis requires:
1. **Instrumented Systems**
2. **An Agent**: Facilitates gathering and transmitting telemetry data to the cloud.

### Data Sources
Options evaluated for sending telemetry back to the cloud:

1. **Azure Monitor Container Insights**:
   - First-party solution from Microsoft.
   - Collects telemetry from edge containers systems.
   - Delivers to Azure Monitor services depending on signal type.
   
2. **OpenTelemetry Collector**:
   - Open-source, vendor-agnostic component.
   - Collects, processes, and exports telemetry data.

3. **Azure Monitor Edge Pipeline (Preview)**:
   - First-party solution for building data ingestion pipelines.
   - Similar to OpenTelemetry Collector but not considered due to preview status.

| **Comparison** | **Container Insights** | **OpenTelemetry** |
|----------------|-------------------------|--------------------|
| Ease of Deployment | Easy, enabled as an extension | Medium, requires YAML configuration |
| Supported Environments | Azure-only | Multi-cloud, hybrid |
| Data Collection | Automatic for predefined resources | Flexible, manual or automatic instrumentation |
| Storage | Azure Monitor | Multiple backends (e.g., Application Insights, Prometheus) |

**Recommendation**: Based on assessment criteria such as network interruptions and bandwidth limitations, OpenTelemetry is recommended due to:
- Reliable telemetry transport during outages.
- Flexibility in filtering metrics, logs, and traces.
- Alignment with Microsoft's observability strategy.

---

## Data Platform
A data platform aggregates, analyzes, and visualizes telemetry data for insights into system performance, health, and operational efficiency. This engagement will utilize Azure Monitor technologies.

### Visualization
Visualization platforms translate complex telemetry data into actionable insights:
- **Azure Managed Prometheus**: PromQL interface for Azure Monitor Metrics.
- **Log Analytics**: Powerful analysis engine with KQL query language.
- **Application Insights**: Correlation for developers.
- **Grafana**: Multi-data source integration with popular plugins.

---

## Proposed Development Plan

### Architecture
1. Deploy an OpenTelemetry Collector instance per environment (SDLC).
2. Configure Azure Monitor Agent (AMA) to pull telemetry from OpenTelemetry Collector's Prometheus.
3. Deploy Kubernetes service for OTLP instrumented workloads to send telemetry.

---

## OpenTelemetry Collector Pipeline

### Receivers
- **OTLP Receiver**: Receives data via gRPC or HTTP using OTLP format.
- **Kubelet Stats Receiver**: Metrics for node, pod, container, and volume.
- **Kubernetes Cluster Receiver**: Cluster-level metrics and events.

### Processors
- **Batch Processor**: Compresses data, reduces outgoing connections.

### Exporters
- **Azure Monitor Exporter**: Sends logs, traces, and metrics to Application Insights.
- **Prometheus Exporter**: Exports data in Prometheus format for scraping by Prometheus server.

---

## Estimating Storage Requirements

### Metrics
Example calculation for Kubelet Stats Receiver:
1 KB payload every 20 seconds. For 1 hour:
```
Payload size * Frequency * Duration = 1 KB * (3600/20) = 180 KB/hour
```

**Daily Storage**: Round up to 5 MB/workload/day.

### Logs & Traces
Estimated at 1 GB/day.

---

## Deployment and Deployment Artifacts
OpenTelemetry Collector deployed using GitOps-based workflow. PersistentVolumeClaim (PVC) will ensure local disk caching.

---

## Merging Azure IoT Operations Configuration
Unified configuration combining AIO telemetry and AMA Prometheus scraping.

---

## Alerting
**Types of Alerts**:
- Metric alerts: Azure Monitor Metrics, Application Insights.
- Log search alerts: Log Analytics Workspace.
- Prometheus alerts: PromQL rules.

**Alert Criteria**:
- Fatal issues
- SQL Server connectivity issues
- Blob Storage connectivity issues

---

## Instrumentation in Workloads
Applications implementing OTLP instrumentation must retrieve values via environment variables:
- `OTEL_SERVICE_NAME`
- `OTEL_RESOURCE_ATTRIBUTES`

---

## Control Tower
Control Tower checkpoints implemented in Azure Table Storage will be replaced with a custom metric `finished_execution`.

---

## Service-Level Indicators
A Grafana dashboard will provide fleet-wide visibility into Control Tower operations. Filtering options for location and environment will be introduced.

---

## Capacity Requirements

### CPU & Memory
Empirical suggestions based on telemetry production rate and queue size.

---

### Disk Space
Each OpenTelemetry instance requires 10 GB of disk space for one day of telemetry storage during network disconnection.

---

## Images
The document references the following image files for visual representation:
- `image_1.png`
- `image_2.png`
- `image_2_1.png`
- `image_2_2.png`
- `image_2_3.png`
- `image_3.png`
- `image_3_4.png`
- `image_3_5.png`
- `image_4.png`
- `image_4_6.png`
- `image_4_7.png`
- `image_5.png`
- `image_5_8.png`
- `image_5_9.png`
- `image_6.png`
- `image_6_10.png`
- `image_6_11.png`
- `image_6_12.png`
- `image_6_13.png`
- `image_6_14.png`
- `image_6_15.png`
- `image_7.png`
- `image_7_16.png`
- `image_7_17.png`
- `image_8.png`
- `image_9.png`
- `image_10.png`
- `image_10_18.png`
- `image_10_19.png`
- `image_11.png`

---

**Credits**: [Azure Monitor Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/overview)