#!/usr/bin/env python3
"""
Main execution script for Grant Henning Trading System
Runs daily analysis and sends email reports
"""

import os
import sys
from datetime import datetime
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from henning_trading_system import HenningTradingSystem

    def main():
        print("🕒 Starting daily analysis at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"))

        # Initialize the trading system
        system = HenningTradingSystem()

        try:
            # Run complete analysis
            html_report, momentum_results, value_results, hybrid_results = system.run_complete_analysis()

            # Send email report
            recipient = os.environ.get('RECIPIENT_EMAIL', 'paras.m.parmar@gmail.com')
            email_sent = system.send_email_report(html_report, recipient)

            if email_sent:
                print(f"✅ Daily report successfully sent to {recipient}")
            else:
                print("❌ Failed to send email report")

            # Print summary statistics
            print("\n📈 DAILY ANALYSIS SUMMARY")
            print("=" * 50)
            print(f"Technical-Momentum Strategy: {len(momentum_results[momentum_results['Rating'].isin(['STRONG_BUY', 'BUY'])])} BUY signals")
            print(f"Fundamental-Value Strategy: {len(value_results[value_results['Value_Rating'].isin(['BUY'])])} BUY signals") 
            print(f"Hybrid Strategy: {len(hybrid_results[hybrid_results['Rating'].isin(['STRONG_BUY', 'BUY'])])} BUY signals")

            # Top picks summary
            print("\n🎯 TOP PICKS OF THE DAY:")
            print("-" * 30)
            if not momentum_results.empty:
                top_momentum = momentum_results.iloc[0]
                print(f"Momentum Leader: {top_momentum['Symbol']} (Score: {top_momentum['Technical_Score']})")

            if not value_results.empty:
                top_value = value_results.iloc[0] 
                print(f"Value Leader: {top_value['Symbol']} (Score: {top_value['Fundamental_Score']})")

            if not hybrid_results.empty:
                top_hybrid = hybrid_results.iloc[0]
                print(f"Hybrid Leader: {top_hybrid['Symbol']} (Score: {top_hybrid['Hybrid_Score']})")

            print("\n✅ Analysis completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Error during analysis: {str(e)}")
            traceback.print_exc()
            return False

    if __name__ == "__main__":
        success = main()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure henning_trading_system.py is in the same directory")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
