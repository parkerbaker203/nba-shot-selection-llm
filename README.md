# NBA Shot Selection LLM Bot 🏀

This project combines **data engineering**, **data science**, and **LLM integration** to analyze NBA shot selection.

## Features
- 📥 **Data Ingestion:** Pull NBA team and shot chart data using the `nba_api`.
- 🔄 **Transformation:** Clean and aggregate shot data for analysis and comparison.
- 📊 **Visualization:** Generate clean shot charts.
- 🤖 **LLM Integration:** Use a free LLM (via Ollama) to summarize team performance and suggest insights.


Must download ollama to run client side: https://ollama.com/download/windows
- Add ollama to PATH variables

Setup environment:
git clone (https://github.com/parkerbaker203/nba-shot-selection-llm.git)
cd nba-shot-selection-llm
py -m venv venv
source venv/bin/activate   # or .\venv\Scripts\Activate on Windows
pip install -r requirements.txt


Run code from terminal with this line:
>> py app/cli_bot.py
---