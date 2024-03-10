# SeasonalityScript

This script creates bank holiday variables as well as other seasonality variables for a specified country.

## Description
1.	Open the “Run” notebook.
2.	Run the first block of code to import all the libraries needed.
3.	The second line of code creates the SeasonalityScript object. At this point you will have to set some parameters:

    1. **country_code** (required): Two-letter code for the country you want to retrieve data from. The most common ones are US (United States), GB (Great Britain), IE (Ireland), and CA (Canada). If you need data for another country, you should call the _get_country_codes()_ function, which returns a list of all countries available with their respective country code.
    2. **start_date** (required): First date of the dataset.
    3. **end_date** (required): End date of your dataset.
    4. **day** (required): First day of the week (i.e., if you’re working with a week commencing Monday, you’ll have to use ‘MON’ as your parameter).
    5. **uk_country** (optional): In case you’re working with a country in the UK (e.g., England) you’ll have to set this parameter to uk_country= “ENG”. Other possible countries could be Wales (WLS), Scotland (SCT) or Northern Ireland (NIR).
    6. **week_ending** (optional): In case you’re working with a week-ending setting, you’ll have to set this parameter to week_ending= True.

7. Finally, you’ll have to run the get_csv() function in the last line of code. This function takes one parameter which is the folder path you want your CSV file to be saved (omit “\Seasonality.csv” to the file path)
