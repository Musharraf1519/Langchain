# lodging_agent_app.py
from dotenv import load_dotenv
import os, re
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
import streamlit as st
import pandas as pd
from amadeus import Client, ResponseError

# -----------------------------
# Load API keys
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET")

# -----------------------------
# Initialize Amadeus client
# -----------------------------
amadeus = Client(client_id=AMADEUS_CLIENT_ID, client_secret=AMADEUS_CLIENT_SECRET)

# -----------------------------
# Initialize LLM
# -----------------------------
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, openai_api_key=OPENAI_API_KEY)

# -----------------------------
# Define Hotel Tool
# -----------------------------
def get_hotels(query: str) -> str:
    try:
        pattern = r"in\s+([A-Za-z\s]+)\s+from\s+(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})"
        m = re.search(pattern, query, re.IGNORECASE)
        if not m:
            return "❌ Invalid query format. Example: 'Find hotels in Paris from 2025-11-01 to 2025-11-05'"

        city, check_in, check_out = m.groups()
        city = city.strip()

        # Get IATA city code
        loc = amadeus.reference_data.locations.get(keyword=city, subType="CITY")
        if not loc or not getattr(loc, "data", None):
            return f"❌ Could not find city '{city}'."
        city_code = loc.data[0].get("iataCode")

        # Get hotels in the city
        hotels_resp = amadeus.reference_data.locations.hotels.by_city.get(cityCode=city_code)
        hotels = getattr(hotels_resp, "data", [])[:5]
        if not hotels:
            return f"⚠️ No hotels found for {city}."

        hotel_ids = [h["hotelId"] for h in hotels if "hotelId" in h]
        if not hotel_ids:
            return f"⚠️ No hotel IDs found for {city}."

        # Get hotel offers
        try:
            offers_resp = amadeus.shopping.hotel_offers_search.get(
                hotelIds=",".join(hotel_ids),
                checkInDate=check_in,
                checkOutDate=check_out,
                adults=2
            )
            offers = getattr(offers_resp, "data", [])
        except Exception:
            offers = []

        # Prepare results
        hotel_list = []
        for h in hotels:
            o = next((x for x in offers if x.get("hotel", {}).get("hotelId") == h["hotelId"]), {})
            offer = o.get("offers", [{}])[0] if o else {}
            price = offer.get("price", {}).get("total", "N/A")
            currency = offer.get("price", {}).get("currency", "")
            name = h.get("name", "N/A")
            address = ", ".join(h.get("address", {}).get("lines", ["N/A"]))

            hotel_list.append({
                "Hotel Name": name,
                "Address": address,
                "Price": price,
                "Currency": currency
            })

        if not hotel_list:
            return f"⚠️ No hotel offers found for {city}."

        df = pd.DataFrame(hotel_list)
        md_table = df.to_markdown(index=False)
        return f"### Hotels in {city}\n{md_table}"

    except ResponseError as e:
        return f"Amadeus API error: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

# -----------------------------
# Define Tool
# -----------------------------
hotel_tool = Tool(
    name="Hotel Finder",
    func=get_hotels,
    description="Find hotels in a city. Example: 'Find hotels in Paris from 2025-11-01 to 2025-11-05'.",
    return_direct=True
)

# -----------------------------
# Initialize Agent
# -----------------------------
agent = initialize_agent(
    tools=[hotel_tool],
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🏨 Lodging Finder Agent")
st.write("Enter your hotel search details below:")

city = st.text_input("City:")
check_in = st.date_input("Check-in date")
check_out = st.date_input("Check-out date")

if st.button("Search Hotels"):
    if city and check_in and check_out:
        query = f"Find hotels in {city} from {check_in} to {check_out}"
        try:
            response = agent.run(query)
        except Exception:
            response = get_hotels(query)
        st.markdown(response)
    else:
        st.warning("Please fill in all details (city, check-in, and check-out).")
