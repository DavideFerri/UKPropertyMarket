import pandas as pd
import numpy as np

# ---------------- IMPORT DATA ---------------------- # 

transactions = pd.read_csv('./data/made/transactions_proc.csv',index_col=0)
properties = pd.read_csv('./data/made/properties_proc.csv',index_col=0)
postcodes_properties = pd.read_csv('./data/made/postcode_properties_proc.csv',index_col = 0)

# postcoded coordinates
coord = pd.read_csv('./data/made/coord_proc.csv',index_col=0)

# make sure formats are consistent
transactions["Transaction Date"] = pd.to_datetime(transactions["Transaction Date"])
postcodes_properties["Postcode"] = postcodes_properties["Postcode"].astype(str)

# --------------- CLASSES --------------------- # 

class Transaction():
    """Class to represent objects in transactions"""
    def __init__(self,id):
        self.id = id
        # attributes
        self.price = transactions.loc[id,"Price"] ; self.date = transactions.loc[id,"Transaction Date"]
        self.age = transactions.loc[id, "Old/New"] ; self.duration = transactions.loc[id, "Duration"]

    def get_properties(self):
        """Get the corresponding property ID"""
        return transactions.loc[self.id,"Property ID"]

class Property():
    """Class to represent objects in properties"""
    def __init__(self,id):
        self.id = id
        # attributes
        self.county = properties.loc[id,"County"] ; self.district = properties.loc[id,"District"]
        self.town = properties.loc[id,"Town/City"] ; self.locality = properties.loc[id,"Locality"]
        self.street = properties.loc[id,"Street"] ; self.PAON = properties.loc[id,"PAON"]
        self.SAON = properties.loc[id, "SAON"] ; self.type = properties.loc[id, "Property Type"]

class PostCode():
    """Class to represent objects in postcode"""

    def __init__(self,id):
        self.id = id

    def get_properties(self):
        """Returns an array of properties associated to postcode"""
        return postcodes_properties[postcodes_properties["Postcode"] == self.id]["Property ID"].values

    def get_transactions(self,initial_date,final_date):
        """Returns an array of transactions associated to postcode"""
        properties_ = self.get_properties()
        transactions_t = transactions[(transactions["Property ID"].isin(properties_))&
                                      (transactions["Transaction Date"] >= initial_date)&
                                      (transactions["Transaction Date"] <= final_date)].index
        return transactions_t

    # ----------------------------- STATIC METHODS ----------------------------------- #

    @staticmethod
    def agg_transactions(year,by):
        """Aggregate transactions in a year by area code - by number / total value. Return a series of area code, result"""
        # check whether parameter is relevant
        if by not in ["number","value"]:
            raise Exception
        # merge data
        data = transactions.merge(postcodes_properties, left_on="Property ID", right_on="Property ID", how="left")
        # select year if relevant
        if year:
            data["Transaction Year"] = data["Transaction Date"].dt.year ; data = data[data["Transaction Year"] == year]
        # create area code
        data['Area Code'] = data['Postcode'].apply(lambda x: x.split(' ')[0])
        # aggregate
        if by == "number":
            return data.groupby("Area Code").size()
        else:
            return data.groupby("Area Code")["Price"].sum()

    @staticmethod
    def find_top_codes(n,initial_year,final_year,by):
        """Find n area codes which have grown the most between initial_year and final_year"""
        # check whether param is relevant
        if by not in ["number","value"]:
            raise Exception
        # get number of transactions
        initial = PostCode.agg_transactions(initial_year,by)
        final = PostCode.agg_transactions(final_year,by)
        # merge
        result = final/initial
        return result.nlargest(n)

    @staticmethod
    def gravity_centre(year,by):
        """Get the UK gravity centre by year and value / number of transactions"""
        # check whether param is relevant
        if by not in ["number","value"]:
            raise Exception
        # get aggregated data for the year
        data = PostCode.agg_transactions(year,by)
        data.rename("weight",inplace = True)
        # aggregate with coordinates
        data = coord.merge(data,left_index=True,right_index=True,how="inner")
        # get gravity centre
        return np.average(a = data[["Longitude","Latitude"]], weights = data["weight"],axis=0)

    @staticmethod
    def distance_predict(area_code,by,year=None):
        """Get a dataframe with distance from area code and average price for year (Optional)"""
        if by not in ["number","value"]:
            raise Exception
        # get aggregated data for the year
        data = PostCode.agg_transactions(year,by)
        data.rename("y",inplace = True)
        # aggregate with coordinates
        data = coord.merge(data,left_index=True,right_index=True,how="inner")
        # measure distance
        target = np.array([data.loc[area_code,"Longitude"],data.loc[area_code,"Latitude"]])
        data["distance"] = data.apply(lambda x : np.linalg.norm(np.array([x["Longitude"],x["Latitude"]]) - target),axis=1)
        # return data without nans
        res = data[["distance","y"]].dropna()
        return res

