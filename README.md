# risk_index_covid
Calculation of risk index based on Government restrictions.

#Requirements
- python 3.7 or higher
- the other packages are installed from root dir
`pip install -r environement/requirements/txt`

#Usage
- Run `application.py` from PyCharm or from src dir
`python3 application.py`
or visit AWS hosted [link](http://flask-aws-ness-inno.eba-ywap8kyv.eu-central-1.elasticbeanstalk.com/)
- Open browser on page `localhost:5000`
- Fill all fields and press `Caclculate` button

#Notes
`application.py` is not separeted into several files in order to
deploy it on AWS using Beanstalk.

#Known bugs
- all field have to be filled
- recaclulating remains all data on a graph. only last is shown but 
the others can be located my mouse.


