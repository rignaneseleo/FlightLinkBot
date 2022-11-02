import pandas as pd
from difflib import SequenceMatcher
import re
import airportsdata
airports = airportsdata.load('IATA')

# process
# full name airport -> airport IATA
# 2x IATA airports -> possible routes with IATA codes
# routes IATA codes -> info airline


class DataSet:
    def __init__(self):
        print("Loading dataset...")
        global airports_csv
        global routes_csv 
        global airlines_csv
        # read the airports data
        airports_csv = pd.read_csv('data/airports.csv', usecols=[
            'iata_code', 'name', 'municipality'])
        airports_csv = pd.DataFrame(airports_csv)
        # merge 2 columns for easier search
        airports_csv['full_name'] = airports_csv['name'] + \
            ' - ' + airports_csv['municipality'] + \
            ' [' + airports_csv['iata_code']+']'
        # print(airports_csv.head())

        # read the routes
        routes_csv = pd.read_csv('data/routes.tsv', sep='\t', usecols=[
            'CallSign', 'Operator_ICAO', 'FromAirport_ICAO', 'ToAirport_ICAO', 'FromAirport_Time'], low_memory=False)
        # print(airports_csv.head())

        # read the airlines
        airlines_csv = pd.read_csv('data/airlines.csv', low_memory=False)
        # print(routes_csv.head())


class Airline:
    code_iata = ''  # 2 letters
    code_icao = ''
    name = ''
    country = ''


class Airport:
    code_iata = ''  # 3 letters
    code_icao = ''
    name = ''
    city = ''


class Route:
    code_IATA = ''
    code_ICAO = ''
    airline = Airline()
    departure_time = ''
    departure_airport = Airport()

    arrival_airport = Airport()

    def getIATASplitCode(self):
        return re.split('(\d+)', self.code_IATA)

    def getICAOSplitCode(self):
        return re.split('(\d+)', self.code_ICAO)

    def getTripComLink(self):
        return "https://www.trip.com/flights/status-"+self.code_IATA

    def getFlightAwareLink(self):
        return "https://flightaware.com/live/flight/"+self.code_ICAO

    def getPlaneMapperLink(self):
        return "https://www.planemapper.com/?flight="+self.code_IATA

    def getFlightStatsLink(self):
        code_split = self.getIATASplitCode()
        return "https://www.flightstats.com/v2/flight-tracker/{0}/{1}".format(code_split[0], code_split[1])

    def getIconUrl(self):
        code_split = self.getICAOSplitCode()
        return "https://raw.githubusercontent.com/sexym0nk3y/airline-logos/main/logos/{}.png".format(code_split[0])


def find_route(input_str):
    if "-" in input_str:
        data = input_str.split('-')
    else:
        data = input_str.split(' ')
        # remove empty elements
        data = [x for x in data if x]

    city_from = data[0].strip()
    departure_airports_mask = airports_csv['full_name'].str.contains(
        city_from, case=False, na=False)
    print(airports_csv[departure_airports_mask].head())

    #city_to = input('City to: ')
    city_to = data[1].strip()
    arrival_airports_mask = airports_csv['full_name'].str.contains(
        city_to, case=False, na=False)
    print(airports_csv[arrival_airports_mask].head())

    # find the routes between the 2 airports
    filtered = routes_csv[routes_csv['FromAirport_ICAO'].isin(
        list(airports_csv[departure_airports_mask]['iata_code']))]
    possible_routes = filtered[filtered['ToAirport_ICAO'].isin(
        list(airports_csv[arrival_airports_mask]['iata_code']))]

    result = []
    for route in possible_routes.values:
        print(route)
        r = Route()
        # route code
        r.code_IATA = route[0]
        # departure data
        r.departure_airport.code_iata = route[2]
        departure_airport_data = airports_csv[airports_csv['iata_code']
                                                      == r.departure_airport.code_iata]
        r.departure_airport.name = departure_airport_data['name'].values[0]
        r.departure_airport.city = departure_airport_data['municipality'].values[0]
        r.departure_time = route[1]
        # arrival data
        r.arrival_airport.code_iata = route[4]
        arrival_airport_data = airports_csv[airports_csv['iata_code']
                                                    == r.arrival_airport.code_iata]
        r.arrival_airport.name = arrival_airport_data['name'].values[0]
        r.arrival_airport.city = arrival_airport_data['municipality'].values[0]
        # airline data
        r.airline.code_iata = r.code_IATA[:2]
        airline_data = airlines_csv[airlines_csv['IATA']
                                            == r.airline.code_iata]
        r.airline.name = airline_data['Airline'].values[0]
        r.airline.country = airline_data['Country'].values[0]
        r.airline.code_icao = airline_data['ICAO'].values[0]
        # route code
        r.code_ICAO = airline_data['ICAO'].values[0]+r.code_IATA[2:]
        result.append(r)

    return result


def main():
    #init dataset
    dataset = DataSet()
    #airports = airportsdata.load('IATA')
    routes = find_route('ein - lhr')
    for route in routes:
        x = 0
        print(route.code_IATA)


if __name__ == "__main__":
    main()
