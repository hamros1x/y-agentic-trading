"""
MARKOV CHAIN INTRADAY PREDICTION SYSTEM
========================================
15-minute intraday prediction system using Markov Chain analysis.

Run from main folder: python strategy_files/markov_trading_system.py
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from collections import defaultdict, Counter


def load_historical_data(file_path='output_data/historical_data.txt'):
    """Load historical price data from the output_data folder."""
    if not os.path.exists(file_path):
        print(f"✗ ERROR: Data file not found at '{file_path}'")
        return None
    
    try:
        try:
            df = pd.read_csv(file_path, sep='\t')
        except:
            try:
                df = pd.read_csv(file_path, sep=',')
            except:
                df = pd.read_csv(file_path, sep=r'\s+', engine='python', on_bad_lines='skip')
        
        if isinstance(df.index, pd.DatetimeIndex):
            df = df.reset_index()
            if 'index' in df.columns:
                df = df.rename(columns={'index': 'Date'})
        
        if 'Datetime' in df.columns and 'Date' not in df.columns:
            df = df.rename(columns={'Datetime': 'Date'})
        
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.dropna()
        df = df.sort_values('Date').reset_index(drop=True)
        
        if 'Close' not in df.columns:
            print("✗ ERROR: 'Close' column not found in data!")
            return None
        
        return df
        
    except Exception as e:
        print(f"✗ ERROR loading data: {str(e)}")
        return None


def build_markov_model(df):
    """
    Build Markov Chain transition matrix from entire dataset.
    
    Returns:
    --------
    tuple : (transition_matrix, pattern_counts)
    """
    transition_matrix = {}
    pattern_counts = defaultdict(Counter)
    
    closes = df['Close'].values
    total_rows = len(closes)
    
    if total_rows < 4:
        print("✗ ERROR: Need at least 4 rows of data")
        return None, None
    
    movements = []
    for i in range(1, total_rows):
        if closes[i] > closes[i-1]:
            movements.append('UP')
        elif closes[i] < closes[i-1]:
            movements.append('DOWN')
        else:
            movements.append('FLAT')
    
    for i in range(3, len(movements)):
        pattern = (movements[i-3], movements[i-2], movements[i-1])
        next_move = movements[i]
        pattern_counts[pattern][next_move] += 1
    
    for pattern in pattern_counts:
        total = sum(pattern_counts[pattern].values())
        transition_matrix[pattern] = {}
        for move in pattern_counts[pattern]:
            transition_matrix[pattern][move] = pattern_counts[pattern][move] / total
    
    return transition_matrix, pattern_counts


def main():
    print("="*80)
    print("MARKOV CHAIN INTRADAY PREDICTION SYSTEM")
    print("="*80)
    
    print("\nLOADING DATA...")
    df = load_historical_data('output_data/historical_data.txt')
    if df is None:
        print("Error: Could not load data")
        sys.exit(1)
    
    if not pd.api.types.is_datetime64_any_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    
    df['TradingDay'] = df['Date'].dt.date
    total_days = df['TradingDay'].nunique()
    total_candles = len(df)
    print(f"✓ Loaded {total_candles} candles covering {total_days} trading days")
    
    print("\nTRAINING MARKOV MODEL...")
    transition_matrix, pattern_counts = build_markov_model(df)
    if transition_matrix is None:
        print("Error: Model training failed")
        sys.exit(1)
    
    unique_patterns = len(transition_matrix)
    avg_frequency = sum(sum(pattern_counts[p].values()) for p in pattern_counts) / unique_patterns if unique_patterns > 0 else 0
    print(f"✓ Trained on {unique_patterns} unique patterns")
    print(f"✓ Average pattern frequency: {avg_frequency:.1f}")
    
    print("\n" + "="*80)
    print("DATE SELECTION")
    print("="*80)
    available_dates = sorted(df['TradingDay'].unique())
    print(f"\nAvailable dates: {available_dates[0]} to {available_dates[-1]}")
    
    prediction_date_str = input("\nEnter date to predict (YYYY-MM-DD): ")
    try:
        prediction_date = pd.to_datetime(prediction_date_str).date()
    except:
        print("Error: Invalid date format")
        sys.exit(1)
    
    if prediction_date not in available_dates:
        print("Error: Date not in dataset")
        sys.exit(1)
    
    pred_index = list(available_dates).index(prediction_date)
    if pred_index == 0:
        print("Error: No previous day data available")
        sys.exit(1)
    
    previous_day = available_dates[pred_index - 1]
    
    prev_day_df = df[df['TradingDay'] == previous_day].copy()
    num_candles = len(prev_day_df)
    print(f"\n✓ Analyzing {num_candles} intraday candles from {previous_day}")
    
    if num_candles < 10:
        print("Error: Insufficient intraday data for prediction")
        sys.exit(1)
    
    prev_day_df['Movement'] = 'FLAT'
    for i in range(1, len(prev_day_df)):
        if prev_day_df.iloc[i]['Close'] > prev_day_df.iloc[i-1]['Close']:
            prev_day_df.iloc[i, prev_day_df.columns.get_loc('Movement')] = 'UP'
        elif prev_day_df.iloc[i]['Close'] < prev_day_df.iloc[i-1]['Close']:
            prev_day_df.iloc[i, prev_day_df.columns.get_loc('Movement')] = 'DOWN'
    
    patterns_found = []
    for i in range(2, len(prev_day_df)):
        pattern = (prev_day_df.iloc[i-2]['Movement'],
                   prev_day_df.iloc[i-1]['Movement'],
                   prev_day_df.iloc[i]['Movement'])
        patterns_found.append(pattern)
    
    total_up = 0.0
    total_down = 0.0
    total_flat = 0.0
    matched_patterns = 0
    
    for pattern in patterns_found:
        if pattern in transition_matrix:
            matched_patterns += 1
            probs = transition_matrix[pattern]
            total_up += probs.get('UP', 0)
            total_down += probs.get('DOWN', 0)
            total_flat += probs.get('FLAT', 0)
    
    if matched_patterns == 0:
        print("Error: No matching patterns found in trained model")
        sys.exit(1)
    
    total = total_up + total_down + total_flat
    confidence_up = (total_up / total) * 100
    confidence_down = (total_down / total) * 100
    confidence_flat = (total_flat / total) * 100
    
    max_confidence = max(confidence_up, confidence_down, confidence_flat)
    if max_confidence == confidence_up:
        prediction = "BULLISH"
        confidence = confidence_up
    elif max_confidence == confidence_down:
        prediction = "BEARISH"
        confidence = confidence_down
    else:
        prediction = "NEUTRAL"
        confidence = confidence_flat
    
    strength_score = ((max_confidence - 33.33) / 66.67) * 100
    if strength_score > 70:
        signal_strength = "Strong"
    elif strength_score > 40:
        signal_strength = "Moderate"
    else:
        signal_strength = "Weak"
    
    last_5 = prev_day_df['Movement'].tail(5).tolist()
    consecutive = 1
    for i in range(len(last_5)-1, 0, -1):
        if last_5[i] == last_5[i-1] and last_5[i] != 'FLAT':
            consecutive += 1
        else:
            break
    
    momentum_type = last_5[-1] if consecutive > 1 else "Mixed"
    if consecutive >= 4:
        momentum = "Strong"
    elif consecutive >= 2:
        momentum = "Moderate"
    else:
        momentum = "Weak"
    
    atr = (prev_day_df['High'] - prev_day_df['Low']).mean()
    volatility = "High" if atr > prev_day_df['Close'].mean() * 0.02 else "Medium" if atr > prev_day_df['Close'].mean() * 0.01 else "Low"
    
    print("\n" + "="*80)
    print("PREDICTION RESULT")
    print("="*80)
    print(f"\nPREDICTION FOR: {prediction_date}")
    print(f"BASED ON ANALYSIS OF: {previous_day}")
    print(f"\n{'─'*80}")
    print("TRAINING DATA SUMMARY")
    print(f"{'─'*80}")
    print(f"Total Candles Analyzed: {total_candles}")
    print(f"Trading Days Covered: {total_days}")
    print(f"Unique Patterns Learned: {unique_patterns}")
    print(f"Average Pattern Frequency: {avg_frequency:.1f}")
    print(f"\n{'─'*80}")
    print("MARKET TREND PREDICTION")
    print(f"{'─'*80}")
    print(f"\nPrimary Signal: {prediction}")
    print(f"Confidence Level: {confidence:.1f}%")
    print(f"Signal Strength: {signal_strength} ({strength_score:.0f}/100)")
    print(f"\nProbability Breakdown:")
    print(f"  • Bullish: {confidence_up:.1f}%")
    print(f"  • Bearish: {confidence_down:.1f}%")
    print(f"  • Neutral: {confidence_flat:.1f}%")
    print(f"\n{'─'*80}")
    print("SUPPORTING INDICATORS")
    print(f"{'─'*80}")
    print(f"\nMomentum: {momentum}")
    print(f"  → {consecutive} consecutive {momentum_type} candles detected")
    print(f"\nVolatility: {volatility}")
    print(f"  → Average True Range: {atr:.2f}")
    print(f"  → Implication: {'More volatile = less reliable' if volatility == 'High' else 'Stable conditions'}")
    print(f"\n{'─'*80}")
    print("PATTERN ANALYSIS")
    print(f"{'─'*80}")
    print(f"Intraday Patterns Analyzed: {len(patterns_found)}")
    print(f"Patterns Matched in Model: {matched_patterns}")
    print(f"Match Quality: {(matched_patterns/len(patterns_found)*100):.1f}%")
    print(f"\n{'─'*80}")
    print("RECOMMENDED ACTION")
    print(f"{'─'*80}")
    
    if prediction == "BULLISH" and signal_strength in ["Strong", "Moderate"]:
        action = "BUY / LONG"
    elif prediction == "BEARISH" and signal_strength in ["Strong", "Moderate"]:
        action = "SELL / SHORT"
    else:
        action = "HOLD / WAIT"
    
    print(f"\nSuggested Action: {action}")
    print(f"Confidence in Signal: {signal_strength}")
    if signal_strength == "Weak":
        print("⚠ Warning: Low confidence - consider waiting for stronger signal")
    
    print("\n" + "="*80)
    
    results_folder = 'results'
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    results_file = f'{results_folder}/prediction_{prediction_date}_{timestamp}.txt'
    
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("MARKOV CHAIN INTRADAY PREDICTION SYSTEM - RESULTS\n")
        f.write("="*80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"PREDICTION FOR: {prediction_date}\n")
        f.write(f"BASED ON ANALYSIS OF: {previous_day}\n\n")
        
        f.write("─"*80 + "\n")
        f.write("TRAINING DATA SUMMARY\n")
        f.write("─"*80 + "\n")
        f.write(f"Total Candles Analyzed: {total_candles}\n")
        f.write(f"Trading Days Covered: {total_days}\n")
        f.write(f"Unique Patterns Learned: {unique_patterns}\n")
        f.write(f"Average Pattern Frequency: {avg_frequency:.1f}\n\n")
        
        f.write("─"*80 + "\n")
        f.write("MARKET TREND PREDICTION\n")
        f.write("─"*80 + "\n")
        f.write(f"\nPrimary Signal: {prediction}\n")
        f.write(f"Confidence Level: {confidence:.1f}%\n")
        f.write(f"Signal Strength: {signal_strength} ({strength_score:.0f}/100)\n\n")
        f.write(f"Probability Breakdown:\n")
        f.write(f"  • Bullish: {confidence_up:.1f}%\n")
        f.write(f"  • Bearish: {confidence_down:.1f}%\n")
        f.write(f"  • Neutral: {confidence_flat:.1f}%\n\n")
        
        f.write("─"*80 + "\n")
        f.write("SUPPORTING INDICATORS\n")
        f.write("─"*80 + "\n")
        f.write(f"\nMomentum: {momentum}\n")
        f.write(f"  → {consecutive} consecutive {momentum_type} candles detected\n\n")
        f.write(f"Volatility: {volatility}\n")
        f.write(f"  → Average True Range: {atr:.2f}\n")
        f.write(f"  → Implication: {'More volatile = less reliable' if volatility == 'High' else 'Stable conditions'}\n\n")
        
        f.write("─"*80 + "\n")
        f.write("PATTERN ANALYSIS\n")
        f.write("─"*80 + "\n")
        f.write(f"Intraday Patterns Analyzed: {len(patterns_found)}\n")
        f.write(f"Patterns Matched in Model: {matched_patterns}\n")
        f.write(f"Match Quality: {(matched_patterns/len(patterns_found)*100):.1f}%\n\n")
        
        f.write("─"*80 + "\n")
        f.write("RECOMMENDED ACTION\n")
        f.write("─"*80 + "\n")
        f.write(f"\nSuggested Action: {action}\n")
        f.write(f"Confidence in Signal: {signal_strength}\n")
        if signal_strength == "Weak":
            f.write("⚠ Warning: Low confidence - consider waiting for stronger signal\n")
        f.write("\n" + "="*80 + "\n")
    
    print(f"\n✓ Prediction results saved to: {results_file}")


if __name__ == "__main__":
    main()
