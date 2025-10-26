# flight_agent_app.py
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
# Define Flight Tool
# -----------------------------
def get_flights(query: str) -> str:
    import re
    import pandas as pd
    from amadeus import ResponseError

    try:
        # Regex to extract cities and dates
        pattern = r"from\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)\s+on\s+(\d{4}-\d{2}-\d{2})(?:\s+returning\s+on\s+(\d{4}-\d{2}-\d{2}))?"
        m = re.search(pattern, query, re.IGNORECASE)
        if not m:
            return "❌ Invalid query format."

        origin_city, dest_city, dep_date, ret_date = m.groups()
        dep_date = dep_date.replace("/", "-")
        ret_date = ret_date.replace("/", "-") if ret_date else None
        # origin_city, dest_city = origin_city.strip(), dest_city.strip()

        # Get IATA codes
        origin_res = amadeus.reference_data.locations.get(keyword=origin_city.strip(), subType="CITY").data
        dest_res = amadeus.reference_data.locations.get(keyword=dest_city.strip(), subType="CITY").data
        if not origin_res or not dest_res:
            return "❌ Could not find IATA code for origin or destination."
        origin = origin_res[0]["iataCode"]
        dest = dest_res[0]["iataCode"]

        # Flight search
        kwargs = dict(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=dep_date,
            adults=1,
            max=5
        )
        if ret_date:
            kwargs["returnDate"] = ret_date

        res = amadeus.shopping.flight_offers_search.get(**kwargs).data
        if not res:
            return "⚠️ No flights found for the given route/date."

        # Separate outbound and return flights
        outbound = []
        return_flights = []

        for offer in res:
            for itinerary in offer["itineraries"]:
                for seg in itinerary["segments"]:
                    flight_info = {
                        "Airline": seg["carrierCode"],
                        "Flight No": seg["number"],
                        "From": seg["departure"]["iataCode"],
                        "To": seg["arrival"]["iataCode"],
                        "Departure": seg["departure"]["at"],
                        "Arrival": seg["arrival"]["at"],
                        "Price": offer["price"]["total"],
                        "Direct": len(itinerary["segments"]) == 1
                    }
                    if seg["departure"]["iataCode"] == origin:
                        outbound.append(flight_info)
                    elif seg["departure"]["iataCode"] == dest:
                        return_flights.append(flight_info)

        # Convert to Markdown tables
        md_outbound = pd.DataFrame(outbound).to_markdown(index=False)
        md_return = pd.DataFrame(return_flights).to_markdown(index=False) if return_flights else None

        result = f"### Outbound Flights\n{md_outbound}"
        if md_return:
            result += f"\n\n### Return Flights\n{md_return}"

        return result

    except ResponseError as e:
        return f"Amadeus API error: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error: {str(e)}"

# -----------------------------
# Define Tool
# -----------------------------
flight_tool = Tool(
    name="Flight Search",
    func=get_flights,
    description="Get available flights from one city to another. Query like 'Find flights from Delhi to Mumbai on 2025-12-20 returning on 2025-12-25'.",
    return_direct=True
)

# -----------------------------
# Initialize Agent
# -----------------------------
agent = initialize_agent(
    tools=[flight_tool],
    llm=llm,
    agent_type=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("✈️ Flight Finder Agent")
st.write("Enter travel details below:")

# Input fields
source_city = st.text_input("Source city:")
dest_city = st.text_input("Destination city:")
travel_date = st.date_input("Departure date")
return_date = st.date_input("Return date (optional)")

# Search button
if st.button("Search Flights"):
    if source_city and dest_city and travel_date:
        query = f"Find flights from {source_city} to {dest_city} on {travel_date}"
        if return_date:
            query += f" returning on {return_date}"

        try:
            response = agent.run(query)
        except Exception:
            response = get_flights(query)

        # Display outbound and return flights one below another
        st.markdown(response)
    else:
        st.warning("Please fill in source, destination, and departure date.")