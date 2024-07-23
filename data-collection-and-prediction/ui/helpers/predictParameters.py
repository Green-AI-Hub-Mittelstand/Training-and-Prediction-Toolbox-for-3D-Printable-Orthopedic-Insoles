from ..models import *
import requests

def _predictParamsFromCSV(csv_path):
    # Send POST request to Flask server with the CSV file
    files = {'file': open(csv_path, 'rb')}
    response = requests.post("http://predictions:5000/predict_params", files=files)

    # Check the response
    if response.status_code == 200:        
        return response.json()
        
    else:
        return []

def predictParams(insole):
    
    leftParams = _predictParamsFromCSV(insole.pressureFileLeftSway.path)
    rightParams = _predictParamsFromCSV(insole.pressureFileRightSway.path)
    
    return (leftParams, rightParams)



# def predictInsole(points,pressureFile):
    
#     insoleParameters = {}

#     insoleParameters['laenge_der_einlage'] = 1
#     insoleParameters['breite_der_einlage_im_vorfussbereich'] = 1
#     insoleParameters['breite_der_einlage_im_rueckfussbereich'] = 1

#     insoleParameters['mfk_1_entlasten'] = 1
#     insoleParameters['mfk_2_entlasten'] = 1
#     insoleParameters['mfk_3_entlasten'] = 1
#     insoleParameters['mfk_4_entlasten'] = 1
#     insoleParameters['mfk_5_entlasten'] = 1

#     insoleParameters['zehe_1_entlasten'] = 1
#     insoleParameters['zehe_2_entlasten'] = 1
#     insoleParameters['zehe_3_entlasten'] = 1
#     insoleParameters['zehe_4_entlasten'] = 1
#     insoleParameters['zehe_5_entlasten'] = 1

#     insoleParameters['pelotten_hoehe'] = 1

#     insoleParameters['pelotten_form'] = 1

#     insoleParameters['laengsgewoelbe_hoehe'] = 1
#     insoleParameters['basis_5_entlasten'] = 1

#     insoleParameters['fersensporn'] = 1

#     insoleParameters['aussenrand_anheben'] = 1
#     insoleParameters['innenrand_anheben'] = 1
#     insoleParameters['verkuerzungsausgleich'] = 1

#     return insoleParameters

# def createPredictedInsoleParameters(insoles):
#     pressureFileLeft = insoles.pressureFileLeft
#     print(insoles)
#     predictionsLeft = PredictionsLeft.objects.get(insoles = insoles)
#     insoleParametersLeft = InsoleParametersProductionLeft.objects.create(insoles = insoles,predictionsleft = predictionsLeft)
    
    

#     leftPoints = PredictedPointLeft.objects.filter(predictions = predictionsLeft)

#     predictedInsoleParametersLeft = predictInsole(leftPoints,pressureFileLeft)

#     insoleParametersLeft.laenge_der_einlage = predictedInsoleParametersLeft['laenge_der_einlage']
#     insoleParametersLeft.breit_der_einlage_im_vorfussbereich =predictedInsoleParametersLeft['breite_der_einlage_im_vorfussbereich']
#     insoleParametersLeft.breite_der_einlage_im_rueckfussbereich = predictedInsoleParametersLeft['breite_der_einlage_im_rueckfussbereich']
#     insoleParametersLeft.mfk_1_entlasten = predictedInsoleParametersLeft['mfk_1_entlasten']
#     insoleParametersLeft.mfk_2_entlasten =predictedInsoleParametersLeft['mfk_2_entlasten']
#     insoleParametersLeft.mfk_3_entlasten = predictedInsoleParametersLeft['mfk_3_entlasten']
#     insoleParametersLeft.mfk_4_entlasten = predictedInsoleParametersLeft['mfk_4_entlasten']
#     insoleParametersLeft.mfk_5_entlasten =predictedInsoleParametersLeft['mfk_5_entlasten']
#     insoleParametersLeft.zehe_1_entlasten =predictedInsoleParametersLeft['zehe_1_entlasten']
#     insoleParametersLeft.zehe_2_entlasten = predictedInsoleParametersLeft['zehe_2_entlasten']
#     insoleParametersLeft.zehe_3_entlasten =predictedInsoleParametersLeft['zehe_3_entlasten']
#     insoleParametersLeft.zehe_4_entlasten = predictedInsoleParametersLeft['zehe_4_entlasten']
#     insoleParametersLeft.zehe_5_entlasten = predictedInsoleParametersLeft['zehe_5_entlasten']
#     insoleParametersLeft.pelotten_hoehe =predictedInsoleParametersLeft['pelotten_hoehe']
#     insoleParametersLeft.pelotten_form = predictedInsoleParametersLeft['pelotten_form']
#     insoleParametersLeft.laengsgewoelbe_hoehe = predictedInsoleParametersLeft['laengsgewoelbe_hoehe']
#     insoleParametersLeft.basis_5_entlasten =predictedInsoleParametersLeft['basis_5_entlasten']
#     insoleParametersLeft.fersensporn = predictedInsoleParametersLeft['fersensporn']
#     insoleParametersLeft.aussenrand_anheben =predictedInsoleParametersLeft['aussenrand_anheben']
#     insoleParametersLeft.innenrand_anheben =predictedInsoleParametersLeft['innenrand_anheben']
#     insoleParametersLeft.verkuerzungsausgleich = predictedInsoleParametersLeft['verkuerzungsausgleich']
#     predictionsLeft.save()
#     insoleParametersLeft.save()
    

#     pressureFileRight = insoles.pressureFileRight

#     predictionsRight = PredictionsRight.objects.get(insoles= insoles)
#     insoleParametersRight = InsoleParametersProductionRight.objects.create(insoles = insoles,predictionsright = predictionsRight)
#     insoleParametersRight.save()
    
#     rightPoints = PredictedPointRight.objects.filter(predictions = predictionsRight)
#     predictedInsoleParametersRight = predictInsole(rightPoints,pressureFileRight)

#     insoleParametersRight.laenge_der_einlage = predictedInsoleParametersRight['laenge_der_einlage']
#     insoleParametersRight.breit_der_einlage_im_vorfussbereich =predictedInsoleParametersRight['breite_der_einlage_im_vorfussbereich']
#     insoleParametersRight.breite_der_einlage_im_rueckfussbereich = predictedInsoleParametersRight['breite_der_einlage_im_rueckfussbereich']
#     insoleParametersRight.mfk_1_entlasten = predictedInsoleParametersRight['mfk_1_entlasten']
#     insoleParametersRight.mfk_2_entlasten =predictedInsoleParametersRight['mfk_2_entlasten']
#     insoleParametersRight.mfk_3_entlasten = predictedInsoleParametersRight['mfk_3_entlasten']
#     insoleParametersRight.mfk_4_entlasten = predictedInsoleParametersRight['mfk_4_entlasten']
#     insoleParametersRight.mfk_5_entlasten =predictedInsoleParametersRight['mfk_5_entlasten']
#     insoleParametersRight.zehe_1_entlasten =predictedInsoleParametersRight['zehe_1_entlasten']
#     insoleParametersRight.zehe_2_entlasten = predictedInsoleParametersRight['zehe_2_entlasten']
#     insoleParametersRight.zehe_3_entlasten =predictedInsoleParametersRight['zehe_3_entlasten']
#     insoleParametersRight.zehe_4_entlasten = predictedInsoleParametersRight['zehe_4_entlasten']
#     insoleParametersRight.zehe_5_entlasten = predictedInsoleParametersRight['zehe_5_entlasten']
#     insoleParametersRight.pelotten_hoehe =predictedInsoleParametersRight['pelotten_hoehe']
#     insoleParametersRight.pelotten_form = predictedInsoleParametersRight['pelotten_form']
#     insoleParametersRight.laengsgewoelbe_hoehe = predictedInsoleParametersRight['laengsgewoelbe_hoehe']
#     insoleParametersRight.basis_5_entlasten =predictedInsoleParametersRight['basis_5_entlasten']
#     insoleParametersRight.fersensporn = predictedInsoleParametersRight['fersensporn']
#     insoleParametersRight.aussenrand_anheben =predictedInsoleParametersRight['aussenrand_anheben']
#     insoleParametersRight.innenrand_anheben =predictedInsoleParametersRight['innenrand_anheben']
#     insoleParametersRight.verkuerzungsausgleich = predictedInsoleParametersRight['verkuerzungsausgleich']
#     predictionsRight.save()
#     insoleParametersRight.save()
