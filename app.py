from flask import Flask, request, send_file, jsonify, Response;
import os;
import sqlite3;
import setting;
import pandas as pan;
from pyspark.sql import SparkSession;



app = Flask(__name__);
spark = SparkSession.builder.getOrCreate();


@app.route('/')
def hello():
    return 'Deploy with Python 3.8';

@app.route('/check_token')
def check_token():           
    headers = {'Authorization': 'Bearer {0} AND {1} AND {0}'.format(os.environ.get('DATABRICKS_AAD_TOKEN'), os.environ.get('COMPUTERNAME'))};
    return headers;

@app.route('/hostname')
def gethostname():
    return str(os.uname());

def __split_hospital_location(hospital_location: str):
    result = hospital_location.split(',');
    result = ["'{}'".format(re.strip()) for re in result];
    print(result);
    return '{0}'.format(','.join(result));

def __sql_flu_count(hosp, start_date, end_date, hosp_enc = False, force = False):
    table_name = '';
    if  hosp_enc == False: 
        table_name = 'all_hospital_forecast_flu_count' if force == False else 'resp_forecasting.all_hospital_forecast_flu_count';
    else:
        table_name = 'all_hospital_forecast_flu_hospital_count' if force == False else 'resp_forecasting.all_hospital_forecast_flu_hospital_count';
    
    return '''
        select ds, yhat_lower, yhat_upper, actual_count 
        from {3} 
        where hospital_location in ({0}) and 
        ds >= '{1}' and
        ds <= '{2}'
        '''.format(__split_hospital_location(hosp), start_date, end_date, table_name);


# /flu_count_forecast?hosp=PARENT MERCY HOSPITAL ST LOUIS&start=2015-01-01&end=2015-01-03
@app.route('/flu_count_forecast')
def flu_count_extract_data_from_local_copy():
    hospital_location = request.args.get('hosp');
    start_date = request.args.get('start');
    end_date = request.args.get('end');

    sql_statement = __sql_flu_count(hospital_location, start_date, end_date, False);
    print(sql_statement)

    with sqlite3.connect(setting.DATABASE) as connection:
        result = pan.read_sql_query(sql_statement, connection);
    
    return jsonify(result.to_dict());


# /flu_count_forecast_force/PARENT MERCY HOSPITAL ST LOUIS/2015-01-01/2015-01-03
# /flu_count_forecast_force?hosp=PARENT MERCY HOSPITAL ST LOUIS, PARENT MERCY HOSPITAL SPRINGFIELD&start=2015-01-01&end=2015-01-03
@app.route('/flu_count_forecast_force')
def flu_count_force_from_remote_databricks():
    hospital_location = request.args.get('hosp');
    start_date = request.args.get('start');
    end_date = request.args.get('end');

    sql_statement = __sql_flu_count(hospital_location, start_date, end_date, False, True);
    print(sql_statement)

    result = spark.sql(sql_statement).toPandas();
    
    return jsonify(result.to_dict());


@app.route('/flu_hospital_count_forecast')
def flu_hospital_count_extract_data_from_local_copy():
    hospital_location = request.args.get('hosp');
    start_date = request.args.get('start');
    end_date = request.args.get('end');

    sql_statement = __sql_flu_count(hospital_location, start_date, end_date, True);
    print(sql_statement)

    with sqlite3.connect(setting.DATABASE) as connection:
        result = pan.read_sql_query(sql_statement, connection);
    
    return jsonify(result.to_dict());


if __name__ == '__main__':
    app.run(debug = True);
