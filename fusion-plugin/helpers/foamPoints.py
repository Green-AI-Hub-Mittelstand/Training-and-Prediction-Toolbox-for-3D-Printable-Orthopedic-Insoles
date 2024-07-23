import math, re

class FoamPointDefinitions:
    VORDERSTER_PUNKT = 0
    
    ZEHE_1 = 1
    ZEHE_2 = 2
    ZEHE_3 = 3
    ZEHE_4 = 4
    ZEHE_5 = 5
    
    BALLENPUNKT_INNEN = 6
    BALLENPUNKT_AUSSEN = 7
    
    MITTELFUSSKOEPFCHEN_1 = 8
    MITTELFUSSKOEPFCHEN_2 = 9
    MITTELFUSSKOEPFCHEN_3 = 10
    MITTELFUSSKOEPFCHEN_4 = 11
    MITTELFUSSKOEPFCHEN_5 = 12
    
    PELOTTENPUNKT = 13
    
    BASIS_MFK_5 = 14
    
    LAENGSGEWOELBESTUETZE = 15
    FERSENSPORNPUNKT = 16
    FERSENMITTELPUNKT = 17
    FERSENBREITE_AUSSEN = 18
    FERSENBREITE_INNEN = 19
    
    HINTERSTER_PUNKT = 20
    SCHNITTACHSE = 21
    
    UNRECOGNIZED = -1
    
    
    
FOAM_POINT_CHOICES = (
    (FoamPointDefinitions.UNRECOGNIZED, "-- nicht erkannt --"),
    (FoamPointDefinitions.VORDERSTER_PUNKT, "Vorderster Punkt"),
    (FoamPointDefinitions.ZEHE_1, "Zehe 1"),
    (FoamPointDefinitions.ZEHE_2, "Zehe 2"),
    (FoamPointDefinitions.ZEHE_3, "Zehe 3"),
    (FoamPointDefinitions.ZEHE_4, "Zehe 4"),
    (FoamPointDefinitions.ZEHE_5, "Zehe 5"),
    (FoamPointDefinitions.BALLENPUNKT_INNEN, "Ballenpunkt Innen"),
    (FoamPointDefinitions.BALLENPUNKT_AUSSEN, "Ballenpunkt Aussen"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_1, "Mittelfusskoepfchen 1"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_2, "Mittelfusskoepfchen 2"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_3, "Mittelfusskoepfchen 3"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_4, "Mittelfusskoepfchen 4"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_5, "Mittelfusskoepfchen 5"),
    (FoamPointDefinitions.PELOTTENPUNKT, "Pelottenpunkt"),
    (FoamPointDefinitions.BASIS_MFK_5, "Basis MFK 5"),
    (FoamPointDefinitions.LAENGSGEWOELBESTUETZE, "Laengsgewoelbestuetze"),
    (FoamPointDefinitions.FERSENSPORNPUNKT, "Fersenspornpunkt"),
    (FoamPointDefinitions.FERSENMITTELPUNKT, "Fersenmittelpunkt"),
    (FoamPointDefinitions.FERSENBREITE_AUSSEN, "Fersenbreite Aussen"),
    (FoamPointDefinitions.FERSENBREITE_INNEN, "Fersenbreite Innen"),
    (FoamPointDefinitions.HINTERSTER_PUNKT, "Hinterster Punkt"),    
    (FoamPointDefinitions.SCHNITTACHSE, "Schnittachse"),    
 
)

FOAM_POINT_CHOICES_SHORT = (
    (FoamPointDefinitions.UNRECOGNIZED, "-- nicht erkannt --"),
    (FoamPointDefinitions.VORDERSTER_PUNKT, "Vord. Punkt"),
    (FoamPointDefinitions.ZEHE_1, "Z 1"),
    (FoamPointDefinitions.ZEHE_2, "Z 2"),
    (FoamPointDefinitions.ZEHE_3, "Z 3"),
    (FoamPointDefinitions.ZEHE_4, "Z 4"),
    (FoamPointDefinitions.ZEHE_5, "Z 5"),
    (FoamPointDefinitions.BALLENPUNKT_INNEN, "BallP Innen"),
    (FoamPointDefinitions.BALLENPUNKT_AUSSEN, "BallP Aussen"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_1, "MFK 1"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_2, "MFK 2"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_3, "MFK 3"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_4, "MFK 4"),
    (FoamPointDefinitions.MITTELFUSSKOEPFCHEN_5, "MFK 5"),
    (FoamPointDefinitions.PELOTTENPUNKT, "Pelo Punkt"),
    (FoamPointDefinitions.BASIS_MFK_5, "Basis MFK 5"),
    (FoamPointDefinitions.LAENGSGEWOELBESTUETZE, "Laengsgewoelbestuetze"),
    (FoamPointDefinitions.FERSENSPORNPUNKT, "Fersenspornpunkt"),
    (FoamPointDefinitions.FERSENMITTELPUNKT, "Fersenmittelpunkt"),
    (FoamPointDefinitions.FERSENBREITE_AUSSEN, "Ferse Aussen"),
    (FoamPointDefinitions.FERSENBREITE_INNEN, "Ferse Innen"),
    (FoamPointDefinitions.HINTERSTER_PUNKT, "Hint. Punkt"),    
    (FoamPointDefinitions.SCHNITTACHSE, "Schnittachse"),    
 
)

def get_label_for_value(value):
    for choice in FOAM_POINT_CHOICES:
        if choice[0] == value:
            return choice[1]
    return None

def cross_product(A, B, C):
    # Calculate vectors AB and AC
    AB = (B.x - A.x, B.y - A.y)
    AC = (C.x - A.x, C.y - A.y)

    # Compute the cross product AB x AC
    cross = AB[0] * AC[1] - AB[1] * AC[0]

    return cross

class InsolePoint:

    def __init__(self, x, y, _type):
        self.x = x
        self.y = y
        self.pointType = _type

        self.x_dist = None
        self.y_dist = None

    def distance(self, other_point):
        return math.sqrt((self.x - other_point.x)**2 + (self.y - other_point.y)**2)


    def find_perpendicular_intersection(self, A, B, newName=""):
        # Step 1: Calculate the slope of line AB
        slope_AB = (B.y - A.y) / (B.x - A.x)
    
        # Step 2: Calculate the negative reciprocal of slope_AB to find the slope of the perpendicular line
        slope_perpendicular = -1 / slope_AB
    
        # Step 3: Use point-slope form to find the equation of the perpendicular line passing through C
        y_intercept = self.y - slope_perpendicular * self.x
    
        # Step 4: Find the intersection point of line AB and the perpendicular line
        x_D = (y_intercept - A.y + slope_AB * A.x) / (slope_AB - slope_perpendicular)
        y_D = slope_AB * (x_D - A.x) + A.y
    
        return InsolePoint(x_D, y_D, newName)

    def getCoordinateOnAxis(self, A,B):
        pp = self.find_perpendicular_intersection(A,B)

        x_dist = pp.distance(self)
        y_dist = pp.distance(A)
        return (x_dist, y_dist)


    
    def determine_position_relative_to_AB(self, A, B):
        C = self
        cross = cross_product(A, B, C)
    
        if cross > 0:
            return 1
        elif cross < 0:
            return 0
        else:
            return 0

    def setCoordinatesOnAxis(self, A, B):
        (_x, _y) = self.getCoordinateOnAxis(A,B)

        self.x_dist =_x
        self.y_dist =_y
        self.side = self.determine_position_relative_to_AB(A,B)

    def __str__(self):
        return "%s -> (%s,%s)" % (get_label_for_value(self.pointType), self.x, self.y)

    def label(self):    
        # Remove special characters and replace whitespace with underscore
        processed_string = re.sub(r'[^a-zA-Z0-9\s]', '', get_label_for_value(self.pointType) )
        processed_string = re.sub(r'\s', '_', processed_string)
        
        # Remove leading and trailing whitespace
        processed_string = processed_string.strip()
        
        return processed_string
    
    
def getPointByType(_type, _points):
    for p in _points:
        if p.pointType == _type:
            return p
    raise Exception("Point %s not found" % get_label_for_value(_type))