<a name="readme-top"></a>


<br />
<div align="center">
  <h1 align="center">Training and Prediction Toolbox for 3D Printable Orthopedic Insoles</h1>
  <h2 align="center">Preprocessing of Foam Prints</h2>
  
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

# Overview

In this repository you will find two Jupyter Notebooks. One to create sticky labels with QR Codes for the foam boxes as well as a script that preprocesses the scanned foam boxes the then upload them to the cloud. 

# Setup
``` 
python -m virtualenv env

# active the env
pip install -r requirements.pip

# start jupyter
jupyter lab
```

# Labels
The `labels.ipynb` is used to generate A4 sheets to be printed on double column sticky labels. See `labels-3.pdf` for an example.

# Foam Print Preprocessing
The `scan2system.ipynb` notebook consumes the scanned individual foam box images, looks for a QR code and saves the images according to the ID of the foam box. Then it is used to upload the scanned and renamed images to the cloud, linking it to the appropriate participant. 

You might need to adapt this based on the file structure your scanner produces.



<a name="license"></a>
## License

The code is distributed under the GPLv3 License. See the `LICENSE` file for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>
