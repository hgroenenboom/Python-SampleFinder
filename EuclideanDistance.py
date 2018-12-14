import math

def printMDArray(mdArray):
    for i in range(len(mdArray)):
        print(str(i) + ": " + str(mdArray[i]))


def getEuclidianDistance(coord1, coord2):
    # print(coord1, "\n", coord2)
    numDimensions = len(coord1)
    eucDist = 0

    for i in range(numDimensions):
        eucDist += pow((coord1[i] - coord2[i]), 2.0)
        # print("adding values to eucDist:", eucDist)

    eucDist = math.sqrt(eucDist)
    # print("after sqrt:", eucDist)

    return eucDist


def getVectorDotProduct(coord1, coord2):
    numDimensions = len(coord1)
    dotProd = 0

    for i in range(numDimensions):
        dotProd += coord1[i] * coord2[i]

    return dotProd


def getShortestDistanceWithPoints(listOfCoords):
    numberOfCoords = len(listOfCoords)
    printMDArray(listOfCoords)
    print()

    # find all possibilities and calculate euclidian distances
    eucDistances = []
    for i in range(numberOfCoords - 1):
        eucDistancesOfCoord_i = []
        for n in range(i + 1, numberOfCoords):
            newDist = getEuclidianDistance(listOfCoords[i], listOfCoords[n])
            eucDistancesOfCoord_i.append(newDist)
        eucDistances.append(eucDistancesOfCoord_i)
    # print(eucDistances)
    # print()

    # get a list of the minimum distance along with the corresponding point per point
    listOfMinimums = []
    for i in range(numberOfCoords - 1):
        newMin = min(range(len(eucDistances[i])), key=eucDistances[i].__getitem__)
        newMinValue = min(eucDistances[i])
        listOfMinimums.append([newMin, newMinValue])
    # printMDArray(listOfMinimums)
    # print()

    # find the absolute shortest distance of all the found shortest distances in listOfMinimums
    listOfMinimums2 = []
    for i in range(len(listOfMinimums)):
        listOfMinimums2.append(listOfMinimums[i][1])

    # get smallest value
    firstPoint = min(range(len(listOfMinimums2)), key=listOfMinimums2.__getitem__)
    secondPoint = firstPoint + listOfMinimums[firstPoint][0] + 1
    distance = min(listOfMinimums2)

    return ["point " + str(firstPoint) + " and " + str(secondPoint), distance]

def getIndexOfClosestPoint(coord, coords):
    distances = []

    for co in coords:
        if coord is not co:
            distances.append( getEuclidianDistance(coord, co) )
        else:
            distances.append( 1000000000 )

    closestPoint = min( range( len(distances) ), key=distances.__getitem__ )
    print("Closest point found: " + str(closestPoint) )

    return closestPoint

def getPointIndicesSortedByClosest(coord, coords):
    distances = []

    for co in coords:
        if coord is not co:
            distances.append( getEuclidianDistance(coord, co) )
        else:
            distances.append( 1000000000 )

    closestPoints = []

    if(len(distances) != len(coords)):
        print("Error length of array changed in EuclideanDistance::getPointIndicesSortedByClosest")
        print("len distances:", len(distances), " - len coords:", len(coords))

    for i in range(len(coords)):
        closestPoint = min( range( len(distances) ), key=distances.__getitem__ )
        closestPoints.append(closestPoint)
        # print(distances[closestPoint])
        distances[closestPoint] = 1000000000

    # print(closestPoints)

    return closestPoints