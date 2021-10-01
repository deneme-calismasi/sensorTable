import modbus_oop as mop
import getMongo as gm
import sys


def main():
    while True:
        rn = mop.ModbusOop()
        rn.window_table()
        rn.update_window_table()
        gvm = gm.GetMongo()
        gvm.get_value_mongo()

        sys.exit()


if __name__ == '__main__':
    main()
