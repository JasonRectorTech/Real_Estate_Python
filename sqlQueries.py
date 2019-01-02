from jsobject import Object
import re

#returns all properties currently being rented
def getAllRentedProperties(cursor):
    dataArray = []

    query = ("""
                SELECT prop.street_address, prop.city, prop.state, prop.zip_code, prop.sqft, prop.beds, prop.baths, prop.neighborhood, MAX(details.rental_price) as rental_price, MAX(details.rental_price_sqft), prop.latitude, prop.longitude, prop.property_url
                FROM `properties` AS prop
                INNER JOIN `property_details` AS details
                ON prop.street_address = details.street_address
                WHERE `is_rental` = True
                AND prop.rental_status = "inactive"
                GROUP BY prop.street_address;
            """)

    cursor.execute(query)
    tupleProperties = cursor.fetchall();

    # convert tuple to array
    for streetAddress, city, state, zipCode, sqft, beds, baths, neighborhood, rentalPrice, rentalPriceSqft, latitude, longitude, propertyURL in tupleProperties:
        dataObject = {
            "streetAddress": streetAddress,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "sqft": sqft,
            "beds": beds,
            "baths": baths,
            "neighborhood": neighborhood,
            "rentalPrice": rentalPrice,
            "rentalPriceSqft": rentalPriceSqft,
            "latitude": latitude,
            "longitude": longitude,
            "propertyURL": propertyURL,
          }

        jsObject = Object(dataObject)

        #store all houses in javascript-like array of objects
        dataArray.append(jsObject)

    return dataArray

#returns all properties currently for sale rented
def getAllForSaleProperties(cursor):
    dataArray = []

    query = ("""
                SELECT prop.street_address, prop.city, prop.state, prop.zip_code, prop.sqft, prop.beds, prop.baths, prop.neighborhood, MAX(details.rental_price) as rental_price, MAX(details.rental_price_sqft), prop.latitude, prop.longitude, prop.property_url
                FROM `properties` AS prop
                INNER JOIN `property_details` AS details
                ON prop.street_address = details.street_address
                WHERE `is_rental` = False
                AND prop.forsale_status = "active"
                AND prop.city = "Bentonville"
                GROUP BY prop.street_address;
            """)

    cursor.execute(query)
    tupleProperties = cursor.fetchall();

    # convert tuple to array
    for streetAddress, city, state, zipCode, sqft, beds, baths, neighborhood, rentalPrice, rentalPriceSqft, latitude, longitude, propertyURL in tupleProperties:
        dataObject = {
            "streetAddress": streetAddress,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "sqft": sqft,
            "beds": beds,
            "baths": baths,
            "neighborhood": neighborhood,
            "rentalPrice": rentalPrice,
            "rentalPriceSqft": rentalPriceSqft,
            "latitude": latitude,
            "longitude": longitude,
            "propertyURL": propertyURL,
          }

        jsObject = Object(dataObject)

        #store all houses in javascript-like array of objects
        dataArray.append(jsObject)

    return dataArray

def getPropertiesByFilter(cursor, cities, minForsalePrice, maxForsalePrice, minSqft, maxSqft, minPriceSqft, maxPriceSqft, isForSale, isForeclosure, isPending,
                        isSold, isRecentlySold, isForRent, isRented, isNoRentals, beds, baths):
    #init variables
    dataArray = []
    params = ""
    formattedCities = ""
    counter = 1

    #format cities into comma separated list
    for city in cities:

        formattedCities += '"' + city + '"'

        if(counter != len(cities)):
            formattedCities += ","

        counter += 1

    #check if price was passed
    if((minForsalePrice > 0) and (maxForsalePrice > 0)):
        params += " AND details.forsale_price BETWEEN " + str(minForsalePrice) + " AND " + str(maxForsalePrice)
    elif(minForsalePrice > 0):
        params += " AND details.forsale_price >= " + str(minForsalePrice)
    elif(maxForsalePrice > 0):
        params += " AND details.forsale_price <= " + str(maxForsalePrice)

    #check if minSqft was passed
    if((minSqft > 0) and (maxSqft > 0)):
        params += " AND prop.sqft BETWEEN " + str(minSqft) + " AND " + str(maxSqft)
    elif(minSqft > 0):
        params += " AND prop.sqft >= " + str(minSqft)
    elif(maxSqft > 0):
        params += " AND prop.sqft <= " + str(maxSqft)

    #check if priceSqft was passed
    if((minPriceSqft > 0) and (maxPriceSqft > 0)):
        params += " AND details.forsale_price_sqft BETWEEN " + str(minPriceSqft) + " AND " + str(maxPriceSqft)
    elif(minPriceSqft > 0):
        params += " AND details.forsale_price_sqft >= " + str(minPriceSqft)
    elif(maxPriceSqft > 0):
        params += " AND details.forsale_price_sqft <= " + str(maxPriceSqft)

    #check if beds was passed
    if(beds != ""):
        #check for the '+' char for exact or >=
        if(re.search(r"\+", beds)):
            pattern = re.compile(r'[0-9]+')
            beds = pattern.search(beds).group(0)
            params += " AND prop.beds >= " + beds
        else:
            params += " AND prop.beds = " + beds

    #check if baths was passed
    if(baths != ""):
        #check for the '+' char for exact or >=
        if(re.search(r"\+", baths)):
            pattern = re.compile(r'[0-9]+')
            baths = pattern.search(baths).group(0)
            params += " AND prop.baths >= " + baths
        else:
            params += " AND prop.baths = " + baths

    #for sale properties
    if(isForSale == True):
        params += " AND prop.forsale_status = 'active'"
    if(isForeclosure == True):
        #not tracking forclosures
        print("Foreclosure passed")
    if(isPending == True):
        #not tracking pending
        print("Pending passed")
    if(isSold == True):
        #need to write query
        print("Sold passed")
    if(isRecentlySold == True):
        #need to write query
        print("Recently Sold passed")

    #renting properties
    if(isForRent == True):
       params += " AND prop.is_rental = True AND prop.rental_status = 'active'"
    if(isRented == True):
        params += " AND prop.is_rental = True AND prop.rental_status = 'inactive'"
    if(isNoRentals == True):
        params += " AND prop.is_rental = False AND prop.rental_status = 'inactive'"

    #TODO use parameters for city
    query = ("""
                SELECT prop.street_address, prop.city, prop.state, prop.zip_code, prop.sqft, prop.beds, prop.baths, prop.neighborhood,
                    MAX(details.forsale_price), MAX(details.forsale_price_sqft), MAX(details.rental_price), MAX(details.rental_price_sqft),
                    details.date, details.event, prop.latitude, prop.longitude, prop.property_url
                FROM `properties` AS prop
                INNER JOIN `property_details` AS details
                ON prop.street_address = details.street_address
                WHERE prop.city in ({0})
                {1}
                GROUP BY prop.street_address;
            """).format(formattedCities, params)

    cursor.execute(query)
    tupleProperties = cursor.fetchall();

    # convert tuple to array
    for streetAddress, city, state, zipCode, sqft, beds, baths, neighborhood, forsalePrice, forsalePriceSqft, rentalPrice, rentalPriceSqft, date, event, latitude, longitude, propertyURL in tupleProperties:
        dataObject = {
            "streetAddress": streetAddress,
            "city": city,
            "state": state,
            "zipCode": zipCode,
            "sqft": sqft,
            "beds": beds,
            "baths": baths,
            "neighborhood": neighborhood,
            "forsalePrice": forsalePrice,
            "forsalePriceSqft": forsalePriceSqft,
            "rentalPrice": rentalPrice,
            "rentalPriceSqft": rentalPriceSqft,
            "date": str(date),
            "event": event,
            "latitude": latitude,
            "longitude": longitude,
            "propertyURL": propertyURL,
          }

        jsObject = Object(dataObject)

        #store all houses in javascript-like array of objects
        dataArray.append(jsObject)

    return dataArray