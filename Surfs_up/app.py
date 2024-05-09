import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
# Database Setup
engine = create_engine(r"sqlite+pysqlite:///C:\Users\Sezy\OneDrive\sqlalchemy_Challenge\sqlalchemy-challenge\Surfs_up\hawaii.sqlite")

Base = automap_base()

Base.prepare(autoload_with=engine)

Measurement = Base.classes.measurement

Station = Base.classes.station

app = Flask(__name__)


@app.route("/")
def homepage():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start><br/>"
        "/api/v1.0/<start>/<end>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
 # Query for the most recent date
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    # Calculate the date one year ago from the most recent date
    one_year_ago = most_recent_date - timedelta(days=365)
    
    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp)\
                                .filter(Measurement.date >= one_year_ago)\
                                .all()
    session.close()

    all_precipitation = []
    for date, prcp in precipitation_data:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        all_precipitation.append(precipitation_dict)
    
    return jsonify(all_precipitation) 




@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    # Query all unique station names
    station_names = session.query(Station.station).distinct().all()
    
    session.close()
    
    # Convert the query results to a list
    stations_list = [name for (name,) in station_names]
    
    # Return the list of stations as JSON
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    # Query for the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station))\
                                .group_by(Measurement.station)\
                                .order_by(func.count(Measurement.station).desc())\
                                .first()[0]
    
    # Query for the most recent date
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    
    # Calculate the date one year ago from the most recent date
    one_year_ago = most_recent_date - timedelta(days=365)
    
    # Query temperature observations for the previous year from the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs)\
                                .filter(Measurement.station == most_active_station)\
                                .filter(Measurement.date >= one_year_ago)\
                                .all()
    
    session.close()
    
    # Convert the query results to a list of dictionaries
    temperature_list = []
    for date, tobs in temperature_data:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs
        temperature_list.append(temperature_dict)
    
    # Return the temperature observations as JSON
    return jsonify(temperature_list)



@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    session = Session(engine)
    
    # Check if the start parameter is a valid date
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start date format. Please use YYYY-MM-DD."}), 400
    
    # Find the most recent date in the dataset
    most_recent_date_str = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = datetime.strptime(most_recent_date_str, '%Y-%m-%d')
    
    # Query for the temperature statistics from the start date to the end of the dataset
    temperature_stats = session.query(func.min(Measurement.tobs).label('min_temperature'),
                                      func.avg(Measurement.tobs).label('avg_temperature'),
                                      func.max(Measurement.tobs).label('max_temperature'))\
                                .filter(Measurement.date >= start_date)\
                                .all()
    
    session.close()
    
    # Extract the temperature statistics from the query result
    min_temp, avg_temp, max_temp = temperature_stats[0]
    
    # Return the temperature statistics as a JSON list
    return jsonify({"min_temperature": min_temp, "avg_temperature": avg_temp, "max_temperature": max_temp})


@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    session = Session(engine)
    
    # Check if the start and end parameters are valid dates
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.strptime(end, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    
    
    
    # Query for the temperature statistics from the start date to the end date
    temperature_stats = session.query(func.min(Measurement.tobs).label('min_temperature'),
                                      func.avg(Measurement.tobs).label('avg_temperature'),
                                      func.max(Measurement.tobs).label('max_temperature'))\
                                .filter(Measurement.date >= start_date)\
                                .filter(Measurement.date <= end_date)\
                                .all()
    
    session.close()
    
    # Extract the temperature statistics from the query result
    min_temp, avg_temp, max_temp = temperature_stats[0]
    
    # Return the temperature statistics as a JSON list
    return jsonify({"min_temperature": min_temp, "avg_temperature": avg_temp, "max_temperature": max_temp})
if __name__ == "__main__":
    app.run(debug=True)