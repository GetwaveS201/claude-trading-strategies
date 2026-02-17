"""
Simple Backtest Web App
FastAPI server that runs backtests on uploaded strategy files
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
import json
from pathlib import Path
from backtest_runner import run_backtest, validate_strategy_code

app = FastAPI(title="Backtest App")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    html_path = Path("static/index.html")
    if not html_path.exists():
        return HTMLResponse("<h1>Error: index.html not found</h1>", status_code=500)
    return FileResponse(html_path)


@app.post("/api/backtest")
async def backtest(
    strategy_file: UploadFile = File(...),
    data_csv: UploadFile = File(...),
    initial_cash: float = Form(10000),
    commission: float = Form(0.001)  # 0.1%
):
    """
    Run backtest on uploaded strategy and data

    Returns:
        JSON with metrics and equity curve
    """

    try:
        # Read uploaded files
        strategy_code = (await strategy_file.read()).decode('utf-8')
        csv_data = (await data_csv.read()).decode('utf-8')

        # Validate strategy code for safety
        is_valid, error_msg = validate_strategy_code(strategy_code)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid strategy: {error_msg}")

        # Run backtest
        results = run_backtest(
            strategy_code=strategy_code,
            csv_data=csv_data,
            initial_cash=initial_cash,
            commission=commission
        )

        return JSONResponse(content=results)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest error: {str(e)}")


@app.get("/api/sample-strategy")
async def get_sample_strategy():
    """Download sample strategy file"""
    sample_path = Path("strategy_templates/sample_strategy.py")
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="Sample strategy not found")

    return FileResponse(
        path=sample_path,
        media_type='text/plain',
        filename='sample_strategy.py'
    )


@app.get("/api/sample-data")
async def get_sample_data():
    """Download sample CSV data"""
    # Generate sample data
    import pandas as pd
    import tempfile

    # Create 2 years of sample data
    dates = pd.date_range(start='2022-01-01', end='2024-01-01', freq='D')

    # Add some realistic price movement
    import random
    random.seed(42)

    prices = []
    current_price = 100
    for i in range(len(dates)):
        change = random.uniform(-2, 2)
        current_price += change
        prices.append(current_price)

    data = {
        'Date': dates.strftime('%Y-%m-%d'),
        'Open': [p * random.uniform(0.99, 1.00) for p in prices],
        'High': [p * random.uniform(1.00, 1.02) for p in prices],
        'Low': [p * random.uniform(0.98, 0.99) for p in prices],
        'Close': prices,
        'Volume': [random.randint(500000, 2000000) for _ in range(len(dates))]
    }
    df = pd.DataFrame(data)

    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
    df.to_csv(temp_file.name, index=False)
    temp_file.close()

    return FileResponse(
        path=temp_file.name,
        media_type='text/csv',
        filename='sample_data.csv'
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
