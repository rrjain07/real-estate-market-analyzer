"""
Pan-India Real Estate Analytics & ML Engine
Supports major Indian Tier-1 and Tier-2 Metros:
Mumbai (MMR), Delhi NCR, Bangalore, Hyderabad, Pune, Chennai, Kolkata, Ahmedabad.
Analyzes market trends, forecasts prices, and identifies investment opportunities nationwide.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Supported Indian Metro Markets and baseline market characteristics
CITIES_DATA = {
    "Bangalore": {
        "avg_rate": 6450,
        "median_price": 78.5,
        "rental_yield": 4.1,
        "baseline_cagr": 10.2,
        "localities": {
            "Whitefield": {"multiplier": 1.15, "tier": "IT Corridor", "cagr": 10.8, "rental_yield": 4.2},
            "Electronic City": {"multiplier": 0.85, "tier": "Tech Hub / Affordable", "cagr": 9.8, "rental_yield": 4.4},
            "Indiranagar": {"multiplier": 1.95, "tier": "Prime Central Core", "cagr": 8.0, "rental_yield": 3.6},
            "Koramangala": {"multiplier": 1.90, "tier": "Startup / Prime Hub", "cagr": 8.2, "rental_yield": 3.7},
            "HSR Layout": {"multiplier": 1.45, "tier": "High Demand Residential", "cagr": 9.5, "rental_yield": 4.0},
            "Hebbal": {"multiplier": 1.25, "tier": "Airport Corridor", "cagr": 11.2, "rental_yield": 3.9},
            "Sarjapur Road": {"multiplier": 1.10, "tier": "Rapid Expansion", "cagr": 10.5, "rental_yield": 4.3},
            "Bellandur": {"multiplier": 1.30, "tier": "Outer Ring Road IT", "cagr": 10.2, "rental_yield": 4.3},
            "Yelahanka": {"multiplier": 0.95, "tier": "North Bangalore Growth", "cagr": 11.0, "rental_yield": 3.8},
            "Marathahalli": {"multiplier": 1.05, "tier": "East Bangalore Commercial", "cagr": 9.0, "rental_yield": 4.2}
        }
    },
    "Mumbai (MMR)": {
        "avg_rate": 21500,
        "median_price": 195.0,
        "rental_yield": 2.8,
        "baseline_cagr": 7.5,
        "localities": {
            "South Mumbai (Worli/Colaba)": {"multiplier": 2.40, "tier": "Ultra Luxury / Island City", "cagr": 6.8, "rental_yield": 2.4},
            "Bandra West": {"multiplier": 2.10, "tier": "Prime Western Suburb", "cagr": 7.2, "rental_yield": 2.6},
            "Andheri West": {"multiplier": 1.35, "tier": "Commercial & Media Hub", "cagr": 7.5, "rental_yield": 2.9},
            "Powai": {"multiplier": 1.25, "tier": "Lakeside Tech Hub", "cagr": 8.0, "rental_yield": 3.2},
            "Thane West": {"multiplier": 0.65, "tier": "Major Suburban Growth", "cagr": 8.5, "rental_yield": 3.1},
            "Navi Mumbai (Vashi/Kharghar)": {"multiplier": 0.60, "tier": "Airport & Metro Infra", "cagr": 9.2, "rental_yield": 3.3},
            "Borivali West": {"multiplier": 0.90, "tier": "Established Western Suburb", "cagr": 7.0, "rental_yield": 2.8},
            "Goregaon East": {"multiplier": 1.05, "tier": "Corporate Hub / Film City", "cagr": 7.8, "rental_yield": 3.0}
        }
    },
    "Delhi NCR": {
        "avg_rate": 9800,
        "median_price": 125.0,
        "rental_yield": 3.4,
        "baseline_cagr": 9.0,
        "localities": {
            "Gurgaon (Golf Course Road)": {"multiplier": 2.20, "tier": "Prime Corporate Corridor", "cagr": 11.0, "rental_yield": 3.8},
            "Gurgaon (Cyber City / DLF)": {"multiplier": 1.80, "tier": "MNC Commercial Center", "cagr": 10.2, "rental_yield": 3.9},
            "Gurgaon (Sohna Road)": {"multiplier": 0.90, "tier": "Growth Suburb", "cagr": 9.5, "rental_yield": 3.6},
            "Noida (Sector 150)": {"multiplier": 0.95, "tier": "Expressway Sports City", "cagr": 10.0, "rental_yield": 3.5},
            "Noida (Sector 62)": {"multiplier": 0.85, "tier": "Established IT District", "cagr": 8.5, "rental_yield": 3.7},
            "Greater Noida West": {"multiplier": 0.55, "tier": "Affordable High-Rise", "cagr": 9.2, "rental_yield": 3.3},
            "South Delhi (GK / Hauz Khas)": {"multiplier": 2.30, "tier": "Heritage Prime Core", "cagr": 6.8, "rental_yield": 2.6},
            "Dwarka (Delhi)": {"multiplier": 1.15, "tier": "Sub-City Diplomatic Enclave", "cagr": 8.5, "rental_yield": 3.0}
        }
    },
    "Hyderabad": {
        "avg_rate": 6900,
        "median_price": 88.0,
        "rental_yield": 4.2,
        "baseline_cagr": 11.5,
        "localities": {
            "Hitec City": {"multiplier": 1.40, "tier": "Core IT Corridor", "cagr": 12.0, "rental_yield": 4.5},
            "Gachibowli": {"multiplier": 1.30, "tier": "Financial District", "cagr": 11.8, "rental_yield": 4.4},
            "Madhapur": {"multiplier": 1.25, "tier": "Tech Commercial Hub", "cagr": 11.0, "rental_yield": 4.3},
            "Jubilee Hills": {"multiplier": 2.10, "tier": "Ultra Luxury / Celebrities", "cagr": 8.5, "rental_yield": 3.2},
            "Banjara Hills": {"multiplier": 2.00, "tier": "Prime Diplomatic Core", "cagr": 8.8, "rental_yield": 3.3},
            "Kondapur": {"multiplier": 1.10, "tier": "High Demand Tech Residential", "cagr": 11.5, "rental_yield": 4.2},
            "Tellapur": {"multiplier": 0.90, "tier": "High Growth Western Suburb", "cagr": 13.0, "rental_yield": 4.0},
            "Kokapet": {"multiplier": 1.35, "tier": "Neopolis SEZ Corridor", "cagr": 13.5, "rental_yield": 4.1}
        }
    },
    "Pune": {
        "avg_rate": 6800,
        "median_price": 72.0,
        "rental_yield": 3.9,
        "baseline_cagr": 8.8,
        "localities": {
            "Hinjewadi": {"multiplier": 0.95, "tier": "Rajiv Gandhi IT Park", "cagr": 9.5, "rental_yield": 4.3},
            "Wakad": {"multiplier": 1.05, "tier": "IT Gateway Residential", "cagr": 9.2, "rental_yield": 4.1},
            "Baner": {"multiplier": 1.35, "tier": "Upscale West Commercial", "cagr": 9.0, "rental_yield": 3.8},
            "Koregaon Park": {"multiplier": 1.85, "tier": "Elite Cultural / Lifestyle", "cagr": 7.2, "rental_yield": 3.3},
            "Kharadi": {"multiplier": 1.20, "tier": "EON IT Park Corridor", "cagr": 9.8, "rental_yield": 4.2},
            "Kothrud": {"multiplier": 1.40, "tier": "Established Cultural Suburb", "cagr": 7.5, "rental_yield": 3.2},
            "Viman Nagar": {"multiplier": 1.30, "tier": "Airport / Business Hub", "cagr": 8.5, "rental_yield": 3.7}
        }
    },
    "Chennai": {
        "avg_rate": 6200,
        "median_price": 68.0,
        "rental_yield": 3.7,
        "baseline_cagr": 7.8,
        "localities": {
            "OMR (IT Expressway)": {"multiplier": 0.95, "tier": "IT Corridor", "cagr": 8.8, "rental_yield": 4.2},
            "ECR (East Coast Road)": {"multiplier": 1.45, "tier": "Coastal Luxury Living", "cagr": 8.0, "rental_yield": 3.1},
            "Anna Nagar": {"multiplier": 1.80, "tier": "Prime Northern Core", "cagr": 7.0, "rental_yield": 3.0},
            "Velachery": {"multiplier": 1.15, "tier": "South Commercial Junction", "cagr": 8.2, "rental_yield": 3.8},
            "T Nagar": {"multiplier": 1.90, "tier": "Central Retail Heartland", "cagr": 6.8, "rental_yield": 3.2},
            "Adyar": {"multiplier": 1.85, "tier": "Prestigious South Chennai", "cagr": 7.2, "rental_yield": 2.9}
        }
    },
    "Kolkata": {
        "avg_rate": 5100,
        "median_price": 54.0,
        "rental_yield": 3.5,
        "baseline_cagr": 7.2,
        "localities": {
            "New Town (Rajarhat)": {"multiplier": 1.15, "tier": "Modern Smart City / IT Hub", "cagr": 8.5, "rental_yield": 3.8},
            "Salt Lake (Sector V)": {"multiplier": 1.30, "tier": "Premier Tech Park", "cagr": 7.8, "rental_yield": 4.0},
            "Ballygunge": {"multiplier": 2.10, "tier": "Heritage South Kolkata", "cagr": 6.2, "rental_yield": 2.6},
            "Alipore": {"multiplier": 2.30, "tier": "Ultra-HNW Luxury District", "cagr": 6.0, "rental_yield": 2.4},
            "EM Bypass": {"multiplier": 1.20, "tier": "High-Rise Growth Corridor", "cagr": 8.0, "rental_yield": 3.5}
        }
    },
    "Ahmedabad": {
        "avg_rate": 4600,
        "median_price": 52.0,
        "rental_yield": 3.6,
        "baseline_cagr": 8.5,
        "localities": {
            "SG Highway": {"multiplier": 1.25, "tier": "Corporate Growth Axis", "cagr": 9.2, "rental_yield": 3.9},
            "GIFT City Corridor": {"multiplier": 1.40, "tier": "International Financial Hub", "cagr": 12.0, "rental_yield": 4.2},
            "Prahlad Nagar": {"multiplier": 1.35, "tier": "Prime West Commercial", "cagr": 8.0, "rental_yield": 3.5},
            "Satellite": {"multiplier": 1.20, "tier": "Established Western Zone", "cagr": 7.8, "rental_yield": 3.4},
            "Bopal (South Bopal)": {"multiplier": 0.85, "tier": "Affordable Residential Expansion", "cagr": 9.5, "rental_yield": 3.8}
        }
    }
}


def get_available_cities():
    """Returns list of supported Indian Metros."""
    return list(CITIES_DATA.keys())


def get_locations_for_city(city: str):
    """Returns localities for a specific city."""
    if city in CITIES_DATA:
        return list(CITIES_DATA[city]["localities"].keys())
    return list(CITIES_DATA["Bangalore"]["localities"].keys())


def get_pan_india_overview(selected_city: str = "All"):
    """Returns high level national or city metrics."""
    if selected_city == "All":
        avg_rates = [c["avg_rate"] for c in CITIES_DATA.values()]
        median_prices = [c["median_price"] for c in CITIES_DATA.values()]
        total_localities = sum(len(c["localities"]) for c in CITIES_DATA.values())
        return {
            "scope": "All India (8 Major Metros)",
            "avg_price_per_sqft": int(np.mean(avg_rates)),
            "median_price_lakhs": round(float(np.mean(median_prices)), 1),
            "total_cities": len(CITIES_DATA),
            "total_localities": total_localities,
            "most_expensive_city": "Mumbai (MMR)",
            "highest_growth_city": "Hyderabad"
        }
    else:
        city_info = CITIES_DATA.get(selected_city, CITIES_DATA["Bangalore"])
        return {
            "scope": selected_city,
            "avg_price_per_sqft": city_info["avg_rate"],
            "median_price_lakhs": city_info["median_price"],
            "total_cities": 1,
            "total_localities": len(city_info["localities"]),
            "most_expensive_city": selected_city,
            "highest_growth_city": selected_city
        }


def predict_price_pan_india(city: str, location: str, sqft: float, bhk: int, bath: int) -> float:
    """
    Predicts property price in Lakhs across any Indian city,
    factoring in city baseline rate, locality premium, BHK scale, and bathroom count.
    """
    city_info = CITIES_DATA.get(city, CITIES_DATA["Bangalore"])
    base_city_rate = city_info["avg_rate"]
    
    loc_info = city_info["localities"].get(location, {"multiplier": 1.0})
    multiplier = loc_info["multiplier"]

    # Base rate per sqft for this location
    effective_rate = base_city_rate * multiplier

    # Configuration adjustment: higher BHK has slight economy of scale per sqft, but luxury finish premium
    bhk_premium = 1.0 + ((bhk - 2) * 0.04) if bhk > 2 else (0.97 if bhk == 1 else 1.0)
    bath_adj = (bath - 2) * 35000 if bath != 2 else 0

    price_inr = (sqft * effective_rate * bhk_premium) + bath_adj
    price_lakhs = round(price_inr / 100000, 2)
    return max(8.0, price_lakhs)


def forecast_price_pan_india(city: str, location: str, current_price_lakhs: float) -> dict:
    """
    Computes 1, 3, and 5-year capital appreciation forecasts based on
    city-specific economic indicators and locality infrastructure tiers.
    """
    city_info = CITIES_DATA.get(city, CITIES_DATA["Bangalore"])
    loc_info = city_info["localities"].get(
        location,
        {"tier": "General Urban Zone", "cagr": city_info["baseline_cagr"], "rental_yield": city_info["rental_yield"]}
    )

    cagr_pct = loc_info["cagr"]
    cagr_decimal = cagr_pct / 100.0

    years = [1, 2, 3, 4, 5]
    trajectory = [
        round(current_price_lakhs * ((1 + cagr_decimal) ** y), 2)
        for y in years
    ]

    return {
        "city": city,
        "location": location,
        "tier": loc_info["tier"],
        "cagr_percent": cagr_pct,
        "rental_yield": loc_info["rental_yield"],
        "current_val": current_price_lakhs,
        "year_1": trajectory[0],
        "year_3": trajectory[2],
        "year_5": trajectory[4],
        "trajectory": trajectory,
        "years": years
    }


def get_pan_india_trends():
    """Generates comparative data across all Indian Metros and their top localities."""
    # 1. City comparison
    city_benchmarks = []
    for city, data in CITIES_DATA.items():
        city_benchmarks.append({
            "city": city,
            "avg_rate": data["avg_rate"],
            "median_price": data["median_price"],
            "rental_yield": data["rental_yield"],
            "baseline_cagr": data["baseline_cagr"]
        })

    # Sort cities by rate
    city_benchmarks = sorted(city_benchmarks, key=lambda x: x["avg_rate"], reverse=True)

    # 2. Top prime localities nationally
    national_prime_localities = []
    for city, cdata in CITIES_DATA.items():
        for loc, ldata in cdata["localities"].items():
            loc_rate = int(cdata["avg_rate"] * ldata["multiplier"])
            national_prime_localities.append({
                "city": city,
                "location": loc,
                "tier": ldata["tier"],
                "rate_per_sqft": loc_rate,
                "cagr": ldata["cagr"],
                "rental_yield": ldata["rental_yield"]
            })

    national_prime_localities = sorted(national_prime_localities, key=lambda x: x["rate_per_sqft"], reverse=True)

    return {
        "city_benchmarks": city_benchmarks,
        "top_localities": national_prime_localities
    }


def find_pan_india_opportunities(city_filter: str = "All", max_budget_lakhs: float = 200, min_roi_pct: float = 9.0):
    """
    Identifies high-yield investment properties across India or within a selected city.
    Calculates Investment Opportunity Index (IOI) Score (1 - 99).
    """
    opportunities = []
    cities_to_scan = [city_filter] if city_filter != "All" and city_filter in CITIES_DATA else list(CITIES_DATA.keys())

    # Generate realistic opportunities based on market properties
    sample_variations = [
        {"bhk": 2, "sqft": 1150, "bath": 2, "discount": 14.5},
        {"bhk": 3, "sqft": 1550, "bath": 3, "discount": 11.2},
        {"bhk": 2, "sqft": 1280, "bath": 2, "discount": 16.0},
        {"bhk": 1, "sqft": 680, "bath": 1, "discount": 12.8},
        {"bhk": 3, "sqft": 1720, "bath": 3, "discount": 9.5}
    ]

    prop_id = 1
    for c_name in cities_to_scan:
        c_info = CITIES_DATA[c_name]
        for loc_name, loc_data in c_info["localities"].items():
            base_rate = int(c_info["avg_rate"] * loc_data["multiplier"])
            
            for var in sample_variations[:2]:
                # Apply discount to create an undervalued opportunity
                discount = var["discount"]
                prop_rate = int(base_rate * (1 - discount / 100))
                prop_price_lakhs = round((prop_rate * var["sqft"]) / 100000, 2)

                if max_budget_lakhs > 0 and prop_price_lakhs > max_budget_lakhs:
                    continue

                rental_yield = loc_data["rental_yield"]
                cagr = loc_data["cagr"]
                total_roi = round(rental_yield + cagr, 1)

                if total_roi < min_roi_pct:
                    continue

                # IOI calculation
                ioi_score = int(np.clip(
                    (discount * 1.6) + (cagr * 3.2) + (rental_yield * 4.5),
                    25,
                    98
                ))

                opportunities.append({
                    "id": prop_id,
                    "city": c_name,
                    "location": loc_name,
                    "tier": loc_data["tier"],
                    "bhk": var["bhk"],
                    "bath": var["bath"],
                    "total_sqft": var["sqft"],
                    "price_lakhs": prop_price_lakhs,
                    "price_per_sqft": prop_rate,
                    "area_avg_rate": base_rate,
                    "discount_pct": discount,
                    "rental_yield": rental_yield,
                    "projected_cagr": cagr,
                    "total_roi": total_roi,
                    "ioi_score": ioi_score
                })
                prop_id += 1

    # Sort opportunities by highest IOI score
    opportunities = sorted(opportunities, key=lambda x: x["ioi_score"], reverse=True)
    return opportunities[:40]


def init_engine():
    """Pan-India engine startup routine."""
    print(f"Pan-India Real Estate Engine initialized with {len(CITIES_DATA)} Metros.")
