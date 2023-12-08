# Import Flask
from flask import Flask, jsonify

# Dependencies and Setup
import numpy as np
import datetime as dt

# Python SQL Toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool

#################################################
# Database Setup
#################################################
# Reference: https://stackoverflow.com/questions/33055039/using-sqlalchemy-scoped-session-in-theading-thread
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={"check_same_thread": False}, poolclass=StaticPool, echo=True)

# Reflect Existing Database Into a New Model
Base = automap_base()
# Reflect the Tables
Base.prepare(engine, reflect=True)

# Save References to Each Table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create Session (Link) From Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Home Route
@app.route("/")
def welcome():
        return """<html>
<h1> Climate Analytics App (Flask API )</h1>
<img src="https://firstanalytics.com/wp-content/uploads/weather-data.jpg" alt="Hawaii Weather"/>

<p>Precipitation Analysis:</p>
<ul>
  <li><a href="/api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
</ul>
<p>Station Analysis:</p>
<ul>
  <li><a href="/api/v1.0/stations">/api/v1.0/stations</a></li>
</ul>
<p>Temperature Analysis:</p>
<ul>
  <li><a href="/api/v1.0/tobs">/api/v1.0/tobs</a></li>
</ul>
<p>Start Day Analysis:</p>
<ul>
  <li><a href="/api/v1.0/2017-03-14">/api/v1.0/2017-03-14</a></li>
</ul>
<p>Start & End Day Analysis:</p>
<ul>
  <li><a href="/api/v1.0/2017-03-14/2017-03-28">/api/v1.0/2017-03-14/2017-03-28</a></li>
</ul>
</html>
"""

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
        try:
                # Convert the Query Results to a Dictionary Using `date` as the Key and `prcp` as the Value
                # Calculate the Date 1 Year Ago from the Last Data Point in the Database
                one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
                # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
                prcp_data = session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= one_year_ago).\
                        order_by(Measurement.date).all()
                # Convert List of Tuples Into a Dictionary
                
                prcp_data_list = dict(prcp_data)
                # Return JSON Representation of Dictionary
                return jsonify(prcp_data_list)
        except Exception as e:
                print(f"Error in precipitation route: {e}")
                return jsonify({"error": "An error occurred"}), 500

# Station Route
@app.route("/api/v1.0/stations")
def stations():
        try:
                # Return a JSON List of Stations From the Dataset
                stations_all = session.query(Station.station, Station.name).all()
                # Convert List of Tuples Into Normal List
                # station_list = list(stations_all)
                station_list = [{"station": station, "name": name} for station, name in stations_all]
                # Return JSON List of Stations from the Dataset
                return jsonify(station_list)
        except Exception as e:
                print(f"Error in station route: {e}")
                return jsonify({"error": "An error occurred"}), 500

# TOBs Route
@app.route("/api/v1.0/tobs")
def tobs():
        try:
                # Query for the Dates and Temperature Observations from a Year from the Last Data Point
                one_year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
                # Design a Query to Retrieve the Last 12 Months of Precipitation Data Selecting Only the `date` and `prcp` Values
                tobs_data = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.date >= one_year_ago).\
                        order_by(Measurement.date).all()
                # Convert List of Tuples Into Normal List
                # tobs_data_list = list(tobs_data)
                tobs_data_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]
                # Return JSON List of Temperature Observations (tobs) for the Previous Year
                return jsonify(tobs_data_list)
        except Exception as e:
                print(f"Error in TOBs route: {e}")
                return jsonify({"error": "An error occurred"}), 500
# Start Day Route
@app.route("/api/v1.0/<start>")
def start_day(start):
        try:
                start_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        group_by(Measurement.date).all()
                # Convert List of Tuples Into Normal List
                # start_day_list = list(start_day)
                start_day_list = [{"date": date, "min_temp": min_temp, "avg_temp": avg_temp, "max_temp": max_temp} for date, min_temp, avg_temp, max_temp in start_day]
                # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start Range
                return jsonify(start_day_list)
        
        except Exception as e:
                print(f"Error in Start day route: {e}")
                return jsonify({"error": "An error occurred"}), 500

# Start-End Day Route
@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start, end):
        try:
                start_end_day = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start).\
                        filter(Measurement.date <= end).\
                        group_by(Measurement.date).all()
                # Convert List of Tuples Into Normal List
                # start_end_day_list = list(start_end_day)
                start_end_day_list = [{"date": date, "min_temp": min_temp, "avg_temp": avg_temp, "max_temp": max_temp} for date, min_temp, avg_temp, max_temp in start_end_day]
                # Return JSON List of Min Temp, Avg Temp and Max Temp for a Given Start-End Range
                return jsonify(start_end_day_list)
        except Exception as e:
                print(f"Error in End day route: {e}")
                return jsonify({"error": "An error occurred"}), 500

# Define Main Behavior
if __name__ == '__main__':
    app.run(debug=True)