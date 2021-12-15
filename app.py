import datetime as dt
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask setup
app = Flask(__name__)


@app.route("/")
def index():
    return (
        "Routes available:<br/>"
        "<i>/api/v1.0/precipitation</i><br/>"
        "<i>/api/v1.0/stations</i><br/>"
        "<i>/api/v1.0/tobs</i><br/>"
        "<i>/api/v1.0/[start_date] (yyyy-mm-dd)</i><br/>"
        "<i>/api/v1.0/[start_date]/[end_date] (yyyy-mm-dd)</i><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create our session to DB
    session = Session(engine)

    #Query all Precipitation
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    prior_date = most_recent_date - dt.timedelta(days=365)
    date_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_date).all()

    session.close()

    #Convert list to Dictionary 
    precip_data = []
    for date,precip  in date_precipitation:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = precip
               
        precip_data.append(prcp_dict)

    #Return JSON
    return jsonify(precip_data)


@app.route("/api/v1.0/stations")
def stations():
    #Create our session to DB
    session = Session(engine)

    #Query all Stations 
    results = session.query(Station.station).all()

    session.close()

    #Convert List of tuples into normal list
    all_stations = [station[0] for station in results]

    return jsonify(all_stations)



@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session to DB
    session = Session(engine)

    #Query the dates and temperature observations of the most active station for the last year 
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    prior_date = most_recent_date - dt.timedelta(days=365)
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    most_active_station = most_active_stations[0][0]
    last_12_months= session.query(Measurement.date, Measurement.tobs).filter(Station.station == Measurement.station).filter(Station.station == most_active_station).filter(Measurement.date > prior_date)

    session.close 

    #Create a dictionary from the row data and append 
    tobs_data = []
    for date, tobs in last_12_months:
        tobs_dict = {}
        tobs_dict["date"] = date 
        tobs_dict["tobs"] = tobs
        tobs_data.append(tobs_dict)
        
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start_date>/")
def start(start_date):
    # Create our session to DB
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    start_date = most_recent_date - dt.timedelta(days=365)

    #Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

    session.close

    #Create a dictionary
    start_data = []
    for min, avg, max in results: 
        start_dict = {}
        start_dict["min"]= min 
        start_dict["avg"] = avg
        start_dict["max"] = max
        start_data.append(start_dict)

    return jsonify(start_data)


@app.route("/api/v1.0/<start_date>/<end_date>")
def starttoend(start_date, end_date):
    # Create our session to DB
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    end_date = dt.datetime.strptime(recent_date, "%Y-%m-%d")
    start_date = end_date - dt.timedelta(days=365)

    #Calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close

    #Create a dictionary
    to_fro = []
    for min, avg, max in results: 
        to_fro_dict = {}
        to_fro_dict["min"]= min 
        to_fro_dict["avg"] = avg
        to_fro_dict["max"] = max
        to_fro.append(to_fro_dict)

    return jsonify(to_fro)


if __name__ == "__main__":
    app.run(debug=True)