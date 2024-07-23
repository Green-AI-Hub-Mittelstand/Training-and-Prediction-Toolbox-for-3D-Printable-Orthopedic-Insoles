

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