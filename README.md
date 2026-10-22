# 🏢 Pan-India Real Estate Market Analysis Tool

> **Project Requirement:** *Analyzes market trends, forecasts prices, and identifies investment opportunities.*  
> **Tech Stack:** **Python (Pandas, NumPy, Plotly, BeautifulSoup), Flask**  
> **Coverage:** **8 Major Indian Metros** (Mumbai MMR, Delhi NCR, Bangalore, Hyderabad, Pune, Chennai, Kolkata, Ahmedabad)

A comprehensive real estate intelligence platform built with Python and Flask. The application analyzes residential property datasets across India's top 8 economic metros, predicts property market valuations, forecasts 5-year capital appreciation trajectories, identifies high-yield investment opportunities, and scrapes property listings using BeautifulSoup.

---

## 🌟 Pan-India Features & Capabilities

### 1. 🇮🇳 Multi-Metro Market Coverage
- **Mumbai (MMR):** South Mumbai (Worli/Colaba), Bandra West, Andheri West, Powai, Thane West, Navi Mumbai.
- **Delhi NCR:** Gurgaon (Golf Course Road, Cyber City, Sohna Rd), Noida (Sec 150, 62), South Delhi, Greater Noida.
- **Bangalore:** Whitefield, Electronic City, Indiranagar, Koramangala, HSR Layout, Hebbal, Bellandur.
- **Hyderabad:** Hitec City, Gachibowli, Madhapur, Jubilee Hills, Banjara Hills, Tellapur, Kokapet.
- **Pune:** Hinjewadi, Wakad, Baner, Koregaon Park, Kharadi, Kothrud, Viman Nagar.
- **Chennai:** OMR (IT Expressway), ECR, Anna Nagar, Velachery, T Nagar, Adyar.
- **Kolkata:** New Town, Salt Lake (Sec V), Ballygunge, Alipore, EM Bypass.
- **Ahmedabad:** SG Highway, GIFT City Corridor, Prahlad Nagar, Satellite, Bopal.

### 2. 📈 National Market Trends (`/trends`)
- **National Metro Comparison:** Interactive Plotly bar chart comparing rate per sq.ft. across all 8 Indian Metros.
- **CAGR vs. Rental Yield:** Dual-bar visualization contrasting capital appreciation vs. annual rental yield.
- **High-Growth Corridors Table:** Detailed benchmarks across 50+ prime Indian localities.

### 3. 🧠 Pan-India Price Forecasting (`/forecast`)
- **Dynamic City-to-Locality Selector:** Changing the metro city dynamically loads real localities.
- **5-Year Growth Trajectory:** Forecasts valuation at Year 1, 2, 3, 4, and 5 based on locality economic tiers (6.8% - 13.5% CAGR).
- **Home Loan EMI Calculator:** Calculates monthly installments for home loans.

### 4. 💎 National Investment Opportunities Finder (`/investments`)
- Filter high-yield properties across **All India** or specific metros.
- **Investment Opportunity Index (IOI Score 1-99):** Multi-factor composite index combining undervaluation discount %, projected CAGR %, and rental yield %.

### 5. 🕷️ Pan-India Web Scraper (`/scraper`)
- Scrapes recent real estate property listings across any Indian city using **BeautifulSoup4** and **Requests**.

---

## 🚀 Running the App

```powershell
cd C:\Users\amitr\.gemini\antigravity\scratch\real-estate-market-analyzer
python app.py
```
Open **`http://localhost:5000`** in your browser.
