from mcp.server.fastmcp import FastMCP
import pandas as pd
import dateutil.parser

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
transactions = pd.read_csv(os.path.join(BASE_DIR, "transactions.csv"))
transactions = transactions.dropna(how="all")
transactions["Date"] = pd.to_datetime(transactions["Date"], dayfirst=True)

mcp = FastMCP("financial analyst")

# Valid months for get_sumamry defensive
valid_months = {
    "january": "January",
    "february": "February",
    "march": "March",
    "april": "April",
    "may": "May",
    "june": "June",
    "july": "July",
    "august": "August",
    "september": "September",
    "october": "October",
    "november": "November",
    "december": "December"
}

# Category aliases — maps what the user might say to what's in the CSV
category_aliases = {
    "food": "Groceries",
    "supermarket": "Groceries",
    "grocery": "Groceries",
    "groceries": "Groceries",
    "eating out": "Eating Out",
    "restaurants": "Eating Out",
    "restaurant": "Eating Out",
    "takeaway": "Eating Out",
    "dining": "Eating Out",
    "entertainment": "Entertainment",
    "fun": "Entertainment",
    "streaming": "Entertainment",
    "transport": "Transport",
    "travel": "Transport",
    "uber": "Transport",
    "shopping": "Shopping",
    "clothes": "Shopping",
    "clothing": "Shopping",
    "utilities": "Utilities",
    "bills": "Utilities",
    "bill": "Utilities",
    "subscriptions": "Subscriptions",
    "subscription": "Subscriptions",
    "health": "Health",
    "gym": "Health",
    "fitness": "Health",
    "rent": "Rent",
    "income": "Income",
    "salary": "Income",
    "wages": "Income",
}

# Phase 1 test functions

@mcp.tool()
def test_connection():
    """Use this when the user wants to test or verify that the MCP server is connected and working"""
    return "connected"

@mcp.tool()
def test_name():
    """When the user asks what name this assistant goes by or what this system is called"""
    return "Jimmy Dodd"

@mcp.tool()
def test_stated_purpose():
    """When the user asks what the stated purpose or mission of this assistant is"""
    return "Ensure financial stability in a tough economy!"

# Phase 2 basic mcp tools

@mcp.tool()
def get_summary(month: str):
    """When the user asks for a summary of their total income, total spending, and net balance for a specific month"""
    month_lower = month.lower().strip()
    if month_lower not in valid_months:
        return "Invalid month. Please specify a month name like January or February."
    month = valid_months[month_lower]

    monthly = transactions[transactions["Date"].dt.strftime("%B") == month]

    if monthly.empty:
        return f"No transaction data found for {month}. The available months in your data are: {', '.join(transactions['Date'].dt.strftime('%B %Y').unique().tolist())}"

    income = monthly[monthly["Amount"] > 0]["Amount"].sum()
    spending = monthly[monthly["Amount"] < 0]["Amount"].sum()
    net = income + spending

    result = f"For the month of {month}, these are the summaries:\nTotal Income: ${income:.2f}\nTotal Spending: ${spending:.2f}\nNet Balance: ${net:.2f}"
    return result

@mcp.tool()
def filter_by_date(start_date: str, end_date: str):
    """When the user needs all transactions between 2 specific dates"""
    start = pd.to_datetime(dateutil.parser.parse(start_date))
    end = pd.to_datetime(dateutil.parser.parse(end_date))

    mask = (transactions["Date"] >= start) & (transactions["Date"] <= end)
    filtered = transactions[mask]

    if filtered.empty:
        return "No transactions were found between those two dates, clarify the dates from the user"
    
    result = f"Between the start date: {start} and end date: {end} these are the transactions found:\n"
    for _, row in filtered.iterrows():
        result += f"{row['Date']} - {row['Description']} - ${row['Amount']:.2f}\n"

    return result

@mcp.tool()
def filter_by_category(category: str, month: str = None):
    """When the user asks to see all transactions in a specific spending category such as groceries, eating out, transport, entertainment, shopping, utilities, subscriptions, health, rent, or income. Optionally accepts a month name to narrow results to a specific month."""
    category_lower = category.lower().strip()
    mapped_category = category_aliases.get(category_lower, category.title())

    filtered = transactions[transactions["Category"].str.lower() == mapped_category.lower()]

    if month:
        month_lower = month.lower().strip()
        month_normalised = valid_months.get(month_lower, month.title())
        filtered = filtered[filtered["Date"].dt.strftime("%B") == month_normalised]

    if filtered.empty:
        available = transactions["Category"].unique().tolist()
        return f"No transactions found for category '{category}'{' in ' + month if month else ''}. Available categories are: {', '.join(available)}"

    total = filtered["Amount"].sum()
    month_label = f" in {month.title()}" if month else ""
    result = f"Transactions in '{mapped_category}'{month_label}:\n"
    for _, row in filtered.iterrows():
        result += f"{row['Date'].strftime('%d/%m/%Y')} - {row['Description']} - ${row['Amount']:.2f}\n"
    result += f"\nTotal: ${total:.2f}"
    return result


if __name__ == "__main__":
    mcp.run()