// Handle form submission
document.getElementById('backtestForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Hide previous results/errors
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';

    // Show loading spinner
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('runBtn').disabled = true;

    try {
        // Get form data
        const formData = new FormData();
        const strategyFile = document.getElementById('strategyFile').files[0];
        const dataFile = document.getElementById('dataFile').files[0];
        const initialCash = parseFloat(document.getElementById('initialCash').value);
        const commission = parseFloat(document.getElementById('commission').value) / 100; // Convert % to decimal

        formData.append('strategy_file', strategyFile);
        formData.append('data_csv', dataFile);
        formData.append('initial_cash', initialCash);
        formData.append('commission', commission);

        // Send request
        const response = await fetch('/api/backtest', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        // Hide loading spinner
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('runBtn').disabled = false;

        if (data.success) {
            displayResults(data);
        } else {
            displayError(data);
        }

    } catch (error) {
        // Hide loading spinner
        document.getElementById('loadingSpinner').style.display = 'none';
        document.getElementById('runBtn').disabled = false;

        displayError({
            error: 'Failed to connect to server',
            traceback: error.toString()
        });
    }
});

// Display results
function displayResults(data) {
    const metrics = data.metrics;

    // Update metrics
    document.getElementById('totalReturn').textContent = `${metrics.total_return_pct >= 0 ? '+' : ''}${metrics.total_return_pct}%`;
    document.getElementById('totalReturn').className = `metric-value ${metrics.total_return_pct >= 0 ? 'positive' : 'negative'}`;

    document.getElementById('netPnl').textContent = `$${metrics.net_pnl.toLocaleString()}`;
    document.getElementById('netPnl').className = `metric-value ${metrics.net_pnl >= 0 ? 'positive' : 'negative'}`;

    document.getElementById('winRate').textContent = `${metrics.win_rate_pct}%`;
    document.getElementById('maxDrawdown').textContent = `${metrics.max_drawdown_pct}%`;
    document.getElementById('totalTrades').textContent = metrics.total_trades;
    document.getElementById('sharpeRatio').textContent = metrics.sharpe_ratio;

    // Display trades summary
    const tradesHtml = `
        <p><strong>Initial Cash:</strong> $${metrics.initial_cash.toLocaleString()}</p>
        <p><strong>Final Value:</strong> $${metrics.final_value.toLocaleString()}</p>
    `;
    document.getElementById('tradesDetails').innerHTML = tradesHtml;

    // Draw equity curve
    drawEquityCurve(data.equity_curve);

    // Show results section
    document.getElementById('resultsSection').style.display = 'block';

    // Scroll to results
    document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });
}

// Display error
function displayError(data) {
    document.getElementById('errorMessage').textContent = data.error || 'Unknown error';
    document.getElementById('errorTraceback').textContent = data.traceback || '';
    document.getElementById('errorSection').style.display = 'block';

    // Scroll to error
    document.getElementById('errorSection').scrollIntoView({ behavior: 'smooth' });
}

// Draw equity curve chart
function drawEquityCurve(equityCurve) {
    const canvas = document.getElementById('equityChart');
    const ctx = canvas.getContext('2d');

    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = 300;

    const width = canvas.width;
    const height = canvas.height;
    const padding = 40;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Find min and max values
    const maxValue = Math.max(...equityCurve);
    const minValue = Math.min(...equityCurve);
    const valueRange = maxValue - minValue;

    // Draw axes
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw equity curve
    ctx.strokeStyle = '#2563eb';
    ctx.lineWidth = 2;
    ctx.beginPath();

    equityCurve.forEach((value, index) => {
        const x = padding + (index / (equityCurve.length - 1)) * (width - 2 * padding);
        const y = height - padding - ((value - minValue) / valueRange) * (height - 2 * padding);

        if (index === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });

    ctx.stroke();

    // Draw labels
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';

    // Y-axis labels
    ctx.fillText(`$${maxValue.toLocaleString()}`, padding - 5, padding + 5);
    ctx.fillText(`$${minValue.toLocaleString()}`, padding - 5, height - padding + 5);

    // X-axis labels
    ctx.textAlign = 'center';
    ctx.fillText('Start', padding, height - padding + 20);
    ctx.fillText('End', width - padding, height - padding + 20);
}

// Download sample strategy
async function downloadSampleStrategy() {
    try {
        const response = await fetch('/api/sample-strategy');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample_strategy.py';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert('Failed to download sample strategy');
    }
}

// Download sample data
async function downloadSampleData() {
    try {
        const response = await fetch('/api/sample-data');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample_data.csv';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        alert('Failed to download sample data');
    }
}
