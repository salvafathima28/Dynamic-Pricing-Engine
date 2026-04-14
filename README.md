# 🚀 Dynamic Pricing Engine — PriceIQ

**Price Smarter. Sell Faster.**

An AI-powered dynamic pricing system that analyzes market data, competitor prices, and demand signals to recommend optimal pricing strategies in real time.

---

## 📌 Overview

PriceIQ is a full-stack pricing intelligence platform designed to help businesses:

- Adjust prices dynamically based on market conditions
- Maximize profit margins
- Stay competitive in real-time
- Identify pricing opportunities and risks

---

## ✨ Key Features

- 📊 **Real-Time Pricing Dashboard**
- 🤖 **AI-Based Price Recommendations**
- 📉 **Profit Margin Analysis**
- 🚨 **Smart Alerts for Price Optimization**
- 📈 **Price History Tracking**
- 🧠 **Machine Learning Pipeline (Demand Forecasting + RL)**

---

## 🖼️ Screenshots

### 🏠 Dashboard
![Dashboard](screenshots/dashboard.png)

### 📊 Profit Margins
![Insights](screenshots/profit.png)

### 🚨 Alerts System
![Alerts](screenshots/alerts.png)

### 📈 Update Prices
![updste_prices](screenshots/update.png)

---

## 🏗️ Project Structure

dynamic-pricing-engine/
│
├── app.py # Main Streamlit app
├── scheduler.py # Fetches and updates market data
├── price_manager.py # Pricing logic and updates
├── pricing_engine.py # Core pricing decision logic
├── market_fetcher.py # Competitor data simulation
├── demand_model.py # Demand prediction model
├── forecaster.py # Forecasting logic
├── config.py # Product configurations
├── products.csv # Product dataset
│
├── *.db # Local databases
├── *.pkl / *.pth # ML models
│
└── README.md


---

## ⚙️ Tech Stack

- **Frontend/UI:** Streamlit  
- **Backend:** Python  
- **Data Processing:** Pandas, NumPy  
- **Visualization:** Plotly  
- **Machine Learning:** XGBoost, Reinforcement Learning (DQN)  
- **Database:** SQLite  

---

## 🧠 How It Works

1. **Market Data Collection**
   - Fetches competitor prices
   - Calculates market averages

2. **Pricing Engine**
   - Compares your price vs market
   - Determines action:
     - Raise
     - Lower
     - Hold

3. **Profit Optimization**
   - Calculates margin and profit
   - Suggests optimal pricing

4. **ML Pipeline**
   - Demand forecasting using features:
     - Price
     - Competitor price
     - Time signals
     - Trend score
   - Reinforcement Learning for pricing strategy

---

## 🚀 Getting Started

### 1. Clone the Repository

git clone https://github.com/salvafathima28/dynamic-pricing-engine.git
cd dynamic-pricing-engine

1. Create Virtual Environment
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate   # Mac/Linux
2. Install Dependencies
pip install -r requirements.txt
3. Run Scheduler (Important)
python scheduler.py
4. Run the App
streamlit run app.py
