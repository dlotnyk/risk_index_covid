# risk_index_covid
Calculation of risk index based on Government restrictions.

## Requirements
- python 3.7 or higher
- the other packages are installed from root dir
`pip install -r environement/requirements.txt`

## Usage
- Run `application.py` from PyCharm or from src dir
`python3 application.py` under Linux or `python application.py` under Win
or visit AWS hosted [link](http://flask-aws-ness-inno.eba-ywap8kyv.eu-central-1.elasticbeanstalk.com/)
where this project is deployed.
- Open browser on page `localhost:5000`
- Fill all fields and press `Caclculate` button

## Notes
`application.py` is not separeted into several files in order to
deploy it on AWS using Beanstalk.

## Known issues
- Free tier of AWS account restricts the overall transfer data which prevents to choose data for a long time range,
approximately up to 5 months long.


