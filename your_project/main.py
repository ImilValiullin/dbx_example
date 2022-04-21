import sys

from pyspark.sql import SparkSession
from pyspark.dbutils import DBUtils

from src.utils.config import load_config

# get path to config file (or any else parameter)
conf_fl = sys.argv[1]
# example for other parameters
# param_2 = sys.argv[2] 
# param1_3 = sys.argv[3]

def main(config_filepath):
    config = load_config(config_filepath)
    file_path = config['path']
    text = config['text']
    
    #create spark session
    spark = SparkSession.builder.getOrCreate()
    #create dbutils
    dbutils = DBUtils(spark)

    #save file
    dbutils.fs.put(file_path, text, overwrite = True)


if __name__ == "__main__":
    main(conf_fl)