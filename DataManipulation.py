__author__ = 'phyllis'

from time import sleep
import rauth
import xlrd
import re
import csv

##### FUNCTIONS THAT HELPED IN DATA PROCESSING #####
def isfloat(x):
    '''
    Tests if something can be converted to a float, returns True or False
    Essentially checks for missing values and returns True if there aren't missing values and False if there are
    '''
    try:
        float(x)
        return True
    except ValueError:
        return False


def citymatch(cities, metro, citytup):
    '''
    Used for matching urban areas to the metropolitan areas they're in, returns none if no match is found.
    INPUT:
    cities - a list of lists where each individual list contains the separated urban area name, and state abbreviation.  Ex: [["Portland", "OR"], ["Salt", "Lake", "City", "UT"]]
    metro - metropolitan area name and state abbreviation as a string.  Ex: "Kennewick-Richland-Pasco, WA"
    citytup - a list of tuples with each tuple containing the urban area name, and the cost of living index.  Ex: [("Akron, OH", 100.2), ("Albany, GA", 90.1)]

    OUTPUT:
    None if no match
    Tuple of Urban Name and Cost of Living Index if match.  Ex: ("Akron, OH", 100.2)
    '''

    ## for each urban area
    for i in range(len(cities)):

        ## if there are no words/state abbreviations in the urban area that aren't in the metropolitan area
        if set(cities[i]) - set(re.findall(r"\w{2,}", metro)) == set():

            ## fix some formatting issues for the urban name from the cost of living dataset
            city = str(citytup[i][0]).strip().split(",")

            ## then return a tuple containing the urban name and cost of living index
            return (''.join(city[:-1]) + "," + city[-1], citytup[i][1])

    ## if there's no metropolitan area that matches the criteria, return None
    return None

def statsDat(fname, wkname):
    '''
    Takes the XLS filename and worksheet name as input, returns a list of dictionaries as output
    '''
    statsdict = []
    workbook1 = xlrd.open_workbook(fname)
    ws1 = workbook1.sheet_by_name(wkname)

    ## for each row in the XLS file
    for i in range(1, ws1.nrows):

        ## if the occupation is statistician, there is a corresponding metropolitan area for the urban area in the cost of living dataset
        ## and there are no missing values
        if ws1.cell_value(i, 4) == 'Statisticians' and isfloat(ws1.cell_value(i, 9)) and isfloat(ws1.cell_value(i, 20)) \
                and isfloat(ws1.cell_value(i, 18)) and isfloat(ws1.cell_value(i, 19)) and  isfloat(ws1.cell_value(i, 21)) \
                and isfloat(ws1.cell_value(i, 22)) and citymatch(citylist, ws1.cell_value(i, 2), CoLlist) != None:

            ## create a dictionary with the following keys and values
            statsJ = {}

            ## state abbreviation as PRIM_STATE
            statsJ[str(ws1.cell_value(0, 0))] = str(ws1.cell_value(i, 0))

            ##name of urban area as AREA_NAME
            statsJ[str(ws1.cell_value(0, 2))] = citymatch(citylist, ws1.cell_value(i, 2), CoLlist)[0]

            ## occupation name (statistician) as OCC_TITLE
            statsJ[str(ws1.cell_value(0, 4))] = str(ws1.cell_value(i, 4))

            ## location quotient as LOC QUOTIENT
            statsJ[str(ws1.cell_value(0, 9))] = ws1.cell_value(i, 9)

            ## Median annual income as A_MEDIAN
            statsJ[str(ws1.cell_value(0, 20))] = int(ws1.cell_value(i, 20))

            ## Cost of living as CostLiv
            statsJ['CostLiv'] = citymatch(citylist, ws1.cell_value(i, 2), CoLlist)[1]

            ## Median income adjusted by cost of living as AdjMedInc
            statsJ['AdjMedInc'] = int(ws1.cell_value(i, 20)/(citymatch(citylist, ws1.cell_value(i, 2), CoLlist)[1]/100))

            ##10th, 25th, 75th, and 90th annual income percentiles as A_PCT10, etc
            statsJ[str(ws1.cell_value(0, 18))] = int(ws1.cell_value(i, 18))
            statsJ[str(ws1.cell_value(0, 19))] = int(ws1.cell_value(i, 19))
            statsJ[str(ws1.cell_value(0, 21))] = int(ws1.cell_value(i, 21))
            statsJ[str(ws1.cell_value(0, 22))] = int(ws1.cell_value(i, 22))

            ## my US STATES REGIONS SUBREGIONS dataset didn't have DC, so I manually matched DC with a region
            if str(ws1.cell_value(i, 0)) == 'DC':
                statsJ['Region'] = 'Northeast'

            ## Region of state as Region
            else:
                statsJ['Region'] = regMap[str(ws1.cell_value(i, 0))]

            ## add the dictionary to the list
            statsdict.append(statsJ)
    return statsdict


## use the dataset with state abbreviations and regions
regions = csv.DictReader(open("C:\PyCharm\SI 601\SI 601 Project\US STATES REGIONS SUBREGIONS.csv", 'rU'), delimiter = ',')

##Create a dictionary to map the state abbreviation to the region
regMap = {}

##create a key for every state abbreviation with its region as the value
for row in regions:
    regMap[row['State Code']] = row['Region']

## open the Cost of Living dataset with the urban area and cost of living index
wkbk = xlrd.open_workbook("C:\PyCharm\SI 601\SI 601 Project\CostofLiving2010.xls")
ws = wkbk.sheet_by_name('0728')

CoLlist = []
## for each urban area, create a tuple for the urban area name, and cost of living index, and append it to the list CoLlist
## this is to create input for the function citymatch
for i in range(4, ws.nrows-2):
    CoLlist.append((ws.cell_value(i, 0), round(ws.cell_value(i, 1), 1)))

##create a list of lists where each list contains the urban area name separated by words.  Ex: [["Anchorage", "AK"], ["Boston", "MA"]]
citylist = [re.findall(r"\w{2,}", key[0]) for key in CoLlist]

## create the list of dictionaries for each separate XLS file for the wages dataset and concatenate all the lists together
AK_IN = statsDat("C:\PyCharm\SI 601\SI 601 Project\MSA_M2013_dl_1_AK_IN.xls", 'MSA_dl_1')
KS_NY = statsDat("C:\PyCharm\SI 601\SI 601 Project\MSA_M2013_dl_2_KS_NY.xls", 'MSA_dl_2')
OH_WY = statsDat("C:\PyCharm\SI 601\SI 601 Project\MSA_M2013_dl_3_OH_WY.xls", 'MSA_dl_3')

#### US_stat is a list of dictionaries where each dictionary contains statistician income info for each Urban area that matched with a Metropolitan area
#### and didn't contain any missing values
US_stat = AK_IN + KS_NY + OH_WY


### for each Urban Area, make a request to the Yelp Search API
for loc in US_stat:
    session = rauth.OAuth1Session(
        consumer_key = "oZ35IZvUFCEq8K-hd4hIZQ"
        ,consumer_secret = "PfxQImL98mcrGz7vq-Evpgl8PTQ"
        ,access_token = "n49axmdxttBKN4UueonlJS8qiNThpaSj"
        ,access_token_secret = "ntIOZ9BWa3kN4ZAUkbNnNe6bhRY")

    ### get the information for seafood restaurants in each location, and sort the list of restaurants by rating
    request = session.get("http://api.yelp.com/v2/search",params={"term": "restaurant", "category_filter": "seafood", "sort":2, "location": loc['AREA_NAME']})

    seaDat = request.json()

    ### if there are businesses
    if "businesses" in seaDat:

        ##add the key "goodSeaR" and get the number of seafood restaurants with a rating above 3 as the value
        loc["goodSeaR"] = len([x for x in seaDat['businesses'] if not x['is_closed'] and x['rating'] > 3])

        ## if there are 20 or more good seafood restaurants, look at the next 20 seafood restaurants
        if loc["goodSeaR"] == 20:
            request = session.get("http://api.yelp.com/v2/search",params={"term": "restaurant", "category_filter": "seafood", "limit": 20, "offset": 20, "sort":2, "location": loc['AREA_NAME']})
            seaDat = request.json()

            ## add however many more good seafood restaurants there are
            loc["goodSeaR"] += len([x for x in seaDat['businesses'] if not x['is_closed'] and x['rating'] > 3])
    else:
        loc["goodSeaR"] = None
    sleep(2)
session.close()


###### write the final dataset as a CSV file ########
indvars = US_stat[0].keys()
finDat_csv = open("C:\PyCharm\SI 601\SI 601 Project\\601ProjFinDat.csv", 'wb')
writefinD = csv.DictWriter(finDat_csv, delimiter=',', fieldnames=indvars)
writefinD.writerow(dict((iv,iv) for iv in indvars))
for city in US_stat:
     writefinD.writerow(city)
finDat_csv.close()