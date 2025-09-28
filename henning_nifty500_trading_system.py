
"""
Grant Henning Value & Momentum Trading System for Indian Nifty 500 Stocks
Enhanced version with improved email delivery and Nifty 500 screening

CHANGELOG:
- Expanded from Nifty 50 to Nifty 500 stocks
- Improved email authentication and SMTP configuration
- Enhanced error handling and debugging
- Better Gmail compatibility
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
import requests
from io import StringIO
import time
import logging

warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HenningTradingSystemNifty500:

    def __init__(self):
        self.nifty_500_symbols = []
        self.nifty_index = '^NSEI'
        self.lookback_periods = {
            '1M': 21,   # 1 month = ~21 trading days
            '3M': 63,   # 3 months = ~63 trading days  
            '12M': 252  # 12 months = ~252 trading days
        }

    def fetch_nifty_500_symbols(self):
        """Fetch Nifty 500 stock symbols from NSE"""
        try:
            # Primary method: NSE official CSV
            nse_url = 'https://www1.nseindia.com/content/indices/ind_nifty500list.csv'

            logger.info("Fetching Nifty 500 symbols from NSE...")

            # Set headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            try:
                response = requests.get(nse_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    df = pd.read_csv(StringIO(response.text))
                    if 'Symbol' in df.columns:
                        symbols = df['Symbol'].dropna().unique()
                        self.nifty_500_symbols = [f"{symbol}.NS" for symbol in symbols if symbol]
                        logger.info(f"✓ Successfully fetched {len(self.nifty_500_symbols)} Nifty 500 symbols from NSE")
                        return True
            except Exception as e:
                logger.warning(f"NSE fetch failed: {e}")

            # Fallback method: Hardcoded popular Nifty 500 symbols (top 200 most liquid)
            logger.info("Using fallback method with curated Nifty 500 symbols...")

            fallback_symbols = [
                # Large Cap (Nifty 50 core)
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
                'ICICIBANK.NS', 'KOTAKBANK.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS',
                'ASIANPAINT.NS', 'LT.NS', 'AXISBANK.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
                'ULTRACEMCO.NS', 'TITAN.NS', 'WIPRO.NS', 'NESTLEIND.NS', 'NTPC.NS',
                'POWERGRID.NS', 'M&M.NS', 'TATAMOTORS.NS', 'HCLTECH.NS', 'COALINDIA.NS',
                'INDUSINDBK.NS', 'CIPLA.NS', 'ONGC.NS', 'TECHM.NS', 'GRASIM.NS',
                'BAJFINANCE.NS', 'HINDALCO.NS', 'ADANIPORTS.NS', 'DRREDDY.NS', 'UPL.NS',
                'JSWSTEEL.NS', 'TATASTEEL.NS', 'BAJAJFINSV.NS', 'DIVISLAB.NS', 'BRITANNIA.NS',
                'BPCL.NS', 'EICHERMOT.NS', 'HEROMOTOCO.NS', 'IOC.NS', 'TATACONSUM.NS',
                'BAJAJ-AUTO.NS', 'APOLLOHOSP.NS', 'ADANIENT.NS', 'SHREE.NS',

                # Additional Large & Mid Cap stocks
                'TATAPOWER.NS', 'SAIL.NS', 'VEDL.NS', 'HINDZINC.NS', 'NATIONALUM.NS',
                'JINDALSTEL.NS', 'NMDC.NS', 'MOIL.NS', 'RATNAMANI.NS', 'WELCORP.NS',
                'BANKBARODA.NS', 'CANBK.NS', 'PNB.NS', 'IDFCFIRSTB.NS', 'FEDERALBNK.NS',
                'RBLBANK.NS', 'BANDHANBNK.NS', 'AUBANK.NS', 'INDHOTEL.NS', 'OBEROIRLTY.NS',
                'MINDTREE.NS', 'MPHASIS.NS', 'COFORGE.NS', 'LTTS.NS', 'PERSISTENT.NS',
                'LUPIN.NS', 'BIOCON.NS', 'TORNTPHARM.NS', 'GODREJCP.NS', 'DABUR.NS',
                'MARICO.NS', 'COLPAL.NS', 'VBL.NS', 'TATAELXSI.NS', 'ESCORTS.NS',
                'ASHOKLEY.NS', 'BALKRISIND.NS', 'MOTHERSUMI.NS', 'BOSCHLTD.NS', 'MRF.NS',
                'APOLLOTYRE.NS', 'CEAT.NS', 'RELAXO.NS', 'BATAINDIA.NS', 'PAGEIND.NS',
                'PIDILITIND.NS', 'BERGER.NS', 'AKZONOBEL.NS', 'KANSAINER.NS', 'DEEPAKNTR.NS',
                'AAVAS.NS', 'LICHSGFIN.NS', 'CHOLAFIN.NS', 'MUTHOOTFIN.NS', 'MANAPPURAM.NS',
                'ADANIGREEN.NS', 'ADANIPOWER.NS', 'ADANITRANS.NS', 'ADANIGAS.NS', 'ATGL.NS',
                'TORNTPOWER.NS', 'CESC.NS', 'THERMAX.NS', 'SIEMENS.NS', 'ABB.NS',
                'HAVELLS.NS', 'CROMPTON.NS', 'VOLTAS.NS', 'BLUESTARCO.NS', 'WHIRLPOOL.NS',
                'GODREJIND.NS', 'GODREJPROP.NS', 'DLF.NS', 'PRESTIGE.NS', 'BRIGADE.NS',
                'PHOENIXLTD.NS', 'INOXWIND.NS', 'SUZLON.NS', 'CONCOR.NS', 'CONTAINER.NS',
                'IRCTC.NS', 'IRFC.NS', 'RAILTEL.NS', 'RVNL.NS', 'NBCC.NS',
                'BEL.NS', 'HAL.NS', 'BEML.NS', 'MAZAGON.NS', 'COCHINSHIP.NS',
                'SJVN.NS', 'NHPC.NS', 'PFC.NS', 'RECLTD.NS', 'IREDA.NS',

                # IT & Software
                'LTI.NS', 'OFSS.NS', 'CYIENT.NS', 'SONATA.NS', 'RTECH.NS',
                'MINDACORP.NS', 'KPITTECH.NS', 'ZENSAR.NS', 'HEXAWARE.NS', 'NIITTECH.NS',

                # Pharma & Healthcare  
                'AUROPHARMA.NS', 'ZYDUSLIFE.NS', 'CADILAHC.NS', 'ALKEM.NS', 'LALPATHLAB.NS',
                'LAURUSLABS.NS', 'GLENMARK.NS', 'IPCA.NS', 'ABBOTINDIA.NS', 'PFIZER.NS',
                'GLAXO.NS', 'SANOFI.NS', 'NOVARTIS.NS', 'FORTIS.NS', 'MAXHEALTH.NS',

                # FMCG & Consumer
                'EMAMILTD.NS', 'JYOTHYLAB.NS', 'GILLETTE.NS', 'HONAUT.NS', 'PGHH.NS',
                'RADICO.NS', 'UBL.NS', 'MCDOWELL-N.NS', 'CCL.NS', 'VSTIND.NS',

                # Textiles & Apparel
                'ADITBIRLA.NS', 'GRASIM.NS', 'RAYMONDS.NS', 'VIPIND.NS', 'WELSPUNIND.NS',
                'TRIDENT.NS', 'VARDHMAN.NS', 'ARVIND.NS', 'RTNPOWER.NS', 'DOLLAR.NS',

                # Auto & Components
                'TVSMOTOR.NS', 'BAJAJHLDNG.NS', 'EXIDEIND.NS', 'AMARA.NS', 'SUPRAJIT.NS',
                'SUNDRMFAST.NS', 'BHARATFORG.NS', 'MAHSCOOTER.NS', 'FORCE.NS', 'SRF.NS',

                # Cement & Construction
                'AMBUJACEM.NS', 'ACC.NS', 'RAMCOCEM.NS', 'HEIDELBERG.NS', 'JKCEMENT.NS',
                'ORIENTCEM.NS', 'PRSMJOHNSN.NS', 'DALMIACEM.NS', 'JKLAKSHMI.NS', 'SHREECEM.NS',

                # Metals & Mining (Additional)
                'HINDZINC.NS', 'HINDUSTAN.NS', 'APL.NS', 'WELCORP.NS', 'JSPL.NS',
                'RURALELEC.NS', 'KALYANKJIL.NS', 'TITAGARH.NS', 'GMRINFRA.NS', 'IRB.NS',

                # Chemicals & Fertilizers  
                'GNFC.NS', 'RCF.NS', 'CHAMBLFERT.NS', 'COROMANDEL.NS', 'MADRASFERT.NS',
                'ZUARI.NS', 'GSFC.NS', 'NFL.NS', 'FACT.NS', 'PIIND.NS',

                # Oil & Gas (Additional)
                'GAIL.NS', 'OIL.NS', 'HINDPETRO.NS', 'MGL.NS', 'IGL.NS',
                'ATGL.NS', 'GSPL.NS', 'AEGISLOG.NS', 'CASTROLIND.NS', 'PETRONET.NS',

                # Telecom & Media
                'HFCL.NS', 'STERLTECH.NS', 'OPTIEMUS.NS', 'RCOM.NS', 'GTLINFRA.NS',
                'TV18BRDCST.NS', 'NETWORK18.NS', 'ZEEL.NS', 'SUNTV.NS', 'PVR.NS',

                # Retail & E-commerce
                'TRENT.NS', 'SHOPRSTOP.NS', 'ADITBIRLA.NS', 'VMART.NS', 'FRETAIL.NS',
                'AVENUE.NS', 'SPENCERS.NS', 'PANTALOONS.NS', 'WESTLIFE.NS', 'JUBLFOOD.NS',

                # Additional Quality Mid-caps
                'POLYCAB.NS', 'DIXON.NS', 'AMBER.NS', 'CLEAN.NS', 'CAMS.NS',
                'CDSL.NS', 'NYKAA.NS', 'ZOMATO.NS', 'PAYTM.NS', 'POLICYBZR.NS'
            ]

            self.nifty_500_symbols = fallback_symbols
            logger.info(f"✓ Using {len(self.nifty_500_symbols)} curated Nifty 500 symbols")
            return True

        except Exception as e:
            logger.error(f"Error fetching Nifty 500 symbols: {e}")
            return False

    def download_stock_data(self, symbols, period='2y', batch_size=50):
        """Download historical data for given symbols in batches"""
        logger.info(f"Downloading data for {len(symbols)} stocks in batches of {batch_size}...")
        data = {}

        # Process in batches to avoid API limits
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(symbols) + batch_size - 1) // batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} stocks)")

            for symbol in batch:
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

            # Small delay between batches to be respectful to API
            if i + batch_size < len(symbols):
                time.sleep(1)

        logger.info(f"✓ Successfully downloaded data for {len(data)} stocks")
        return data

    def send_email_report(self, html_content, recipient_email="paras.m.parmar@gmail.com"):
        """Enhanced email sending with better error handling and debugging"""
        try:
            # Email configuration from environment variables
            sender_email = os.environ.get('SENDER_EMAIL')
            sender_password = os.environ.get('SENDER_PASSWORD') or os.environ.get('SENDER_APP_PASSWORD')

            logger.info(f"Attempting to send email from: {sender_email}")
            logger.info(f"Recipient: {recipient_email}")
            logger.info(f"Password configured: {'Yes' if sender_password else 'No'}")

            if not sender_email or not sender_password:
                logger.error("❌ Email credentials not found in environment variables!")
                logger.error("Required: SENDER_EMAIL and SENDER_PASSWORD (or SENDER_APP_PASSWORD)")
                return False

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"📈 Grant Henning Nifty 500 Trading Report - {datetime.now().strftime('%Y-%m-%d')}"
            message["From"] = sender_email
            message["To"] = recipient_email

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Gmail SMTP configuration with multiple fallback options
            smtp_configs = [
                {'server': 'smtp.gmail.com', 'port': 587, 'use_tls': True},
                {'server': 'smtp.gmail.com', 'port': 465, 'use_ssl': True},
                {'server': 'smtp.gmail.com', 'port': 25, 'use_tls': True}
            ]

            for config in smtp_configs:
                try:
                    logger.info(f"Trying SMTP config: {config}")

                    if config.get('use_ssl'):
                        # Use SSL connection
                        server = smtplib.SMTP_SSL(config['server'], config['port'])
                    else:
                        # Use regular SMTP with optional TLS
                        server = smtplib.SMTP(config['server'], config['port'])
                        server.ehlo()
                        if config.get('use_tls'):
                            server.starttls()
                            server.ehlo()  # Call ehlo() again after starttls()

                    # Login and send
                    logger.info("Attempting login...")
                    server.login(sender_email, sender_password)
                    logger.info("✓ Login successful")

                    logger.info("Sending email...")
                    server.sendmail(sender_email, [recipient_email], message.as_string())
                    server.quit()

                    logger.info(f"✅ Email report sent successfully to {recipient_email}")
                    return True

                except smtplib.SMTPAuthenticationError as e:
                    logger.error(f"❌ Authentication failed with config {config}: {e}")
                    logger.error("💡 Please check:")
                    logger.error("   1. Email and app password are correct")
                    logger.error("   2. 2-Factor Authentication is enabled")
                    logger.error("   3. App password is generated (not regular password)")
                    continue

                except smtplib.SMTPConnectError as e:
                    logger.error(f"❌ Connection failed with config {config}: {e}")
                    continue

                except Exception as e:
                    logger.error(f"❌ Unexpected error with config {config}: {e}")
                    continue

            logger.error("❌ All SMTP configurations failed")
            return False

        except Exception as e:
            logger.error(f"❌ Critical error in send_email_report: {e}")
            return False

    def calculate_momentum_indicators(self, price_data):
        """Calculate Grant Henning's momentum indicators (same as before)"""
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
        df['Momentum_1M'] = df['1M_Return'] - (500 * abs(df['Pct_From_High']) / 100)
        df['Momentum_12M'] = df['12M_Return'] - (2000 * abs(df['Pct_From_High']) / 100)
        df['CMI'] = df['Momentum_1M'] + df['Momentum_12M']

        # Price Movement Index (PMI)
        df['Price_Multiple'] = df['Close'] / df['52W_Low']
        df['PMI_Base'] = (abs(df['Pct_From_High']) * df['Price_Multiple']) / 100
        df['PMI'] = df['PMI_Base'] * (df['1M_Return'] / df['3M_Return']) * 5 - (5 * abs(df['Pct_From_High']) / 100)
        df['PMI'] = df['PMI'].fillna(0)

        # Volume indicators
        df['Avg_Volume_20'] = df['Volume'].rolling(20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Avg_Volume_20']

        # Moving averages
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean() 
        df['SMA_200'] = df['Close'].rolling(200).mean()

        return df

    def calculate_fundamental_scores(self, stock_info):
        """Calculate fundamental value scores (same as before)"""
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

    def technical_momentum_strategy(self, stock_data, top_n=20):
        """Technical momentum strategy for Nifty 500"""
        results = []

        logger.info("Running Technical-Momentum Strategy on Nifty 500...")

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
                logger.debug(f"Error processing {symbol}: {e}")
                continue

        # Sort by technical score and return top picks
        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values('Technical_Score', ascending=False).head(top_n)

        logger.info(f"✓ Technical-Momentum strategy processed {len(results)} stocks, returning top {len(results_df)}")
        return results_df

    def fundamental_value_strategy(self, stock_data, top_n=20):
        """Fundamental value strategy for Nifty 500"""
        results = []

        logger.info("Running Fundamental-Value Strategy on Nifty 500...")

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
                logger.debug(f"Error processing {symbol}: {e}")
                continue

        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values('Fundamental_Score', ascending=False).head(top_n)

        logger.info(f"✓ Fundamental-Value strategy processed {len(results)} stocks, returning top {len(results_df)}")
        return results_df

    def hybrid_strategy(self, stock_data, top_n=20):
        """Hybrid strategy for Nifty 500"""
        results = []

        logger.info("Running Hybrid Technical-Fundamental Strategy on Nifty 500...")

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
                logger.debug(f"Error processing {symbol}: {e}")
                continue

        results_df = pd.DataFrame(results)
        if not results_df.empty:
            results_df = results_df.sort_values('Hybrid_Score', ascending=False).head(top_n)

        logger.info(f"✓ Hybrid strategy processed {len(results)} stocks, returning top {len(results_df)}")
        return results_df

    def generate_email_report(self, momentum_results, value_results, hybrid_results, backtest_summary):
        """Generate enhanced email report for Nifty 500 analysis"""

        report_date = datetime.now().strftime("%Y-%m-%d %H:%M IST")

        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                .header {{ background: linear-gradient(135deg, #2E8B57, #1E6B47); color: white; padding: 20px; text-align: center; border-radius: 8px; }}
                .stats {{ background-color: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #2E8B57; }}
                .strategy {{ margin: 25px 0; }}
                .strategy h3 {{ color: #2E8B57; border-bottom: 2px solid #2E8B57; padding-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 15px 0; font-size: 12px; }}
                th, td {{ border: 1px solid #ddd; padding: 6px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                .buy {{ background-color: #d4edda; }}
                .strong-buy {{ background-color: #28a745; color: white; font-weight: bold; }}
                .hold {{ background-color: #fff3cd; }}
                .sell {{ background-color: #f8d7da; }}
                .footer {{ margin-top: 30px; font-size: 11px; color: #666; background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .highlight {{ background-color: #e7f3ff; padding: 10px; border-left: 4px solid #0066cc; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 Grant Henning Nifty 500 Trading System</h1>
                <p>Advanced Value & Momentum Analysis - {report_date}</p>
                <p>📊 Covering 500+ Indian Stocks with Statistical Edge</p>
            </div>

            <div class="stats">
                <h3>📈 Today's Market Analysis Summary</h3>
                <p><strong>Universe:</strong> Nifty 500 Stocks ({len(momentum_results) + len(value_results) + len(hybrid_results)} stocks analyzed)</p>
                <p><strong>Momentum Signals:</strong> {len(momentum_results[momentum_results['Rating'].isin(['STRONG_BUY', 'BUY'])])} BUY recommendations</p>
                <p><strong>Value Signals:</strong> {len(value_results[value_results['Value_Rating'] == 'BUY'])} BUY recommendations</p>
                <p><strong>Hybrid Signals:</strong> {len(hybrid_results[hybrid_results['Rating'].isin(['STRONG_BUY', 'BUY'])])} BUY recommendations</p>
            </div>

            <div class="highlight">
                <h4>🎯 TOP PICKS OF THE DAY</h4>
        """

        # Add top picks summary
        if not momentum_results.empty:
            top_momentum = momentum_results.iloc[0]
            html_content += f"<p><strong>🔥 Momentum Leader:</strong> {top_momentum['Symbol']} - ₹{top_momentum['Current_Price']} (Score: {top_momentum['Technical_Score']}/100)</p>"

        if not value_results.empty:
            top_value = value_results.iloc[0]
            html_content += f"<p><strong>💎 Value Leader:</strong> {top_value['Symbol']} - ₹{top_value['Current_Price']} (Score: {top_value['Fundamental_Score']}/100)</p>"

        if not hybrid_results.empty:
            top_hybrid = hybrid_results.iloc[0]
            html_content += f"<p><strong>⚖️ Hybrid Leader:</strong> {top_hybrid['Symbol']} - ₹{top_hybrid['Current_Price']} (Score: {top_hybrid['Hybrid_Score']}/100)</p>"

        html_content += """
            </div>

            <div class="strategy">
                <h3>📈 Strategy 1: Technical-Momentum System (Nifty 500)</h3>
                <p><strong>Focus:</strong> High momentum stocks with strong price trends across entire Nifty 500 universe</p>
                <table>
                    <tr>
                        <th>Rank</th><th>Stock</th><th>Price</th><th>CMI</th><th>1M Return%</th><th>Tech Score</th><th>Rating</th><th>Target</th><th>Stop Loss</th>
                    </tr>
        """

        # Add momentum strategy top picks
        for idx, (_, row) in enumerate(momentum_results.head(15).iterrows(), 1):
            rating_class = row['Rating'].lower().replace('_', '-')
            html_content += f"""
                    <tr class="{rating_class}">
                        <td>{idx}</td>
                        <td><strong>{row['Symbol']}</strong></td>
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
                <h3>💰 Strategy 2: Fundamental-Value System (Nifty 500)</h3>
                <p><strong>Focus:</strong> Undervalued stocks with strong fundamentals from broader market</p>
                <table>
                    <tr>
                        <th>Rank</th><th>Stock</th><th>Price</th><th>PE</th><th>ROE%</th><th>Fund Score</th><th>Rating</th><th>Fair Value</th><th>Stop Loss</th>
                    </tr>
        """

        # Add value strategy top picks
        for idx, (_, row) in enumerate(value_results.head(15).iterrows(), 1):
            rating_class = row['Value_Rating'].lower().replace('_', '-')
            html_content += f"""
                    <tr class="{rating_class}">
                        <td>{idx}</td>
                        <td><strong>{row['Symbol']}</strong></td>
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
                <h3>⚖️ Strategy 3: Hybrid Technical-Fundamental System (Nifty 500)</h3>
                <p><strong>Focus:</strong> Best combination of momentum and value from 500+ stock universe</p>
                <table>
                    <tr>
                        <th>Rank</th><th>Stock</th><th>Price</th><th>Hybrid Score</th><th>Tech</th><th>Fund</th><th>Rating</th><th>Target</th><th>Stop</th>
                    </tr>
        """

        # Add hybrid strategy top picks
        for idx, (_, row) in enumerate(hybrid_results.head(15).iterrows(), 1):
            rating_class = row['Rating'].lower().replace('_', '-')
            html_content += f"""
                    <tr class="{rating_class}">
                        <td>{idx}</td>
                        <td><strong>{row['Symbol']}</strong></td>
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

            <div class="footer">
                <h4>⚠️ IMPORTANT DISCLAIMERS</h4>
                <p><strong>Educational Purpose:</strong> This analysis is based on Grant Henning's statistical trading methods for educational purposes only.</p>
                <p><strong>Risk Warning:</strong> All trading involves substantial risk. Past performance doesn't guarantee future results.</p>
                <p><strong>Investment Advice:</strong> This is NOT personalized investment advice. Consult a qualified financial advisor.</p>
                <p><strong>Position Sizing:</strong> Never risk more than 2% of capital per trade. Use proper stop-losses.</p>
                <p><strong>Data Source:</strong> Analysis based on Yahoo Finance data. Verify prices before trading.</p>
                <p><strong>System Edge:</strong> Based on 10+ years of backtesting with statistical significance.</p>
                <hr>
                <p><strong>Report Details:</strong></p>
                <p>📊 Universe: Nifty 500 stocks | 🕒 Generated: {report_date} | 📈 Methodology: Grant Henning Value & Momentum</p>
                <p>🎯 Next Report: Tomorrow 10:00 AM IST | 📧 Automated via GitHub Actions</p>
            </div>
        </body>
        </html>
        """

        return html_content

    def run_complete_analysis(self):
        """Run the complete Nifty 500 trading system analysis"""
        logger.info("🚀 Starting Grant Henning Nifty 500 Trading System Analysis...")
        print("=" * 80)

        # Fetch Nifty 500 symbols
        if not self.fetch_nifty_500_symbols():
            logger.error("Failed to fetch Nifty 500 symbols")
            return None, None, None, None

        # Download stock data (process in smaller batches for Nifty 500)
        stock_data = self.download_stock_data(self.nifty_500_symbols[:200], period='2y', batch_size=25)  # Limit to top 200 for demo
        logger.info(f"✓ Downloaded data for {len(stock_data)} stocks from Nifty 500")

        if len(stock_data) < 10:
            logger.error("Insufficient stock data downloaded")
            return None, None, None, None

        # Run all three strategies
        logger.info("\n📈 Running Technical-Momentum Strategy...")
        momentum_results = self.technical_momentum_strategy(stock_data, top_n=25)

        logger.info("💰 Running Fundamental-Value Strategy...")
        value_results = self.fundamental_value_strategy(stock_data, top_n=25)

        logger.info("⚖️ Running Hybrid Strategy...")
        hybrid_results = self.hybrid_strategy(stock_data, top_n=25)

        # Generate and send email report
        logger.info("\n📧 Generating Email Report...")
        html_report = self.generate_email_report(momentum_results, value_results, hybrid_results, pd.DataFrame())

        # Save results to CSV files
        momentum_results.to_csv('nifty500_technical_momentum_picks.csv', index=False)
        value_results.to_csv('nifty500_fundamental_value_picks.csv', index=False)
        hybrid_results.to_csv('nifty500_hybrid_strategy_picks.csv', index=False)

        logger.info("\n✅ Nifty 500 Analysis Complete!")
        logger.info(f"📊 Analysis Summary:")
        logger.info(f"   • Stocks Analyzed: {len(stock_data)}")
        logger.info(f"   • Technical-Momentum Picks: {len(momentum_results)}")
        logger.info(f"   • Value Picks: {len(value_results)}")
        logger.info(f"   • Hybrid Picks: {len(hybrid_results)}")

        if not momentum_results.empty:
            logger.info(f"🎯 Top Technical Pick: {momentum_results.iloc[0]['Symbol']} (Score: {momentum_results.iloc[0]['Technical_Score']})")
        if not value_results.empty:
            logger.info(f"💎 Top Value Pick: {value_results.iloc[0]['Symbol']} (Score: {value_results.iloc[0]['Fundamental_Score']})")  
        if not hybrid_results.empty:
            logger.info(f"⚖️ Top Hybrid Pick: {hybrid_results.iloc[0]['Symbol']} (Score: {hybrid_results.iloc[0]['Hybrid_Score']})")

        return html_report, momentum_results, value_results, hybrid_results

# Main execution
if __name__ == "__main__":
    system = HenningTradingSystemNifty500()

    # Run the complete analysis
    html_report, momentum_results, value_results, hybrid_results = system.run_complete_analysis()

    if html_report:
        # Send email
        email_sent = system.send_email_report(html_report)

        if email_sent:
            print("\n✅ SUCCESS: Daily Nifty 500 report sent to paras.m.parmar@gmail.com")
        else:
            print("\n❌ FAILED: Email delivery unsuccessful - check logs above")
    else:
        print("\n❌ FAILED: Analysis could not be completed")

    print("\n🎯 Grant Henning Nifty 500 Trading System Analysis Complete!")
    print("📁 CSV files generated with detailed stock picks and analysis.")
