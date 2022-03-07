from pyspark.sql import SparkSession;
import sqlite3;
import pandas as pan;
import logging;

DATABASE = '/app/database/flu_forecast.db';
spark = SparkSession.builder.getOrCreate();
logging.basicConfig(filename = '/app/backend-app/log/update.log', filemode = 'a', format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO);

def run_sql(sql_statement) -> pan.DataFrame:
    result_df = spark.sql(sql_statement).toPandas();
    return result_df;

def generate_local_copy(sql_statement, table_name):
    logging.info('Retrieve data from databricks, DB = resp_forecasting');
    result = run_sql(sql_statement);

    connection = sqlite3.connect(DATABASE);
    logging.info('Save data to local sqlite, save to Table = {0}'.format(table_name));
    result.to_sql(table_name, con = connection, if_exists = 'replace', index = False);

    # create index
    cur = connection.cursor();
    logging.info('Create index on {0}'.format(table_name));
    cur.execute('create unique index idx_{0} on {0}(ds, hospital_location)'.format(table_name));
    connection.commit();

    connection.close();



# resp_forecasting.all_hospital_forecast_flu_count
# ds,   yhat,  yhat_lower, yhat_upper, actual_count, hospital_location
# date, float, float,      float,      float,        string

# resp_forecasting.all_hospital_forecast_flu_hospital_count

if __name__ == '__main__':
    
    table_name = 'all_hospital_forecast_flu_count';
    sql_statement = '''select * from resp_forecasting.{0}'''.format(table_name);
    generate_local_copy(sql_statement, table_name);

    table_name = 'all_hospital_forecast_flu_hospital_count';
    sql_statement = '''select * from resp_forecasting.{0}'''.format(table_name);
    generate_local_copy(sql_statement, table_name);
