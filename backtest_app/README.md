# Backtesting Web App

A simple browser-based backtesting application for trading strategies using Backtrader.

## Features

- 📤 Upload custom Backtrader strategies (.py files)
- 📊 Upload CSV data with OHLCV format
- 💰 Configure initial cash and commission rates
- 📈 View detailed backtest results and metrics
- 🎨 Visual equity curve chart
- 🔒 Secure code validation to prevent malicious imports
- 📥 Download sample strategy and data templates

## Installation

### Step 1: Create Virtual Environment

```bash
python -m venv .venv
```

### Step 2: Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the App

### Step 4: Start the Server

```bash
uvicorn app:app --reload
```

### Step 5: Open in Browser

Navigate to: **http://127.0.0.1:8000**

The web interface will open automatically.

## Usage

### 1. Upload Strategy File

Click "Choose File" under Strategy File and select your `.py` file containing a Backtrader strategy class.

**Requirements:**
- Must define a class that inherits from `bt.Strategy`
- Only `backtrader`, `pandas`, and `numpy` imports allowed
- No dangerous functions (`eval`, `exec`, `open`, etc.)

**Example:**
```python
import backtrader as bt

class MyStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SMA(period=20)

    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.close()
```

### 2. Upload CSV Data

Click "Choose File" under Data File and select your `.csv` file with market data.

**Required columns:**
- `Date` (YYYY-MM-DD format)
- `Open`
- `High`
- `Low`
- `Close`
- `Volume`

**Example CSV:**
```csv
Date,Open,High,Low,Close,Volume
2023-01-01,100.5,102.3,99.8,101.2,1000000
2023-01-02,101.0,103.5,100.5,102.8,1200000
2023-01-03,102.5,104.0,101.8,103.2,1100000
```

### 3. Configure Parameters

- **Initial Cash**: Starting capital for the backtest (default: $10,000)
- **Commission**: Trading commission as a percentage (default: 0.1%)

### 4. Run Backtest

Click "Run Backtest" to execute the strategy on the provided data.

### 5. View Results

The results section displays:

**Metrics:**
- Total Return %
- Net P&L ($)
- Win Rate %
- Max Drawdown %
- Total Trades
- Sharpe Ratio

**Visualizations:**
- Equity curve chart
- Trades summary

## Sample Files

Click the "Download Sample Strategy" or "Download Sample Data" buttons to get example files:

- **sample_strategy.py**: Simple moving average crossover strategy
- **sample_data.csv**: Example OHLCV market data

## Security

The app validates uploaded strategy code to prevent:

❌ Forbidden imports (os, sys, subprocess, socket, requests, etc.)
❌ Dangerous functions (eval, exec, compile, open)
❌ File system access
❌ Network operations

✅ Only allows: backtrader, pandas, numpy, and basic Python built-ins

## API Endpoints

- `GET /` - Main web interface
- `POST /api/backtest` - Run backtest (multipart form data)
- `GET /api/sample-strategy` - Download sample strategy file
- `GET /api/sample-data` - Download sample CSV data

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
uvicorn app:app --reload --port 8001
```

### Strategy Not Found Error

Make sure your strategy file contains a class that inherits from `bt.Strategy`:

```python
class YourStrategy(bt.Strategy):
    pass
```

### CSV Format Error

Ensure your CSV has the required columns: `Date, Open, High, Low, Close, Volume`

### Import Error

Only `backtrader`, `pandas`, and `numpy` imports are allowed. Remove any other imports from your strategy file.

## File Structure

```
backtest_app/
├── app.py                          # FastAPI server
├── backtest_runner.py              # Backtest execution engine
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── static/
│   ├── index.html                  # Web interface
│   ├── app.js                      # Frontend JavaScript
│   └── styles.css                  # CSS styling
└── strategy_templates/
    └── sample_strategy.py          # Example strategy
```

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Backtrader**: Backtesting engine
- **Pandas**: Data manipulation
- **Python-multipart**: File upload handling

## License

This project is provided as-is for educational and testing purposes.

## Support

For issues or questions, check that:
1. Virtual environment is activated
2. All dependencies are installed (`pip install -r requirements.txt`)
3. Strategy file follows the required format
4. CSV data has the required columns
5. Port 8000 is not already in use

---

**Happy Backtesting! 📈**
