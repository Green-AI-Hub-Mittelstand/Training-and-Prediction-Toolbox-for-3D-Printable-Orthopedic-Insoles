<a name="readme-top"></a>



<br />
<div align="center">
  <h1 align="center">Training and Prediction Toolbox for 3D Printable Orthopedic Insoles</h1>
  <h2 align="center">Training</h2>
  
  <p align="center">
    <a href="">Report Bug</a>
    ·
    <a href="">Request Feature</a>
  </p>

  <br />

  <p align="center">
    <a href="https://www.green-ai-hub.de">
    <img src="images/green-ai-hub-keyvisual.svg" alt="Logo" width="80%">
  </a>
    <br />
    <h3 align="center"><strong>Green-AI Hub Mittelstand</strong></h3>
    <a href="https://www.green-ai-hub.de"><u>Homepage</u></a> 
    | 
    <a href="https://www.green-ai-hub.de/kontakt"><u>Contact</u></a>
  
   
  </p>
</div>

<br/>

# Training

## General Overview
The prediction of the insole parameters is two staged. In a first step, the points of interest are predicted based on the digital pressure data. In a second step, the parameters of the insole are predicted in separate models.


## Getting started

### Setup with virtual environment (VE)
`python -m virtualenv env` 

#### Activate VE
`.\env\Scripts\activate.ps1` on Windows
`source env/bin/activate` on *nix

#### Install dependencies
`pip install -r requirements.pip`

### Setup with Docker
Since the code needs a Unix environment, you can also use the supplied Dockerfile

### Setup Authentication
`cp secrets.py.template secretToken.py` and set the Token in this file. Avoid secrets.py as it conflicts with a file having the same name in numpy.

## Download Participant Data
Open Jupyter Notebook `downloadData.ipynb` and run it. It will download the data of the participants listed in the code. It will then create a directory as follows:

```
- {PARTICIPANT_ID}
        - {PARTICIPANT_ID}.json - Contains Questionnaire Data and comments
        - feet
            - left
                - insole.json - Contains Parameters of the insole that shoud be predicted
                - samples
                    - {SAMPLE_ID}
                        - pressure.csv - Contains the Pressure Data, uncropped in a 32x64 "pressure image"
                        - points.json - Contains the individual points  that should be predicted: float coordinates within the 32x64 and the type of point
                        - meta.json - Contains fit_quality(*1), pressure_type(*2), id
            - right 
                - ...

(*1) fit_quality: how good the pressure data could be fit into the foam print: 1 - bad, 2 - ok, 3 - good
(*2) pressure_type: there is either walking or swaying. walking has multiple samples per participant, sway only one per foot.
```

## Preview Data
To look at a pressure recording with the superimposed points, you can use `previewData.ipynb`


## Training Steps

1. Download the data
2. use DataPreprocessing to prepare data frames
3. use training_code* to train the models based on your needs.

## Additional Scripts
You will also find additional scripts that show the experiments that we did with the data. 



<a name="license"></a>
## License

The code is distributed under the GPLv3 License. See the `LICENSE` file for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
