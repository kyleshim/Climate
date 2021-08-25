# import numpy 
import numpy as np

# import sqlalchemy
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# import Flask
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app, being sure to pass __name__
app = Flask(__name__)

# 3. Home Page
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-08-23<br/>"
        f"/api/v1.0/2016-08-23/2017-08-23<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    print("Server received request for 'Precipitation' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query date and prcp
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
                    order_by(Measurement.date.asc()).filter(Measurement.date > '2016-08-23')
    
    # Prep empty dictionary
    prcp_dict = {}

    # Fill dictionary
    for date, prcp in prcp_data:
        prcp_dict[f"{date}"] = prcp

    # Close session
    session.close()

    # Return JSON results
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stat():
    print("Server received request for 'Stations' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query stations
    active_ordered = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    
    # Convert list of tuples into normal list
    station_list = list(np.ravel(active_ordered))

    # Close session
    session.close()

    # Return JSON results
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'TOBS' page...")

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the last 12 months of temperature observation data for most active station
    active_temps = session.query(Measurement.tobs).\
                    order_by(Measurement.date.asc()).filter(Measurement.date > '2016-08-23').filter(Measurement.station == 'USC00519281').all()
  
    # Convert list of tuples into normal list
    temps_list = list(np.ravel(active_temps))

    # Close session
    session.close()

    # Return JSON results
    return jsonify(temps_list)

@app.route("/api/v1.0/<start>")
def st(start):
    print("Server received request for 'Start' page...")

     # Create our session (link) from Python to the DB   
    session = Session(engine)

    canonicalized = start.replace(" ", "").lower()
    describe_temps = session.query(func.min(Measurement.tobs),\
                                 func.max(Measurement.tobs),\
                                 func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= canonicalized).all()
    temps_dict = {}
    temps_dict = {'Min':describe_temps[0][0],
                    'Max':describe_temps[0][1],
                    'Avg':round(describe_temps[0][2],2)}
    session.close()

    return jsonify(temps_dict)

@app.route("/api/v1.0/<start>/<end>")
def st_end(start, end):
    print("Server received request for 'Start' page...")
    session = Session(engine)
    canonicalized = start.replace(" ", "").lower()
    canonicalized_2 = end.replace(" ", "").lower()
    describe_temps_2 = session.query(func.min(Measurement.tobs),\
                                 func.max(Measurement.tobs),\
                                 func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= canonicalized).\
                    filter(Measurement.date <= canonicalized_2).all()
    temps_dict_2 = {}
    temps_dict_2 = {'Min':describe_temps_2[0][0],
                    'Max':describe_temps_2[0][1],
                    'Avg':round(describe_temps_2[0][2],2)}
    session.close()

    return jsonify(temps_dict_2)

if __name__ == "__main__":
    app.run(debug=True)
