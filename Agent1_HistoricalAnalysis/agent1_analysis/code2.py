import pandas as pd
import numpy as np
from scipy import stats
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def load_data(ticker):
    daily_path = f'data/{ticker}_daily.csv'
    intraday_path = f'data/{ticker}_15min.csv'
    
    if not os.path.exists(daily_path):
        raise FileNotFoundError(f"Daily data not found: {daily_path}")
    if not os.path.exists(intraday_path):
        raise FileNotFoundError(f"15-min data not found: {intraday_path}")
    
    daily = pd.read_csv(daily_path)
    intraday = pd.read_csv(intraday_path)
    
    daily['Date'] = pd.to_datetime(daily['Date'])
    intraday['Datetime'] = pd.to_datetime(intraday['Datetime'])
    
    daily = daily.sort_values('Date').reset_index(drop=True)
    intraday = intraday.sort_values('Datetime').reset_index(drop=True)
    
    return daily, intraday


def find_support_resistance(daily, lookback_days):
    recent = daily.tail(lookback_days).copy()
    
    highs = []
    lows = []
    
    for i in range(1, len(recent) - 1):
        if recent.iloc[i]['High'] > recent.iloc[i-1]['High'] and recent.iloc[i]['High'] > recent.iloc[i+1]['High']:
            highs.append(recent.iloc[i]['High'])
        if recent.iloc[i]['Low'] < recent.iloc[i-1]['Low'] and recent.iloc[i]['Low'] < recent.iloc[i+1]['Low']:
            lows.append(recent.iloc[i]['Low'])
    
    all_levels = highs + lows
    if not all_levels:
        return []
    
    clusters = []
    sorted_levels = sorted(all_levels)
    
    for level in sorted_levels:
        added = False
        for cluster in clusters:
            if abs(level - cluster['price']) / cluster['price'] < 0.02:
                cluster['prices'].append(level)
                cluster['price'] = np.mean(cluster['prices'])
                cluster['touches'] += 1
                added = True
                break
        if not added:
            clusters.append({'price': level, 'prices': [level], 'touches': 1})
    
    for cluster in clusters:
        bounces = []
        for _, row in recent.iterrows():
            if abs(row['Low'] - cluster['price']) / cluster['price'] < 0.02:
                future = recent[recent['Date'] > row['Date']].head(5)
                if len(future) > 0:
                    bounce = ((future['High'].max() - row['Low']) / row['Low']) * 100
                    bounces.append(bounce)
            elif abs(row['High'] - cluster['price']) / cluster['price'] < 0.02:
                future = recent[recent['Date'] > row['Date']].head(5)
                if len(future) > 0:
                    bounce = ((row['High'] - future['Low'].min()) / row['High']) * 100
                    bounces.append(bounce)
        
        cluster['avg_bounce'] = np.mean(bounces) if bounces else 0
        cluster['bounce_count'] = len(bounces)
    
    # FIX 6: Better confidence scoring
    for cluster in clusters:
        sample_size = cluster['touches']
        effect_size = cluster['avg_bounce']
        
        sample_factor = np.sqrt(sample_size) / 30
        effect_factor = min(1.0, abs(effect_size) / 5.0)
        recency_weight = 0.8
        
        confidence = min(0.95, sample_factor * effect_factor * recency_weight)
        cluster['confidence'] = max(0.0, confidence)
    
    clusters.sort(key=lambda x: x['confidence'], reverse=True)
    return clusters[:5]


def analyze_support_resistance(daily):
    results = {}
    for period, days in [('1M', 21), ('3M', 63), ('6M', 126)]:
        results[period] = find_support_resistance(daily, days)
    return results


def analyze_volume_profile(daily):
    price_min = daily['Low'].min()
    price_max = daily['High'].max()
    bins = np.linspace(price_min, price_max, 101)
    
    volume_by_price = np.zeros(100)
    
    for _, row in daily.iterrows():
        price_range = row['High'] - row['Low']
        if price_range == 0:
            bin_idx = np.digitize(row['Close'], bins) - 1
            bin_idx = max(0, min(99, bin_idx))
            volume_by_price[bin_idx] += row['Volume']
        else:
            for i in range(100):
                bin_low = bins[i]
                bin_high = bins[i+1]
                overlap = max(0, min(row['High'], bin_high) - max(row['Low'], bin_low))
                if overlap > 0:
                    volume_by_price[i] += row['Volume'] * (overlap / price_range)
    
    poc_idx = np.argmax(volume_by_price)
    poc_price = (bins[poc_idx] + bins[poc_idx + 1]) / 2
    
    total_volume = volume_by_price.sum()
    
    # FIX 2: POC-outward expansion for Value Area
    left_idx = right_idx = poc_idx
    cumulative = volume_by_price[poc_idx]
    
    while cumulative < 0.7 * total_volume and (left_idx > 0 or right_idx < len(volume_by_price) - 1):
        left_vol = volume_by_price[left_idx - 1] if left_idx > 0 else 0
        right_vol = volume_by_price[right_idx + 1] if right_idx < len(volume_by_price) - 1 else 0
        
        if left_vol > right_vol and left_idx > 0:
            left_idx -= 1
            cumulative += volume_by_price[left_idx]
        elif right_idx < len(volume_by_price) - 1:
            right_idx += 1
            cumulative += volume_by_price[right_idx]
        else:
            break
    
    vah_price = bins[right_idx + 1]
    val_price = bins[left_idx]
    
    hvn_threshold = np.percentile(volume_by_price, 80)
    hvn_indices = np.where(volume_by_price >= hvn_threshold)[0]
    hvns = [(bins[i] + bins[i+1]) / 2 for i in hvn_indices]
    
    lvn_threshold = np.percentile(volume_by_price, 20)
    lvn_indices = np.where(volume_by_price <= lvn_threshold)[0]
    lvns = [(bins[i] + bins[i+1]) / 2 for i in lvn_indices]
    
    # FIX 6: Better confidence scoring
    sample_size = len(daily)
    sample_factor = np.sqrt(sample_size) / 30
    confidence = min(0.95, sample_factor * 0.8)
    
    return {
        'poc': poc_price,
        'vah': vah_price,
        'val': val_price,
        'hvns': hvns[:3],
        'lvns': lvns[:2],
        'confidence': confidence
    }


def analyze_gaps(daily):
    gaps = []
    
    for i in range(1, len(daily)):
        prev_close = daily.iloc[i-1]['Close']
        curr_open = daily.iloc[i]['Open']
        gap_pct = abs((curr_open - prev_close) / prev_close) * 100
        
        if gap_pct > 1.0:
            gap_direction = 'up' if curr_open > prev_close else 'down'
            gaps.append({
                'date': daily.iloc[i]['Date'],
                'gap_pct': gap_pct,
                'direction': gap_direction,
                'open': curr_open,
                'prev_close': prev_close,
                'index': i
            })
    
    if not gaps:
        return {'total': 0, 'fill_same_day': 0, 'fill_1day': 0, 'fill_5day': 0, 'avg_time': 0, 'confidence': 0}
    
    fill_same_day = 0
    fill_1day = 0
    fill_5day = 0
    fill_times = []
    
    for gap in gaps:
        idx = gap['index']
        filled = False
        
        if gap['direction'] == 'up':
            if daily.iloc[idx]['Low'] <= gap['prev_close']:
                fill_same_day += 1
                fill_1day += 1
                fill_5day += 1
                fill_times.append(0)
                filled = True
        else:
            if daily.iloc[idx]['High'] >= gap['prev_close']:
                fill_same_day += 1
                fill_1day += 1
                fill_5day += 1
                fill_times.append(0)
                filled = True
        
        if not filled:
            for days_ahead in range(1, 6):
                if idx + days_ahead >= len(daily):
                    break
                
                if gap['direction'] == 'up':
                    if daily.iloc[idx + days_ahead]['Low'] <= gap['prev_close']:
                        if days_ahead == 1:
                            fill_1day += 1
                        fill_5day += 1
                        fill_times.append(days_ahead)
                        break
                else:
                    if daily.iloc[idx + days_ahead]['High'] >= gap['prev_close']:
                        if days_ahead == 1:
                            fill_1day += 1
                        fill_5day += 1
                        fill_times.append(days_ahead)
                        break
    
    total_gaps = len(gaps)
    avg_time = np.mean(fill_times) if fill_times else 0
    
    # FIX 6: Better confidence scoring
    sample_size = total_gaps
    sample_factor = np.sqrt(sample_size) / 30
    confidence = min(0.95, sample_factor * 0.8)
    
    return {
        'total': total_gaps,
        'fill_same_day': (fill_same_day / total_gaps) * 100,
        'fill_1day': (fill_1day / total_gaps) * 100,
        'fill_5day': (fill_5day / total_gaps) * 100,
        'avg_time': avg_time,
        'confidence': confidence
    }


def calculate_hurst_exponent(prices, max_lag=20):
    lags = range(2, max_lag)
    tau = []
    
    for lag in lags:
        pp = np.subtract(prices[lag:], prices[:-lag])
        tau.append(np.std(pp))
    
    if len(tau) == 0:
        return 0.5, 0.0
    
    poly = np.polyfit(np.log(lags), np.log(tau), 1)
    hurst = poly[0]
    
    # FIX 6: Better confidence scoring
    sample_factor = np.sqrt(len(prices)) / 30
    confidence = min(0.95, sample_factor * 0.8)
    
    return hurst, confidence


def analyze_hurst(daily):
    prices = daily['Close'].values
    hurst, confidence = calculate_hurst_exponent(prices)
    
    if hurst < 0.5:
        interpretation = 'Mean-Reverting'
    elif hurst > 0.5:
        interpretation = 'Trending'
    else:
        interpretation = 'Random'
    
    return {'hurst': hurst, 'interpretation': interpretation, 'confidence': confidence}


def analyze_volatility_regime(daily):
    daily_copy = daily.copy()
    daily_copy['Returns'] = daily_copy['Close'].pct_change()
    daily_copy['Volatility'] = daily_copy['Returns'].rolling(window=20).std()
    
    current_vol = daily_copy['Volatility'].iloc[-1]
    vol_percentile = stats.percentileofscore(daily_copy['Volatility'].dropna(), current_vol)
    
    if vol_percentile > 70:
        regime = 'High'
    elif vol_percentile < 30:
        regime = 'Low'
    else:
        regime = 'Transitional'
    
    recent_vol = daily_copy['Volatility'].tail(10).std()
    stability = 1.0 / (1.0 + recent_vol) if recent_vol > 0 else 1.0
    
    # FIX 6: Better confidence scoring
    sample_factor = np.sqrt(len(daily_copy)) / 30
    confidence = min(0.95, stability * sample_factor * 0.8)
    
    return {'regime': regime, 'percentile': vol_percentile, 'confidence': confidence}


def analyze_correlation_with_index(daily):
    try:
        import yfinance as yf
        start_date = daily['Date'].min()
        end_date = daily['Date'].max()
        nifty = yf.download('^NSEI', start=start_date, end=end_date, progress=False)
        
        if nifty.empty:
            return {'corr_5d': 0, 'corr_20d': 0, 'corr_60d': 0, 'confidence': 0}
        
        nifty = nifty.reset_index()
        nifty.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        
        # FIX 1: Proper data join and NaN handling
        merged = pd.merge(daily[['Date', 'Close']], nifty[['Date', 'Close']], on='Date', suffixes=('_stock', '_nifty'))
        
        merged['ret_stock'] = merged['Close_stock'].pct_change()
        merged['ret_nifty'] = merged['Close_nifty'].pct_change()
        
        # Remove NaN rows before correlation
        merged = merged.dropna(subset=['ret_stock', 'ret_nifty'])
        
        if len(merged) < 60:
            return {'corr_5d': 0, 'corr_20d': 0, 'corr_60d': 0, 'confidence': 0}
        
        corr_5d = merged['ret_stock'].tail(5).corr(merged['ret_nifty'].tail(5))
        corr_20d = merged['ret_stock'].tail(20).corr(merged['ret_nifty'].tail(20))
        corr_60d = merged['ret_stock'].tail(60).corr(merged['ret_nifty'].tail(60))
        
        # FIX 6: Better confidence scoring
        corr_std = np.std([corr_5d, corr_20d, corr_60d])
        sample_factor = np.sqrt(len(merged)) / 30
        stability_factor = 1.0 / (1.0 + corr_std)
        confidence = min(0.95, sample_factor * stability_factor * 0.8)
        
        return {
            'corr_5d': corr_5d if not np.isnan(corr_5d) else 0,
            'corr_20d': corr_20d if not np.isnan(corr_20d) else 0,
            'corr_60d': corr_60d if not np.isnan(corr_60d) else 0,
            'confidence': confidence
        }
    except Exception as e:
        print(f"Warning: Could not fetch NIFTY data: {e}")
        return {'corr_5d': 0, 'corr_20d': 0, 'corr_60d': 0, 'confidence': 0}


def analyze_day_of_week(daily):
    daily_copy = daily.copy()
    daily_copy['DayOfWeek'] = pd.to_datetime(daily_copy['Date']).dt.dayofweek
    daily_copy['Returns'] = daily_copy['Close'].pct_change() * 100
    
    day_stats = {}
    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    
    for day_num, day_name in enumerate(day_names):
        day_data = daily_copy[daily_copy['DayOfWeek'] == day_num]['Returns'].dropna()
        day_stats[day_name] = {
            'avg_return': day_data.mean() if len(day_data) > 0 else 0,
            'samples': len(day_data)
        }
    
    strongest_day = max(day_stats.items(), key=lambda x: x[1]['avg_return'])
    total_samples = sum(d['samples'] for d in day_stats.values())
    
    # FIX 6: Better confidence scoring
    sample_factor = np.sqrt(total_samples) / 30
    confidence = min(0.95, sample_factor * 0.8)
    
    return {'day_stats': day_stats, 'strongest_day': strongest_day[0], 'confidence': confidence}


def analyze_opening_range(intraday, daily):
    intraday_copy = intraday.copy()
    intraday_copy['Date'] = pd.to_datetime(intraday_copy['Datetime']).dt.date
    intraday_copy['Time'] = pd.to_datetime(intraday_copy['Datetime']).dt.time
    
    # FIX 3: Calculate ATR for buffer
    daily_copy = daily.copy()
    daily_copy['TR'] = daily_copy.apply(
        lambda row: max(
            row['High'] - row['Low'],
            abs(row['High'] - daily_copy['Close'].shift(1).loc[row.name]) if row.name > 0 else row['High'] - row['Low'],
            abs(row['Low'] - daily_copy['Close'].shift(1).loc[row.name]) if row.name > 0 else row['High'] - row['Low']
        ),
        axis=1
    )
    atr = daily_copy['TR'].rolling(14).mean().iloc[-1]
    buffer = 0.25 * atr
    
    days = intraday_copy.groupby('Date')
    breakout_count = 0
    follow_through = []
    total_days = 0
    
    for date, day_data in days:
        day_data = day_data.sort_values('Datetime').reset_index(drop=True)
        
        first_30min = day_data.head(2)
        if len(first_30min) < 2:
            continue
        
        or_high = first_30min['High'].max()
        or_low = first_30min['Low'].min()
        
        rest_of_day = day_data.iloc[2:]
        if len(rest_of_day) == 0:
            continue
        
        total_days += 1
        
        # FIX 3: Require close beyond OR with buffer
        broke_high = (rest_of_day['Close'] > or_high + buffer).any()
        broke_low = (rest_of_day['Close'] < or_low - buffer).any()
        
        if broke_high or broke_low:
            breakout_count += 1
            
            if broke_high:
                breakout_price = or_high + buffer
                eod_price = day_data.iloc[-1]['Close']
                ft = ((eod_price - breakout_price) / breakout_price) * 100
                follow_through.append(ft)
            elif broke_low:
                breakout_price = or_low - buffer
                eod_price = day_data.iloc[-1]['Close']
                ft = ((breakout_price - eod_price) / breakout_price) * 100
                follow_through.append(ft)
    
    breakout_rate = (breakout_count / total_days * 100) if total_days > 0 else 0
    avg_follow_through = np.mean(follow_through) if follow_through else 0
    
    # FIX 6: Better confidence scoring
    sample_factor = np.sqrt(total_days) / 30
    confidence = min(0.95, sample_factor * 0.8)
    
    return {
        'breakout_rate': breakout_rate,
        'avg_follow_through': avg_follow_through,
        'days_analyzed': total_days,
        'confidence': confidence
    }


def analyze_vwap_intraday(intraday):
    intraday_copy = intraday.copy()
    
    # FIX 5: Add timezone handling (if data is in UTC)
    try:
        intraday_copy['Datetime'] = pd.to_datetime(intraday_copy['Datetime']).dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
    except:
        # Data might already be in local time or aware
        intraday_copy['Datetime'] = pd.to_datetime(intraday_copy['Datetime'])
    
    intraday_copy['Date'] = intraday_copy['Datetime'].dt.date
    intraday_copy['Time'] = intraday_copy['Datetime'].dt.time
    intraday_copy['Hour'] = intraday_copy['Datetime'].dt.hour
    intraday_copy['Minute'] = intraday_copy['Datetime'].dt.minute
    
    # FIX 5: Filter to market hours (09:15 - 15:30 IST)
    intraday_copy = intraday_copy[
        ((intraday_copy['Hour'] == 9) & (intraday_copy['Minute'] >= 15)) |
        ((intraday_copy['Hour'] >= 10) & (intraday_copy['Hour'] < 15)) |
        ((intraday_copy['Hour'] == 15) & (intraday_copy['Minute'] <= 30))
    ]
    
    days = intraday_copy.groupby('Date')
    reversion_count = 0
    total_observations = 0
    
    open_drive_returns = []
    midday_volatility = []
    close_returns = []
    
    # FIX 4: Better VWAP reversion tracking
    deviation_threshold = 0.002  # 0.20%
    reversion_threshold = 0.001  # 0.10%
    
    for date, day_data in days:
        day_data = day_data.sort_values('Datetime').reset_index(drop=True)
        
        if len(day_data) < 5:
            continue
        
        day_data['TypicalPrice'] = (day_data['High'] + day_data['Low'] + day_data['Close']) / 3
        day_data['TPV'] = day_data['TypicalPrice'] * day_data['Volume']
        day_data['VWAP'] = day_data['TPV'].cumsum() / day_data['Volume'].cumsum()
        
        # FIX 4: Track deviations and reversions properly
        already_counted = set()
        for i in range(len(day_data) - 1):
            if i in already_counted:
                continue
                
            vwap = day_data.iloc[i]['VWAP']
            close = day_data.iloc[i]['Close']
            deviation = abs(close - vwap) / vwap
            
            if deviation > deviation_threshold:
                # Look ahead for reversion
                for j in range(i+1, len(day_data)):
                    future_close = day_data.iloc[j]['Close']
                    future_vwap = day_data.iloc[j]['VWAP']
                    future_deviation = abs(future_close - future_vwap) / future_vwap
                    
                    if future_deviation <= reversion_threshold:
                        reversion_count += 1
                        already_counted.add(i)
                        break
                total_observations += 1
        
        # First hour analysis
        first_hour = day_data[day_data['Hour'] == day_data.iloc[0]['Hour']]
        if len(first_hour) >= 2:
            open_ret = ((first_hour.iloc[-1]['Close'] - first_hour.iloc[0]['Open']) / first_hour.iloc[0]['Open']) * 100
            open_drive_returns.append(open_ret)
        
        # FIX 5: Midday with safety check
        midday = day_data[(day_data['Hour'] >= 11) & (day_data['Hour'] < 14)]
        if len(midday) > 1:
            midday_vol = midday['Close'].pct_change().std() * 100
            if not np.isnan(midday_vol):
                midday_volatility.append(midday_vol)
        
        # Last hour analysis
        last_hour = day_data[day_data['Hour'] == day_data.iloc[-1]['Hour']]
        if len(last_hour) >= 2:
            close_ret = ((last_hour.iloc[-1]['Close'] - last_hour.iloc[0]['Open']) / last_hour.iloc[0]['Open']) * 100
            close_returns.append(close_ret)
    
    reversion_rate = (reversion_count / total_observations * 100) if total_observations > 0 else 0
    avg_open_drive = np.mean(open_drive_returns) if open_drive_returns else 0
    avg_midday_vol = np.mean(midday_volatility) if midday_volatility else 0
    avg_close = np.mean(close_returns) if close_returns else 0
    
    # FIX 6: Better confidence scoring
    sample_factor = np.sqrt(len(days)) / 30
    confidence = min(0.95, sample_factor * 0.8)
    
    return {
        'reversion_rate': reversion_rate,
        'open_drive': avg_open_drive,
        'midday_vol': avg_midday_vol,
        'close': avg_close,
        'confidence': confidence
    }


def generate_report(ticker, daily, intraday, results):
    os.makedirs('output', exist_ok=True)
    output_path = f'output/{ticker}_agent1_analysis.txt'
    
    with open(output_path, 'w') as f:
        f.write("=== AGENT 1: HISTORICAL DATA ANALYSIS ===\n")
        f.write(f"Stock: {ticker}\n")
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"Daily Data: {daily['Date'].min().strftime('%Y-%m-%d')} to {daily['Date'].max().strftime('%Y-%m-%d')}\n")
        f.write(f"15-min Data: {intraday['Datetime'].min().strftime('%Y-%m-%d')} to {intraday['Datetime'].max().strftime('%Y-%m-%d')}\n\n")
        
        f.write("SUPPORT & RESISTANCE\n")
        for period, levels in results['sr'].items():
            f.write(f"[{period} Lookback]\n")
            for i, level in enumerate(levels, 1):
                f.write(f"Level {i}: ${level['price']:.2f} | Touches: {level['touches']} | Avg Bounce: {level['avg_bounce']:.2f}% | Confidence: {level['confidence']:.2f}\n")
            f.write("\n")
        
        vp = results['volume_profile']
        f.write("VOLUME PROFILE\n")
        f.write(f"POC: ${vp['poc']:.2f}\n")
        f.write(f"VAH: ${vp['vah']:.2f} | VAL: ${vp['val']:.2f}\n")
        f.write(f"Top HVNs: {', '.join([f'${p:.2f}' for p in vp['hvns']])}\n")
        f.write(f"Top LVNs: {', '.join([f'${p:.2f}' for p in vp['lvns']])}\n")
        f.write(f"Confidence: {vp['confidence']:.2f}\n\n")
        
        gaps = results['gaps']
        f.write("GAP BEHAVIOR\n")
        f.write(f"Total Gaps: {gaps['total']}\n")
        f.write(f"Fill Rate (Same Day): {gaps['fill_same_day']:.2f}%\n")
        f.write(f"Fill Rate (1 Day): {gaps['fill_1day']:.2f}%\n")
        f.write(f"Fill Rate (5 Days): {gaps['fill_5day']:.2f}%\n")
        f.write(f"Avg Time to Fill: {gaps['avg_time']:.2f} days\n")
        f.write(f"Confidence: {gaps['confidence']:.2f}\n\n")
        
        hurst = results['hurst']
        f.write("HURST EXPONENT\n")
        f.write(f"H: {hurst['hurst']:.2f}\n")
        f.write(f"Interpretation: {hurst['interpretation']}\n")
        f.write(f"Confidence: {hurst['confidence']:.2f}\n\n")
        
        vol = results['volatility']
        f.write("VOLATILITY REGIME\n")
        f.write(f"Current Regime: {vol['regime']}\n")
        f.write(f"Volatility Percentile: {vol['percentile']:.2f}%\n")
        f.write(f"Confidence: {vol['confidence']:.2f}\n\n")
        
        corr = results['correlation']
        f.write("CORRELATION WITH NIFTY 50\n")
        f.write(f"5-Day: {corr['corr_5d']:.2f}\n")
        f.write(f"20-Day: {corr['corr_20d']:.2f}\n")
        f.write(f"60-Day: {corr['corr_60d']:.2f}\n")
        f.write(f"Confidence: {corr['confidence']:.2f}\n\n")
        
        dow = results['day_of_week']
        f.write("DAY-OF-WEEK SEASONALITY\n")
        for day, stats in dow['day_stats'].items():
            sign = '+' if stats['avg_return'] >= 0 else ''
            f.write(f"{day}: {sign}{stats['avg_return']:.2f}% ({stats['samples']} samples)\n")
        f.write(f"Strongest Day: {dow['strongest_day']} | Confidence: {dow['confidence']:.2f}\n\n")
        
        or_analysis = results['opening_range']
        f.write("OPENING RANGE ANALYSIS\n")
        f.write(f"OR Breakout Rate: {or_analysis['breakout_rate']:.2f}%\n")
        f.write(f"Avg Follow-Through: {or_analysis['avg_follow_through']:.2f}%\n")
        f.write(f"Days Analyzed: {or_analysis['days_analyzed']}\n")
        f.write(f"Confidence: {or_analysis['confidence']:.2f}\n\n")
        
        vwap = results['vwap_intraday']
        f.write("INTRADAY VWAP & TIME PATTERNS\n")
        f.write(f"VWAP Reversion Rate: {vwap['reversion_rate']:.2f}%\n")
        sign = '+' if vwap['open_drive'] >= 0 else ''
        f.write(f"Open Drive (First Hour): {sign}{vwap['open_drive']:.2f}% avg return\n")
        f.write(f"Midday (11am-2pm): {vwap['midday_vol']:.2f}% avg volatility\n")
        sign = '+' if vwap['close'] >= 0 else ''
        f.write(f"Close (Last Hour): {sign}{vwap['close']:.2f}% avg return\n")
        f.write(f"Confidence: {vwap['confidence']:.2f}\n\n")
        
        f.write("=== END OF ANALYSIS ===\n")
    
    return output_path


def main():
    ticker = input("Enter stock ticker (must match CSV filenames, e.g., RELIANCE.NS): ").strip()
    
    try:
        print(f"\nLoading data for {ticker}...")
        daily, intraday = load_data(ticker)
        
        print("Running analysis modules...")
        results = {}
        
        print("  - Support & Resistance...")
        results['sr'] = analyze_support_resistance(daily)
        
        print("  - Volume Profile...")
        results['volume_profile'] = analyze_volume_profile(daily)
        
        print("  - Gap Behavior...")
        results['gaps'] = analyze_gaps(daily)
        
        print("  - Hurst Exponent...")
        results['hurst'] = analyze_hurst(daily)
        
        print("  - Volatility Regime...")
        results['volatility'] = analyze_volatility_regime(daily)
        
        print("  - Correlation with NIFTY 50...")
        results['correlation'] = analyze_correlation_with_index(daily)
        
        print("  - Day-of-Week Seasonality...")
        results['day_of_week'] = analyze_day_of_week(daily)
        
        print("  - Opening Range Breakout...")
        results['opening_range'] = analyze_opening_range(intraday, daily)
        
        print("  - VWAP & Intraday Patterns...")
        results['vwap_intraday'] = analyze_vwap_intraday(intraday)
        
        print("\nGenerating report...")
        output_path = generate_report(ticker, daily, intraday, results)
        
        print(f"\n✓ Analysis complete! Report saved to: {output_path}")
        
    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please ensure CSV files exist in the data/ folder with the correct ticker name.")
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()