# TCB-AI: Intelligent Banking Agent System

An AI-powered agent system for banking and financial services that provides automated feature selection, model training, data cleaning, and predictive analytics capabilities.

## 🚀 Features

- **Feature Selection Agent**: Intelligent feature engineering and selection for ML models
- **Model Training Agent**: Automated machine learning model training and evaluation
- **Data Cleaning Agent**: AI-powered data quality assessment and cleaning
- **Model Explanation Agent**: Generate interpretable explanations for model predictions
- **ETL Pipeline**: Comprehensive data extraction, transformation, and loading capabilities
- **Real-time Streaming**: Server-sent events for real-time agent responses
- **Multi-threaded Conversations**: Persistent chat history across sessions

## 🏗️ Architecture

The system is built using:
- **LangGraph**: For agent orchestration and workflow management
- **FastAPI**: RESTful API backend with streaming support
- **SQLAlchemy**: Database ORM with async support
- **Streamlit**: Simple UI for testing and demonstration
- **scikit-learn**: Machine learning model training and inference
- **Pandas**: Data manipulation and analysis

## 📋 Prerequisites

- Python 3.9+
- UV package manager (recommended) or pip
- PostgreSQL database (optional, uses mock data by default)

## 🛠️ Installation

### Quick Setup with UV (Recommended)

```bash
# Install UV package manager
pip install uv

# Clone the repository
git clone https://github.com/yourusername/tcb-ai.git
cd tcb-ai

# Install dependencies
uv sync --frozen

# Activate virtual environment
source .venv/bin/activate
```

### Alternative Setup with pip

```bash
# Clone the repository
git clone https://github.com/yourusername/tcb-ai.git
cd tcb-ai

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Usage

### Start the AI Backend

```bash
# Activate environment
source .venv/bin/activate

# Start the development server
make dev
```

The API server will be available at `http://localhost:8000`

### Launch the UI

```bash
# In a new terminal, activate environment
source .venv/bin/activate

# Start the Streamlit UI
make dev-ui
```

The UI will be available at `http://localhost:8501`

## 🤖 Available Agents

### 1. Feature Selection Agent

Helps select optimal features for ML model training:

```bash
curl -X 'POST' \
  'http://localhost:8000/select_feature_agent/stream' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Help me select features for credit card recommendation",
    "category_config": {
      "category_id": "CreditCard"
    }
  }'
```

### 2. Model Training Agent

Trains and evaluates machine learning models:

```bash
curl -X 'POST' \
  'http://localhost:8000/train_model_agent/stream' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Train a model for credit card recommendations",
    "category_config": {
      "category_id": "CreditCard"
    },
    "model_training_config": {
      "max_depth": 5,
      "min_samples_split": 2
    }
  }'
```

### 3. Data Cleaning Agent

Analyzes and cleans data for warehouse ingestion:

```bash
curl -X 'POST' \
  'http://localhost:8000/data_cleaning_agent/stream' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Clean this transaction data",
    "data_cleaning_config": {
      "column_name": "transaction_amount",
      "column_info": {
        "description": "Transaction amount field",
        "actual_type": "string",
        "quality_issues": ["Non-numeric values", "Missing data"]
      },
      "sample_data": [
        {"transaction_amount": "123.45", "currency": "USD"},
        {"transaction_amount": "invalid", "currency": "EUR"}
      ]
    }
  }'
```

### 4. Model Explanation Agent

Provides interpretable explanations for model predictions:

```bash
curl -X 'POST' \
  'http://localhost:8000/explain_model_agent/stream' \
  -H 'Content-Type: application/json' \
  -d '{
    "message": "Explain why this customer was recommended a credit card",
    "model_explain_config": {
      "user_id": "customer-123",
      "product_id": "credit-card-456"
    }
  }'
```

## 📊 Model Inference

Run batch inference on trained models:

```bash
curl -X 'POST' \
  'http://localhost:8000/inference' \
  -H 'Content-Type: application/json' \
  -d '{
    "model_id": "model_CreditCard_20250614_015533"
  }'
```

## 💾 Data Management

### Raw Data Operations

```bash
# Get current raw data
curl -X 'GET' 'http://localhost:8000/data_cleaning_agent/raw_data'

# Transform raw data with Python code
curl -X 'POST' \
  'http://localhost:8000/data_cleaning_agent/transform_raw_data' \
  -H 'Content-Type: application/json' \
  -d '{
    "python_code": "df[\"amount\"] = pd.to_numeric(df[\"amount\"], errors=\"coerce\")"
  }'

# Refresh raw data from source
curl -X 'POST' 'http://localhost:8000/data_cleaning_agent/refresh_raw_data'
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key
DEFAULT_MODEL=gpt-4o-mini

# Database Configuration (optional)
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=tcb

# Application Settings
AUTH_SECRET=your_auth_secret
DATA_PATH=./notebooks/data
```

### Model Configuration

Models are automatically saved in the `models/` directory with timestamps. The system supports:
- Decision Trees
- Random Forests
- Custom scikit-learn models

## 📁 Project Structure

```
tcb-ai/
├── src/
│   ├── agents/           # AI agent implementations
│   ├── service/          # FastAPI application
│   ├── database/         # Database connectors and mock data
│   ├── schema/           # Pydantic models and validation
│   ├── core/             # Core utilities and settings
│   └── train_model/      # ML training and inference
├── notebooks/            # Jupyter notebooks for analysis
├── models/              # Trained model artifacts
├── tests/               # Test suite
└── docs/                # Documentation
```

## 🧪 Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Docker Development

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in development mode
docker-compose -f docker-compose.dev.yml up
```

## 📈 Monitoring and Observability

The system includes built-in monitoring through:
- **Health checks**: `/health` endpoint
- **Chat history**: Persistent conversation tracking
- **Feedback system**: Model performance feedback loop
- **Streaming responses**: Real-time agent output

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For support and questions:
- Create an issue on GitHub
- Contact the development team
- Check the [documentation](docs/) for detailed guides

## 🔮 Roadmap

- [ ] Advanced model interpretability features
- [ ] Integration with more data sources
- [ ] Enhanced UI with React frontend
- [ ] Support for additional ML frameworks
- [ ] Real-time model monitoring dashboard