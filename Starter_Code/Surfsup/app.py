# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# 2. Create an app, being sure to pass __name__
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(f'Available Routes<br/>'
           f'/api/v1.0/precipitation<br/>'
           f'/api/v1.0/stations<br/>'
           f'/api/v1.0/tobs<br/>'
           f'/api/v1.0/start_date(YYYY-MM-DD)<br/>'
           f'/api/v1.0/start_date(YYYY-MM-DD)_end_date(YYYY-MM-DD)<br/>')

    
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    # Calculate the date one year from the last date in data set.
    twelve_months_earlier = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    twelve_months_precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>=twelve_months_earlier).all()

    # Extract data into a list of dictionaries
    data_dictionary = { date:prcp for date,prcp in twelve_months_precipitation_data}
    # Return results as a JSON response
    return jsonify(data_dictionary)

@app.route("/api/v1.0/stations")
def station():
    # Get the list of Stations
    stations = session.query(Station.station).all()

    # Create a list to hold the station values
    # Extract the station values into a list using list comprehension
    station_list = [row.station for row in stations]
    # Return results as a JSON response
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Starting from the most recent data point in the database. 
    # Calculate the date one year from the last date in data set.
    most_active_station_twelve_months_earlier = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Query the last 12 months of temperature observation data for this station
    most_active_station_twelve_months_precipitation_data = session.query(Measurement).\
        filter(Measurement.date>=most_active_station_twelve_months_earlier).filter(Measurement.station == 'USC00519281').all()
    
    # Extract data into a list
    data_list_temp = [data.tobs for data in most_active_station_twelve_months_precipitation_data]
    # Return results as a JSON response
    return jsonify(data_list_temp)

@app.route('/api/v1.0/<start>', methods=['GET'])
@app.route('/api/v1.0/<start>/<end>', methods=['GET'])
def temperature_stats(start, end=None):
    #Return the minimum, average, and maximum temperatures for a given start date or a range from start date to end date.
    if end:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        results = session.query(
            func.min(Measurement.tobs),
            func.avg(Measurement.tobs),
            func.max(Measurement.tobs)
        ).filter(Measurement.date >= start).all()

    # Extract the results
    temps = list(results[0])
    temp_data = {
        "TMIN": temps[0],
        "TAVG": temps[1],
        "TMAX": temps[2]
    }
    # Return results as a JSON response
    return jsonify(temp_data)
    
# Close Session
session.close()

if __name__ == "__main__":
    app.run(debug=True)