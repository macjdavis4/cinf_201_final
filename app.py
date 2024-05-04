from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    conn = sqlite3.connect('travel_planner.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM Airports ORDER BY city")
    cities = cur.fetchall()
    conn.close()
    return render_template('index.html', cities=cities)

@app.route('/airports')
def show_airports():
    conn = sqlite3.connect('travel_planner.db')
    cur = conn.cursor()
    cur.execute("SELECT airport_id, city, state FROM Airports")
    airports = cur.fetchall()
    return render_template('airports.html', airports=airports)

@app.route('/search', methods=['POST'])
def search():
    source_airport_code = request.form['source_city'].upper()
    destination_airport_code = request.form['dest_city'].upper()
    conn = sqlite3.connect('travel_planner.db')
    cur = conn.cursor()

    query = """
            SELECT 
                a.name AS Airline,
                ap1.name AS SourceAirport,
                ap2.name AS DestinationAirport,
                r.depart_time,
                r.arrive_time,
                r.airline_route_number,
                'Direct' AS RouteType
            FROM Routes r
            JOIN Airlines a ON r.airline_id = a.airline_id
            JOIN Airports ap1 ON r.source_airport_id = ap1.airport_id
            JOIN Airports ap2 ON r.dest_airport_id = ap2.airport_id
            WHERE r.source_airport_id = ?
            AND r.dest_airport_id = ?

            UNION

            SELECT 
                a.name AS Airline,
                ap1.name AS SourceAirport,
                ap4.name AS FinalDestinationAirport,
                r1.depart_time AS FirstDepartTime,
                r2.arrive_time AS FinalArriveTime,
                r1.airline_route_number || ' -> ' || r2.airline_route_number AS RouteNumber,
                'Connecting' AS RouteType
            FROM Routes r1
            JOIN Routes r2 ON r1.dest_airport_id = r2.source_airport_id AND r2.depart_time > r1.arrive_time
            JOIN Airlines a ON r1.airline_id = a.airline_id
            JOIN Airports ap1 ON r1.source_airport_id = ap1.airport_id
            JOIN Airports ap4 ON r2.dest_airport_id = ap4.airport_id
            WHERE r1.source_airport_id = ?
            AND r2.dest_airport_id = ?
            ORDER BY Airline, RouteType, FirstDepartTime;
            """

    cur.execute(query, (source_airport_code, destination_airport_code, source_airport_code, destination_airport_code))
    routes = cur.fetchall()
    conn.close()

    return render_template('results.html', routes=routes, source_airport_code=source_airport_code,
                           destination_airport_code=destination_airport_code)

if __name__ == "__main__":
        app.run(debug=True)
