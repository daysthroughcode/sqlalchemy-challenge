#Import Flask and Set app
from flask import Flask, jsonify
app = Flask(__name__)

#Import dependencies
import datetime as dt
import numpy as np
import pandas as pd

#Import SQL alchemy packages
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#Set up database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect Database
Base = automap_base()
Base.prepare(engine, reflect=True)

#save to table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Link session to DB
session = Session(bind=engine)

#Route /

@app.route('/')
def welcome():
    """List of available api routes."""
    return (
        f"Welcome<br>"
        f"Options Available:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start Replace <start> with date in format YYYY,M,D <br>"
        f"/api/v1.0/start/end Replace <start> and <end> with date in format YYYY,M,D <br>"
    )

#Route precipitation
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Return 1 Years worth of Precipitation Data"""
    #Calculate the date 1 year ago from the last datapoint in DB
    year_prev = dt.date(2017,8,23) - dt.timedelta(days=365)

    #Query for the date and precipitation for last year
    data_precip = (session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date>= year_prev)).all()

    #Convert results to a dictionary using date as key and prcp as value
    precipitation = {date: prcp for date, prcp in data_precip}
    return jsonify(precipitation)

#Route Stations
@app.route('/api/v1.0/stations')
def stations():
    """Return a list of stations"""
    results = session.query(Station.station).all()
    
    #Put results into list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    """Return 1 Years worth of temperature observations"""
    year_prev = dt.date(2017,8,23) - dt.timedelta(days=365)

    stat_dat = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    act_stat = stat_dat[0][0]

    #Query most active station tobs
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == act_stat).\
        filter(Measurement.date >= year_prev).all()

    #Convert to list
    temps = list(np.ravel(results))

    #return results as json
    return jsonify(temps)

@app.route('/api/v1.0/<start>', defaults={'end': None})
@app.route("/api/v1.0/<start>/<end>")
def determine_temps_for_date_range(start, end):
    """Return min temperature, the average temp, and the max temp for a given range."""

    #Start and End.
    if end != None:
        result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(
            Measurement.date <= end).all()
    #Start only.
    else:
        result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()

    # Convert to list.
    temp_list = []
    no_data = False
    for min_temp, avg_temp, max_temp in result:
        if min_temp == None or avg_temp == None or max_temp == None:
            no_data = True
        temp_list.append(min_temp)
        temp_list.append(avg_temp)
        temp_list.append(max_temp)
    # Return JSON.
    if no_data == True:
        return f"No Data in Date Range"
    else:
        return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)