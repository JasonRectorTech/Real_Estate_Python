from flask import Flask, jsonify, request
import credentials
import mysql.connector
import traceback
import sqlQueries

#init Flask application
application = Flask(__name__)

#handling cors
@application.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', 'http://real-estate-maps.s3-website.us-east-2.amazonaws.com')
  response.headers.add('Access-Control-Allow-Headers', '*')
  response.headers.add('Access-Control-Allow-Methods', 'GET')
  return response

#returns all currently rented properties
@application.route('/getAllRentedProperties', methods=["GET"])
def getAllRentedProperties():
    try:
        cnx, cursor = connectDB()

        #closes connection
        cursor.close()
        cnx.close()

        #gets all property details from the properties table by county
        rentedProperties = sqlQueries.getAllRentedProperties(cursor)
    except:
        errorMessage = str(traceback.format_exc())
        print(errorMessage)

    response = jsonify(results=rentedProperties)
    response.status_code = 200

    return response

@application.route('/getAllForSaleProperties', methods=["GET"])
def getAllForSaleProperties():
    try:
        cnx, cursor = connectDB()

        #gets all property details from the properties table by county
        forSaleProperties = sqlQueries.getAllForSaleProperties(cursor)

        #closes connection
        cursor.close()
        cnx.close()
    except:
        errorMessage = str(traceback.format_exc())
        print(errorMessage)

    response = jsonify(results=forSaleProperties)
    response.status_code = 200

    return response

#gets properties from filter
@application.route('/getProperties', methods=["GET"])
def getPropertiesByFilter():
    rentedProperties = []

    #get parameters
    #TODO add logic to pass in an array of cities
    #city is required
    cities = request.args.getlist("cities")

    (
        minForsalePrice,
        maxForsalePrice,
        minSqft,
        maxSqft,
        minPriceSqft,
        maxPriceSqft,
        isForSale,
        isForeclosure,
        isPending,
        isSold,
        isRecentlySold,
        isForRent,
        isRented,
        isNoRentals,
        beds,
        baths
    ) = initParams(request)


    try:
        cnx, cursor = connectDB()

        #gets all property details from the properties table by county
        rentedProperties = sqlQueries.getPropertiesByFilter(cursor, cities, minForsalePrice, maxForsalePrice, minSqft, maxSqft, minPriceSqft, maxPriceSqft,
                                                          isForSale, isForeclosure, isPending, isSold, isRecentlySold,
                                                          isForRent, isRented, isNoRentals, beds, baths)

        #closes connection
        cursor.close()
        cnx.close()
    except:
        errorMessage = str(traceback.format_exc())
        print(errorMessage)

    response = jsonify(results=rentedProperties)
    response.status_code = 200

    return response

def initParams(request) :
    #if not passed in, defaulting to 0 which is assuming unlimited
    minForsalePrice = request.args.get("minForsalePrice", 0.0, type=float)
    maxForsalePrice = request.args.get("maxForsalePrice", 0.0, type=float)

    minSqft = request.args.get("minSqft", 0, type=float)
    maxSqft = request.args.get("maxSqft", 0, type=float)

    minPriceSqft = request.args.get("minPriceSqft", 0.0, type=float)
    maxPriceSqft = request.args.get("maxPriceSqft", 0.0, type=float)

    #for sale is the most common use case, so assuming true if not passed in
    isForSale = request.args.get("isForSale", True, type=bool)

    isForeclosure = request.args.get("isForeclosure", False, type=bool)

    isPending = request.args.get("isPending", False, type=bool)

    isSold = request.args.get("isSold", False, type=bool)

    isRecentlySold = request.args.get("isRecentlySold", False, type=bool)

    isForRent = request.args.get("isForRent", False, type=bool)

    isRented = request.args.get("isRented", False, type=bool)

    isNoRentals = request.args.get("isNoRentals", True, type=bool)

    #strings because of '3plus'
    beds = request.args.get("beds", "1+", type=str)
    baths = request.args.get("baths", "1+", type=str)

    return (
        minForsalePrice,
        maxForsalePrice,
        minSqft,
        maxSqft,
        minPriceSqft,
        maxPriceSqft,
        isForSale,
        isForeclosure,
        isPending,
        isSold,
        isRecentlySold,
        isForRent,
        isRented,
        isNoRentals,
        beds,
        baths
    )

# sets up the db connection
def connectDB():
    env = "dev"

    #gets username and password based on current environment
    username, password = credentials.getDBCredentials(env)

    #gets host based on current environment
    host = credentials.getHost(env)

    cnx = mysql.connector.connect(user=username, password=password, host=host, database='house_db')
    cursor = cnx.cursor()

    return cnx, cursor

if __name__ == '__main__':
    application.debug = True
    application.run()