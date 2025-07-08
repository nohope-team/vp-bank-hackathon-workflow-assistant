# VPBank workflow assistant

## 🛠️ Installation

### Quick Setup with UV (Recommended)

```bash
# Install UV package manager
pip install uv

# Clone the repository

# Install dependencies
uv sync --frozen

# Activate virtual environment
source .venv/bin/activate
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
