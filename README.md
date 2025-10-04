# 📡 Telecom Fraud Detection with Neo4j

This project demonstrates how **graph databases** can be applied to detect telecom fraud patterns such as **International Revenue Share Fraud (IRSF)**, **Wangiri (one-ring scam)**, **SIM Box Fraud**, and **PBX Toll Fraud**.
It uses a synthetic dataset generator to simulate **Call Detail Records (CDRs)**, inject fraud patterns, and load the data into **Neo4j** for analysis with Cypher queries and Jupyter notebooks.

Fraud in telecom is a **multi-billion dollar problem** — the [CFCA (Communications Fraud Control Association)](https://cfca.org/fraudloss/) estimates global telecom fraud losses at **$39.9B in 2021**.
Graphs are a natural fit because fraudsters often operate in **networks of hidden relationships** (shared devices, numbers, routes).

---

## 🚨 Fraud Types Covered

### 🔹 International Revenue Share Fraud (IRSF)

Fraudsters generate artificial traffic to **premium-rate destinations**, often in Africa, the Caribbean, or other high-cost regions. Carriers are left with inflated bills.

* **Pattern**: Sudden spikes of calls to premium prefixes like `+882`, `+979`, `+44-9xxx`.
* [IRSF overview](https://www.akamai.com/blog/security/understanding-international-revenue-share-fraud#:~:text=Executive%20summary,What%20is%20IRSF?)

### 🔹 Wangiri Fraud (“One-Ring Scam”)

Fraudsters call and hang up after one ring. Victims call back and are routed to premium numbers.

* **Pattern**: Many short-duration international calls, followed by callbacks.
* [Wangiri alert](https://seon.io/resources/dictionary/wangiri-scam-fraud/)

### 🔹 SIM Box Fraud (Bypass Fraud)

Fraudsters use banks of SIM cards (“SIM Boxes”) to bypass international rates by terminating calls as local traffic.

* **Pattern**: Hundreds of phone numbers linked to the same device/IMEI.
* [SIM Box Fraud](https://www.subex.com/blog/simbox-fraud-challenges-and-ai-powered-solutions-for-telecom-operators/)

### 🔹 PBX / Toll Fraud

Attackers hack into an enterprise PBX system and generate calls to premium destinations (often at night/weekends).

* **Pattern**: Burst of premium calls during off-hours from one subscriber.
* [Toll Fraud](https://xorcom.com/choosing-the-wrong-ip-pbx-can-cost-you-in-toll-fraud/)

---

## 🗂 Graph Data Model

![Graph Data Model](neo4j_telco_fraud_model.png)

**Nodes**

* **Subscriber** – customer entity (id, name)
* **PhoneNumber** – MSISDN, type (mobile/fixed/premium), country
* **Device** – IMEI/IP, shared by many numbers in SIM box fraud
* **Location** – optional node (country/tower)

**Relationships**

* `(:Subscriber)-[:OWNS]->(:PhoneNumber)`
* `(:PhoneNumber)-[:USES]->(:Device)`
* `(:PhoneNumber)-[:CALLS {ts, duration, cost, caller_country, callee_country}]->(:PhoneNumber)`

This schema makes it easy to query for **clusters, anomalies, and hidden connections**.

---

## ⚙️ Setup Instructions (Docker Only)

Clone the repo and start everything with Docker Compose:

```bash
git clone https://github.com/yourname/neo4j-telco-fraud-demo.git
cd neo4j-telco-fraud-demo
docker-compose up --build
```

This will:

1. Start a Neo4j instance at [http://localhost:7474](http://localhost:7474)

   * Username: `neo4j`
   * Password: `demoPassword123`
2. Run the **CDR generator** → synthetic + fraud-injected CSVs stored in `data/import/`
3. Neo4j is ready to load those CSVs.

---

## 📥 Loading Data into Neo4j

Run all Cypher loading scripts inside the Neo4j container:

```bash
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /load_cypher/00_constraints.cypher
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /load_cypher/10_load_subscribers.cypher
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /load_cypher/20_load_numbers.cypher
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /load_cypher/30_load_devices.cypher
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /load_cypher/40_load_cdrs.cypher
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /load_cypher/50_link_numbers_devices.cypher
```

---

## 🔎 Fraud Detection Queries

Queries are stored in the `queries/` folder. Examples:

### Detect IRSF

```bash
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /queries/10_detect_irsf.cypher
```

### Detect Wangiri

```bash
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /queries/20_detect_wangiri.cypher
```

### Detect SIM Box

```bash
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /queries/30_detect_simbox.cypher
```

### Detect PBX Toll Fraud

```bash
docker exec -it neo4j-telco cypher-shell -u neo4j -p demoPassword123 -f /queries/40_detect_pbx_tollfraud.cypher
```

---

## 📊 Jupyter Notebook Analysis

The notebook [`fraud_analysis.ipynb`](fraud_analysis.ipynb) connects to Neo4j with the Bolt driver, runs queries, and visualizes the results with **Pandas** and **Matplotlib**.

### Example outputs

* **IRSF** → Top premium numbers by fraudulent call cost
* **Wangiri** → Short-duration call attempts
* **SIM Box** → Devices linked to many numbers

Run locally:

```bash
pip install jupyterlab pandas matplotlib neo4j
jupyter lab
```

Open `fraud_analysis.ipynb` and run the cells.

---

## 🚀 Extending the Project

* **Neo4j Bloom**: Natural language graph exploration.
* **Neo4j Graph Data Science (GDS)**: Use Louvain community detection or centrality to identify fraud rings.
* **Real-time integration**: Stream CDRs into Neo4j/Kafka pipelines for continuous fraud monitoring.

---

## 📚 References

* [IRSF overview](https://www.akamai.com/blog/security/understanding-international-revenue-share-fraud#:~:text=Executive%20summary,What%20is%20IRSF?)
* [GSMA Fraud & Security Resources](https://www.gsma.com/security/)
* [Wangiri alert](https://seon.io/resources/dictionary/wangiri-scam-fraud/)
* [Toll Fraud](https://xorcom.com/choosing-the-wrong-ip-pbx-can-cost-you-in-toll-fraud/)