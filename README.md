# Personal Stock Info - a small Flask app for analyzing stocks
If uses yfinance to retrieve the data.
The DCF code was taken from https://youtu.be/Vi-BQx4gE3k?si=xMHgucXiXcHOM71B

### Configure
Start the Python Virtual Environment and install the dependencies:
```
virtualenv venv
. venv/bin/activate

cat > requirements.in
yfinance
flask

pip install -r requirements.in
pip freeze --all > requirements.txt
```

### Run
Run the script:
```angular2html
python ./app.py
```

The application should start running. 
You can access it by opening a web browser and going to http://127.0.0.1:5000/.
