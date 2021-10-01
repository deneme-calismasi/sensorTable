import configparser
import ast


class cnfOperation():

    @staticmethod
    def readModBusHost():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return config['Modbus_host']['host']

    @staticmethod
    def readSensorTypeNo():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return config['Sensor_Type_No']['sensorTypeNo']

    @staticmethod
    def readLineNo():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return config['Line_No']['lineNo']

    @staticmethod
    def readSensorNo():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return ast.literal_eval(config.get("Sensor_No", "sensorNo"))

    @staticmethod
    def readMongoDb():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return config['Mongo_DB']['client']

    @staticmethod
    def readMy_Db():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return config['My_DB']['my_client']

    @staticmethod
    def readMy_Col():
        config = configparser.ConfigParser()
        config.read('Config.ini')
        return config['My_Col']['My_db']
