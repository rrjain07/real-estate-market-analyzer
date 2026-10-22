"""
Real Estate Market Analysis Tool - Pan-India Flask Web Application
Analyzes market trends, forecasts prices, and identifies investment opportunities
across major Indian Metros (Mumbai, Delhi NCR, Bangalore, Hyderabad, Pune, Chennai, Kolkata, Ahmedabad).
Tech Stack: Python (Pandas, NumPy, Plotly, BeautifulSoup), Flask.
"""

import json
from flask import Flask, render_template, request, jsonify
import plotly
import plotly.graph_objects as go
import plotly.express as px

import ml_engine
import scraper

app = Flask(__name__)

ml_engine.init_engine()


@app.context_processor
def inject_common():
    """Injects all supported Indian cities across all templates."""
    cities = ml_engine.get_available_cities()
    return {
        "cities": cities,
        "default_city": "Bangalore"
    }


@app.route("/api/localities")
def api_localities():
    """Returns list of localities for the selected city."""
    city = request.args.get("city", "Bangalore")
    localities = ml_engine.get_locations_for_city(city)
    return jsonify({"city": city, "localities": localities})


@app.route("/")
def index():
    """Dashboard homepage with Pan-India overview & investment spotlight."""
    selected_city = request.args.get("city", "All")
    overview = ml_engine.get_pan_india_overview(selected_city)
    top_opportunities = ml_engine.find_pan_india_opportunities(city_filter=selected_city, max_budget_lakhs=180, min_roi_pct=12.0)[:4]
    
    # Plotly Chart: National Metro Rate Comparison
    trends_data = ml_engine.get_pan_india_trends()
    metro_names = [b["city"] for b in trends_data["city_benchmarks"]]
    metro_rates = [b["avg_rate"] for b in trends_data["city_benchmarks"]]

    fig = go.Figure(data=[
        go.Bar(
            x=metro_names,
            y=metro_rates,
            marker_color=["#2563EB" if c != "Mumbai (MMR)" else "#EF4444" for c in metro_names],
            text=[f"₹{r:,}" for r in metro_rates],
            textposition='auto',
        )
    ])
    fig.update_layout(
        title="Average Rate / Sq.Ft. Across Indian Metros (₹)",
        margin=dict(l=20, r=20, t=40, b=60),
        height=280,
        xaxis_tickangle=-25,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor="#E2E8F0")
    )
    metro_chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    initial_localities = ml_engine.get_locations_for_city("Bangalore")

    return render_template(
        "index.html",
        selected_city=selected_city,
        overview=overview,
        top_opportunities=top_opportunities,
        metro_chart_json=metro_chart_json,
        initial_localities=initial_localities
    )


@app.route("/trends")
def trends():
    """Market trends analysis comparing all Indian Metros and prime localities."""
    trends_data = ml_engine.get_pan_india_trends()
    
    # 1. Metro Comparison Chart
    metro_names = [b["city"] for b in trends_data["city_benchmarks"]]
    metro_rates = [b["avg_rate"] for b in trends_data["city_benchmarks"]]
    metro_cagrs = [b["baseline_cagr"] for b in trends_data["city_benchmarks"]]
    metro_yields = [b["rental_yield"] for b in trends_data["city_benchmarks"]]

    fig_metro = go.Figure(data=[
        go.Bar(
            name="Avg. Rate / Sq.Ft. (₹)",
            x=metro_names,
            y=metro_rates,
            marker_color="#2563EB",
            text=[f"₹{r:,}" for r in metro_rates],
            textposition='auto'
        )
    ])
    fig_metro.update_layout(
        title="India's Top Real Estate Metros Ranked by Rate per Sq. Ft.",
        margin=dict(l=20, r=20, t=40, b=60),
        height=360,
        xaxis_tickangle=-25,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor="#E2E8F0")
    )
    chart_metro_json = json.dumps(fig_metro, cls=plotly.utils.PlotlyJSONEncoder)

    # 2. Growth vs Yield Chart (Bubble / Bar)
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Bar(
        name="Historical CAGR (%)",
        x=metro_names,
        y=metro_cagrs,
        marker_color="#10B981"
    ))
    fig_growth.add_trace(go.Bar(
        name="Rental Yield (%)",
        x=metro_names,
        y=metro_yields,
        marker_color="#F59E0B"
    ))
    fig_growth.update_layout(
        title="Annual Capital Growth (CAGR) vs. Rental Yield (%)",
        barmode='group',
        margin=dict(l=20, r=20, t=40, b=60),
        height=360,
        xaxis_tickangle=-25,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(gridcolor="#E2E8F0")
    )
    chart_growth_json = json.dumps(fig_growth, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "trends.html",
        city_benchmarks=trends_data["city_benchmarks"],
        top_localities=trends_data["top_localities"],
        chart_metro_json=chart_metro_json,
        chart_growth_json=chart_growth_json
    )


@app.route("/forecast", methods=["GET", "POST"])
def forecast():
    """Forecasts prices and projects 5-year capital appreciation for any Indian city."""
    result = None
    forecast_chart_json = None
    
    city = request.form.get("city", "Bangalore")
    location = request.form.get("location", "Whitefield")
    sqft = float(request.form.get("sqft", 1250))
    bhk = int(request.form.get("bhk", 2))
    bath = int(request.form.get("bath", 2))

    localities = ml_engine.get_locations_for_city(city)
    if location not in localities:
        location = localities[0]

    if request.method == "POST":
        predicted_lakhs = ml_engine.predict_price_pan_india(city, location, sqft, bhk, bath)
        forecast_info = ml_engine.forecast_price_pan_india(city, location, predicted_lakhs)
        
        price_per_sqft = round((predicted_lakhs * 100000) / sqft)
        
        # Monthly EMI calculation (8.5% for 20 yrs on 80% loan)
        loan_amount = predicted_lakhs * 0.8 * 100000
        monthly_rate = (8.5 / 12) / 100
        n_months = 20 * 12
        emi = round(loan_amount * monthly_rate * ((1 + monthly_rate) ** n_months) / (((1 + monthly_rate) ** n_months) - 1))

        result = {
            "city": city,
            "location": location,
            "sqft": sqft,
            "bhk": bhk,
            "bath": bath,
            "price_lakhs": predicted_lakhs,
            "price_per_sqft": price_per_sqft,
            "emi": emi,
            "growth": forecast_info
        }

        # Plotly Trajectory Curve
        x_years = ["Current", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
        y_values = [predicted_lakhs] + forecast_info["trajectory"]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x_years,
            y=y_values,
            mode='lines+markers+text',
            name='Forecast Valuation',
            line=dict(color='#2563EB', width=3),
            marker=dict(size=8, color='#1D4ED8'),
            text=[f"₹{v:.1f}L" for v in y_values],
            textposition="top center"
        ))
        fig.update_layout(
            title=f"5-Year Forecast Trajectory ({city} - {location})",
            xaxis_title="Timeline",
            yaxis_title="Valuation (₹ Lakhs)",
            height=340,
            margin=dict(l=20, r=20, t=50, b=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor="#E2E8F0")
        )
        forecast_chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "forecast.html",
        selected_city=city,
        selected_location=location,
        localities=localities,
        sqft=sqft,
        bhk=bhk,
        bath=bath,
        result=result,
        forecast_chart_json=forecast_chart_json
    )


@app.route("/investments")
def investments():
    """Identifies high-yield investment properties across India."""
    city_filter = request.args.get("city", "All")
    budget = float(request.args.get("budget", 250))
    min_roi = float(request.args.get("min_roi", 10.0))

    opportunities = ml_engine.find_pan_india_opportunities(
        city_filter=city_filter,
        max_budget_lakhs=budget,
        min_roi_pct=min_roi
    )

    return render_template(
        "investments.html",
        selected_city=city_filter,
        opportunities=opportunities,
        budget=budget,
        min_roi=min_roi
    )


@app.route("/scraper", endpoint="scraper")
@app.route("/scraper", endpoint="web_scraper")
def web_scraper():
    """Scrapes live real estate property listings across any Indian city using BeautifulSoup."""
    city = request.args.get("city", "Mumbai")
    scraped_listings = scraper.scrape_real_estate_listings(locality=city, limit=10)

    return render_template(
        "scraper.html",
        listings=scraped_listings,
        city=city
    )


# --- REST APIs ---

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON API to get price prediction and 5-year forecast across any Indian city."""
    data = request.get_json() or {}
    city = data.get("city", "Bangalore")
    location = data.get("location", "Whitefield")
    sqft = float(data.get("sqft", 1200))
    bhk = int(data.get("bhk", 2))
    bath = int(data.get("bath", 2))

    price_lakhs = ml_engine.predict_price_pan_india(city, location, sqft, bhk, bath)
    forecast_info = ml_engine.forecast_price_pan_india(city, location, price_lakhs)

    return jsonify({
        "status": "success",
        "city": city,
        "location": location,
        "predicted_price_lakhs": price_lakhs,
        "price_per_sqft": round((price_lakhs * 100000) / sqft),
        "forecast": forecast_info
    })


@app.route("/api/opportunities", methods=["GET"])
def api_opportunities():
    """JSON API for nationwide investment opportunities."""
    city = request.args.get("city", "All")
    budget = float(request.args.get("budget", 200))
    min_roi = float(request.args.get("min_roi", 9.0))

    results = ml_engine.find_pan_india_opportunities(city, budget, min_roi)
    return jsonify({
        "status": "success",
        "count": len(results),
        "opportunities": results
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
