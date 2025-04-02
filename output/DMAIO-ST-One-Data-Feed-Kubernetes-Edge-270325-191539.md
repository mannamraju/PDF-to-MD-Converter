# ST-One Data Feed in Kubernetes on the Edge

## Architecture Diagram

## ST-One Data Feed Process

1. PLCs and factory equipment send data to the ST -One devices inside the OT  network  
2. ST-One devices batch and send data up to the ST -One cloud where it is made available through an API.  
   This process exists today and is a black-box that we will leave unchanged.  
3. ST-One devices batch and send data to the ST -One RabbitMQ broker in the IT  network.  
4. The ST -One Ingest Service processes the batch messages from the ST -One devices.  
5. The ST -One Ingest Service places individual telemetry messages back into RabbitMQ.  
   The Ingest service is a black-box that hosts proprietary ST -One algorithms for handling batching and compression. PostgreSQL  is  
   used to store time-series data needed for the Ingest Service.  
6. The Mosquitto broker bridges topics from RabbitMQ. These are individual telemetry messages.  
   Mosquitto is required to bridge topics due to incompatibilities between RabbitMQ’ s MQTT  plugin and AIO’s MQ bridging.  
7. The Mosquitto broker bridges topics into AIO MQ to be made available for AIO components.  
8. AIO Data Processing pipelines or Cloud Connectors read messages from the AIO MQ.  
   The AIO MQ service may be redundant if AIO features can read messages directly from Mosquitto.ST-One and AIO components will be in their own namespaces  

```
Azure Stack HCI
AKS on HCI
ST-OneEdge Data
FeedBlob StorageMessage V alidation ST-One APICloudMosquitto AIO MQAIO Data Processor
Cloud ConnectorRabbitMQ Ingest Service PostgreSQL5GB 5GB 40GBPLC
PLC
PLCST-One DevicesOT
IT1
23
4
5
6
7 8
9
10 105GB 5GB
```

We can query data from PostgreSQL  directly for detailed validation & comparison. May require a dif ferent set of networking &  
connectivity challenges, but could be a fallback if AIO pipelines don’t work.

This would decouple proving 2 things:  
1. ST-One data flow at the edge  
2. AIO data pipelines & cloud connectors  

9. AIO Data Processing pipelines or Cloud Connectors write telemetry to Blob Storage in the cloud.  
10. The Message V alidation component reads individual messages from Blob Storage and the ST -One API to compare and validate ST -  
    One messages flowing through the Azure Stack HCI AKS cluster .  

## ST-One Kubernetes Components

The components that make up the ST -One portion in Kubernetes include:

1. **RabbitMQ**: A message broker  that supports MQTT  through a plugin.  
   - requires a 5GB mounted volume for storing queued messages.  
   - Deployed as a single pod Kubernetes StatefulSet and configured with ConfigMaps and Secrets.  
   - See Deploying RabbitMQ to Kubernetes: What's Involved?  for more details on deploying in Kubernetes.

2. **The Ingest Service**: A proprietary service that manages messages from the OT  network through RabbitMQ and includes custom batch  
   decompression logic for placing individual telemetry messages back into RabbitMQ.  
   - requires 5GB mounted volume to use for caching.  
   - Deployed as a Kubernetes Deployment and configured with ConfigMaps and Secrets.

3. **PostreSQL**: Implemented as timescaledb  to store time series data. This provides backing storage for the Ingest service.  
   - requires 40GB mounted volume for longer term persistence.  
   - Deployed as a single pod Kubernetes StatefulSet and configured with ConfigMaps and Secrets.  
   - Timescale used to support a helm chart , but recently deprecated it in favor of PostgreSQL  operators for Kubernetes .  
   - More details on resource usage can be found in Resource Utilization & Capacity Estimates .

## AIO Kubernetes Components

The components that make up the AIO portion in Kubernetes include:

1. **Mosquitto**: not specific to AIO, but required to bridge messages with ST -One’ s RabbitMQ.  
   - requires a 5GB mounted volume for storing queued messages.  
   - Deployed as a StatefulSet and configured with ConfigMaps and Secrets  
   - See Spike - Connect AIO with External Message Broker  for more details on setting up a mosquitto broker as a bridge in  
     Kubernetes.

2. **AIO MQ**: AIO’s MQTT  message broker. This component may be redundant with the mosquitto broker depending on whether AIO  
   features can integrate well with mosquitto.  
   - This is installed as part of AIO itself. There is no need to deploy additional pods.  
   - AIO MQ can be configured to use persistent storage for storing queued messages , we will configure 5GB for this purpose.

3. **AIO Data Processor & Cloud Connector**: AIO’s features that can transport data from message brokers to the cloud (blob storage).  
   - We would only need one of these options to send data from an MQTT  broker to Blob Storage.  
   - AIO Data Processor  runs generic no-code pipelines for processing data at the edge. W e would not directly deploy the pods that  
     these pipelines run on.  
   - Cloud Connectors  are no-code components the define connections that bridge data between a source and destination. W e would  
     not directly deploy the pods that these connectors run on.

## Container Images

The table below shows all of the container images that are required to power the system above. Platform-level components can pull from  
mcr.microsoft.com  for images while custom components and open source images will be hosted in Kraft’ s ACR to enable security  
scanning, but we can pull from Dockerhub for the POC.

```
RabbitMQ Docker Community rabbitmq Public khazeus2controltowecacr001.azur
ecr.io
Ingest Service ST-One --- Private khazeus2controltowecacr001.azur
ecr.io
PostgreSQL Timescale timescale/timescal
edb-haPublic khazeus2controltowecacr001.azur
ecr.io
Mosquitto Eclipse Foundation eclipse-mosquitto Public khazeus2controltowecacr001.azur
ecr.io
AIO MQ Microsoft --- Public mcr.microsoft.com
AIO Data Processor & 
Cloud ConnectorMicrosoft --- Public mcr.microsoft.comKubernetes 
ComponentMaintainer Image Public/Private Container Registry
```

(Above lines represent the original text content as extracted; below is a correctly formatted table interpretation of the same entries for clarity.)

| Kubernetes Component                       | Maintainer           | Image                         | Public/Private | Container Registry                                 |
|-------------------------------------------|----------------------|--------------------------------|----------------|----------------------------------------------------|
| RabbitMQ                                  | Docker Community     | rabbitmq                      | Public         | khazeus2controltowecacr001.azur<br>ecr.io          |
| Ingest Service                            | ST-One              | ---                           | Private        | khazeus2controltowecacr001.azur<br>ecr.io          |
| PostgreSQL                                | Timescale           | timescale/timescaledb-ha      | Public         | khazeus2controltowecacr001.azur<br>ecr.io          |
| Mosquitto                                 | Eclipse Foundation  | eclipse-mosquitto             | Public         | khazeus2controltowecacr001.azur<br>ecr.io          |
| AIO MQ                                    | Microsoft           | ---                           | Public         | mcr.microsoft.com                                  |
| AIO Data Processor & Cloud Connector      | Microsoft           | ---                           | Public         | mcr.microsoft.com                                  |

## ST-One Operations and Monitoring

All components in the system will be operated and monitored using Kraft’ s infrastructure.  
This means ST -One and AIO components will be monitored and managed using the same services. This includes deployment through  
GitOps and Fleet Management as well as using a common observability stack.

ST-One will aid in managing ST -One services by being onboarded to Kraft’ s domain and gaining Azure RBAC and other required roles for  
managing the system. These roles include:

1. A-ID accounts and Azure RBAC Contributor roles to the Dev Resource group in Azure  
2. ZScaler set up for network connectivity to Kraft environments  
3. ACR tokens scoped to only ST -One image repositories  
4. GitHub access to the ST -One Data Feed application repositories  
   a. Source Repository  
   b. Config Repository  
   c. GitOps Repository  

```
 RabbitMQ Docker Community rabbitmq Public khazeus2controltowecacr001.azur
ecr.io
Ingest Service ST-One --- Private khazeus2controltowecacr001.azur
ecr.io
PostgreSQL Timescale timescale/timescal
edb-haPublic khazeus2controltowecacr001.azur
ecr.io
Mosquitto Eclipse Foundation eclipse-mosquitto Public khazeus2controltowecacr001.azur
ecr.io
AIO MQ Microsoft --- Public mcr.microsoft.com
AIO Data Processor & 
Cloud ConnectorMicrosoft --- Public mcr.microsoft.comKubernetes 
ComponentMaintainer Image Public/Private Container Registry
```

(End of PDF content)