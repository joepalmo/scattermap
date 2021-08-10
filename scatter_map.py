#get mapbox token
import configparser
from os import close

from pandas.core.indexes.datetimes import DatetimeIndex
config = configparser.ConfigParser()
config.read('config.ini')
mapbox_token = config['mapbox']['secret_token']

#load data
import pandas as pd
df = pd.read_csv('wildfires1h.csv')

import numpy as np
#process data
def process_data(df):
    #rename columns
    clean = df.copy(deep=True)[['timestamp', 'pm1', 'pm25', 'pm10', 'PMc', 'lat', 'lon', 'sn']]
    clean.columns = [col.lower() for col in clean.columns]

    #save sensor location
    #sensor_position = clean[['timestamp', 'sn', 'lat', 'lon']]

    clean = pd.pivot_table(clean, index=['timestamp', 'sn'])

    #trying to set lat long for missing node
    #print(clean.loc[:,("MOD-PM-00102", 'lat')])# = 64.76
    #clean.loc[ "MOD-PM-00102", 'lon'] = -147.31
    #clean.xs("MOD-PM-00102", level='sn')['lat'] = 64.76
    #clean.xs("MOD-PM-00102", level='sn')['lon'] = -147.31
    
    #clean = clean.join(sensor_position)

    return clean

df = process_data(df)
df.dropna(inplace=True)

#make visualization
import plotly.graph_objects as go

'''
# Create the figure and feed it all the prepared columns
fig = go.Figure(
    go.Scattermapbox(
        lat=tmp['lat'],
        lon=tmp['lon'],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=tmp['pm25'],
            color=tmp['pm25'],
            showscale=True,
            colorbar={'title':'PM 2.5', 'titleside':'top', 'thickness':4, 'ticksuffix':r'$ (\frac{\mu g}{m^3})'},
        )
    )
)

# Specify layout information
fig.update_layout(
    mapbox=dict(
        accesstoken=mapbox_token, #
        center=go.layout.mapbox.Center(lat=45, lon=-120),
        zoom=2.5
    )
)


customdata=np.stack(
  (pd.Series(tmp.index),
   tmp['pm1'],
   tmp['pm25'],
   tmp['pm10']),
  axis=-1
),

hovertemplate="""
  <extra></extra>
  <em>%{customdata[0]}  </em><br>
  PM 1  %{customdata[1]}<br>
  PM 2.5  %{customdata[2]}<br>
  PM 10  %{customdata[3]}
  """,
'''

hours = df.index.levels[0].tolist()
frames = [{   
    'name':'frame_{}'.format(hour),
    'data':[
        {
        'type':'scattermapbox',
        'lat':df.xs(hour)['lat'],
        'lon':df.xs(hour)['lon'],
        'marker':go.scattermapbox.Marker(
            size=df.xs(hour)['pm25'],
            sizemode='area',
            sizeref=2.*(df.xs(hour)['pm25'].nlargest(2)[1])/(55.**2),
            sizemin=4,
            color=df.xs(hour)['pm25'],
            cmax=75,
            cmin=0,
            showscale=True,
            colorbar={'title':'PM 2.5 (micrograms per cubic meter)', 'titleside':'top', 'thickness':4, 'ticksuffix':''},
            colorscale="RdYlGn_r",
            
        ),
        'customdata' :np.stack(
                (pd.Series(df.xs(hour).index),
                round(df.xs(hour)['pm1'],2),
                round(df.xs(hour)['pm25'],2),
                round(df.xs(hour)['pm10'],2)),
                axis=-1
                ),

'hovertemplate': "<extra></extra> <em>%{customdata[0]}  </em><br> PM 1 =   %{customdata[1]}<br> PM 2.5 =   %{customdata[2]}<br> PM 10 =  %{customdata[3]}",
            },
            ],           
} for hour in hours]  


sliders = [{
    'transition':{'duration': 0},
    'x':0.08, 
    'len':0.88,
    'currentvalue':{'font':{'size':15}, 'prefix':'📅 ', 'visible':True, 'xanchor':'center'},  
    'steps':[
        {
            'label':hour,
            'method':'animate',
            'args':[
                ['frame_{}'.format(hour)],
                {'mode':'immediate', 'frame':{'duration':50, 'redraw': True}, 'transition':{'duration':0}}
              ],
        } for hour in hours]
}]


play_button = [dict(
    type ='buttons',
    showactive =True,
    x=0.045, y=-0.08,
    buttons=[dict( 
        label='Play', # Play
        method='animate',
        args=[None,
        {
                'frame':{'duration':50, 'redraw':True},
                'transition':{'duration':30},
                'fromcurrent':True,
                'mode':'immediate',
        }
        ]
)])],


# Defining the initial state
data = frames[0]['data']

# Adding all sliders and play button to the layout
layout = go.Layout(
    sliders=sliders,
    #updatemenus=play_button,
    updatemenus=[dict(
            type="buttons",
            showactive=True,
            x=0.005, y=-0.08,
            buttons=[dict(label="🎬",
                          method="animate",
                          args=[None,
                          {
                        'frame':{'duration':150, 'redraw':True},
                        'transition':{'duration':50},
                        'fromcurrent':True,
                        'mode':'immediate',
                        }
                          ]),
                    dict(
                    args = [[None], {"frame": {"duration": 0, "redraw": False},
                                    "mode": "immediate",
                                    "transition": {"duration": 0}}],
                    label = "🛑",
                    method = "animate"
                    )
                          ])],
    mapbox=dict(
        accesstoken=mapbox_token, #
        center=go.layout.mapbox.Center(lat=45, lon=-120),
        zoom=2.4,
        style='light'
    )
)

# Creating the figure
fig = go.Figure(data=data, layout=layout, frames=frames)

# Displaying the figure
fig.show()

