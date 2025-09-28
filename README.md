# Grant Henning Value & Momentum Trading System

[![Trading Analysis](https://github.com/your-username/henning-trading-system/actions/workflows/trading-analysis.yml/badge.svg)](https://github.com/your-username/henning-trading-system/actions/workflows/trading-analysis.yml)

An automated trading system for Indian Nifty stocks based on Grant Henning's "The Value and Momentum Trader" methodology. This system implements three core strategies with 10-year backtesting and sends daily email reports.

## 🎯 Features

- **Three Trading Strategies**: Technical-Momentum, Fundamental-Value, and Hybrid approaches
- **Automated Daily Analysis**: Runs every weekday at 10:00 AM IST
- **Email Reports**: Detailed HTML reports with stock picks and analysis
- **10-Year Backtesting**: Historical performance analysis
- **Risk Management**: Built-in stop-losses and position sizing
- **Indian Market Focus**: Optimized for NSE/BSE stocks

## 📊 Strategies Implemented

### 1. Technical-Momentum System
- **Focus**: High momentum stocks with strong price trends
- **Indicators**: Cumulative Momentum Index (CMI), Price Movement Index (PMI)
- **Timeframe**: Daily with monthly rebalancing
- **Assets**: Nifty 50 stocks

### 2. Fundamental-Value System  
- **Focus**: Undervalued stocks with strong fundamentals
- **Metrics**: PE ratio, ROE, Debt/Equity, Cash flow
- **Timeframe**: Weekly analysis with quarterly rebalancing
- **Assets**: Nifty 200 stocks

### 3. Hybrid Technical-Fundamental System
- **Focus**: Best combination of momentum and value
- **Approach**: 60% technical + 40% fundamental weighting
- **Timeframe**: Daily monitoring with bi-weekly rebalancing
- **Assets**: Nifty 100 + Midcap 50

## 🚀 Setup Instructions

### 1. Repository Setup
```bash
git clone https://github.com/your-username/henning-trading-system.git
cd henning-trading-system
```

### 2. GitHub Secrets Configuration
Go to your repository Settings → Secrets and variables → Actions, and add:

- `SENDER_EMAIL`: Your Gmail address (e.g., youremail@gmail.com)
- `SENDER_APP_PASSWORD`: Gmail App Password (not regular password)

### 3. Gmail App Password Setup
1. Enable 2-Factor Authentication on your Gmail account
2. Go to Google Account Settings → Security → 2-Step Verification → App passwords
3. Generate an app password for "Mail"
4. Use this password in `SENDER_APP_PASSWORD` secret

### 4. Schedule Configuration
The system runs automatically every weekday at 10:00 AM New Delhi Time.
To modify the schedule, edit the cron expression in `.github/workflows/trading-analysis.yml`:

```yaml
schedule:
  - cron: '30 4 * * 1-5'  # 10:00 AM IST (04:30 AM UTC)
```

## 📈 Grant Henning's Core Indicators

### Momentum Indicators
- **1-Month Momentum Index**: `1M_Return - (500 * |Pct_From_High|)`
- **12-Month Momentum Index**: `12M_Return - (2000 * |Pct_From_High|)`
- **Cumulative Momentum Index (CMI)**: Sum of 1M and 12M momentum
- **Price Movement Index (PMI)**: Advanced momentum measure with volume

### Value Indicators
- **PE Ratio Analysis**: Below sector average
- **Book Value Assessment**: P/B ratio evaluation
- **Earnings Growth**: 3-year EPS growth consistency
- **Cash Flow Analysis**: Free cash flow generation
- **Balance Sheet Strength**: Debt/equity and current ratios

## 📧 Email Report Features

Daily reports include:
- **Top 10 picks** from each strategy
- **Entry prices** with stop-loss and target levels
- **Technical and fundamental scores**
- **10-year backtesting performance**
- **Risk metrics** and position sizing guidance

## 📊 Backtesting Results

The system performs 10-year historical backtesting with metrics:
- **Total Return**: Absolute performance
- **CAGR**: Compound annual growth rate
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Peak-to-trough decline
- **Win Rate**: Percentage of profitable trades

## 🔧 Local Development

### Run Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export SENDER_EMAIL="your_email@gmail.com"
export SENDER_APP_PASSWORD="your_app_password"

# Run analysis
python henning_trading_system.py
```

### Test Without Email
Comment out the email sending line in `henning_trading_system.py`:
```python
# system.send_email_report(html_report)  # Comment this line
```

## 📋 File Structure

```
henning-trading-system/
├── .github/workflows/
│   └── trading-analysis.yml       # GitHub Actions workflow
├── henning_trading_system.py      # Main trading system
├── main.py                        # Execution script
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── output files:
    ├── technical_momentum_picks.csv
    ├── fundamental_value_picks.csv
    ├── hybrid_strategy_picks.csv
    └── henning_strategies_config.json
```

## ⚠️ Risk Disclaimer

This system is for educational purposes based on Grant Henning's statistical trading methods. 

**Important Warnings:**
- Past performance does not guarantee future results
- All trading involves substantial risk of loss
- Use proper position sizing and risk management
- Consult a financial advisor before making investment decisions
- The author is not responsible for any trading losses

## 📚 Based on

"The Value and Momentum Trader: Dynamic Stock Selection Models to Beat the Market" by Grant Henning (Wiley Trading Series)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For issues or questions:
- Open a GitHub issue
- Check the troubleshooting section below

## 🔧 Troubleshooting

### Common Issues

**Email not sending:**
- Verify Gmail App Password is correct
- Check GitHub Secrets are properly set
- Ensure 2FA is enabled on Gmail account

**Analysis failing:**
- Check if yfinance API is accessible
- Verify stock symbols are correct
- Ensure sufficient historical data available

**GitHub Action not running:**
- Check cron syntax is correct
- Verify workflow file is in `.github/workflows/`
- Check GitHub Actions tab for error messages

### Manual Trigger
You can manually trigger the analysis:
1. Go to Actions tab in your repository
2. Select "Grant Henning Trading System - Daily Analysis"
3. Click "Run workflow"

## 📊 Performance Monitoring

The system automatically tracks:
- Daily analysis success/failure rates
- Email delivery status
- Strategy performance metrics
- Backtesting accuracy

Results are saved as artifacts and can be downloaded from the Actions tab.
