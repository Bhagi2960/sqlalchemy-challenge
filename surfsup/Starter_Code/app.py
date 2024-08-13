# Import the dependencies.
import numpy as np
import json
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify, Response


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
session.query(measurement.date).order_by(measurement.date.desc()).first()
preYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
session.close()


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date]<br/>"
        f"/api/v1.0/[start_date]/[end_date]"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create a session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitations """
    # Query all precipitation values for last year
    results = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= preYear).all()

    #results = session.query(measurement.date, measurement.prcp).all()

    session.close()

# Create a dictionary from the row data and append to a list 
    prcp = []
    for result in results:
        prcp_dict = {}
        prcp_dict["date"] = result[0]
        prcp_dict["prcp"] = result[1]
        prcp.append(prcp_dict)

    return jsonify(prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations """
    # Query all stations
    results = session.query(station.station,station.name).all()

    return { id:loc for id,loc in results }

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations """
    # Query all dates and temperature observations of the most active station for the last year of data
    results = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= preYear).all()

    session.close()

    return { d:t for d,t in results}

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def data_range(start, end='2017-08-23'):   
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of agg data"""
    # Query TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
    min,max,avg = session.query(
        func.min(measurement.tobs), 
        func.max(measurement.tobs), 
        func.avg(measurement.tobs
    )).filter(measurement.date >= end).first()

    return {'Min_Temp':min,'Max_temp':max,'Avg_Temp':avg}

if __name__ == '__main__':
    app.run(debug=True)