# Financial Advisor MCP Server

A fully local AI-powered personal finance assistant built with the Model Context Protocol (MCP). Ask questions about your bank transactions in plain English — no cloud, no API costs, no data leaving your machine.

---

## What it does

You export your bank transactions as a CSV file. The MCP server loads that data and exposes it as a set of tools. A locally running Llama 3.1 model connects to those tools and lets you have a natural language conversation about your finances directly in your terminal.

```
You: give me a summary of my financials for January
Assistant: For the month of January, these are the summaries:
Total Income: $3200.00
Total Spending: $1612.61
Net Balance: $1587.39

You: show me all my eating out expenses
Assistant: Transactions in 'Eating Out':
07/01/2024 - Costa Coffee - $-4.75
14/01/2024 - Nandos - $-28.50
20/01/2024 - Deliveroo - $-22.99
25/01/2024 - Waterfall Bar - $-38.00
...
Total: $-228.73
```

---

## How it works

The project has two files:

**`server.py`** — the MCP server. Loads your CSV on startup and exposes three tools Llama can call: `get_summary`, `filter_by_date`, and `filter_by_category`. Each tool is a Python function decorated with `@mcp.tool()`. The function's docstring is what the model reads to decide when to call it.

**`main.py`** — the conversation loop. Connects to the MCP server, loads the tool definitions, and runs a terminal chat interface. On every message it sends your question plus the full conversation history to Llama via Ollama. If Llama decides to call a tool, `main.py` executes it against the MCP server and sends the result back to Llama to form a final answer.

```
You type a question
        ↓
main.py sends question + tool definitions to Llama (via Ollama)
        ↓
Llama decides which tool to call
        ↓
main.py calls the tool on server.py
        ↓
server.py queries the CSV and returns real data
        ↓
Llama forms a natural language answer
        ↓
Answer printed in terminal
```

---

## Tools

These tools are just simple tools to demonstrate the proof of concept. Adding more tools, with more precise functionalities
and purposes will strengthen the MCP and allow the LLM to perform much more in terms of functionality

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_summary` | Total income, spending, and net balance for a month | `month` (string) |
| `filter_by_date` | All transactions between two dates | `start_date`, `end_date` (strings) |
| `filter_by_category` | All transactions in a spending category | `category` (string), `month` (optional) |

---

## Tech stack

- **Python 3.11**
- **[Ollama](https://ollama.com)** — runs Llama 3.1 locally
- **[Llama 3.1 8B](https://ollama.com/library/llama3.1)** — the local language model
- **[mcp](https://github.com/anthropics/mcp)** — Anthropic's MCP framework
- **[pandas](https://pandas.pydata.org)** — CSV loading and data filtering
- **[python-dateutil](https://dateutil.readthedocs.io)** — flexible date parsing

---

## Setup

**1. Install Ollama and pull Llama 3.1**

```bash
brew install ollama
ollama pull llama3.1
```

**2. Clone the repo**

```bash
git clone https://github.com/vg3131/financial-advisor-mcp-server.git
cd financial-advisor-mcp-server
```

**3. Create a virtual environment and install dependencies**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install mcp pandas python-dateutil ollama
```

**4. Add your transactions CSV**

Export your bank transactions as a CSV file named `transactions.csv` and place it in the project root. The file should have these columns:

```
Date,Description,Amount,Category,Balance
```

Dates should be in DD/MM/YYYY format. Negative amounts are spending, positive amounts are income.

**5. Run the assistant**

Make sure Ollama is running first:

```bash
ollama serve
```

Then in a new terminal:

```bash
python main.py
```

---

## Example questions

```
give me a summary for January
show me all my transport expenses
what did I spend on groceries in February
show me transactions between January 10 2024 and January 20 2024
what categories do I have
```

---

## Limitations

This project was built to understand MCP servers and local model tool use. A few honest observations from stress testing:

- **Single tool questions work reliably** — summaries, category filters, date ranges all return accurate data
- **Multi-tool chaining is unreliable** — questions requiring two tool calls (e.g. comparing two months) sometimes result in the model hallucinating figures instead of calling both tools
- **Natural language date parsing has limits** — specifying the full year (e.g. "January 2024") produces more reliable results than relative references like "last month"
- **Root cause** — these are mostly model ceiling limitations of Llama 3.1 8B, not code problems. A stronger model (Claude, GPT-4, or Llama 70B) would handle these cases reliably. Some of the issue blame can be attributed to the constant need to strengthen the
prompts via sophisticated prompt engineering

---

## What I learned

- How MCP servers work — the protocol, tool definitions, and the request/response cycle
- How a local LLM connects to and uses external tools via Ollama
- How prompt engineering shapes model behaviour — and where its limits are
- The difference between model limitations and prompt engineering problems
- How to stress test an AI system and document failure modes
