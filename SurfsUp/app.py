import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np

# Create our session (link) from Python to the DB
connection_url = "sqlite:///Resources/hawaii.sqlite"
engine = create_engine(connection_url)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

app=Flask(__name__)

#Create the Homepage with all Available Routes
@app.route("/")
def welcome():
    return (
        f"Welcome to my Climate App!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[enter start date]<br/>"
        f"/api/v1.0/[enter start date]/[enter end date]"
    )

#Convert query results to a dictionary, use DateTime to only get the last year of results
@app.route("/api/v1.0/precipitation")
def Precipitation():
    session=Session(bind=engine)
    date = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    date = date.strftime('%Y-%m-%d')

    results = session.query(Measurement.prcp, Measurement.date).\
    filter(Measurement.date > date).\
    filter(Measurement.prcp != None).\
    order_by(Measurement.date).all()
    results_json = {date: prcp for prcp, date in results}
    session.close()
    return jsonify(results_json)

#Generate jsonified list of all stations
@app.route("/api/v1.0/stations")
def Stations():
    session=Session(bind=engine)
    list_stations = session.query(Station.station).all()
    json_stations = list(np.ravel(list_stations))
    session.close()
    return jsonify(json_stations)

#Query jsonified temperature observations, using DateTime to get only previous year of data
@app.route("/api/v1.0/tobs")
def Temperature():
    session=Session(bind=engine)
    date = dt.date(2017, 8, 23)-dt.timedelta(days=365)
    date = date.strftime('%Y-%m-%d')

    temp_observations = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').filter(Measurement.date > date).all()
    json_temps = list(np.ravel(temp_observations))
    session.close()
    return jsonify(json_temps)

#Return jsonified list of min, max, and avg temps for a specified start range
@app.route("/api/v1.0/<start>")
def Temp_By_Start(start):
    session=Session(bind=engine)
    Total_Dates = session.query(Measurement.date).all()
    json_dates = list(np.ravel(Total_Dates))
    for date in json_dates:
        search_date = date

        if search_date == start:
            temp_info = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.station == 'USC00519281').filter(Measurement.date > search_date).all()
            json_temp_info = list(np.ravel(temp_info))
            session.close()
            return jsonify(json_temp_info)
    session.close()
    return jsonify({"error": "Date not found. Use format 'YYYY-MM-DD'"}), 404

#Return jsonified list of min, max, and avg temps for a specified start and end range
@app.route("/api/v1.0/<start>/<end>")
def Temp_By_Start_and_End(start, end):
    session=Session(bind=engine)
    Total_Dates = session.query(Measurement.date).all()
    json_dates = list(np.ravel(Total_Dates))
    for date in json_dates:
        search_date = date

        if search_date == start:
            end_date = end
            temp_info = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.station == 'USC00519281').filter(Measurement.date > search_date).filter(Measurement.date < end_date).all()
            json_temp_info = list(np.ravel(temp_info))
            session.close()
            return jsonify(json_temp_info)
    session.close()
    return jsonify({"error": "Date not found. Use format 'YYYY-MM-DD'"}), 404

if __name__=='__main__': 
    app.run(debug=True)