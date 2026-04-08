# HealthWatch AI: Complete Project Workflow Documentation
## Digital Twin for Hospital Records - Full System Guide

> **Project Version:** 1.0.0  
> **Last Updated:** February 2026  
> **Purpose:** Comprehensive workflow documentation with all diagrams and implementation details

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [System Architecture](#3-system-architecture)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
5. [Machine Learning Pipeline](#5-machine-learning-pipeline)
6. [Blockchain Integration](#6-blockchain-integration)
7. [Privacy & Security](#7-privacy--security)
8. [API Endpoints](#8-api-endpoints)
9. [Frontend Components](#9-frontend-components)
10. [Database Schema](#10-database-schema)
11. [Deployment Workflow](#11-deployment-workflow)
12. [Testing & Validation](#12-testing--validation)
13. [User Workflows](#13-user-workflows)
14. [Troubleshooting](#14-troubleshooting)
15. [Visual Architecture Diagrams](#15-visual-architecture-diagrams)

---

## 1. System Overview

### 1.1 Project Vision

**HealthWatch AI** is a privacy-preserving digital twin system for hospital records that combines:
- **Multi-modal deep learning** for patient deterioration prediction
- **Blockchain audit trails** for data integrity
- **Local Differential Privacy (LDP)** for data protection
- **Zero-Knowledge Proofs** for authentication
- **Real-time analytics** for hospital operations

### 1.2 Key Features

| Feature | Technology | Benefit |
|---------|-----------|---------|
| **Deterioration Prediction** | Temporal Fusion Network (LSTM + Attention) | 85%+ AUROC, 24-48h advance warning |
| **Privacy Protection** | Local Differential Privacy (ε=1.0) | Mathematical privacy guarantees |
| **Audit Trail** | Dual Blockchain (Local + Polygon) | Tamper-proof, low-cost verification |
| **Gas Optimization** | Context-Aware Gas Pricing (CAGP) | 12-15% cost reduction |
| **Prescription Digitization** | Gemini Vision API + OCR | 90%+ accuracy on handwritten Rx |
| **Knowledge Graph** | NetworkX + PageRank | Relationship discovery |

### 1.3 High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        A1[IoT Wearables]
        A2[Manual Entry]
        A3[Prescription Images]
    end
    
    subgraph "Backend Layer"
        B1[FastAPI Server]
        B2[SQLite Database]
        B3[Redis Cache]
    end
    
    subgraph "AI/ML Engine"
        C1[Deterioration Predictor]
        C2[Symptom Analyzer]
        C3[Analytics Engine]
        C4[Knowledge Graph]
    end
    
    subgraph "Blockchain Layer"
        D1[Local Ethereum Sim]
        D2[Polygon Mainnet]
        D3[Gas Optimizer]
    end
    
    subgraph "Privacy Layer"
        E1[LDP Engine]
        E2[ZK Proof System]
    end
    
    subgraph "Frontend"
        F1[React Dashboard]
        F2[Doctor View]
        F3[Patient View]
        F4[Analytics View]
    end
    
    A1 & A2 & A3 --> B1
    B1 --> B2
    B1 --> B3
    B1 --> C1 & C2 & C3 & C4
    B1 --> D1 & D2
    B1 --> E1 & E2
    B1 --> F1
    F1 --> F2 & F3 & F4
    
    D3 -.->|Optimizes| D1 & D2
```

---

## 2. Technology Stack

### 2.1 Backend Technologies

```mermaid
graph LR
    subgraph "Core Backend"
        A[Python 3.9+]
        B[FastAPI]
        C[Uvicorn ASGI]
    end
    
    subgraph "Data Layer"
        D[SQLAlchemy ORM]
        E[SQLite]
        F[Redis]
    end
    
    subgraph "AI/ML"
        G[PyTorch]
        H[Scikit-learn]
        I[Sentence-BERT]
        J[NetworkX]
    end
    
    subgraph "Blockchain"
        K[Web3.py]
        L[Solidity]
        M[Polygon SDK]
    end
    
    A --> B --> C
    B --> D --> E
    B --> F
    B --> G & H & I & J
    B --> K --> L & M
```

**Key Dependencies:**
- **FastAPI**: Modern async web framework
- **PyTorch**: Deep learning models
- **Web3.py**: Blockchain interaction
- **Redis**: High-speed caching
- **Sentence-Transformers**: Clinical text embeddings

### 2.2 Frontend Technologies

```mermaid
graph LR
    subgraph "UI Framework"
        A[React 18]
        B[Vite Build Tool]
    end
    
    subgraph "Visualization"
        C[Recharts]
        D[D3.js]
    end
    
    subgraph "State Management"
        E[React Hooks]
        F[Context API]
    end
    
    subgraph "Styling"
        G[CSS3]
        H[Responsive Design]
    end
    
    A --> B
    A --> C & D
    A --> E & F
    A --> G & H
```

### 2.3 Development Tools

| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **npm** | Package management |
| **pip** | Python packages |
| **PowerShell** | Windows terminal |
| **VS Code** | Code editor |

---

## 3. System Architecture

### 3.1 Complete System Architecture

```mermaid
graph TD
    subgraph "Presentation Layer"
        UI1[Patient Dashboard]
        UI2[Doctor Dashboard]
        UI3[Analytics Dashboard]
        UI4[Blockchain Explorer]
    end
    
    subgraph "API Gateway"
        API[FastAPI REST API]
        WS[WebSocket Server]
    end
    
    subgraph "Business Logic"
        BL1[User Management]
        BL2[Vitals Processing]
        BL3[Alert System]
        BL4[Medical Records]
    end
    
    subgraph "AI/ML Services"
        ML1[Deterioration Predictor]
        ML2[Anomaly Detector]
        ML3[Risk Calculator]
        ML4[Symptom Analyzer]
        ML5[Knowledge Graph]
    end
    
    subgraph "Blockchain Services"
        BC1[Local Ethereum]
        BC2[Polygon Client]
        BC3[Gas Optimizer]
        BC4[ZK Proof]
    end
    
    subgraph "Data Layer"
        DB1[(SQLite)]
        DB2[(Redis Cache)]
    end
    
    subgraph "External Services"
        EXT1[Gemini API]
        EXT2[Polygon Network]
    end
    
    UI1 & UI2 & UI3 & UI4 --> API
    API --> WS
    API --> BL1 & BL2 & BL3 & BL4
    BL2 --> ML1 & ML2 & ML3 & ML4
    BL4 --> ML5
    BL2 & BL4 --> BC1 & BC2
    BC2 --> BC3
    API --> BC4
    BL1 & BL2 & BL3 & BL4 --> DB1
    BL2 --> DB2
    ML4 --> EXT1
    BC2 --> EXT2
```

### 3.2 Component Responsibilities

#### **Presentation Layer**
- **Patient Dashboard**: Real-time vitals, chatbot, prescription upload
- **Doctor Dashboard**: Patient list, vitals monitoring, medical records
- **Analytics Dashboard**: Forecasting, outbreak risk, model comparison
- **Blockchain Explorer**: Audit trail, gas optimization metrics

#### **API Gateway**
- RESTful endpoints for CRUD operations
- WebSocket for real-time data streaming
- CORS handling for cross-origin requests

#### **Business Logic**
- User authentication and authorization
- Vital signs validation and storage
- Alert generation and notification
- Medical record management

#### **AI/ML Services**
- Multi-modal deterioration prediction
- Anomaly detection in vitals
- Risk score calculation
- NLP-based symptom analysis
- Medical knowledge graph construction

#### **Blockchain Services**
- Local Ethereum simulation for fast audits
- Polygon integration for public immutability
- Context-aware gas price optimization
- Zero-knowledge proof authentication

---

## 4. Data Flow Diagrams

### 4.1 Patient Vital Signs Flow

```mermaid
sequenceDiagram
    participant P as Patient/IoT Device
    participant API as FastAPI Backend
    participant DB as SQLite Database
    participant Redis as Redis Cache
    participant ML as ML Engine
    participant Alert as Alert System
    participant BC as Blockchain
    participant UI as Dashboard
    
    P->>API: POST /vitals/ (heart_rate, spo2, etc.)
    API->>DB: Verify user exists
    DB-->>API: User confirmed
    
    API->>DB: Store vital reading
    DB-->>API: Reading ID
    
    par Parallel Processing
        API->>Redis: Cache latest vitals
        API->>ML: Run anomaly detection
        API->>ML: Calculate health score
        API->>BC: Log to blockchain
    end
    
    ML-->>API: Anomaly result
    API->>Alert: Check thresholds
    Alert-->>API: Generate alerts
    
    API->>DB: Store alerts & health score
    API->>Redis: Cache alerts
    
    API-->>P: 200 OK + Reading ID
    
    UI->>API: GET /vitals/user/{id}/latest
    API->>Redis: Fetch from cache
    Redis-->>API: Latest vitals
    API-->>UI: Display vitals
```

### 4.2 Symptom Analysis Flow

```mermaid
sequenceDiagram
    participant P as Patient (Chatbot)
    participant API as Backend API
    participant NLP as Symptom Analyzer
    participant DB as Database
    participant Alert as Alert System
    participant D as Doctor Dashboard
    
    P->>API: POST /symptoms/analyze<br/>"I have severe chest pain"
    
    API->>NLP: Analyze symptom text
    NLP->>NLP: Keyword matching<br/>(chest pain → cardiac)
    NLP-->>API: {symptoms: [cardiac], severity: severe}
    
    API->>API: Generate vital adjustments<br/>(heart_rate: 105, stress: 4.0)
    
    API->>DB: Update patient vitals
    API->>DB: Create medical record
    
    alt Severe Symptoms
        API->>Alert: Create CRITICAL alert
        Alert->>DB: Store alert
        Alert->>D: Real-time notification
    end
    
    API-->>P: "⚠️ Seek immediate medical attention"
```

### 4.3 Deterioration Prediction Flow

```mermaid
flowchart TD
    Start[Doctor requests prediction] --> Fetch[Fetch 48h vital history]
    Fetch --> Check{Sufficient data?}
    
    Check -->|No| Error[Return error message]
    Check -->|Yes| Process[Preprocess data]
    
    Process --> Normalize[Personalized baseline<br/>normalization]
    Normalize --> LSTM[Bi-LSTM encoding]
    
    LSTM --> Attention[Temporal attention<br/>mechanism]
    Attention --> Fusion[Multi-modal fusion]
    
    Fusion --> MC[Monte Carlo Dropout<br/>50 forward passes]
    MC --> Aggregate[Aggregate predictions]
    
    Aggregate --> Risk[Calculate risk score<br/>& confidence interval]
    Risk --> Explain[Generate explanation<br/>(attention weights)]
    
    Explain --> Store[Store prediction in DB]
    Store --> Return[Return to dashboard]
    
    Return --> Display[Display risk gauge<br/>+ key factors]
```

### 4.4 Blockchain Audit Flow

```mermaid
sequenceDiagram
    participant Doc as Doctor
    participant API as Backend
    participant DB as SQLite
    participant Local as Local Ethereum
    participant Gas as Gas Optimizer
    participant Polygon as Polygon Network
    
    Doc->>API: Update patient record
    API->>DB: Save clinical data
    DB-->>API: Record hash
    
    par Dual Blockchain Audit
        API->>Gas: Get optimal gas price
        Gas->>Local: Analyze recent blocks
        Gas-->>API: {safeLow, standard, fast}
        
        API->>Local: Mine block with record hash
        Local->>Local: Proof-of-Work (SHA3-256)
        Local-->>API: Block confirmed (< 50ms)
    and
        API->>Polygon: addRecord(patient, hash)
        Polygon->>Polygon: Smart contract execution
        Polygon-->>API: Transaction hash (< 2s)
    end
    
    API->>DB: Store blockchain references
    API-->>Doc: Success + audit proof
```

---

## 5. Machine Learning Pipeline

### 5.1 ML Architecture Overview

```mermaid
graph TB
    subgraph "Data Preparation"
        A1[Raw Vitals] --> A2[Normalization]
        A3[Clinical Notes] --> A4[Sentence-BERT]
        A5[Demographics] --> A6[One-Hot Encoding]
    end
    
    subgraph "Feature Engineering"
        A2 --> B1[Sequence Padding]
        A4 --> B2[Text Embeddings]
        A6 --> B3[Static Features]
    end
    
    subgraph "Model Architecture"
        B1 --> C1[Bi-LSTM<br/>128 units]
        C1 --> C2[Temporal Attention]
        B2 --> C3[Dense Layer]
        B3 --> C4[Dense Layer]
        
        C2 & C3 & C4 --> C5[Fusion Layer]
        C5 --> C6[Dropout 0.3]
        C6 --> C7[Dense 64]
        C7 --> C8[Output Sigmoid]
    end
    
    subgraph "Prediction"
        C8 --> D1[MC Dropout<br/>50 passes]
        D1 --> D2[Mean & Std]
        D2 --> D3[Risk Score<br/>+ Uncertainty]
    end
```

### 5.2 Training Workflow

```mermaid
flowchart LR
    A[Synthetic Data<br/>Generator] --> B[1000 Patient<br/>Trajectories]
    B --> C[Train/Val Split<br/>80/20]
    
    C --> D[Model Training]
    D --> E{Validation<br/>AUROC > 0.85?}
    
    E -->|No| F[Adjust Hyperparameters]
    F --> D
    
    E -->|Yes| G[Save best_model.pt]
    G --> H[IEEE Validation Suite]
    
    H --> I[Generate Metrics]
    I --> J[ROC Curve]
    I --> K[PR Curve]
    I --> L[Calibration Plot]
    I --> M[Confusion Matrix]
```

### 5.3 Model Components

#### **Temporal Fusion Network**

**File:** `backend/ml/temporal_fusion_model.py`

**Architecture:**
1. **Input Layer**: 48-hour vital sequences (heart_rate, spo2, temp, stress)
2. **Bi-LSTM**: 128 hidden units, captures temporal dependencies
3. **Attention Mechanism**: Learns which time steps are most important
4. **Text Encoder**: Sentence-BERT embeddings (768 dimensions)
5. **Fusion Layer**: Concatenates temporal + text + demographics
6. **Predictor Head**: Dense layers with dropout for regularization
7. **Uncertainty**: Monte Carlo Dropout (50 forward passes)

**Mathematical Formulation:**

$$
\begin{align}
h_t &= \text{BiLSTM}(x_t, h_{t-1}) \\
\alpha_t &= \frac{\exp(W_a h_t)}{\sum_{i=1}^{T} \exp(W_a h_i)} \\
c &= \sum_{t=1}^{T} \alpha_t h_t \\
z &= [c \oplus e_{text} \oplus e_{demo}] \\
P(y|X) &= \frac{1}{N} \sum_{i=1}^{N} \sigma(W_p z_i + b_p)
\end{align}
$$

### 5.4 Analytics Engine

**File:** `backend/ml/analytics_engine.py`

```mermaid
graph LR
    subgraph "Forecasting Models"
        A1[Patient Inflow] --> A2[Time Series<br/>+ Seasonality]
        A3[Outbreak Risk] --> A4[Symptom Scoring]
    end
    
    subgraph "Security Analytics"
        B1[Blockchain Audit] --> B2[Integrity Score]
    end
    
    subgraph "Model Comparison"
        C1[Baseline Models] --> C2[Performance Metrics]
    end
    
    A2 & A4 & B2 & C2 --> D[Analytics Dashboard]
```

**Algorithms:**

1. **Patient Inflow Forecasting**
   ```
   forecast = base + trend * k + seasonality(t+k) + noise
   seasonality = 10 * sin(2π * t / 7)  // Weekly cycle
   ```

2. **Outbreak Risk Scoring**
   ```
   risk = Σ (weight_i * symptom_count_i)
   weights: {fever: 2, cough: 2, breathing: 3, fatigue: 1}
   ```

---

## 6. Blockchain Integration

### 6.1 Dual-Mode Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        A[Medical Record Update]
    end
    
    subgraph "Blockchain Abstraction"
        B[Blockchain Service]
    end
    
    subgraph "Local Chain (Fast Audit)"
        C1[Ethereum Simulator]
        C2[Proof-of-Work]
        C3[Gas Tracking]
        C4[Chain Validation]
    end
    
    subgraph "Public Chain (Immutable Proof)"
        D1[Polygon Mumbai/Mainnet]
        D2[Smart Contract]
        D3[Web3.py Client]
    end
    
    A --> B
    B --> C1 & D1
    C1 --> C2 --> C3 --> C4
    D1 --> D2 --> D3
```

### 6.2 Local Ethereum Simulation

**File:** `backend/blockchain/chain.py`

**Features:**
- **Consensus**: Proof-of-Work (SHA3-256, difficulty=2)
- **Block Structure**: Index, timestamp, transactions, previous_hash, nonce
- **Gas System**: Tracks gas used per transaction
- **Validation**: Full chain integrity verification

**Block Mining Process:**

```mermaid
flowchart TD
    Start[New Transaction] --> Create[Create Block]
    Create --> Init[nonce = 0]
    Init --> Hash[Calculate SHA3-256]
    Hash --> Check{Hash starts<br/>with '00'?}
    Check -->|No| Inc[nonce++]
    Inc --> Hash
    Check -->|Yes| Valid[Valid Block]
    Valid --> Add[Add to Chain]
    Add --> Broadcast[Broadcast to Network]
```

### 6.3 Polygon Integration

**File:** `backend/blockchain/polygon_client.py`

**Smart Contract:** `backend/blockchain/contracts/MedicalRecords.sol`

```solidity
contract MedicalRecords {
    struct Record {
        address patient;
        bytes32 dataHash;
        uint256 timestamp;
        bool active;
    }
    
    mapping(uint256 => Record) public records;
    mapping(address => bool) public authorizedProviders;
    
    event RecordAdded(uint256 indexed recordId, address patient, bytes32 dataHash);
    
    function addRecord(address _patient, bytes32 _hash) public {
        require(authorizedProviders[msg.sender], "Unauthorized");
        records[recordCount] = Record(_patient, _hash, block.timestamp, true);
        emit RecordAdded(recordCount, _patient, _hash);
        recordCount++;
    }
}
```

### 6.4 Context-Aware Gas Pricing (CAGP)

**File:** `backend/blockchain/chain.py` (GasOptimizer class)

**Algorithm Workflow:**

```mermaid
flowchart TD
    Start[Transaction Request] --> Analyze[Analyze Last 5 Blocks]
    Analyze --> Congestion[Calculate Congestion<br/>= avg_gas / max_gas]
    
    Congestion --> Context[Calculate Context Factor<br/>β = 1 + 0.5 * sin(t/10000)]
    
    Context --> Adjust{Congestion Level}
    Adjust -->|> 0.5| High[Multiplier = 1.125]
    Adjust -->|< 0.5| Low[Multiplier = 0.875]
    Adjust -->|= 0.5| Normal[Multiplier = 1.0]
    
    High & Low & Normal --> Calculate[P_gas = P_base * multiplier * β]
    
    Calculate --> Tiers[Generate Tiers]
    Tiers --> Output[safeLow: 0.8x<br/>standard: 1.0x<br/>fast: 1.2x]
```

**Cost Savings:**
- Average: 12-15% reduction vs. fixed pricing
- Peak hours: Up to 20% savings

---

## 7. Privacy & Security

### 7.1 Local Differential Privacy (LDP)

**File:** `backend/ml/privacy_engine.py`

**Laplace Mechanism:**

```python
def add_laplace_noise(value, sensitivity=1.0, epsilon=1.0):
    scale = sensitivity / epsilon
    noise = np.random.laplace(0, scale)
    return value + noise
```

**Privacy Guarantee:**
- ε = 1.0 (privacy budget)
- Any individual record has plausible deniability
- Aggregate statistics remain accurate

**Use Cases:**
- Average heart rate across patients
- Symptom prevalence statistics
- Demographic distributions

### 7.2 Zero-Knowledge Proof Authentication

**File:** `backend/blockchain/zk_proof.py`

**Schnorr Protocol:**

```mermaid
sequenceDiagram
    participant P as Prover (Patient)
    participant V as Verifier (System)
    
    Note over P: Secret: x<br/>Public: y = g^x mod p
    
    P->>P: Generate random r
    P->>V: Commitment: t = g^r mod p
    
    V->>V: Generate random challenge c
    V->>P: Challenge: c
    
    P->>P: Calculate z = r + c*x
    P->>V: Response: z
    
    V->>V: Verify: g^z == t * y^c mod p
    
    alt Valid Proof
        V->>P: ✅ Access Granted
    else Invalid
        V->>P: ❌ Access Denied
    end
```

**Security Properties:**
- **Completeness**: Honest prover always convinces verifier
- **Soundness**: Dishonest prover cannot forge proof
- **Zero-Knowledge**: Verifier learns nothing about secret x

---

## 8. API Endpoints

### 8.1 Complete API Reference

#### **Authentication**

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/auth/login` | POST | User login | `{email, password}` | User object + token |
| `/api/blockchain/zk-verify` | POST | ZK proof authentication | `{user_id}` | Proof trace |

#### **User Management**

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/users/` | POST | Create user | `UserCreate` | User object |
| `/users/{user_id}` | GET | Get user details | `user_id` | User object |
| `/users/` | GET | List all users | `skip, limit` | User array |
| `/users/{user_id}` | PUT | Update user | `user_id, UserUpdate` | Updated user |

#### **Vital Signs**

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/vitals/` | POST | Create vital reading | `VitalReadingCreate` | Reading object |
| `/vitals/user/{user_id}/latest` | GET | Get latest vitals | - | Latest reading |
| `/vitals/user/{user_id}/history` | GET | Get vital history | `limit` | Reading array |
| `/vitals/user/{user_id}/update` | PUT | Update vitals (doctor) | `VitalReadingUpdate` | Updated reading |

#### **Symptoms & Analysis**

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/symptoms/analyze` | POST | Analyze symptoms | `{user_id, symptoms}` | Analysis result |

#### **ML Predictions**

| Endpoint | Method | Description | Parameters | Response |
|----------|--------|-------------|------------|----------|
| `/api/ml/predict-deterioration` | POST | Predict deterioration | `patient_id, horizon_hours` | Risk score + explanation |
| `/api/ml/deterioration-history/{patient_id}` | GET | Get prediction history | `patient_id, limit` | Prediction array |
| `/api/ml/model-info` | GET | Get model metadata | - | Model info |

#### **Analytics**

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/analytics/predictions/inflow` | GET | Patient inflow forecast | 7-day forecast |
| `/analytics/security-audit` | GET | Blockchain integrity score | Audit metrics |
| `/api/analytics/model-comparison` | GET | Model performance comparison | Metrics comparison |
| `/api/analytics/knowledge-graph` | GET | Medical knowledge graph | Nodes + edges |

#### **Blockchain**

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/blockchain/chain` | GET | Get full blockchain | Chain data |
| `/blockchain/validate` | GET | Validate blockchain | Validation result |
| `/api/blockchain/gas-forecast` | GET | Get gas price forecast | CAGP estimates |

---

## 9. Frontend Components

### 9.1 Component Architecture

```mermaid
graph TB
    subgraph "App.js (Root)"
        A[Router]
    end
    
    subgraph "Views"
        B1[LoginView]
        B2[PatientDashboard]
        B3[DoctorDashboard]
        B4[AnalyticsDashboard]
        B5[BlockchainView]
    end
    
    subgraph "Patient Components"
        C1[VitalsCard]
        C2[HealthScoreGauge]
        C3[AlertsList]
        C4[Chatbot]
        C5[PrescriptionScanner]
    end
    
    subgraph "Doctor Components"
        D1[PatientList]
        D2[VitalsMonitor]
        D3[MedicalRecords]
        D4[DeteriorationDashboard]
    end
    
    subgraph "Analytics Components"
        E1[InflowForecast]
        E2[OutbreakRisk]
        E3[ModelComparison]
        E4[KnowledgeGraph]
    end
    
    subgraph "Blockchain Components"
        F1[ChainExplorer]
        F2[GasOptimizer]
        F3[ZKProofDemo]
    end
    
    A --> B1 & B2 & B3 & B4 & B5
    B2 --> C1 & C2 & C3 & C4 & C5
    B3 --> D1 & D2 & D3 & D4
    B4 --> E1 & E2 & E3 & E4
    B5 --> F1 & F2 & F3
```

---

## 10. Database Schema

### 10.1 Entity Relationship Diagram

```mermaid
erDiagram
    User ||--o{ VitalReading : has
    User ||--o{ MedicalRecord : has
    User ||--o{ Alert : receives
    User ||--o{ HealthScore : has
    User ||--o{ DeteriorationPrediction : has
    
    User {
        int id PK
        string name
        string email UK
        int age
        string gender
        string user_type
        string password_hash
        string eth_address
        datetime created_at
    }
    
    VitalReading {
        int id PK
        int user_id FK
        float heart_rate
        float spo2
        float temperature
        float stress_level
        int steps
        int calories
        float sleep_hours
        datetime timestamp
    }
    
    MedicalRecord {
        int id PK
        int user_id FK
        string record_type
        text content
        string blockchain_hash
        string polygon_tx_hash
        datetime created_at
    }
    
    Alert {
        int id PK
        int user_id FK
        string alert_type
        string title
        text message
        bool is_read
        datetime created_at
    }
    
    HealthScore {
        int id PK
        int user_id FK
        float score
        string risk_level
        float cardiac_risk
        float respiratory_risk
        float stress_risk
        datetime timestamp
    }
    
    DeteriorationPrediction {
        int id PK
        int user_id FK
        int prediction_horizon_hours
        float risk_score
        float confidence_lower
        float confidence_upper
        string risk_level
        json top_features
        json attention_weights
        datetime prediction_time
    }
```

---

## 11. Deployment Workflow

### 11.1 Complete Setup Process

```mermaid
flowchart TD
    Start[Fresh System] --> Check[Check Prerequisites]
    Check --> Install1[Install Python 3.9+]
    Check --> Install2[Install Node.js 16+]
    
    Install1 & Install2 --> Clone[Clone Repository]
    
    Clone --> Backend[Backend Setup]
    Backend --> B1[cd backend]
    B1 --> B2[python -m venv venv]
    B2 --> B3[Activate venv]
    B3 --> B4[pip install -r requirements.txt]
    B4 --> B5[python run_simulation.py --mode init]
    B5 --> B6[uvicorn main:app --reload]
    
    Clone --> Frontend[Frontend Setup]
    Frontend --> F1[cd frontend]
    F1 --> F2[npm install]
    F2 --> F3[Create .env file]
    F3 --> F4[npm start]
    
    B6 & F4 --> Running[System Running]
    Running --> Verify[Verify at localhost:3000]
```

### 11.2 Step-by-Step Commands

#### **Terminal 1: Backend**

```powershell
# Navigate to backend
cd d:\AIML\Digital-twin-for-hospital-records\Digital-twin-for-hospital-records\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python run_simulation.py --mode init

# Start backend server
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### **Terminal 2: Frontend**

```powershell
# Navigate to frontend
cd d:\AIML\Digital-twin-for-hospital-records\Digital-twin-for-hospital-records\frontend

# Install dependencies
npm install

# Create .env file (if not exists)
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start frontend
npm start
```

**Expected Output:**
```
Compiled successfully!
Local: http://localhost:3000
```

---

## 12. Testing & Validation

### 12.1 ML Model Validation

**File:** `backend/ml/run_ieee_validation.py`

**Run Validation:**
```powershell
cd backend/ml
python run_ieee_validation.py
```

**Output:**
- `models/ieee_validation/figures/` - Plots
- `models/ieee_validation/tables/` - LaTeX tables
- `models/ieee_validation/VALIDATION_SUMMARY.json` - Metrics

---

## 13. User Workflows

### 13.1 Patient Workflow

```mermaid
flowchart TD
    Start[Patient Login] --> Dashboard[View Dashboard]
    Dashboard --> Check{What to do?}
    
    Check -->|View Vitals| Vitals[See Latest Vitals<br/>& Health Score]
    Check -->|Report Symptoms| Chat[Use Chatbot]
    Check -->|Upload Rx| Scan[Prescription Scanner]
    
    Chat --> Analyze[AI Analyzes Symptoms]
    Analyze --> Update[Auto-Update Vitals]
    Update --> Alert{Severe?}
    Alert -->|Yes| Notify[Notify Doctor]
    Alert -->|No| Record[Record in DB]
    
    Scan --> OCR[Gemini Vision OCR]
    OCR --> Extract[Extract Medications]
    Extract --> Save[Save to Medical Records]
    
    Vitals & Record & Save --> End[Return to Dashboard]
```

### 13.2 Doctor Workflow

```mermaid
flowchart TD
    Start[Doctor Login] --> List[View Patient List]
    List --> Select[Select Patient]
    
    Select --> View{What to view?}
    
    View -->|Vitals| Monitor[Real-time Vitals Monitor]
    View -->|Risk| Predict[Deterioration Prediction]
    View -->|Records| History[Medical Records]
    View -->|Alerts| Alerts[Critical Alerts]
    
    Predict --> ML[Run ML Model]
    ML --> Display[Risk Gauge + Explanation]
    Display --> Decision{High Risk?}
    
    Decision -->|Yes| Intervene[Plan Intervention]
    Decision -->|No| Continue[Continue Monitoring]
    
    Intervene --> Update[Update Treatment Plan]
    Update --> Blockchain[Log to Blockchain]
    
    Blockchain --> End[Return to Patient List]
```

---

## 14. Troubleshooting

### 14.1 Common Issues

#### **Issue 1: Backend Won't Start**

**Symptom:** `ModuleNotFoundError` or import errors

**Solution:**
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version
python --version  # Should be 3.9+
```

#### **Issue 2: Login Fails**

**Symptom:** "Invalid email or password"

**Default Credentials:**
- **Doctor**: `doctor@healthwatch.ai` / `doctor123`
- **Patient**: `patient@healthwatch.ai` / `patient123`

**Solution:**
```powershell
# Check database users
cd backend
python check_users.py

# Reset password if needed
python reset_doctor_password.py
```

---

## 15. Visual Architecture Diagrams

### 15.1 Main System Architecture

![Main Architecture](file:///d:/AIML/Digital-twin-for-hospital-records/Digital-twin-for-hospital-records/main_architecture.jpeg)

### 15.2 Machine Learning Architecture

![ML Architecture](file:///d:/AIML/Digital-twin-for-hospital-records/Digital-twin-for-hospital-records/ml_architecture.jpeg)

### 15.3 Blockchain Architecture

![Blockchain Architecture](file:///d:/AIML/Digital-twin-for-hospital-records/Digital-twin-for-hospital-records/blockchain.jpeg)

### 15.4 Prescription Analysis Workflow

![Prescription Workflow](file:///d:/AIML/Digital-twin-for-hospital-records/Digital-twin-for-hospital-records/prescription.jpeg)

### 15.5 System Results & Metrics

![Results](file:///d:/AIML/Digital-twin-for-hospital-records/Digital-twin-for-hospital-records/results.jpeg)

---

## 16. Performance Metrics

### 16.1 System Performance

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| **API Response Time** | < 500ms | < 200ms | ✅ |
| **ML Prediction Time** | < 2s | < 1.5s | ✅ |
| **Blockchain Latency (Local)** | < 100ms | < 50ms | ✅ |
| **Blockchain Latency (Polygon)** | < 5s | < 2s | ✅ |
| **Frontend Load Time** | < 3s | < 2s | ✅ |

### 16.2 ML Model Performance

| Model | AUROC | Sensitivity | Specificity | Improvement |
|-------|-------|-------------|-------------|-------------|
| **HealthWatch AI** | **0.85** | **0.85** | **0.82** | **Baseline** |
| Simple LSTM | 0.79 | 0.76 | 0.78 | -6% |
| Random Forest | 0.76 | 0.72 | 0.74 | -9% |
| Logistic Regression | 0.72 | 0.68 | 0.70 | -13% |

---

## 17. Quick Reference

### 17.1 Essential Commands

**Start Backend:**
```powershell
cd backend
.\venv\Scripts\Activate
uvicorn main:app --reload
```

**Start Frontend:**
```powershell
cd frontend
npm start
```

**Run Simulation:**
```powershell
cd backend
python run_simulation.py --mode simulate --user_id 1 --duration 120
```

**Validate ML Model:**
```powershell
cd backend/ml
python run_ieee_validation.py
```

### 17.2 Important URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Blockchain Explorer**: http://localhost:3000/blockchain

---

**End of Complete Project Workflow Documentation**

> **For Support:** Review this document first, then check troubleshooting section  
> **For Development:** Follow the deployment workflow and testing guidelines  
> **For Research:** Refer to IEEE_PAPER_DOCUMENTATION.md for technical details
