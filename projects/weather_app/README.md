# Weather App

A real, lightweight command-line weather app. It finds a city using Open-Meteo's geocoding endpoint, then fetches its current conditions from the forecast endpoint. It uses only the Python standard library and needs no API key for this personal project.

## Run

From this project folder:

```powershell
C:\Users\iamaa\AppData\Local\Programs\Python\Python313\python.exe src\main.py "Delhi, India"
```

Replace `Delhi, India` with another city, for example `Mumbai, India`.

## Test

```powershell
C:\Users\iamaa\AppData\Local\Programs\Python\Python313\python.exe -m unittest discover -s tests -v
```

## Data source

Open-Meteo Geocoding API and Weather Forecast API. Internet access is required to retrieve live conditions.
