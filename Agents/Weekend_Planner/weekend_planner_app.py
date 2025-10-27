# multi_agent_planner.py (Final Version with Separate Flight Tables)

from dotenv import load_dotenv
import os, re
import requests
import streamlit as st
import pandas as pd
from amadeus import Client, ResponseError

# --- LangChain Imports ---
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType 

# -----------------------------
# 1. SETUP & INITIALIZATION
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Initialize Clients & LLM 
amadeus = Client(client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET)
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0, openai_api_key=OPENAI_API_KEY)


# -----------------------------
# 2. TOOL FUNCTION DEFINITIONS
# -----------------------------

def get_weather(city: str) -> str:
    """Get the current weather for a city in the world."""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        data = requests.get(url).json()

        if data.get("cod") != 200:
            return f"❌ Weather API Error for {city.title()}: {data.get('message', 'Unknown error')}"

        weather = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        
        return (
            f"### ☀️ Weather Information\n"
            f"The current weather in **{city.title()}** is **{weather}** with a temperature of **{temp}°C**.\n"
        )
    except Exception as e:
        return f"⚠️ Weather Tool Error: {str(e)}"

def get_flights(query: str) -> str:
    """
    Find available flights. Input must be a string formatted like:
    'FROM: [Origin City] TO: [Destination City] DEPART: [YYYY-MM-DD] RETURN: [YYYY-MM-DD]'
    """
    try:
        pattern = r"FROM:\s*(.+?)\s*TO:\s*(.+?)\s*DEPART:\s*(\d{4}-\d{2}-\d{2})\s*RETURN:\s*(\d{4}-\d{2}-\d{2})"
        m = re.search(pattern, query, re.IGNORECASE)
        if not m:
            return "❌ Flight Tool Error: Input must be 'FROM: [Origin] TO: [Dest] DEPART: [YYYY-MM-DD] RETURN: [YYYY-MM-DD]'"

        origin_city, dest_city, dep_date, ret_date = [g.strip() for g in m.groups()]

        origin_res = amadeus.reference_data.locations.get(keyword=origin_city, subType="CITY").data
        dest_res = amadeus.reference_data.locations.get(keyword=dest_city, subType="CITY").data
        if not origin_res or not dest_res:
            return "❌ Could not find IATA code for flight origin or destination."
        origin_iata = origin_res[0]["iataCode"]
        dest_iata = dest_res[0]["iataCode"]

        kwargs = dict(originLocationCode=origin_iata, destinationLocationCode=dest_iata, departureDate=dep_date, adults=1, max=3, returnDate=ret_date)
        res = amadeus.shopping.flight_offers_search.get(**kwargs).data
        if not res: return "⚠️ No flights found for the given route/date."
        
        # --- NEW LOGIC FOR SEPARATE TABLES ---
        outbound_data = []
        return_data = []
        
        for offer in res:
            itinerary = offer["itineraries"]
            
            # Identify legs
            outbound_segments = itinerary[0]["segments"]
            return_segments = itinerary[1]["segments"] if len(itinerary) > 1 else []
            
            if not return_segments and len(outbound_segments) > 1:
                midpoint = len(outbound_segments) // 2
                return_segments = outbound_segments[midpoint:]
                outbound_segments = outbound_segments[:midpoint]

            # --- Price Details (Apply to both tables for context) ---
            price_total = offer.get('price', {}).get('total', 'N/A')
            price_currency = offer.get('price', {}).get('currency', '')
            total_price_str = f"**{price_total} {price_currency}**" if price_total != 'N/A' else 'Price Unavailable'

            # --- Outbound Details ---
            out_first_seg = outbound_segments[0] if outbound_segments else None
            out_flight_str = "N/A"
            out_stops = "N/A"
            out_dep_time = "N/A"
            if out_first_seg:
                carrier = out_first_seg['carrierCode']
                flight_num = out_first_seg['number']
                out_dep_time = out_first_seg["departure"]["at"].split("T")[1][:5]
                layovers = len(outbound_segments) - 1
                out_flight_str = f"{carrier}{flight_num}"
                out_stops = f"{layovers} stop{'s' if layovers != 1 else ''}"
                
                outbound_data.append({
                    "Total Offer Price": total_price_str,
                    "Flight Number": out_flight_str,
                    "Departure Time": out_dep_time,
                    "Stops": out_stops,
                    "Departure Airport": out_first_seg["departure"]["iataCode"],
                    "Arrival Airport": outbound_segments[-1]["arrival"]["iataCode"]
                })
            
            # --- Return Details ---
            ret_first_seg = return_segments[0] if return_segments else None
            ret_flight_str = "N/A"
            ret_stops = "N/A"
            ret_dep_time = "N/A"
            if ret_first_seg:
                carrier = ret_first_seg['carrierCode']
                flight_num = ret_first_seg['number']
                ret_dep_time = ret_first_seg["departure"]["at"].split("T")[1][:5]
                layovers = len(return_segments) - 1
                ret_flight_str = f"{carrier}{flight_num}"
                ret_stops = f"{layovers} stop{'s' if layovers != 1 else ''}"
                
                return_data.append({
                    "Total Offer Price": total_price_str,
                    "Flight Number": ret_flight_str,
                    "Departure Time": ret_dep_time,
                    "Stops": ret_stops,
                    "Departure Airport": ret_first_seg["departure"]["iataCode"],
                    "Arrival Airport": return_segments[-1]["arrival"]["iataCode"]
                })

        # --- Generate Final Markdown Output ---
        outbound_markdown = f"\n### ✈️ Outbound Flights ({origin_iata} to {dest_iata})\n\n{pd.DataFrame(outbound_data).to_markdown(index=False)}"
        return_markdown = f"\n### ✈️ Return Flights ({dest_iata} to {origin_iata})\n\n{pd.DataFrame(return_data).to_markdown(index=False)}"
        
        return outbound_markdown + "\n\n" + return_markdown

    except ResponseError as e:
        return f"❌ Amadeus API error (Flights): {e}"
    except Exception as e:
        return f"⚠️ Flight Tool Unexpected Error: {str(e)}"

def get_hotels(query: str) -> str:
    """
    Find hotels in a city. Input must be a string formatted like:
    'CITY: [City Name] CHECKIN: [YYYY-MM-DD] CHECKOUT: [YYYY-MM-DD]'
    """
    try:
        pattern = r"CITY:\s*(.+?)\s*CHECKIN:\s*(\d{4}-\d{2}-\d{2})\s*CHECKOUT:\s*(\d{4}-\d{2}-\d{2})"
        m = re.search(pattern, query, re.IGNORECASE)
        if not m:
            return "❌ Hotel Tool Error: Input must be 'CITY: [City] CHECKIN: [YYYY-MM-DD] CHECKOUT: [YYYY-MM-DD]'"

        city, check_in, check_out = [g.strip() for g in m.groups()]

        loc = amadeus.reference_data.locations.get(keyword=city, subType="CITY").data
        if not loc:
            return f"❌ Could not find city '{city}' for lodging search."
        city_code = loc[0].get("iataCode")

        hotels_resp = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        hotel_ids = [h["hotelId"] for h in getattr(hotels_resp, "data", [])[:3] if "hotelId" in h]

        if not hotel_ids: return f"⚠️ No top hotels found for **{city}**."
        
        offers_resp = amadeus.shopping.hotel_offers_search.get(
            hotelIds=",".join(hotel_ids), checkInDate=check_in, checkOutDate=check_out, adults=1 
        )
        offers = getattr(offers_resp, "data", [])

        hotel_list = []
        for offer in offers:
            hotel = offer.get("hotel", {})
            price = offer.get("offers", [{}])[0].get("price", {})
            
            address_info = hotel.get('address', {})
            street = address_info.get('lines', ['N/A'])[0]
            city_name = address_info.get('cityName', '')
            postal_code = address_info.get('postalCode', '')
            country_code = address_info.get('countryCode', '')
            full_address = f"{street}, {city_name} {postal_code}, {country_code}"
            if full_address.strip(', ') == 'N/A,,':
                 full_address = "Address details unavailable"

            hotel_list.append({
                "Hotel Name": hotel.get("name", "N/A"),
                "Address": full_address,
                "Price": f"**{price.get('total', 'N/A')} {price.get('currency', '')}**",
            })
        
        return f"\n### 🏨 Lodging Options\n\nThe top available hotel offers in **{city}** for your dates are:\n{pd.DataFrame(hotel_list).to_markdown(index=False)}"

    except ResponseError as e:
        return f"❌ Amadeus API error (Hotels): {e}"
    except Exception as e:
        return f"⚠️ Hotel Tool Unexpected Error: {str(e)}"


# -----------------------------
# 3. INITIALIZE THE MASTER MULTI-AGENT
# -----------------------------

# Define Tools - Tool names use underscores
tools = [
    Tool(
        name="weather_info", 
        func=get_weather,
        description="""
        Use this tool FIRST. Useful for finding the current weather of a city. 
        The input MUST be only the city name, e.g., 'Paris'.
        """
    ),
    Tool(
        name="flight_finder", 
        func=get_flights,
        description="""
        Use this tool SECOND. Useful for finding flights. 
        Input MUST be in the exact format: 'FROM: [Origin City] TO: [Destination City] DEPART: [YYYY-MM-DD] RETURN: [YYYY-MM-DD]'.
        """
    ),
    Tool(
        name="hotel_finder", 
        func=get_hotels,
        description="""
        Use this tool THIRD. Useful for finding hotels. 
        Input MUST be in the exact format: 'CITY: [City Name] CHECKIN: [YYYY-MM-DD] CHECKOUT: [YYYY-MM-DD]'.
        """
    ),
]

# Initialize the Master Agent - AgentType switched to OPENAI_FUNCTIONS
master_agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS, 
    verbose=True, 
    handle_parsing_errors=True,
)


# -----------------------------
# 4. STREAMLIT UI & AGENT EXECUTION
# -----------------------------

st.title("✈️🏨 Weekend Planner 🤖")
st.markdown("This uses a single **Master Agent (LLM)** to decide the sequence and inputs for the three specialized tools.")

# Input fields
current_city = st.text_input("1. Your Current City (for flight origin):", "Delhi")
dest_city = st.text_input("2. Destination City:", "Paris")
default_dep_date = pd.to_datetime('today').date()
default_ret_date = pd.to_datetime('today').date() + pd.Timedelta(days=2) 
dep_date = st.date_input("3. Departure Date", value=default_dep_date)
ret_date = st.date_input("4. Return Date", value=default_ret_date)

if st.button("🚀 Plan Trip (Multi-Agent)"):
    if not (current_city and dest_city and dep_date and ret_date):
        st.error("Please fill in all required fields.")
    else:
        # 1. Format Dates for LLM to use in tool calls
        dep_date_str = dep_date.strftime("%Y-%m-%d")
        ret_date_str = ret_date.strftime("%Y-%m-%d")

        # 2. Construct the single, complex prompt for the Master Agent
        complex_prompt = f"""
        Execute a full travel plan based on the following steps and details, ensuring the final output is explanatory and structured using the information provided by the tools.
        
        **Steps:**
        1. Find the weather for the destination city.
        2. Find flights (round trip).
        3. Find lodging.
        
        **Trip Details:**
        - Origin City: {current_city}
        - Destination City: {dest_city}
        - Departure Date: {dep_date_str}
        - Return Date: {ret_date_str}

        **Final Response Structure (CRITICAL):**
        The final answer must be a single, cohesive markdown response. Include a summary introduction, then use the markdown output (including the tables) from the tools. The flight information must be presented in two separate tables: one for outbound flights and one for return flights. The Lodging Options table must include the hotel name, price, and address.
        """
        
        st.subheader("Master Agent Execution Log")
        with st.spinner("Master Agent is reasoning and delegating tasks... (Check your terminal for verbose output)"):
            
            try:
                final_response = master_agent.run(complex_prompt)
                
                st.markdown("---")
                st.subheader("✅ Final Trip Plan Summary")
                st.write(final_response) 
                st.balloons()
            except Exception as e:
                st.error(f"Master Agent failed to complete the task. Please check your API keys and the terminal output. Error: {e}")