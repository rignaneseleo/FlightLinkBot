import pandas as pd
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Airline:
    code_iata: str = ""  # 2 letters
    code_icao: str = ""
    name: str = ""
    country: str = ""


@dataclass
class Airport:
    code_iata: str = ""  # 3 letters
    code_icao: str = ""
    name: str = ""
    city: str = ""


@dataclass
class Route:
    code_IATA: str = ""
    code_ICAO: str = ""
    airline: Airline = Airline()
    departure_time: str = ""
    departure_airport: Airport = Airport()
    arrival_airport: Airport = Airport()

    def getIATASplitCode(self) -> List[str]:
        return re.split("(\d+)", self.code_IATA)

    def getICAOSplitCode(self) -> List[str]:
        return re.split("(\d+)", self.code_ICAO)

    def getTripComLink(self) -> str:
        return f"https://www.trip.com/flights/status-{self.code_IATA}"

    def getFlightAwareLink(self) -> str:
        return f"https://flightaware.com/live/flight/{self.code_ICAO}"

    def getPlaneMapperLink(self) -> str:
        return f"https://www.planemapper.com/?flight={self.code_IATA}"

    def getFlightStatsLink(self) -> str:
        code_split = self.getIATASplitCode()
        return f"https://www.flightstats.com/v2/flight-tracker/{code_split[0]}/{code_split[1]}"

    def getIconUrl(self) -> str:
        code_split = self.getICAOSplitCode()
        return f"https://raw.githubusercontent.com/sexym0nk3y/airline-logos/main/logos/{code_split[0]}.png"


class DataSet:
    def __init__(self):
        print("Loading dataset...")
        self.airports_df = self._load_airports()
        self.routes_df = self._load_routes()
        self.airlines_df = self._load_airlines()

    def _load_airports(self) -> pd.DataFrame:
        df = pd.read_csv(
            "data/airports.csv", usecols=["iata_code", "name", "municipality"]
        )
        df["full_name"] = (
            df["name"] + " - " + df["municipality"] + " [" + df["iata_code"] + "]"
        )
        return df

    def _load_routes(self) -> pd.DataFrame:
        return pd.read_csv(
            "data/routes.tsv",
            sep="\t",
            usecols=[
                "CallSign",
                "Operator_ICAO",
                "FromAirport_ICAO",
                "ToAirport_ICAO",
                "FromAirport_Time",
            ],
            low_memory=False,
        )

    def _load_airlines(self) -> pd.DataFrame:
        return pd.read_csv("data/airlines.csv", low_memory=False)

    def find_route(self, input_str: str) -> List[Route]:
        try:
            cities = [x.strip() for x in re.split("[-\s]", input_str) if x.strip()]
            if len(cities) < 2:
                return []

            city_from, city_to = cities[0], cities[1]

            departure_airports = self.airports_df[
                self.airports_df["full_name"].str.contains(
                    city_from, case=False, na=False
                )
            ]["iata_code"]
            arrival_airports = self.airports_df[
                self.airports_df["full_name"].str.contains(
                    city_to, case=False, na=False
                )
            ]["iata_code"]

            possible_routes = self.routes_df[
                self.routes_df["FromAirport_ICAO"].isin(departure_airports)
                & self.routes_df["ToAirport_ICAO"].isin(arrival_airports)
            ]

            result = []
            for route_data in possible_routes.itertuples():
                route = Route()
                route.code_IATA = route_data.CallSign

                # Set departure airport details
                route.departure_airport.code_iata = route_data.FromAirport_ICAO
                dep_airport = self.airports_df[
                    self.airports_df["iata_code"] == route.departure_airport.code_iata
                ].iloc[0]
                route.departure_airport.name = dep_airport["name"]
                route.departure_airport.city = dep_airport["municipality"]
                route.departure_time = route_data.FromAirport_Time

                # Set arrival airport details
                route.arrival_airport.code_iata = route_data.ToAirport_ICAO
                arr_airport = self.airports_df[
                    self.airports_df["iata_code"] == route.arrival_airport.code_iata
                ].iloc[0]
                route.arrival_airport.name = arr_airport["name"]
                route.arrival_airport.city = arr_airport["municipality"]

                # Set airline details
                route.airline.code_iata = route.code_IATA[:2]
                airline = self.airlines_df[
                    self.airlines_df["IATA"] == route.airline.code_iata
                ]
                if airline.empty:
                    print(f"Airline not found. IATA code: {route.airline.code_iata}")
                    continue

                airline = airline.iloc[0]
                route.airline.name = airline["Airline"]
                route.airline.country = airline["Country"]
                route.airline.code_icao = airline["ICAO"]
                route.code_ICAO = f"{airline['ICAO']}{route.code_IATA[2:]}"

                result.append(route)

            return result

        except Exception as e:
            print(f"Error finding route: {e}")
            return []
