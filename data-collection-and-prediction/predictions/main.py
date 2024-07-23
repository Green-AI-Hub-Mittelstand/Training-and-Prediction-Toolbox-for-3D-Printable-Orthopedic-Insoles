from pprint import pprint
import pandas as pd
import os, csv, json, re
import sklearn.metrics

import pickle

import autosklearn.classification

from flask import Flask, request, jsonify, abort

import numpy as np
from pprint import pprint

import pandas as pd

from sklearn.datasets import make_regression
# from autosklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

import autosklearn


app = Flask(__name__)

# Load your AutoSklearn model here
# Example:
# model = autosklearn.classification.AutoSklearnClassifier()
# model.fit(X_train, y_train)

# Dummy function for classification, replace with actual AutoSklearn model prediction
def predict_class(input_data):
    # Dummy code for classification, replace with actual AutoSklearn prediction
    return ["class1"] * len(input_data)




class PointOfInterest:
    def __init__(self, x, y, role):
        self.x = x
        self.y = y
        self.role = role

    def __str__(self):
        return "(%s, %s) %s" % (self.x, self.y, self.role)


def loadStreamCSV(s):
    
    
    
    df_raw = pd.read_csv(s, delimiter=";", decimal=",", header=None, skiprows=4)
    df_raw.columns = [f"Column{i}" for i in range(len(df_raw.columns))]
    df_raw.drop(columns="Column0", axis=1, inplace=True)
    df_raw = df_raw[df_raw.sum(axis=1) != 0]
    average_non_zero = df_raw.mean()
    pressure_data = average_non_zero.tolist()
    
    return np.asarray(pressure_data).reshape(1,len(pressure_data))

def reshape(data):
    y_prediction = np.asarray(data.tolist())

    num_columns = 22  # Number of columns (pointType_<num>)
    arr_3d = y_prediction.reshape(y_prediction.shape[0], num_columns, 2)


    column_names = [f"pointType_{i}" for i in range(num_columns)]
    data_dict = {col: arr_3d[:, i, :].tolist() for i, col in enumerate(column_names)}

    # Create the DataFrame
    df_reversed = pd.DataFrame(data_dict)
    df = df_reversed
    
    points_data = []
    for row in df.items():
        # print(row[0],row[1])
        # print(int(re.findall(r'\d+', row[0])[0]))
        points_data.append({"points": row[1].to_list()[0], "pointType": int(re.findall(r'\d+', row[0])[0])})
        
    return points_data
    

def _predictPoints(fileStream):
    data = loadStreamCSV(fileStream)
    
    print("loading model")
    
    predictions = None
    with open("./models/data_averaged_time5hours_perRun300_model.pkl", 'rb') as f:
        automl = pickle.load(f)
        
        print("model loaded")
        
        predictions = automl.predict(data)
        
    return reshape(predictions)
    


@app.route('/predict_points', methods=['POST'])
def predict_predict_points():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Empty filename'})
    
    

    if file:
        
        points = _predictPoints(file)
        
        
        # Read CSV file
        #df = pd.read_csv(file)

        # Call the predict function with the input data
        #predictions = predict_class(df)
        
        
        
                    
        #return result

        return jsonify({'predictions': points})
    
    return jsonify({'predictions': []})



@app.route('/predict_params', methods=['POST'])
def predict_params():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'})

    file = request.files['file']
    
    

    if file.filename == '':
        return jsonify({'error': 'Empty filename'})

    if file:
        result = {
            
            "laenge_der_einlage": 274,
            "breit_der_einlage_im_vorfussbereich": 113,
            "breite_der_einlage_im_rueckfussbereich": 68,
            "mfk_1_entlasten": 0,
            "mfk_2_entlasten": 5,
            "mfk_3_entlasten": 5,
            "mfk_4_entlasten": 0,
            "mfk_5_entlasten": 7,
            "zehe_1_entlasten": 0,
            "zehe_2_entlasten": 0,
            "zehe_3_entlasten": 0,
            "zehe_4_entlasten": 0,
            "zehe_5_entlasten": 0,
            "pelotten_hoehe": 5,
            "pelotten_form": 1,
            "laengsgewoelbe_hoehe": 8,
            "basis_5_entlasten": 4,
            "fersensporn": False,
            "aussenrand_anheben": 0,
            "innenrand_anheben": 0,
            "verkuerzungsausgleich": 0,
            "comments": "",
            
        }
        
        return jsonify({'predictions': result})

    return jsonify({'predictions': {}})



    
@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0")