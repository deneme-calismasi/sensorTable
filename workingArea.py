import tkinter as tk
from tkinter import ttk
from tkinter import *
import tkinter
import numpy as np
from pyModbusTCP.client import ModbusClient
import pymongo
import datetime as dt
import plotly.express as px
import pandas as pd
import cnfOperations as cnf


class App(object):
    def __init__(self):
        self.count = int(cnf.cnfOperation.readModBusCount())
        self.root = tk.Tk()
        self.tree = ttk.Treeview(self.root)

    def connect_modbus(self):
        host = cnf.cnfOperation.readModBusHost()
        port = cnf.cnfOperation.readModBusPort()

        sensor_no = ModbusClient(host=host, port=port, unit_id=1, auto_open=True)
        sensor_no.open()
        regs = sensor_no.read_holding_registers(0, self.count)
        if regs:
            print(regs)
        else:
            print("read error")

        for n in range(self.count // 2):
            data_count = n * 2
            regs[data_count], regs[data_count + 1] = regs[data_count + 1], regs[data_count]

        dec_array = regs

        data_bytes = np.array(dec_array, dtype=np.uint16)
        data_as_float = data_bytes.view(dtype=np.float32)
        return data_as_float

    def list_to_dict(self):
        value = [[num for num in range(1, 1 + self.count // 2)],
                 [num for num in range(1, 1 + self.count // 2)],
                 self.connect_modbus()]

        data = np.array(value).T.tolist()

        products = data
        arr = []
        for product in products:
            vals = {}
            vals["Sensor No"] = str(int(product[1]))
            vals["Temp"] = str(round(product[2], 4))
            vals["Time"] = str(dt.datetime.now().strftime('%Y-%m-%d %X'))
            arr.append(vals)
        return arr

    def record_mongo(self):
        myclient = pymongo.MongoClient(cnf.cnfOperation.readMongoDb())
        mydb = myclient[cnf.cnfOperation.readMy_Db()]

        global mycol
        mycol = mydb[cnf.cnfOperation.readMy_Col()]

        mycol.insert_many(self.list_to_dict())

        documents = list(mycol.find({}, {'_id': 0}))
        res = [list(idx.values()) for idx in documents]

        for index1, row in enumerate(res):
            for index2, item in enumerate(row):
                try:
                    res[index1][index2] = (float(item))
                except ValueError:
                    pass
        return res

    @staticmethod
    def get_value_mongo():
        myclient = pymongo.MongoClient(cnf.cnfOperation.readMongoDb())
        mydb = myclient[cnf.cnfOperation.readMy_Db()]
        mycol = mydb[cnf.cnfOperation.readMy_Col()]
        mydoc_all = mycol.find()
        df = pd.DataFrame(list(mydoc_all))
        return df.to_csv("abc.csv", sep=",")

    def on_double_click(self, event):
        item = self.tree.identify('item', event.x, event.y)

        print(self.tree.item(item, "text"))

        xs_doc = list(
            mycol.find(
                {"$and": [{"Sensor No": self.tree.item(item, "text")},
                          {"Time": {"$gte": "2021-05-31 13:14:58",
                                    "$lt": dt.datetime.now().strftime('%Y-%m-%d %X')}}]},
                {'_id': 0}))

        print(xs_doc)
        xs_res = [list(idx.values()) for idx in xs_doc]

        df = pd.DataFrame(list(xs_doc))
        df.to_csv("sensor_no.csv", sep=",")

        for index1, row in enumerate(xs_res):
            for index2, item in enumerate(row):
                try:
                    xs_res[index1][index2] = (float(item))
                except ValueError:
                    pass

    @staticmethod
    def draw_figure():

        df = pd.read_csv('C:/Users/halilerhan.orun/IdeaProjects/modbusOOP/sensor_no.csv')
        fig = px.line(df, x='Time', y='Temp', title='Temperature °C - Time', color='Sensor No')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        return fig.show()

    def _quit(self):
        self.root.quit()
        self.root.destroy()

    def window_table(self):

        self.root.title("Sensor's Temperatures °C")
        self.root.geometry("480x630")
        self.root.grid()

        self.tree.pack(side='top', fill=tkinter.BOTH, expand=True)

        verscrlbar = ttk.Scrollbar(self.root,
                                   orient="vertical",
                                   command=self.tree.yview)

        self.tree.configure(xscrollcommand=verscrlbar.set)

        self.tree["columns"] = ("1", "2", "3")

        self.tree['show'] = 'headings'

        self.tree.column("1", width=125, minwidth=30, anchor='c')
        self.tree.column("2", width=65, minwidth=30, anchor='c')
        self.tree.column("3", width=115, minwidth=30, anchor='c')

        self.tree.heading("1", text="Time")
        self.tree.heading("2", text="Sensor No")
        self.tree.heading("3", text="Temperature °C")

        self.tree.bind("<Double-1>", self.on_double_click)

        start_range = 0

        for record in self.record_mongo()[-(self.count // 2):]:
            self.tree.insert("", index='end', text="%s" % int(record[0]), iid=start_range,
                             values=(str(record[2]), int(record[0]), float(record[1])))
            start_range += 1

        menu = Menu(self.root)
        self.root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label='File', menu=filemenu)
        filemenu.add_command(label='New')
        filemenu.add_command(label='Open Calendar')
        filemenu.add_separator()
        filemenu.add_command(label='Exit', command=self._quit)
        helpmenu = Menu(menu)
        menu.add_cascade(label='Figure', command=self.draw_figure)
        helpmenu.add_command(label='About')
        return self.root.mainloop()
