# import dependencies
import datetime as dt
from typing_extensions import runtime
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

# create a function to connect to the sqlite database
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#set up the flask app
app = Flask(__name__)

@app.route("/")

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API! \n
    Available Routes: \n
    /api/v1.0/precipation \n
    /api/v1.0/stations \n
    /api/v1.0/tobs \n
    /api/v1.0/temp/start/end \n
    '''
    )

# add the precipation page
@app.route("/api/v1.0/precipation")

def precipitation():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp) \
        .filter(Measurement.date >= prev_year) \
        .all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

#add route for stations
@app.route("/api/v1.0/stations")

def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#add route for tobs
@app.route("/api/v1.0/tobs")

def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#add route for min, max, ave temps
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel) \
            .filter(Measurement.date >= start) \
            .all()
        temps = list(np.ravel(results))
        return jsonify(temps = temps)

    results = session.query(*sel) \
        .filter(Measurement.date >= start) \
        .filter(Measurement.date <= end) \
        .all()
    
    temps = list(np.ravel(results))

    return jsonify(temps)
