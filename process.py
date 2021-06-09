import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# ---------------------------- IMPORT DATA ---------------------------------------- #

# house transactions
data = pd.read_csv('./data/made/pp-post_2013_reduced.csv')

# postcoded coordinates
coord = pd.read_csv('./data/row/National_Statistics_Postcode_Lookup_UK_Coordinates.csv')

# avg price data
avg_price = pd.read_csv('./data/row/Average-prices-2021-03.csv')

# get CPI data
CPI = pd.read_csv('./data/row/mm23.csv')

# ----------------------------- TRANSFORMATIONS ---------------------------------------- #

# transform cols to str
cols_to_str = ["Transaction ID","Postcode","County","District","Town/City","Locality","Street","PAON","SAON","Property Type"]
data[cols_to_str] = data[cols_to_str].astype(str)

# transformations on avg price data - keep England only, get data at monthly freq, keep only date and avg price
avg_price = avg_price[avg_price["Region_Name"] == "England"]
avg_price['Date'] = pd.to_datetime(avg_price['Date']).dt.to_period('M')
# keep only average price as column
avg_price = avg_price[['Date','Average_Price']].set_index("Date")

# transformations on CPI - keep only monthly data for rents index
CPI = CPI.loc[1008:,['Title','CPI INDEX 04.1 : ACTUAL RENTS FOR HOUSING 2015=100']].rename(columns =
                {'Title':'Date','CPI INDEX 04.1 : ACTUAL RENTS FOR HOUSING 2015=100':'Value'})
CPI["Date"] = pd.to_datetime(CPI["Date"]).dt.to_period('M')
CPI.set_index('Date',inplace=True)

# transformations on coordinates - get area code and find its location (average)
coord['Area Code'] = coord['Postcode 3'].apply(lambda x: x.split(' ')[0])
coord = coord.groupby('Area Code')[["Longitude","Latitude"]].mean()

# ------------------------------ DEFINE PROPERTY ID --------------------------------- # 

# define property ID
data["Property ID"] = data["County"] + '-' +  data["District"] + '-' + data["Town/City"] \
                      + '-' + data["Locality"] + '-' + data["Street"] + '-' + data["PAON"] + '-' + data['SAON'] + \
                    '-' + data['Property Type']

# ------------------------------ BUILD PROPERTY DATASET -------------------------- #

keep_cols = ['Property ID',"County","District","Town/City","Locality","Street","PAON","SAON","Property Type"]
properties = data[keep_cols].drop_duplicates(subset=['Property ID']).set_index('Property ID')

# ------------------------------ BUILD TRANSACTIONS DATASET ---------------------- # 

transactions = data[["Transaction ID","Property ID","Price","Transaction Date","Old/New","Duration",
                     "PPD Category Type"]].set_index("Transaction ID")

# ------------------------------ BUILD POSTCODE DATASET -------------------------- # 

postcodes_properties = data[["Property ID","Postcode"]].reset_index(drop=True)

# ------------------------------ EXPORT DATA -------------------------------- # 

transactions.to_csv("./data/made/transactions_proc.csv")
properties.to_csv("./data/made/properties_proc.csv")
postcodes_properties.to_csv("./data/made/postcode_properties_proc.csv")
coord.to_csv("./data/made/coord_proc.csv")
CPI.to_csv('./data/made/CPI_proc.csv')
avg_price.to_csv('./data/made/Avg_price_proc.csv')