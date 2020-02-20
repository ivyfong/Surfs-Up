# Dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Create database connection - Database will be created if none exist
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Create classes by reflecting the database
Base = automap_base()
Base.prepare(engine,reflect=True)

# Save classes as objects
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create app
app = Flask(__name__)

# Define home page
@app.route("/")
def index():
    return (f"Welcome  to the Hawaii Temperature App</br>"
            f"</br>"
            f" Available Routes:</br>"
            f"/api/v1.0/precipitation</br>"
            f"/api/v1.0/stations</br>"
            f"/api/v1.0/tobs</br>"
            f"/api/v1.0/start_date</br>"
            f"/api/v1.0/start_date/end_date</br>"
            f"</br>"
            f"Notes:</br>"
            f"Input start_date and end_date in this format: yyyy-mm-dd</br>"
            f"Dates must be between 2010-01-01 and 2017-08-23")
    
# Return a JSON list of precipitation data for the previous year
    # With date as the key and prcp as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    query_date = dt.date(2016, 8, 23)
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date > query_date).\
                order_by(Measurement.date).all()  
    session.close()
    
    prcp_df = pd.DataFrame(data=prcp_data)
    prcp_dict = prcp_df.set_index('date').to_dict()
    return jsonify(prcp_dict)
    
 # Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_counts = session.query(Measurement.station,func.count(Measurement.station).label("Observation Counts")).\
                     group_by(Measurement.station).\
                     order_by(func.count(Measurement.station).desc()).all()
    session.close()
    
    stations_df = pd.DataFrame(data=station_counts)
    stations_dict = stations_df.set_index('station').to_dict()
    return jsonify(stations_dict)

# Return a JSON list of temperature observations (tobs) for the previous year
    # For the most active station (USC00519281)
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query_date = dt.date(2016, 8, 23)
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.date > query_date).\
                order_by(Measurement.date).all()
    session.close()
    
    tobs_df = pd.DataFrame(data=tobs_data)
    tobs_dict = tobs_df.set_index('date').to_dict()
    return jsonify(tobs_dict)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_results = session.query(func.min(Measurement.tobs).label("Minimum Temperature"),\
                        func.avg(Measurement.tobs).label("Average Temperature"),\
                        func.max(Measurement.tobs).label("Maximum Temperature")).\
                        filter(Measurement.date >= start).all()
    session.close()
    
    start_df = pd.DataFrame(data=start_results)
    start_dict, = start_df.to_dict(orient="records")
    return jsonify(start_dict)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    start_end_results = session.query(func.min(Measurement.tobs).label("Minimum Temperature"),\
                        func.avg(Measurement.tobs).label("Average Temperature"),\
                        func.max(Measurement.tobs).label("Maximum Temperature")).\
                        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    
    start_end_df = pd.DataFrame(data=start_end_results)
    start_end_dict, = start_end_df.to_dict(orient="records")
    return jsonify(start_end_dict)
 
# Run code
if __name__ == "__main__":
    app.run(debug=True)