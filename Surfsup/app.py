from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
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

#################################################
# Flask Setup
#################################################

# create app
app = Flask(__name__)

# Define function that calculates and returns the date one year from most recent date
def prev_year_date():
# Create our session (link) from Python to the DB
    session = Session(engine)

    # Define most recent date in measurement data
    # Then use most recent date to calculate one year from last date
    most_recent = session.query(func.max(Measurement.date)).first()[0]
    first_date = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365)

    # close the session
    session.close()

    # Return the date
    return(first_date)

#################################################
# Flask Routes
#################################################

# Define what to do when user gets to home page
@app.route("/")
def homepage():
    return """ <h1> Honolulu, Hawaii Climate API By Mayra M! </h1>
    <h3> The available routes are: </h3>
    <ul>
    <li><a href = "/api/v1.0/precipitation"> Precipitation</a>: <strong>/api/v1.0/precipitation</strong> </li>
    <li><a href = "/api/v1.0/stations"> Stations </a>: <strong>/api/v1.0/stations</strong></li>
    <li><a href = "/api/v1.0/tobs"> TOBS </a>: <strong>/api/v1.0/tobs</strong></li>
    <li>To retrieve the lowest, average, and highest temperatures for a specific start date, use <strong>/api/v1.0/&ltstart&gt</strong> (replace start date in yyyy-mm-dd format)</li>
    <li>To retrieve the lowest, average, and highest temperatures for a specific start-end range, use <strong>/api/v1.0/&ltstart&gt/&ltend&gt</strong> (replace start and end date in yyyy-mm-dd format)</li>
    </ul>
    """

# Define what to do when user gets to precipitation URL
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    # Query precipitation data from last 12 months from most recent date from measurement table
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prev_year_date()).all()

    # Close session
    session.close()

    # Create dictionary from row data and append to list of prcp
    prcp_list = []
    for date, prcp in prcp_data:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_list.append(prcp_dict)

    # Return list of jsonified precipitation data for the last 12 months
    return jsonify(prcp_list)

# Define what to do when user gets to station URL
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    
    # Query station data from dataset
    station_data = session.query(Station.station).all()

    # Close session
    session.close()

    # Convert tuples list into normal list
    station_list = list(np.ravel(station_data))

    # Return list of jsonified stations data
    return jsonify(station_list)

# Define what to do when user gets to tobs URL
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # Query tobs data from last 12 months from most recent date in Measurement table
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= prev_year_date()).filter(Measurement.station == 'USC00519281').all()

    # Close session
    session.close()

    # Create dictionary from row data and append to tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return list of jsonified tobs data
    return jsonify(tobs_list)

# Define what to do when user gets to URL with specific start date
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)

    # Create query for lowest, average, and highest tobs where query date is greater than or equal to user input
    start_date_tobs = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    # Create list of lowest, avg, and max temps to append with dictionary
    start_date_tobs_list = []
    for min, avg, max in start_date_tobs:
        start_date_tobs_dict = {}
        start_date_tobs_dict['min'] = min
        start_date_tobs_dict['avg'] = avg
        start_date_tobs_dict['max'] = max
        start_date_tobs_list.append(start_date_tobs_dict)

    return jsonify(start_date_tobs_list)

# Define what to do when user gets to URL with specific start-end range
@app.route("/api/v1.0/<start>/<end>")
def temp_cal(start=None, end=None):
    session = Session(engine)

    # Make a list to query lowest, average, and highest temps
    temp_list = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    # Check if there is end date 
    if end == None:
        # Query data from start date to most recent
        start_data = session.query(*temp_list).filter(Measurement.date >= start).all()

        # Convert tuple list into normal
        start_list = list(np.ravel(start_data))

        # Return list of jsonified lowest, average, and highest temperatures for start date
        return jsonify(start_list)
    else:
        # Query the data from start to end date
        start_end_data = session.query(*temp_list).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        # Convert tuple list into normal
        start_end_list = list(np.ravel(start_end_data))

        # Return list of jsonified lowest, average, and highest temps for start-end date range
        return jsonify(start_end_list)
    
# Close session    
def new_func(session):
    session.close()

    new_func(session)

# Define main branch
if __name__ == "__main__":
    app.run(debug=True)
    