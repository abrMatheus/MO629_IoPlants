import bokeh
from bokeh.models import ColumnDataSource, DataTable, DateFormatter, \
      TableColumn, TabPanel, Tabs
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.layouts import column, row
from PIL import Image
from datetime import datetime
from pandas import json_normalize
import pandas as pd
import numpy as np


from konker import fetch_connection_konker, get_data_from_channel

MAX_TEMP=35
MIN_TEP=10
MIN_HUM=70
MIN_SOIL=50
MAX_LUM=100

fetch_connection_konker()

im = Image.open('../../data/0001_0007.png') # just replace any image that you want here
imarray = np.array(im.convert("RGBA"))
gradcam = Image.open('../../data/gradcam.jpg') # just replace any image that you want here
gradarray = np.array(gradcam.convert("RGBA"))



data_source = ColumnDataSource(data = {"Temperature": [],
                                       "Humidity": [], 
                                       "SoilHumidity": [], 
                                       "Luminosity":[],  
                                       "DateTime": []}) ## Data Source


## Create Line Chart to attribute of plant condition
fig = figure(x_axis_type="datetime",
            #width=500,
             height=300,
             tooltips=[("Temperature", "@Temperature"),
                       ("Humidity", "@Humidity"),
                       ("Soil Humidity", "@SoilHumidity"),
                       ("Luminosity", "@Luminosity")], 
             title = "Plant Condition Live (Every Second)",
             output_backend="webgl", # use webgl to speed up rendering
             toolbar_location=None,# hide entirely toolbar
             )

l0 = fig.line(x="DateTime", y="Temperature", legend_label="Temperature", line_color="red", line_width=1.0, source=data_source,)
l1 = fig.line(x="DateTime", y="Humidity",legend_label="Humidity", line_color="blue", line_width=1.0, source=data_source,)
l2 = fig.line(x="DateTime", y="SoilHumidity",legend_label="Soil Humidity", line_color="green", line_width=1.0, source=data_source,)
l3 = fig.line(x="DateTime", y="Luminosity",legend_label="Luminosity", line_color="yellow", line_width=1.0, source=data_source,)



#fig.multi_line(xs="DateTime",ys="Condition", line_color="tomato", line_width=3.0, source=data_source,)
fig.xaxis.axis_label="Date"
fig.yaxis.axis_label="Condition"

fig.legend.click_policy="hide"

fig.legend.location = "top_left"
fig.xaxis.formatter = DatetimeTickFormatter(years="%d/%m/%Y \n %H:%M:%S",
                                          months="%d/%m/%Y \n %H:%M:%S",
                                          days="%d/%m/%Y \n %H:%M:%S",
                                          hours="%d/%m/%Y \n %H:%M:%S",
                                          hourmin="%d/%m/%Y \n %H:%M:%S",
                                          minutes="%d/%m/%Y \n %H:%M:%S",
                                          minsec="%d/%m/%Y \n %H:%M:%S",
                                          seconds="%d/%m/%Y \n %H:%M:%S",
                                          milliseconds="%d/%m/%Y \n %H:%M:%S",
                                          microseconds="%d/%m/%Y \n %H:%M:%S")

## Create a Data Table widgets to attribute of plant condition

table_columns = [
        TableColumn(field="DateTime", title="Date", 
                    formatter=DateFormatter(),),
        TableColumn(field="Temperature", title="Temperature"),
        TableColumn(field="Humidity", title="Humidity"),
        TableColumn(field="SoilHumidity", title="Soil"),
        TableColumn(field="Luminosity", title="Luminosity"),
    ]
data_table = DataTable(source=data_source, columns=table_columns, 
                       width=350, 
                       height=200, # make sure the same of line graph plot
                       index_position=None, # hide index column

                       )
data_table.selectable = False # HINT: set to false to avoid bug when select cell of data table will disable the line in graph that share the same DataSource

## Create a Data Table widget to show alert messages of plant condition
from datetime import date
from random import randint
prototype_alert_data = dict(
        dates=[date(2023, 3, i+1) for i in range(10)],
        messages=["High temperature detected." for i in range(10)],
    )
prototype_alert_source = ColumnDataSource(prototype_alert_data)

alert_table_columns = [
        TableColumn(field="dates", title="Date", 
                    formatter=DateFormatter(),),
        TableColumn(field="messages", title="Message"),
        
    ]
alert_table = DataTable(source=prototype_alert_source,
                        columns=alert_table_columns, 
                        width=350, 
                        height=200, # make sure the same of line graph plot
                        index_position=None, # hide index column
                       )
## Define a Tab widget to select each table. For more information: https://docs.bokeh.org/en/latest/docs/user_guide/interaction/widgets.html#tabs
tab1 = TabPanel(child=data_table, title="Plant")
tab2 = TabPanel(child=alert_table, title="Alerts")
tabs_component = Tabs(tabs=[tab1, tab2])

## Create a figure to show the result of classification of plant disease
color = R, G, B = (75, 125, 125)
text_color = (255, 255, 255)
classification_information = "classe: mantegosa"
# create a data source to enable refreshing of fill & text color
classification_report_source = ColumnDataSource(data=dict(classification_information=[classification_information],
                                                          color=[color], 
                                                          text_color=[text_color]))

p = figure(width=imarray.shape[0]*2, height=imarray.shape[1]*2,
           title='Classification result', tools='',
                        toolbar_location=None,# hide entirely toolbar
                        outline_line_color=None,# hide grid line color
                        

)
p.axis.visible = False

p.rect(0, 0, width=imarray.shape[0], height=imarray.shape[1], 
        fill_color='color',
        line_color = 'black', source=classification_report_source)

p.text(0, 0, text='classification_information', text_color='text_color',
       alpha=0.6667, text_font_size='20px', 
       #text_baseline='middle',
       text_align='center', 
       source=classification_report_source)

## Define Callbacks to update the figures in real time 
def update_plant_condition_live_charts():
    global data_source
    
    channel_list = ["lum", "hum", "soil", "temp"]
    device_name = "sensor001"

    data = []
    for i, channel in enumerate(channel_list):
        resp = get_data_from_channel(channel=channel_list[i], 
                                                device_name = device_name)
        resp_json = resp['result']
        df = json_normalize(resp_json).set_index('timestamp')

        current_data = np.array(df['payload.value'].iloc[-1]).tolist()
        current_data = np.round(current_data,2)
        data.append(current_data)

#    data = np.clip(data,np.min(data),np.max(data))


    print("[INFO] Current data:", data)

    new_row = {"Temperature":  [data[0]],
               "Humidity":  [data[1]],
               "SoilHumidity":  [data[2]],
               "Luminosity":  [data[3]], 
               "DateTime": [datetime.now(),]}
    data_source.stream(new_row)

update_period_milliseconds = 1000 # 1minute = 6000 ms
curdoc().add_periodic_callback(update_plant_condition_live_charts,
                                update_period_milliseconds)


#https://stackoverflow.com/questions/59673478/bokeh-on-click-function-changes-text-only-after-entire-function-has-completed
#https://stackoverflow.com/questions/34646270/how-do-i-work-with-images-in-bokeh-python
# TODO Button to call the api classify a image
# TODO Recieve image and class from api. The model will detect and classify a patche of plant with disease
# 



#from bokeh.models import FileInput

# file input buuton
#file_input = FileInput()

# button
from bokeh.models import Button
from bokeh.events import ButtonClick # for more https://docs.bokeh.org/en/latest/docs/reference/events.html

def button_callback(event):
    print('Get current information about plant condition by classes backend image API')

button = Button(label="Press to detect and classify actual diseases", button_type="primary")
button.on_event(ButtonClick, button_callback)


#load image
img_fig = figure(width=imarray.shape[0]*2, height=imarray.shape[1]*2, 
                 toolbar_location=None,# hide entirely toolbar

                 )
plotted_image = img_fig.image_rgba(image=[imarray.view("uint32").reshape(imarray.shape[:2])], x=0, y=0, dw=imarray.shape[0], dh=imarray.shape[1])
#load gradcam
gradcam_fig = figure(width=gradarray.shape[0]*2, height=gradarray.shape[1]*2,
                    toolbar_location=None,# hide entirely toolbar
                    )
plotted_gradcam = gradcam_fig.image_rgba(image=[gradarray.view("uint32").reshape(gradarray.shape[:2])], x=0, y=0, dw=gradarray.shape[0], dh=gradarray.shape[1])


# curdoc().theme = "caliber"
# curdoc().theme = "dark_minimal"
# curdoc().theme = "light_minimal"
curdoc().theme = "night_sky"
# curdoc().theme = "contrast"

# hide some component of toolbar on figures
#img_fig.toolbar.logo = None
#gradcam_fig.toolbar.logo = None
#fig.toolbar.logo = None


from bokeh.layouts import layout
image_layout = row([img_fig, gradcam_fig, p], 
                      sizing_mode="scale_width")

layout = layout(
    [
        [fig, tabs_component],
        [button, 
         #file_input
         ],
         [image_layout]
       
    ],
    sizing_mode="stretch_width",
)
# TODO: colocar panel com botão onde o usuário colocar temp max e temp min onde isso é regra 
# de alerta
# TODO: fazer botão de upload de imagem
curdoc().add_root(layout)
"""
curdoc().add_root(column(fig, 
                         button,
                         #file_input, 
                         img_fig) )
"""
# usage bokeh serve --show app.py 
# usage bokeh serve app.py