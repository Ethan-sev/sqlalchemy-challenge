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

# Station = Base.classes.station

app = Flask(__name__)


@app.route("/")
def homepage():
    """List all available API routes."""
    return (
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs"
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

if __name__ == "__main__":
    app.run(debug=True)
