import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

version = {"Current version": "1.0.0"}

class SeasonalityScript:
    def __init__(self, country_code: str, start_date: str, end_date: str, day: str, uk_country: str = None, week_ending: bool = False):
        '''
        Creates the object with all the important functions.

        
        :param country_code: str | two letter code for the country you want to retrieve data from
        :param start_date: str | first date in your dataset. it should have the following format: %dd%mm%yyyy.
        :param end_date: str | last date in your dataset. it should have the following format: %dd%mm%yyyy.
        :param day: str | the first day of the week (i.e. SUN or MON or TUE...)
        :param uk_country: str | filters between countries in the UK. None by default.
        :param week_ending: bool | converts data from daily to week ending. False by default.
        '''
        try:
            print("Creating object...")
            self.years = []
            self.holidays = {}
            self.week_numbers = []
            self.week_dummies = {}
            self.month_numbers = []
            self.month_dummies = {}
            self.country_names = {}
            # self.df = None
            # self.weekly_df = None
            # self.monthly_df = None

            self.country_id = country_code
            self.week_ending = week_ending
            self.day = day
            self.uk_country = uk_country
            self.start_date = datetime.strptime(start_date, r"%d/%m/%Y").strftime(r"%Y-%m-%d")
            self.end_date = datetime.strptime(end_date, r"%d/%m/%Y").strftime(r"%Y-%m-%d")

            start_year = int(datetime.strptime(start_date, r"%d/%m/%Y").strftime(r"%Y"))
            end_year = int(datetime.strptime(end_date, r"%d/%m/%Y").strftime(r"%Y"))

            while start_year <= end_year:
                self.years.append(start_year)
                start_year += 1
            
            # Creates a dictionary with the country code and name
            url = r'https://date.nager.at/api/v3/AvailableCountries'
            connection = requests.get(url)
            response = json.loads(connection.content)
    
            for item in response:
                self.country_names[item["countryCode"]] = item["name"]
            
            result = {"SeasonalityScript successfully created": True}
            print(result)
        except Exception as error:
            print(error)
            raise
    
    def get_version(self):
        print(version)
    
    def get_country_codes(self):
        '''
        :reurns: str | all available countries and their country codes.
        '''
        self.country_info = {}

        url = r'https://date.nager.at/api/v3/AvailableCountries'
        connection = requests.get(url)
        response = json.loads(connection.content)
        
        for item in response:
            country_name = item["name"]
            country_code = item["countryCode"]
            self.country_info[country_name] = country_code
        
        return print(self.country_info)

    def build_dataframe(self):
        '''
        Builds the structure of the DataFrame.

        :returns: bool | boolean expression indicating whether the process was successfully completed or not.
        '''
        try:
            print("Building DataFrame...")
            # Creates a list with all the dates between the start_date and end_date
            # Creates a DataFrame with only one column: 'date'
            dates = pd.date_range(start= self.start_date, end= self.end_date, freq= f"D")
            self.df = pd.DataFrame({"date": dates})

            result = {"DataFrame built succesfully": True}
            print(result)
        except Exception as error:
            print(error)
            raise
    
    def get_holidays(self):
        '''
        Retrieves data and creates the bank holiday variables.

        :returns: pandas.DataFrame | short view of the DataFrame if the process was successfully completed.
        :returns: bool | boolean expression if the process was not successfully completed.
        '''
        try:      
            # Code for countries requests (excl. the UK)
            if self.uk_country == None:
                print(f"Getting holidays for {self.country_names[self.country_id]}...")

                # Makes the API requests for all the years between the start_date and end_date
                # It also creates a (key, value) pair for each bank holiday and its dates
                for year in self.years:
                    uri = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{self.country_id}"
                    connection = requests.get(uri)
                    response = json.loads(connection.content)
                    
                    # Parses the API's response
                    for item in response:
                        # Filters by national and public bank holidays
                        if item["types"][0] == "Public" and item["counties"] == None:
                            # Extracts the name of the bank holiday and the date
                            holiday_name = item["name"]
                            holiday_date = pd.to_datetime(item["date"], format= r"%Y-%m-%d")
                            
                            # Creates the (key, value) pair
                            if holiday_name not in self.holidays:
                                self.holidays[holiday_name] = []
                                self.holidays[holiday_name].append(holiday_date)
                            else:
                                self.holidays[holiday_name].append(holiday_date)

                # Parses the holiday dictionary (i.e., iterates through all holidays)
                for holiday in self.holidays:
                    new_column = list()

                    # Creates a list containing 1s and 0s
                    for (index, row) in self.df.iterrows():
                        if row["date"] in self.holidays[holiday][:]:
                            new_column.append(1)
                        else:
                            new_column.append(0)

                    # Creates the bank holiday column
                    self.df[holiday + " BH"] = new_column
                
                # Converts the daily data to weekly
                if self.week_ending == False:
                    self.df = self.df.resample(f"W-{self.day}", label= "left", closed= "left", on= "date").sum()
                else:
                    self.df = self.df.resample(f"W-{self.day}", label= "right", closed= "right", on= "date").sum()
                
                # Resets index and changes the dates format
                self.df.reset_index(inplace= True)
                self.df["date"] = self.df["date"].dt.strftime(r"%d/%m/%Y")

                # Handles punctuation issues
                if self.country_id == "AR":
                    self.df = self.df.rename(columns= {'''General José de San Martín Memorial Day''': '''General Jose de San Martin Memorial Day''',
                                                       '''Anniversary of the Passing of General Martín Miguel de Güemes''': '''Anniversary of the Passing of General Martin Miguel de Güemes'''})

                result = {f"Holidays for {self.country_names[self.country_id]} successfully added to DataFrame": True}
                print(result)
            # Code only for the UK requests
            if self.uk_country != None:
                country = f"{self.country_names[self.country_id]} - {self.uk_country}"
                print(f"Getting holidays for {country}...")

                # Makes the API requests for all the years between the start_date and end_date
                # It also creates a (key, value) pair for each bank holiday and its dates
                for year in self.years:
                    uri = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{self.country_id}"
                    connection = requests.get(uri)
                    response = json.loads(connection.content)
                    
                    # Parses the API's response
                    # In this case, it will filter by the public holidays that are either unique for the country or shared by all of them
                    for item in response:
                        try:
                            if item["types"][0] == "Public" and country in item["counties"]:
                                # Extracts the name of the bank holiday and the date
                                holiday_name = item["name"]
                                holiday_date = pd.to_datetime(item["date"], format= r"%Y-%m-%d")
                                
                                # Creates the (key, value) pair
                                if holiday_name not in self.holidays:
                                    self.holidays[holiday_name] = []
                                    self.holidays[holiday_name].append(holiday_date)
                                else:
                                    self.holidays[holiday_name].append(holiday_date)
                        except:
                            if item["types"][0] == "Public" or item["counties"] == None:
                                # Extracts the name of the bank holiday and the date
                                holiday_name = item["name"]
                                holiday_date = pd.to_datetime(item["date"], format= r"%Y-%m-%d")

                                # Creates the (key, value) pair     
                                if holiday_name not in self.holidays:
                                    self.holidays[holiday_name] = list()
                                    self.holidays[holiday_name].append(holiday_date)
                                else:
                                    self.holidays[holiday_name].append(holiday_date)
                
                # Parses the holiday dictionary (i.e., iterates through all holidays)    
                for holiday in self.holidays:
                    new_column = list()

                    # Creates a list containing 1s and 0s
                    for (index, row) in self.df.iterrows():
                        if row["date"] in self.holidays[holiday][:]:
                            new_column.append(1)
                        else:
                            new_column.append(0)

                    # Creates the bank holiday column
                    self.df[holiday + " BH"] = new_column

                # Converts daily data to weekly
                if self.week_ending == False:
                    self.df = self.df.resample(f"W-{self.day}", label= "left", closed= "left", on= "date").sum()
                else:
                    self.df = self.df.resample(f"W-{self.day}", label= "right", closed= "right", on= "date").sum()

                # Resets index and changes the dates format
                self.df.reset_index(inplace= True)
                self.df["date"] = self.df["date"].dt.strftime(r"%d/%m/%Y")

                # Solves punctuation issues
                self.df = self.df.rename(columns= {'''Queen’s Platinum Jubilee BH''': '''Queen's Platinum Jubilee BH''', '''Queen’s State Funeral BH''': '''Queen's State Funeral BH''',
                                                "Early May Bank Holiday BH": "Early May BH", "Spring Bank Holiday BH": "Spring BH", "Coronation Bank Holiday BH": "Coronation BH"})
                
                result = {f"Holidays for {country} successfully added to DataFrame": True}
                print(result)
        except Exception as error:
            print(error)
            raise

    def build_weekly_dummies(self):
        '''
        Builds a DataFrame containing all weekly dummies.

        :returns: pandas.DataFrame | short view of the DataFrame if the process was successfully completed.
        :returns: bool | boolean expression if the process was not successfully completed.
        '''
        try:
            print("Building weekly dummies...")
            # Creates a new DataFrame with a daily frequency
            dates = pd.date_range(start= self.start_date, end= self.end_date, freq= "D")
            self.weekly_df = pd.DataFrame({"date": dates})

            # Creates the 'Week #' column that will be used to create the dummy variables
            for (index, row) in self.weekly_df.iterrows():
                self.week_numbers.append(row["date"].isocalendar().week)
            self.weekly_df["Week #"] = self.week_numbers
            
            # Creates the dummy columns and appends them to the DataFrame
            for i in range(1, 54):
                week = f"Week {i}"
                if week not in self.week_dummies:
                    self.week_dummies[week] = []
                
                for (index, row) in self.weekly_df.iterrows():
                    if row["Week #"] == i:
                        self.week_dummies[week].append(1)
                    else:
                        self.week_dummies[week].append(0)
                
                self.weekly_df[f"Dummy {week}"] = self.week_dummies[week]
            
            # Drop the 'Week #' column
            self.weekly_df = self.weekly_df.drop(columns= "Week #")

            # Converts daily weeks to weekly
            if self.week_ending == False:
                self.weekly_df = self.weekly_df.resample(f"W-{self.day}", label= "left", closed= "left", on= "date").sum()
            else:
                self.weekly_df = self.weekly_df.resample(f"W-{self.day}", label= "right", closed= "right", on= "date").sum()
            
            # Replaces values to 1s and 0s
            for column in self.weekly_df.columns:
                self.weekly_df[column] = (self.weekly_df[column] > 3).astype(int)
            
            # Resets index and changes the date format 
            self.weekly_df.reset_index(inplace= True)
            self.weekly_df["date"] = self.weekly_df["date"].dt.strftime(r"%d/%m/%Y")

            result = {"Weekly dummies built successfully": True}
            print(result)
        except Exception as error:
            print(error)
            raise

    def build_monthly_dummies(self):
        '''
        Builds a DataFrame containing all monthly dummies.

        :returns: pandas.DataFrame | short view of the DataFrame if the process was successfully completed.
        :returns: bool | boolean expression if the process was not successfully completed.
        '''
        try:
            print("Building monthly dummies...")

            # Creates a new DataFrame with a daily frequency
            dates = pd.date_range(start= self.start_date, end= self.end_date, freq= "D")
            self.monthly_df = pd.DataFrame({"date": dates})

            # Creates the 'Month #' column that's use to create the dummy variables
            for (index, row) in self.monthly_df.iterrows():
                self.month_numbers.append(row["date"].month)
            self.monthly_df["Month #"] = self.month_numbers
            
            # Creates the dummy variables and appends them to the DataFrame
            months = ["January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]

            for i in range(1, 13):
                month = months[i - 1]

                if month not in self.month_dummies: 
                    self.month_dummies[month] = []

                for (index, row) in self.monthly_df.iterrows():
                    if row["Month #"] == i:
                        self.month_dummies[month].append(1)
                    else:
                        self.month_dummies[month].append(0)

                self.monthly_df[f"Dummy {month}"] = self.month_dummies[month]
            
            # Drops unused columns
            self.monthly_df = self.monthly_df.drop(columns= ["Month #"])
            
            # Converts daily data to weekly
            if self.week_ending == False:
                self.monthly_df = self.monthly_df.resample(f"W-{self.day}", label= "left", closed= "left", on= "date").sum()
            else:
                self.monthly_df = self.monthly_df.resample(f"W-{self.day}", label= "right", closed= "right", on= "date").sum()
            
            # Replaces values to 0s and 1s
            for column in self.monthly_df.columns:
                self.monthly_df[column] = (self.monthly_df[column] > 3).astype(int)

            # Resets index and changes the dates formats
            self.monthly_df.reset_index(inplace= True)
            self.monthly_df["date"] = self.monthly_df["date"].dt.strftime(r"%d/%m/%Y")

            result = {"Monthly dummies built successfully": True}
            print(result)
        except Exception as error:
            print(error)
            raise
        
    def join_dataframes(self):
        '''
        Joins all DataFrames created into one.

        :returns: bool | boolean expression indicating if the process was completed or not.
        '''
        try:
            print("Joining all dataframes...")

            # Joins the weekly and monthly dummies DataFrames
            # It uses the 'inner join' method and the 'date' column
            self.new_df = self.weekly_df.merge(self.monthly_df, how= "inner", on= "date")

            # Joins the bank holidays DataFrame with the new one
            # It uses the 'inner join' method and the 'date' column
            self.df = self.df.merge(self.new_df, how= "inner", on= "date")

            result = {"DataFrames successfully joined": True}
            print(result)
        except Exception as error:
            print(error)
            raise

    def get_csv(self, outpath: str):
        '''
        Creates the Seasonality csv file.

        :param outpath: str | folder in which data should be written to.
        
        :returns: bool | boolean expression indicating whether the process was successfully completed or not.
        '''
        try:
            self.build_dataframe()
            self.get_holidays()
            self.build_weekly_dummies()
            self.build_monthly_dummies()
            self.join_dataframes()

            ## Creates the 'account' column and change the order of columns
            # self.df["account"] = "national"
            # columns = self.df.columns.tolist()
            # columns = columns[-1:] + columns[:-1]
            # self.df = self.df[columns]

            print("Preparing CSV file...")

            ## Creates an array with the DataFrame's headers
            ## That row will be added at the top of the DataFrame before adding the blank rows
            # headers_row = list()
            # for header in self.df.columns:
            #     headers_row.append(header)
            # headers_row = np.array([headers_row])

            ## Saves the DataFrame into a CSV file and
            ## opens it without the headers
            self.df.to_csv(outpath + r"Seasonality.csv", index= False)

            # self.df = pd.read_csv(outpath + r"Seasonality.csv", skiprows= [0], header= None)
            # headers_row = pd.DataFrame(headers_row, columns= self.df.columns, index= [0])

            ## Creates a DataFrame with the blank rows needed for the modeling tool
            # rows = list()
            # for r in range(0, 10):
            #     row = list()
            #     if r == 9:
            #         for c in range(0, len(self.df.columns)):
            #             if c == 0 or c == 1: row.append(None)
            #             else: row.append("SUB")
            #     else:        
            #         for c in range(0, len(self.df.columns)):
            #             row.append("Blank")
            #     rows.append(row)
            # blank = pd.DataFrame(data= rows, columns= self.df.columns)

            ## Adds the headers row at the top of the new DataFrame
            # self.df = pd.concat([headers_row, self.df], ignore_index= True)

            ## Concatenate both DataFrames and saves the new CSV file
            # self.df = pd.concat([blank, self.df], ignore_index= True)
            # self.df = self.df.iloc[1:, :]
            # self.df.to_csv(outpath + r"\Seasonality.csv", index= False, header= None)

            result = {"CSV file successfully written": True}
            print(result)
        except Exception as error:
            print(error)
            raise

class Date:
    def date_convertion(self, wc, date):
        try:
            if wc == "MON":
                if date.weekday() != 0:
                    date = date - timedelta(date.weekday())
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
            elif wc == "TUE":
                if date.weekday() != 1:
                    date = date - timedelta(date.weekday() - 1)
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
            elif wc == "WED":
                if date.weekday() != 2:
                    date = date - timedelta(date.weekday() - 2)
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
            elif wc == "THU":
                if date.weekday() != 3:
                    date = date - timedelta(date.weekday() - 3)
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
            elif wc == "FRI":
                if date.weekday() != 4:
                    date = date - timedelta(date.weekday() - 4)
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
            elif wc == "SAT":
                if date.weekday() != 5:
                    date = date - timedelta(date.weekday() - 5)
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
            elif wc == "SUN":
                if date.weekday() != 6:
                    date = date - timedelta(date.weekday() - 6)
                    return date.strftime(r"%d/%m/%Y")
                else:
                    return date.strftime(r"%d/%m/%Y")
        except Exception as ex:
            print("Something went wrong on the date_convertion() function...")
            print(ex)
