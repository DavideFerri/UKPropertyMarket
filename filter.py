import pandas as pd
import datetime

# download house transactions data
data = pd.read_csv('pp-complete.csv')

# initial date
initial_date = datetime.datetime(2013,1,1)

# set data columns
data.columns = ["Transaction ID","Price","Transaction Date","Postcode",
             "Property Type","Old/New","Duration","PAON","SAON",
              "Street","Locality","Town/City","District","County","PPD Category Type","Record Status"]

# get date in datetime
data["Transaction Date"] = pd.to_datetime(data["Transaction Date"])

# filter by date
data = data[data["Transaction Date"] >= initial_date]

# sample
data = data.sample(n = 3000)

# export
data.to_csv('pp-post_2013_reduced.csv')

