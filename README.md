# CO2 Hackaton API Data
> This is the API for the CO2 Hackaton project

# Table of content

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
This project was made during the CO2 Hackaton. We wanted to raise awareness about the importance of the CO2 footprint of users

The API is made with FastAPI and the data is fetched from OpenStreetMap API

## Installation
Make sure you have installed Python 3.12 or higher and pip. You can install the required packages 

## Run
```bash
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn main:app --reload
```

You can also run the API with docker
```bash
$ docker build -t co2-hackaton-api .
$ docker run -d -p 8000:8000 co2-hackaton-api
```

The notebook is available in the **analysis** folder. You can run it with jupyter notebook or jupyter lab.

## Contributing
If you want to contribute to this project you can fork this repository and make a pull request with your changes.

## License
This project is under the MIT license.