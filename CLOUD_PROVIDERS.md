# Cloud providers review

## AWS

## Free tier listing

[AWS Services](https://aws.amazon.com/free/)

### ETL (AWS Glue)

Free Tier: 
* 1 Million objects stored in the AWS Glue Data Catalog
* 1 Million requests made per month to the AWS Glue Data Catalog

Because Free Tier only apply to AWS Glue Data Catalog, the ETL is not free:

Example for US East : $0.44 per DPU-Hour, billed per second, with a 1-minute minimum for each ETL job of type Python shell


## Azure

Fewer options than AWS

[Azure services](https://azure.microsoft.com/en-us/free/)

* Azure Functions: 1,000,000 requests per month

* Azure Cosmos DB: 400 RU/s and 5GB per month

* Azure Notification Hubs: 1,000,000

## GCP

This provider provides a small VM to run code

[GCP Services](https://cloud.google.com/free/)

* Cloud run: 2,000,000 per month (A fully managed environment to run stateless containers.)

* Firestore: 1GB, 50,000 reads, 20,000 writes, 20,000 deletes per day

* Compute Engine: 1 F1-micro instance per month (0.2 VCPU, 600mo ram)

* Pub/Sub: 10 GB of messages per month

* Cloud functions: 2,000,000 invocations per month

