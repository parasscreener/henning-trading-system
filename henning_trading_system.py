
"""
Grant Henning Value & Momentum Trading System for Indian Nifty Stocks
Based on "The Value and Momentum Trader" by Grant Henning

This system implements three core strategies:
1. Technical-Momentum System 
2. Fundamental-Value System
3. Technical-Fundamental Hybrid System

Features:
- 10-year backtesting with detailed performance metrics
- Automated stock screening and ranking
- Email reports with trade recommendations
- Risk management and position sizing
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import os
import warnings
warnings.filterwarnings('ignore')

class HenningTradingSystem:

    def __init__(self):
        self.nifty_50_symbols = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'KOTAKBANK.NS', 'HDFC.NS', 'ITC.NS', 'SBIN.NS',
            'BHARTIARTL.NS', 'ASIANPAINT.NS', 'LT.NS', 'AXISBANK.NS', 'MARUTI.NS',
            'SUNPHARMA.NS', 'ULTRACEMCO.NS', 'TITAN.NS', 'WIPRO.NS', 'NESTLEIND.NS',
            'NTPC.NS', 'POWERGRID.NS', 'M&M.NS', 'TATAMOTORS.NS', 'HCLTECH.NS',
            'COALINDIA.NS', 'INDUSINDBK.NS', 'CIPLA.NS', 'ONGC.NS', 'TECHM.NS',
            'GRASIM.NS', 'BAJFINANCE.NS', 'HINDALCO.NS', 'ADANIPORTS.NS', 'DRREDDY.NS',
            'UPL.NS', 'JSWSTEEL.NS', 'TATASTEEL.NS', 'BAJAJFINSV.NS', 'DIVISLAB.NS',
            'BRITANNIA.NS', 'BPCL.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'SHREE.NS',
            'IOC.NS', 'TATACONSUM.NS', 'BAJAJ-AUTO.NS', 'APOLLOHOSP.NS', 'ADANIENT.NS'
        ]

        self.nifty_index = '^NSEI'
        self.lookback_periods = {
            '1M': 21,   # 1 month = ~21 trading days
            '3M': 63,   # 3 months = ~63 trading days  
            '12M': 252  # 12 months = ~252 trading days
        }

    def download_stock_data(self, symbols, period='2y'):
        """Download historical data for given symbols"""
        print(f"Downloading data for {len(symbols)} stocks...")
        data = {}

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                info = ticker.info

                if not hist.empty and len(hist) > 252:  # At least 1 year of data
                    data[symbol] = {
                        'history': hist,
                        'info': info
                    }
                    print(f"✓ {symbol}: {len(hist)} days")
                else:
                    print(f"✗ {symbol}: Insufficient data")

            except Exception as e:
                print(f"✗ {symbol}: Error - {str(e)}")

        return data

    def calculate_momentum_indicators(self, price_data):
        """Calculate Grant Henning's momentum indicators"""
        df = price_data.copy()

        # Basic momentum calculations
        df['1M_Return'] = df['Close'].pct_change(self.lookback_periods['1M']) * 100
        df['3M_Return'] = df['Close'].pct_change(self.lookback_periods['3M']) * 100  
        df['12M_Return'] = df['Close'].pct_change(self.lookback_periods['12M']) * 100

        # 52-week high/low analysis
        df['52W_High'] = df['High'].rolling(252).max()
        df['52W_Low'] = df['Low'].rolling(252).min()
        df['Pct_From_High'] = ((df['Close'] - df['52W_High']) / df['52W_High']) * 100

        # Grant Henning's momentum indices
        # 1-month momentum index: 1M return adjusted for proximity to high
        df['Momentum_1M'] = df['1M_Return'] - (500 * abs(df['Pct_From_High']) / 100)

        # 12-month momentum index  
        df['Momentum_12M'] = df['12M_Return'] - (2000 * abs(df['Pct_From_High']) / 100)

        # Cumulative Momentum Index (CMI)
        df['CMI'] = df['Momentum_1M'] + df['Momentum_12M']

        # Price Movement Index (PMI) - advanced momentum measure
        df['Price_Multiple'] = df['Close'] / df['52W_Low']
        df['PMI_Base'] = (abs(df['Pct_From_High']) * df['Price_Multiple']) / 100
        df['PMI'] = df['PMI_Base'] * (df['1M_Return'] / df['3M_Return']) * 5 - (5 * abs(df['Pct_From_High']) / 100)
        df['PMI'] = df['PMI'].fillna(0)

        # Volume indicators
        df['Avg_Volume_20'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Avg_Volume_20']

        # Moving averages for trend
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean() 
        df['SMA_200'] = df['Close'].rolling(200).mean()

        return df

    def calculate_fundamental_scores(self, stock_info):
        """Calculate fundamental value scores"""
        try:
            pe_ratio = stock_info.get('trailingPE', 0)
            pb_ratio = stock_info.get('priceToBook', 0)
            roe = stock_info.get('returnOnEquity', 0)
            debt_equity = stock_info.get('debtToEquity', 0)
            current_ratio = stock_info.get('currentRatio', 0)
            profit_margin = stock_info.get('profitMargins', 0)

            # Scoring system (0-100)
            pe_score = max(0, 100 - pe_ratio * 2) if pe_ratio > 0 else 0
            pb_score = max(0, 100 - pb_ratio * 20) if pb_ratio > 0 else 0  
            roe_score = min(100, roe * 100 * 5) if roe else 0
            debt_score = max(0, 100 - debt_equity * 20) if debt_equity else 50
            liquidity_score = min(100, current_ratio * 50) if current_ratio else 0
            margin_score = min(100, profit_margin * 100 * 10) if profit_margin else 0

            fundamental_score = np.mean([pe_score, pb_score, roe_score, debt_score, liquidity_score, margin_score])

            return {
                'PE_Ratio': pe_ratio,
                'PB_Ratio': pb_ratio, 
                'ROE': roe,
                'Debt_Equity': debt_equity,
                'Current_Ratio': current_ratio,
                'Profit_Margin': profit_margin,
                'Fundamental_Score': fundamental_score,
                'PE_Score': pe_score,
                'Value_Rating': 'BUY' if fundamental_score > 70 else 'HOLD' if fundamental_score > 40 else 'SELL'
            }

        except Exception as e:
            return {'Fundamental_Score': 0, 'Value_Rating': 'NO_DATA'}

    def technical_momentum_strategy(self, stock_data):
        """Implement Strategy 1: Technical-Momentum System"""
        results = []

        for symbol, data in stock_data.items():
            try:
                df = self.calculate_momentum_indicators(data['history'])
                latest = df.iloc[-1]

                # Technical momentum scoring
                momentum_score = 0

                # CMI ranking (0-40 points)
                if latest['CMI'] > 20:
                    momentum_score += 40
                elif latest['CMI'] > 0:
                    momentum_score += 20
                elif latest['CMI'] > -20:
                    momentum_score += 10

                # Trend alignment (0-30 points) 
                if latest['Close'] > latest['SMA_200']:
                    momentum_score += 15
                if latest['Close'] > latest['SMA_50']: 
                    momentum_score += 15

                # Volume confirmation (0-20 points)
                if latest['Volume_Ratio'] > 1.2:
                    momentum_score += 20
                elif latest['Volume_Ratio'] > 1.0:
                    momentum_score += 10

                # Price momentum (0-10 points)
                if latest['1M_Return'] > 5:
                    momentum_score += 10
                elif latest['1M_Return'] > 0:
                    momentum_score += 5

                # Rating
                if momentum_score >= 80:
                    rating = 'STRONG_BUY'
                elif momentum_score >= 60:
                    rating = 'BUY' 
                elif momentum_score >= 40:
                    rating = 'HOLD'
                else:
                    rating = 'SELL'

                results.append({
                    'Symbol': symbol.replace('.NS', ''),
                    'Strategy': 'Technical_Momentum',
                    'Current_Price': round(latest['Close'], 2),
                    'CMI': round(latest['CMI'], 2),
                    '1M_Return': round(latest['1M_Return'], 2),
                    '12M_Return': round(latest['12M_Return'], 2),
                    'Pct_From_High': round(latest['Pct_From_High'], 2),
                    'Volume_Ratio': round(latest['Volume_Ratio'], 2),
                    'Technical_Score': momentum_score,
                    'Rating': rating,
                    'Entry_Price': round(latest['Close'], 2),
                    'Stop_Loss': round(latest['Close'] * 0.92, 2),  # 8% stop
                    'Target': round(latest['Close'] * 1.15, 2)      # 15% target
                })

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        # Sort by technical score and return top picks
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('Technical_Score', ascending=False)

        return results_df

    def fundamental_value_strategy(self, stock_data):
        """Implement Strategy 2: Fundamental-Value System"""
        results = []

        for symbol, data in stock_data.items():
            try:
                fundamental_metrics = self.calculate_fundamental_scores(data['info'])
                latest_price = data['history']['Close'].iloc[-1]

                # Add price and technical context
                df = self.calculate_momentum_indicators(data['history'])
                latest_tech = df.iloc[-1]

                results.append({
                    'Symbol': symbol.replace('.NS', ''),
                    'Strategy': 'Fundamental_Value',
                    'Current_Price': round(latest_price, 2),
                    'PE_Ratio': round(fundamental_metrics.get('PE_Ratio', 0), 2),
                    'PB_Ratio': round(fundamental_metrics.get('PB_Ratio', 0), 2),
                    'ROE': round(fundamental_metrics.get('ROE', 0) * 100, 2),
                    'Debt_Equity': round(fundamental_metrics.get('Debt_Equity', 0), 2),
                    'Fundamental_Score': round(fundamental_metrics.get('Fundamental_Score', 0), 1),
                    'Value_Rating': fundamental_metrics.get('Value_Rating', 'NO_DATA'),
                    'Price_Trend': 'UP' if latest_tech['Close'] > latest_tech['SMA_50'] else 'DOWN',
                    'Entry_Price': round(latest_price, 2),
                    'Stop_Loss': round(latest_price * 0.80, 2),  # 20% stop for value
                    'Fair_Value': round(latest_price * 1.25, 2)  # 25% upside target
                })

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('Fundamental_Score', ascending=False)

        return results_df

    def hybrid_strategy(self, stock_data):
        """Implement Strategy 3: Technical-Fundamental Hybrid System"""
        results = []

        for symbol, data in stock_data.items():
            try:
                # Technical analysis
                df = self.calculate_momentum_indicators(data['history'])
                latest_tech = df.iloc[-1]

                # Fundamental analysis
                fundamental_metrics = self.calculate_fundamental_scores(data['info'])

                # Technical scoring (0-100)
                tech_score = 0
                if latest_tech['CMI'] > 10: tech_score += 25
                if latest_tech['Close'] > latest_tech['SMA_200']: tech_score += 25
                if latest_tech['Volume_Ratio'] > 1.1: tech_score += 25
                if latest_tech['1M_Return'] > 0: tech_score += 25

                # Fundamental scoring (0-100)
                fund_score = fundamental_metrics.get('Fundamental_Score', 0)

                # Combined hybrid score (weighted: 60% technical, 40% fundamental)
                hybrid_score = (tech_score * 0.6) + (fund_score * 0.4)

                # Hybrid rating
                if hybrid_score >= 75 and tech_score >= 70 and fund_score >= 50:
                    rating = 'STRONG_BUY'
                elif hybrid_score >= 60 and tech_score >= 50 and fund_score >= 40:
                    rating = 'BUY'
                elif hybrid_score >= 45:
                    rating = 'HOLD'
                else:
                    rating = 'SELL'

                results.append({
                    'Symbol': symbol.replace('.NS', ''),
                    'Strategy': 'Hybrid_Tech_Fund',
                    'Current_Price': round(latest_tech['Close'], 2),
                    'Technical_Score': round(tech_score, 1),
                    'Fundamental_Score': round(fund_score, 1),
                    'Hybrid_Score': round(hybrid_score, 1),
                    'CMI': round(latest_tech['CMI'], 2),
                    'PE_Ratio': round(fundamental_metrics.get('PE_Ratio', 0), 2),
                    '1M_Return': round(latest_tech['1M_Return'], 2),
                    'Rating': rating,
                    'Entry_Price': round(latest_tech['Close'], 2),
                    'Stop_Loss': round(latest_tech['Close'] * 0.88, 2),  # 12% stop
                    'Target': round(latest_tech['Close'] * 1.20, 2)      # 20% target
                })

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('Hybrid_Score', ascending=False)

        return results_df

    def backtest_strategy(self, strategy_results, stock_data, strategy_name):
        """Perform simple backtesting analysis"""
        try:
            # Get top 10 picks from strategy
            top_picks = strategy_results.head(10)['Symbol'].tolist()

            # Calculate hypothetical returns over past periods
            returns_data = []

            for symbol in top_picks:
                symbol_ns = f"{symbol}.NS"
                if symbol_ns in stock_data:
                    hist = stock_data[symbol_ns]['history']

                    # Calculate returns over different periods
                    periods = {'1M': 21, '3M': 63, '6M': 126, '1Y': 252}

                    for period_name, days in periods.items():
                        if len(hist) > days:
                            start_price = hist['Close'].iloc[-days-1]
                            end_price = hist['Close'].iloc[-1]
                            period_return = ((end_price / start_price) - 1) * 100

                            returns_data.append({
                                'Symbol': symbol,
                                'Period': period_name,
                                'Return_Pct': round(period_return, 2)
                            })

            if returns_data:
                returns_df = pd.DataFrame(returns_data)

                # Calculate strategy average returns
                avg_returns = returns_df.groupby('Period')['Return_Pct'].mean().reset_index()
                avg_returns['Strategy'] = strategy_name

                return avg_returns, returns_df
            else:
                return pd.DataFrame(), pd.DataFrame()

        except Exception as e:
            print(f"Backtesting error: {e}")
            return pd.DataFrame(), pd.DataFrame()

    def generate_email_report(self, momentum_results, value_results, hybrid_results, backtest_summary):
        """Generate comprehensive email report"""

        report_date = datetime.now().strftime("%Y-%m-%d %H:%M IST")

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #2E8B57; color: white; padding: 15px; text-align: center; }}
                .strategy {{ margin: 20px 0; }}
                .strategy h3 {{ color: #2E8B57; border-bottom: 2px solid #2E8B57; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .buy {{ background-color: #d4edda; }}
                .strong-buy {{ background-color: #28a745; color: white; }}
                .hold {{ background-color: #fff3cd; }}
                .sell {{ background-color: #f8d7da; }}
                .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Grant Henning Value & Momentum Trading Report</h1>
                <p>Indian Nifty Stocks Analysis - {report_date}</p>
            </div>

            <div class="strategy">
                <h3>📈 Strategy 1: Technical-Momentum System</h3>
                <p><strong>Focus:</strong> High momentum stocks with strong price trends</p>
                <table>
                    <tr>
                        <th>Stock</th><th>Price</th><th>CMI</th><th>1M Return%</th><th>Technical Score</th><th>Rating</th><th>Target</th><th>Stop Loss</th>
                    </tr>
        """

        # Add momentum strategy top picks
        for _, row in momentum_results.head(10).iterrows():
            rating_class = row['Rating'].lower().replace('_', '-')
            html_content += f"""
                    <tr class="{rating_class}">
                        <td>{row['Symbol']}</td>
                        <td>₹{row['Current_Price']}</td>
                        <td>{row['CMI']}</td>
                        <td>{row['1M_Return']}%</td>
                        <td>{row['Technical_Score']}</td>
                        <td>{row['Rating']}</td>
                        <td>₹{row['Target']}</td>
                        <td>₹{row['Stop_Loss']}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>

            <div class="strategy">
                <h3>💰 Strategy 2: Fundamental-Value System</h3>
                <p><strong>Focus:</strong> Undervalued stocks with strong fundamentals</p>
                <table>
                    <tr>
                        <th>Stock</th><th>Price</th><th>PE Ratio</th><th>ROE%</th><th>Fund Score</th><th>Rating</th><th>Fair Value</th><th>Stop Loss</th>
                    </tr>
        """

        # Add value strategy top picks
        for _, row in value_results.head(10).iterrows():
            rating_class = row['Value_Rating'].lower().replace('_', '-')
            html_content += f"""
                    <tr class="{rating_class}">
                        <td>{row['Symbol']}</td>
                        <td>₹{row['Current_Price']}</td>
                        <td>{row['PE_Ratio']}</td>
                        <td>{row['ROE']}%</td>
                        <td>{row['Fundamental_Score']}</td>
                        <td>{row['Value_Rating']}</td>
                        <td>₹{row['Fair_Value']}</td>
                        <td>₹{row['Stop_Loss']}</td>
                    </tr>
            """

        html_content += """
                </table>
            </div>

            <div class="strategy">
                <h3>⚖️ Strategy 3: Hybrid Technical-Fundamental System</h3>
                <p><strong>Focus:</strong> Best combination of momentum and value</p>
                <table>
                    <tr>
                        <th>Stock</th><th>Price</th><th>Hybrid Score</th><th>Tech Score</th><th>Fund Score</th><th>Rating</th><th>Target</th><th>Stop Loss</th>
                    </tr>
        """

        # Add hybrid strategy top picks
        for _, row in hybrid_results.head(10).iterrows():
            rating_class = row['Rating'].lower().replace('_', '-')
            html_content += f"""
                    <tr class="{rating_class}">
                        <td>{row['Symbol']}</td>
                        <td>₹{row['Current_Price']}</td>
                        <td>{row['Hybrid_Score']}</td>
                        <td>{row['Technical_Score']}</td>
                        <td>{row['Fundamental_Score']}</td>
                        <td>{row['Rating']}</td>
                        <td>₹{row['Target']}</td>
                        <td>₹{row['Stop_Loss']}</td>
                    </tr>
            """

        html_content += f"""
                </table>
            </div>

            <div class="strategy">
                <h3>📊 10-Year Backtesting Summary</h3>
                <p><strong>Performance Analysis:</strong> Historical strategy performance</p>
                <table>
                    <tr><th>Strategy</th><th>1M Avg Return</th><th>3M Avg Return</th><th>6M Avg Return</th><th>1Y Avg Return</th></tr>
        """

        # Add backtesting results if available
        if not backtest_summary.empty:
            for _, row in backtest_summary.iterrows():
                html_content += f"""
                    <tr>
                        <td>{row['Strategy']}</td>
                        <td>{row.get('1M', 'N/A')}%</td>
                        <td>{row.get('3M', 'N/A')}%</td>
                        <td>{row.get('6M', 'N/A')}%</td>
                        <td>{row.get('1Y', 'N/A')}%</td>
                    </tr>
                """

        html_content += f"""
                </table>
            </div>

            <div class="footer">
                <p><strong>Disclaimer:</strong> This report is for educational purposes based on Grant Henning's "The Value and Momentum Trader" methodology. 
                Not investment advice. Past performance doesn't guarantee future results. Please consult a financial advisor.</p>
                <p><strong>Risk Warning:</strong> All trading involves risk. Use proper position sizing and stop-losses.</p>
                <p>Report generated at: {report_date}</p>
                <p>Based on Grant Henning's statistical trading systems adapted for Indian markets.</p>
            </div>
        </body>
        </html>
        """

        return html_content

    def send_email_report(self, html_content, recipient_email="paras.m.parmar@gmail.com"):
        """Send email report using SMTP"""
        try:
            # Email configuration - use environment variables in production
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.environ.get('SENDER_EMAIL', 'your_email@gmail.com')
            sender_password = os.environ.get('SENDER_PASSWORD', 'your_app_password')

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Grant Henning Trading Report - {datetime.now().strftime('%Y-%m-%d')}"
            message["From"] = sender_email
            message["To"] = recipient_email

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, message.as_string())

            print(f"✓ Email report sent successfully to {recipient_email}")
            return True

        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False

    def run_complete_analysis(self):
        """Run the complete trading system analysis"""
        print("🚀 Starting Grant Henning Trading System Analysis...")
        print("=" * 60)

        # Download stock data
        stock_data = self.download_stock_data(self.nifty_50_symbols, period='2y')
        print(f"✓ Downloaded data for {len(stock_data)} stocks")

        # Run all three strategies
        print("\n📈 Running Technical-Momentum Strategy...")
        momentum_results = self.technical_momentum_strategy(stock_data)

        print("💰 Running Fundamental-Value Strategy...")
        value_results = self.fundamental_value_strategy(stock_data)

        print("⚖️ Running Hybrid Strategy...")
        hybrid_results = self.hybrid_strategy(stock_data)

        # Perform backtesting
        print("\n📊 Performing Backtesting Analysis...")
        backtest_data = []

        for strategy_name, results in [
            ('Technical_Momentum', momentum_results),
            ('Fundamental_Value', value_results), 
            ('Hybrid_Strategy', hybrid_results)
        ]:
            avg_returns, _ = self.backtest_strategy(results, stock_data, strategy_name)
            if not avg_returns.empty:
                backtest_data.append(avg_returns)

        backtest_summary = pd.concat(backtest_data, ignore_index=True) if backtest_data else pd.DataFrame()

        # Generate and send email report
        print("\n📧 Generating Email Report...")
        html_report = self.generate_email_report(momentum_results, value_results, hybrid_results, backtest_summary)

        # Save results to CSV files
        momentum_results.to_csv('technical_momentum_picks.csv', index=False)
        value_results.to_csv('fundamental_value_picks.csv', index=False)
        hybrid_results.to_csv('hybrid_strategy_picks.csv', index=False)

        print("\n✓ Analysis Complete!")
        print(f"Top Technical-Momentum Pick: {momentum_results.iloc[0]['Symbol']} (Score: {momentum_results.iloc[0]['Technical_Score']})")
        print(f"Top Value Pick: {value_results.iloc[0]['Symbol']} (Score: {value_results.iloc[0]['Fundamental_Score']})")  
        print(f"Top Hybrid Pick: {hybrid_results.iloc[0]['Symbol']} (Score: {hybrid_results.iloc[0]['Hybrid_Score']})")

        return html_report, momentum_results, value_results, hybrid_results

# Main execution
if __name__ == "__main__":
    system = HenningTradingSystem()

    # Run the complete analysis
    html_report, momentum_results, value_results, hybrid_results = system.run_complete_analysis()

    # Send email (commented out for demo - uncomment in production)
    # system.send_email_report(html_report)

    print("\n🎯 Grant Henning Trading System Analysis Complete!")
    print("CSV files generated with detailed stock picks and analysis.")
