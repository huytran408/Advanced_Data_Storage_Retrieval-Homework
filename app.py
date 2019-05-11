import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.pool import StaticPool
from flask import Flask, jsonify

####################
# Database Setup
####################

engine = create_engine("sqlite:///Resources/hawaii.sqlite",
						connect_args={'check_same_thread':False},
                    poolclass=StaticPool)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

####################
# Flask Setup
####################
app = Flask(__name__)



########################
# setting time variables
########################

#Retreive the latest date present in the database
Latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()


#converted to string
Latest_date_str=str(Latest_date).split("'")[1]

# Determine the date point one year from the most recent date
most_recent_date=dt.datetime.strptime(Latest_date_str,"%Y-%m-%d")
one_year_ago = most_recent_date-dt.timedelta(days=365)

#converted to string
one_year_ago_str = one_year_ago.strftime("%Y-%m-%d")


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Note: Paste the routes in the browsing after the default link<br/>"
        f"Available Routes Below:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"""/api/v1.0/'start date'<br/>"""
        f"Put the start date in 'YYYY-MM-DD' format<br/>"
        f"<br/>"
        f"""/api/v1.0/'Start Date'/'End Date'<br/>"""  
        f"Put the dates in 'YYYY-MM-DD/YYYY-MM-DD' format<br/>"
        )  

@app.route("/api/v1.0/precipitation")
def precipitation():
# Query for the dates and temperature observations from the last year.   
    End_date = Latest_date_str
    Start_date = one_year_ago_str
    
    
    results = session.query(Measurement.date, Measurement.station,Measurement.prcp)\
    						.filter(Measurement.date <= End_date)\
                            .filter(Measurement.date >= Start_date).all()                                                                  
    list = []
    for result in results:
        dict = {"Date":result[0],"Station":result[1],"Precipitation":result[2]}
        list.append(dict)
    return jsonify(list)

@app.route("/api/v1.0/stations")
def stations():

#Returnb JSON list of stations
    stations = session.query(Station.station,Station.name).all()
    
    list=[]
    for station in stations:
        dict = {"Station ID:":stations[0],"Station Name":stations[1]}
        list.append(dict)

    return jsonify(list)

@app.route("/api/v1.0/tobs")
def tobs():

#Return a JSON list of Temperature Observations (tobs) for the previous year.
    End_date = Latest_date_str
    Start_date = one_year_ago_str
    
    tobs = session.query(Measurement.date,Measurement.tobs).\
                            filter(Measurement.date <= End_date).\
                            filter(Measurement.date >= Start_date).all()
    list = []
    for temp in tobs:
        dict = {"date": temp[0], "tobs": temp[1]}
        list.append(dict)

    return jsonify(list)  



@app.route("/api/v1.0/<start>")
def tstart(start):

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))\
                .filter(Measurement.date >= start)\
                .order_by(Measurement.date.desc()).all()
    
    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
        
    return jsonify(dict) 

@app.route("/api/v1.0/<start>/<end>")
def tstartend(start,end):             
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs))\
                .filter(Measurement.date >= start, Measurement.date <= end)\
                .order_by(Measurement.date.desc()).all()

    for temps in results:
        dict = {"Minimum Temp":results[0][0],"Average Temp":results[0][1],"Maximum Temp":results[0][2]}
    return jsonify(dict)   

if __name__ == '__main__':
    app.run(debug=True)