"""
Charts Module
Matplotlib chart generation for financial visualizations
"""

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import pandas as pd
import numpy as np
from typing import Optional, List
from datetime import datetime
import os
from data_fetcher import StockData
import config
import utils


def setup_chart_style() -> None:
    """Configure matplotlib style settings"""
    try:
        plt.style.use(config.CHART_STYLE)
    except:
        plt.style.use('default')
    
    # Set default figure parameters
    plt.rcParams['figure.figsize'] = config.CHART_FIGSIZE
    plt.rcParams['figure.dpi'] = config.CHART_DPI
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12


# Initialize chart style
setup_chart_style()



def create_revenue_chart(data: StockData, save_path: str) -> Optional[str]:
    """Generate bar chart of revenue trend"""
    if data.income_statement is None or data.income_statement.empty:
        return None
    
    try:
        df = data.income_statement
        if 'Total Revenue' not in df.index:
            return None
        
        # Get last 4 years
        revenue_data = df.loc['Total Revenue']
        years = revenue_data.index[:4] if len(revenue_data) >= 4 else revenue_data.index
        values = [revenue_data[year] / 1_00_00_000 for year in years]  # Convert to Crores
        year_labels = [str(year)[:4] for year in years]
        
        if len(values) < 2:
            return None
        
        # Create chart
        fig, ax = plt.subplots()
        ax.bar(year_labels, values, color='#2E86AB', alpha=0.8)
        ax.set_title(f'Revenue Trend - {data.ticker}', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Revenue (₹ Crores)')
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        plt.close()
        return None


def create_profit_chart(data: StockData, save_path: str) -> Optional[str]:
    """Generate bar chart of net income trend"""
    if data.income_statement is None or data.income_statement.empty:
        return None
    
    try:
        df = data.income_statement
        if 'Net Income' not in df.index:
            return None
        
        # Get last 4 years
        profit_data = df.loc['Net Income']
        years = profit_data.index[:4] if len(profit_data) >= 4 else profit_data.index
        values = [profit_data[year] / 1_00_00_000 for year in years]  # Convert to Crores
        year_labels = [str(year)[:4] for year in years]
        
        if len(values) < 2:
            return None
        
        # Create chart with color based on positive/negative
        colors = ['#06A77D' if v >= 0 else '#D62828' for v in values]
        
        fig, ax = plt.subplots()
        ax.bar(year_labels, values, color=colors, alpha=0.8)
        ax.set_title(f'Net Income Trend - {data.ticker}', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Net Income (₹ Crores)')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        plt.close()
        return None


def create_eps_chart(data: StockData, save_path: str) -> Optional[str]:
    """Generate line chart of EPS trend"""
    if data.income_statement is None or data.income_statement.empty:
        return None
    
    try:
        df = data.income_statement
        # Try different possible EPS field names
        eps_field = None
        for field in ['Basic EPS', 'Diluted EPS', 'Basic Average Shares']:
            if field in df.index:
                eps_field = field
                break
        
        if not eps_field:
            return None
        
        eps_data = df.loc[eps_field]
        years = eps_data.index[:4] if len(eps_data) >= 4 else eps_data.index
        values = [eps_data[year] for year in years]
        year_labels = [str(year)[:4] for year in years]
        
        if len(values) < 2:
            return None
        
        fig, ax = plt.subplots()
        ax.plot(year_labels, values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
        ax.set_title(f'EPS Trend - {data.ticker}', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('EPS (₹)')
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        plt.close()
        return None



def create_debt_equity_chart(data: StockData, save_path: str) -> Optional[str]:
    """Generate stacked bar chart of debt vs equity"""
    if data.balance_sheet is None or data.balance_sheet.empty:
        return None
    
    try:
        df = data.balance_sheet
        
        # Find debt and equity fields
        debt_field = 'Total Debt' if 'Total Debt' in df.index else None
        equity_field = 'Stockholders Equity' if 'Stockholders Equity' in df.index else None
        
        if not debt_field or not equity_field:
            return None
        
        debt_data = df.loc[debt_field]
        equity_data = df.loc[equity_field]
        
        years = debt_data.index[:4] if len(debt_data) >= 4 else debt_data.index
        debt_values = [debt_data[year] / 1_00_00_000 for year in years]  # Convert to Crores
        equity_values = [equity_data[year] / 1_00_00_000 for year in years]
        year_labels = [str(year)[:4] for year in years]
        
        if len(debt_values) < 2:
            return None
        
        fig, ax = plt.subplots()
        ax.bar(year_labels, debt_values, label='Debt', color='#D62828', alpha=0.8)
        ax.bar(year_labels, equity_values, bottom=debt_values, label='Equity', color='#06A77D', alpha=0.8)
        
        ax.set_title(f'Debt vs Equity - {data.ticker}', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Amount (₹ Crores)')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        plt.close()
        return None


def create_margin_chart(data: StockData, save_path: str) -> Optional[str]:
    """Generate line chart of profit margin trend"""
    if data.income_statement is None or data.income_statement.empty:
        return None
    
    try:
        df = data.income_statement
        
        # Calculate margins from revenue and net income
        if 'Total Revenue' not in df.index or 'Net Income' not in df.index:
            return None
        
        revenue = df.loc['Total Revenue']
        net_income = df.loc['Net Income']
        
        years = revenue.index[:4] if len(revenue) >= 4 else revenue.index
        margins = [(net_income[year] / revenue[year] * 100) if revenue[year] != 0 else 0 for year in years]
        year_labels = [str(year)[:4] for year in years]
        
        if len(margins) < 2:
            return None
        
        fig, ax = plt.subplots()
        ax.plot(year_labels, margins, marker='o', linewidth=2, markersize=8, color='#06A77D')
        ax.set_title(f'Profit Margin Trend - {data.ticker}', fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Net Profit Margin (%)')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        ax.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        
        return save_path
    except Exception as e:
        plt.close()
        return None


def create_roe_chart(data: StockData, save_path: str) -> Optional[str]:
    """Generate line chart of ROE trend"""
    # Note: ROE trend calculation requires historical data
    # For now, we'll skip this if we don't have the data
    # This would need historical ROE values which aren't always available
    return None



def generate_all_charts(data: StockData, ticker: str) -> List[str]:
    """
    Generate all charts and return list of file paths
    
    Args:
        data: StockData object
        ticker: Stock ticker symbol
    
    Returns:
        List of successfully generated chart file paths
    """
    # Create charts directory
    timestamp = utils.get_timestamp()
    charts_dir = os.path.join(config.CHARTS_DIR, ticker)
    utils.create_directory(charts_dir)
    
    generated_charts = []
    
    # Revenue chart
    revenue_path = os.path.join(charts_dir, f"{ticker}_revenue_{timestamp}.png")
    result = create_revenue_chart(data, revenue_path)
    if result:
        generated_charts.append(result)
    
    # Profit chart
    profit_path = os.path.join(charts_dir, f"{ticker}_profit_{timestamp}.png")
    result = create_profit_chart(data, profit_path)
    if result:
        generated_charts.append(result)
    
    # EPS chart
    eps_path = os.path.join(charts_dir, f"{ticker}_eps_{timestamp}.png")
    result = create_eps_chart(data, eps_path)
    if result:
        generated_charts.append(result)
    
    # Debt vs Equity chart
    debt_equity_path = os.path.join(charts_dir, f"{ticker}_debt_equity_{timestamp}.png")
    result = create_debt_equity_chart(data, debt_equity_path)
    if result:
        generated_charts.append(result)
    
    # Margin chart
    margin_path = os.path.join(charts_dir, f"{ticker}_margin_{timestamp}.png")
    result = create_margin_chart(data, margin_path)
    if result:
        generated_charts.append(result)
    
    # ROE chart (currently not implemented due to data limitations)
    # roe_path = os.path.join(charts_dir, f"{ticker}_roe_{timestamp}.png")
    # result = create_roe_chart(data, roe_path)
    # if result:
    #     generated_charts.append(result)
    
    return generated_charts
