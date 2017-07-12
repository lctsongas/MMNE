
#Positioning Calculations

##########
#
#A x,y coordinate frame is attached to the robot. With the origin set to
#   the initial starting location facing the (+)x-axis.
#
#Units: 1 unit in the coordinate frame represents 1 meter
#Heading: the direction the robot is pointing
#Bearing: angle in degrees between destination and x-axis
#           (traditionally, bearing is angle between destination and North)
#
##########
import math

#find distance to destination from current position
def distance_togo(xCurrent, yCurrent, xDestination, yDestination):
    xydist = math.sqrt(((xDestination - xCurrent) * (xDestination - xCurrent)) \
                                + ((yDestination - yCurrent) * (yDestination - yCurrent)))
    return xydist

#find bearing in degrees relative to x-axis
def bearing_deg(xCurrent, yCurrent, xDestination, yDestination):
    xyangle = math.degrees(math.atan2((yDestination - yCurrent),(xDestination - xCurrent)))
    return xyangle

#Return degree angle between current heading and bearing
def angle_diff(heading, bearing):
    angle = math.fmod((heading - bearing + 3600), 360)
    if angle > 180:
        angle = 360 - angle
    return angle

#determine clockwise(CW) or counterclockwise(CCW) rotation toward bearing
def rotation_dir(heading, bearing):
    dif = bearing - heading
    if dif > 0:
        if dif > 180:
            CW = False
        else:
            CW = True
    else:
        if dif >= -180:
            CW = False
        else:
            CW = True
    return CW

#Haversine calculation to determine distance between 2 sets of Lat/Lon coordinates
def haversine(startLat, startLon, endLat, endLon):
    lat1 = math.radians(math.fabs(startLat))
    lon1 = math.radians(math.fabs(startLon))
    lat2 = math.radians(math.fabs(endLat))
    lon2 = math.radians(math.fabs(endLon))

    EarthRadius = 6371000 #Earth's radius = 6,371 km

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    hav_step1 = math.sin(delta_lat/2) * math.sin(delta_lat/2) \
            + math.cos(lat1) * math.cos(lat2) \
            * math.sin(delta_lon/2) * math.sin(delta_lon/2)
    hav_step2 = 2 * math.atan2(math.sqrt(hav_step1), math.sqrt(1 - hav_step1))
    distance = EarthRadius * hav_step2
    return distance

#get angle between two Lat and Lon
def gpsbearing(lat1, lon1, lat2, lon2):
    #delta_lon = math.fabs(lat2 - lat1)
    lat1 = math.radians(math.fabs(lat1))
    lon1 = math.radians(math.fabs(lon1))
    lat2 = math.radians(math.fabs(lat2))
    lon2 = math.radians(math.fabs(lon2))

    delta_lon = lat2 - lat1
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = (math.cos(lat1) * math.sin(lat2)) \
        - (math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1))
    deg = math.degrees(math.atan2(y, x))
    initial_bearing = (deg + 360) % 360
    final_bearing = (initial_bearing + 180) % 360
    return initial_bearing

#simplified gps to xy coord HUGE ERROR (only for small areas) - not used, for testing
def xyprojection_errorlarge(lat, lon):
    EarthRadius = 6371000 #Earth's radius = 6,371 km
    lat = math.radians(math.fabs(lat))
    lon = math.radians(math.fabs(lon))
    y = EarthRadius * lat
    x = EarthRadius * lon * math.cos(lat)
    return x, y

#get x,y coord based on angle and distance from origin
#used in converting a gps coordinate to rectangular coord after getting dist and angle
def xy_getpoint(angle, distance): #need angle in degrees
    angle = math.radians(angle)
    y = distance * math.sin(angle)
    x = distance * math.cos(angle)
    return x, y
