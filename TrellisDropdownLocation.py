import plotly
plotly.offline.init_notebook_mode(connected=True)
import plotly.plotly as py
import plotly.graph_objs as go
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import json
import copy
import math
import time

# Public access token for Mapbox API
mapbox_access_token = 'pk.eyJ1IjoiY2hhcmxpZWJ1c2hyb3ciLCJhIjoiY2lxY2NpaTh5MDIzMGZxbTF1OXMwMDh3YyJ9.QXiq6Oj8YYes1wdMTX4baw'

# Loading input files
preloadFile = pd.read_csv(r'../Inputs/SimInputPreloaded.csv') # file used to define "Preloaded Visual" content
simInFile = pd.read_csv(r'../Inputs/SimInput.csv') # file that gets written to by "Inputs" page
emmaInFile = pd.read_csv(r'../Inputs/EmMAInput.csv') # file defining agent characteristics used in simulation

# Loading the header images
boozAllen = 'https://tco17.topcoder.com/wp-content/uploads/sites/2/2017/02/bah-only-logo.png'
dashPlotly = 'https://cdn.rawgit.com/plotly/dash-docs/b1178b4e/images/dash-logo-stripe.svg'
trellisLogo = 'https://d30y9cdsu7xlg0.cloudfront.net/png/160790-200.png'


# App initialization
app = dash.Dash()
app.title = 'Trellis Disaster Model' # Title that appears on webpage tab

app.config.supress_callback_exceptions = True

# App layout
# Defines a single div with id "page-content" that gets filled with content based on the url specified.
# Buttons update the url and thus repopulate the page with the appropriate content--this is Dash's version of links.
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='loadVizPageSignal', style={'display': 'none'}),
    html.Div(id='page-content'),
])


#===========================================================================================================================
#========================================================Index Page=========================================================
#===========================================================================================================================

# Index page or splash page that loads when the app gets run.
# Any url extension besides '/preloadedviz', '/inputs', and '/viz' will show this page content

index_layout = html.Div([
    html.Div([

        # Dash by Plotly logo image that is linked to the dash website
        html.Div([
            dcc.Link(
                html.Img(src=dashPlotly,
                    style={
                        'height': '55px',
                        'float': 'left',
                        'position': 'absolute',
                        'top': '23px',
                        'left': '15px'
                    },
                ),
                href='http://plot.ly/products/dash/'
            )],
        ),

        # Booz Allen logo image that is linked to the Booz Allen website
        html.Div([
            dcc.Link(
                html.Img(src=boozAllen,
                    style={
                        'height': '30px',
                        'float': 'right',
                        'position': 'absolute',
                        'top': '35px',
                        'right': '25px'

                    },
                ),
                href='http://www.boozallen.com'
            )],
        )],
        style={
            'padding': '5px 5px 0px 5px',
        }
    ),

    # Main page title: trellis logo and large font "trellis"
    html.Div([
        html.Img(src=trellisLogo,
                 style={
                     'height': '70px',
                     'display': 'inline-block',
                     'padding': '10px 15px 0px 15px'
                 }
                ),
        html.P('trellis',
              style={
                  'fontSize': '72pt',
                  'fontFamily': 'verdana',
                  'display': 'inline-block'
              }),
    ],
    style={
        'width': '100%',
        'textAlign': 'center',
    }),

    # tagline
    html.Div([
        html.P('An agent-based modeling framework with a wide range of applications.',
              style={
                  'fontSize': '24pt',
                  'fontFamily': 'verdana'
              }),
        html.P('View a pre-loaded simulation or define your own inputs.',
              style={
                  'fontSize': '12pt',
                  'fontFamily': 'verdana'
              }),
    ],
    style={
        'width': '100%',
        'textAlign': 'center',
    }),

    # Button linked to '/preloadedviz' content--loads content specific to preloadFile
    html.Div([
        html.Button(
            html.H3(
                dcc.Link(
                    'Go to Pre-Loaded Simulation Visualization',
                    href='/preloadedviz', # updates the url
                    style = {'cursor':'pointer'}
                )
            )
        )],
        style={
            'width':'25%',
            'float':'left',
            'textAlign': 'center',
            'backgroundColor': '#FFFFFF',
            'padding': '5% 5% 5% 20%'
        }
    ),

    # Button linked to '/inputs' content--allows user to write to simInFile and emmaInFile
    html.Div([
        html.Button(
            html.H3(
                dcc.Link(
                    'Define Disaster Simulation Inputs',
                    href='/inputs',
                    style = {'cursor':'pointer'}
                )
            )
        )],
        style={
            'width':'25%',
            'float':'right',
            'textAlign': 'center',
            'backgroundColor': '#FFFFFF',
            'padding': '5% 20% 5% 5%'
        }
    )      
])
#===========================================================================================================================
#==============================================Preloaded Visual Page========================================================
#===========================================================================================================================

# Essentially a copy of the standard visual page, but with everything preloaded for the situation defined in preloadFile.
# This can be adjusted in the csv, but the purpose is to have a separate, set file that will load a known situation, while
# the inputs page allows for writing to and adjustment of a different file. Functions, IDs, and variables have a "1"
# added to their name to differentiate them from their copies because the copied functions and variables are all already
# loaded, they are just not displayed on the page.

preloadIn = list(preloadFile.values[0])
emmaIn = list(emmaInFile.values[0])

location1 = preloadIn[0]
simLength1 = int(preloadIn[1])
simExtract1 = int(preloadIn[3])

nodesFile1 = pd.read_csv(preloadIn[7])
disasterFile1 = pd.read_csv(preloadIn[9])
agentFile1 = pd.read_csv(preloadIn[10])


# Functions to be used in defining the page layout--separation allows for easier adjustment

# Set time slider max to the length of the simulation in seconds
def getSliderMax1():
    max = simLength1*60*60
    return max


# Set time slider step to the smallest unit for which data is available--the extract interval
def getSliderStep1():
    step = simExtract1
    return step


# Set distance between marks on the time slider--too many looks congested, too few isn't as useful
def getSliderMarks1():
    valMax = getSliderMax1()
    step = getSliderStep1()
    marks = {}

    # Starts at time=0, goes to slider max + 1 so that the max is included
    # Arbitrary decision to have a mark every 5 timesteps for spacing--doesn't always include the max value
    for i in range(0, valMax+1, step*5):
        # Includes units for start and end marks only
        if(i==0 or i==valMax):
            marks.update({i: '{} {}'.format(i, 'Seconds')})
        # All other marks do not include units
        else:
            marks.update({i: '{}'.format(i)})
    return marks


#============================================================= Layout ============================================================

# Defines the page content for '/preloadedviz'
preloadedvisuals_layout = html.Div([
    html.Div([

        # Top of page div (Logos, Headers, Links)
        html.Div([
            html.Div([
                # Dash logo
                html.Img(src=dashPlotly,
                    style={
                        'height': '55px',
                        'float': 'left',
                        'position': 'absolute',
                        'top': '23px',
                        'left': '15px'
                    },
                )],
            ),
            # Header and links
            html.Div([
                html.H2('Evacuation Movement', 
                    style={
                        'textAlign': 'center',
                        'fontFamily': 'verdana'
                       }),
                html.Div([
                    # Link to inputs page
                    html.Div([
                        dcc.Link('Define Inputs',
                            href='/inputs',
                            style = {'color':'#004F98',
                                'textDecoration':'underline',
                                'cursor':'pointer'}
                        )],
                    style={
                        'padding': '0px 15px 0px 2px',
                        'display': 'inline-block'
                    }),
                    # Link to home page
                    html.Div([
                        dcc.Link('Return Home',
                            href='/home',
                            style = {'color':'#004F98',
                                'textDecoration':'underline',
                                 'cursor':'pointer'}
                        )],
                    style={
                        'padding': '0px 2px 0px 15px',
                        'display': 'inline-block'
                    })
                ],
                style={
                    'textAlign': 'center',
                    'fontSize': '9pt',
                    'fontFamily': 'verdana'
                }),
            ]),
            # Booz Allen logo
            html.Div([
                html.Img(src=boozAllen,
                    style={
                        'height': '30px',
                        'float': 'right',
                        'position': 'absolute',
                        'top': '35px',
                        'right': '25px'

                    },
                )],
            )],
            style={
                'padding': '5px 5px 0px 5px',
            }
        ),
        html.Br(),
        # Middle of page split into two divs: 74% and 25%

        # Left div (Dropdowns, Safe Graph, Map)
        html.Div([
            # 74% div split into two divs: dropdowns=33% (~24% of whole page width), map=66% (~49% of page)

            # Left div (Dropdowns/Visualization Options)
            html.Div([

                # Header
                html.Div([
                    html.Div([
                        html.P('Visualization Options:',
                            style={
                                'textAlign': 'center',
                                'fontFamily': 'verdana',
                                'fontSize': '10pt'
                            }),
                    ]),
                ],
                style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '5px 5px 5px 5px',
                }),
                html.Br(),

                # Dropdowns
                dcc.Dropdown(
                    id='dataSelect1',
                    options=[
                        {'label': 'Show disaster and people\'s movement', 'value': 'both'},
                        {'label': 'Show people\'s movement', 'value': 'people'},
                        {'label': 'Show disaster\'s movement', 'value': 'disaster'},
                    ],
                    value='both',
                    placeholder='Select data of interest...',
                ),
                html.Br(),
                dcc.Dropdown(
                    id='mapstyleDropdown1',
                    options=[
                        {'label': 'Map style: Outdoors', 'value': 'outdoors'},
                        {'label': 'Map style: Dark', 'value': 'dark'},
                        {'label': 'Map style: Satellite', 'value': 'satellite'},
                        {'label': 'Map style: Streets', 'value': 'streets'}
                    ],
                    value='outdoors',
                    placeholder='Select a map style...'
                ),
                html.Br(),
                dcc.Dropdown(id='agentColorDropdown1',
                    options=[
                        {'label': 'Agent colorscale: ' + i, 'value': i}\
                        for i in ['Blackbody','Bluered','Blues','Earth','Electric',\
                                  'Greens','Greys','Hot','Jet','Picnic','Portland',\
                                  'Rainbow','RdBu','Reds','Viridis','YlGnBu','YlOrRd']
                    ],
                    value='Reds',
                    placeholder='Select agent colorscale...'
                ),
                html.Br(),
                dcc.Dropdown(id='disasterColorDropdown1',
                    options=[
                        {'label': 'Disaster colorscale: ' + i, 'value': i}\
                        for i in ['Blue', 'Green', 'Yellow', 'Red', 'White', 'Black']
                    ],
                    value='Blue',
                    placeholder='Select disaster colorscale...'
                ),
                html.Br(),

                # Graph showing number of agents that have reached the defined safe zones
                dcc.Graph(id='safePeople-graph1',
                         config = {'displayModeBar': False})
            ],
            style={
                'width': '33%',
                'float': 'left',
                'textAlign': 'center',
                'fontFamily': 'verdana',
                'fontSize': '10pt'
            }),

            # Right div (Map)
            html.Div([

                # Header
                html.Div([
                    html.Div([
                        html.P(
                            id='mapHeader1',
                            style={
                                'textAlign': 'center',
                                'fontFamily': 'verdana',
                                'fontSize': '10pt'
                            }),
                    ]),
                ],
                style={
                    'borderBottom': 'thin lightgrey solid',
                    'backgroundColor': 'rgb(250, 250, 250)',
                    'padding': '5px 5px 5px 5px',
                }),
                html.Br(),

                # Map
                dcc.Graph(
                    id='graphWithSlider1',
                    animate=True,
                    hoverData = {'points':[{'customdata': 3}]},
                    config = {'displayModeBar': False}
                ),
            ],
            style={
                'width': '66%',
                'float': 'right'
            })
        ],
        style={
            'width': '74%',
            'float': 'left'
        }),
        
        # Right div (Hover Info Graphs)
        html.Div([

            # Header
            html.Div([
                html.P('Hover over points for more information.',
                    style={
                        'textAlign': 'center',
                        'fontFamily': 'verdana',
                        'fontSize': '10pt'
                   })
            ],
            style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '5px 5px 5px 5px',
            }),
            html.Br(),

            # Graphs showing information relevant to node mouse is hovering over
            html.Div([
                dcc.Graph(id='numPeople-graph1',
                         config = {'displayModeBar': False}),
                html.Br(),
                dcc.Graph(id='second-graph1',
                         config = {'displayModeBar': False})
            ])
        ],
        style={
            'width': '25%',
            'float': 'right'
        }),

        # Bottom of page div (Time Slider)
        html.Div([
            html.Div([
                html.Br(),
                dcc.Slider(
                    id='timestepSlider1',
                    min=0,
                    max=getSliderMax1(),
                    step=getSliderStep1(),
                    marks=getSliderMarks1(),
                    value=0,
                    updatemode='drag'
                )
            ],
            style={
                'width': '85%',
                'align': 'center',
                'display': 'inline-block'
            })
        ],
        style={
            'textAlign': 'center',
        })
    ]),
])

# ============================================================== Functions ==========================================================

# Functions to be used in data manipulation, graph creation, and map visualization

# Adjusts the color and size of each node based on the number of agents at it in the given timestep
# Returns 'marker' dictionary
def getPeopleNodeMarker1(time, agentColorScale):
    nf=nodesFile1
    tf=agentFile1

    tff=tf[tf['TIME']==time]    # Create dataframe with only agent locations at given time
    tfff=tff.groupby('CURRENT_NODE')['AGENT_ID'].count()    # Translate tff to number of agents at each node

    impassible=tff[tff['ACTIVITY']==False]  # Identify impassible nodes at timestep by their 'Activity' status
    impassible = sorted(list(impassible['CURRENT_NODE'].unique()))  # Generate list of impassible nodes w/o duplicates

    # Creates list of number of agents at each node with zeroes at impassible nodes
    numVisitors=[]
    for node in nf['OBJECTID']:
        if node not in impassible:
            try:
                numVisitors.append(tfff[node])
            except:
                numVisitors.append(0)  
        else:
            numVisitors.append(0)

    # Arbitrary scaling of node size distribution to look better
    nodeSize = numVisitors
    for i in range(len(nodeSize)):
        nodeSize[int(i)] = (nodeSize[int(i)]**0.45)*4
    
    marker = dict(
        size=nodeSize,
        color=numVisitors,
        colorscale=agentColorScale,
        opacity=0.8,
    )
                   
    return marker
    

# Adjusts color and size of nodes to visualize flood location and depth at a given timestep for flood scenario
# Returns 'marker' dictionary
def getFloodNodeMarker1(time,colorway):
    sizes = []
    # Sets marker size = 70 if there is any water at the node (disasterFile measurements not binary; shows depth)
    for index in range(len(disasterFile1[str(time)])):
        if disasterFile1[str(time)][index] == 0:
            sizes.append(0)
        else:
            sizes.append(70)
    
    # Sets default flood color to blue colorway
    if colorway is None:
        colorway = 'Blue'

    # Defines shades of each color to represent varying water depths
    spectrum = {
        'Red':
            ['rgba(253, 237, 236, 0.7)',
            'rgba(250, 219, 216, 0.7)',
            'rgba(241, 148, 138, 0.7)',
            'rgba(231, 76, 60, 0.7)',
            'rgba(176, 58, 46, 0.7)',
            'rgba(120, 40, 31, 0.7)'],
        'Yellow':
            ['rgba(249, 231, 159, 0.7)',
            'rgba(247, 220, 111, 0.7)',
            'rgba(241, 196, 15, 0.7)',
            'rgba(212, 172, 13, 0.7)',
            'rgba(183, 149, 11, 0.7)',
            'rgba(154, 125, 10, 0.7)'],
        'Green':
            ['rgba(234, 250, 241, 0.7)',
            'rgba(171, 235, 198, 0.7)',
            'rgba(88, 214, 141, 0.7)',
            'rgba(40, 180, 99, 0.7)',
            'rgba(29, 131, 72, 0.7)',
            'rgba(24, 106, 59, 0.7)'],
        'Blue':
            ['rgba(234, 242, 248, 0.7)',
            'rgba(212, 230, 241, 0.7)',
            'rgba(127, 179, 213, 0.7)',
            'rgba(41, 128, 185, 0.7)',
            'rgba(31, 97, 141, 0.7)',
            'rgba(21, 67, 96, 0.7)'],
        'White':
            ['rgba(253, 254, 254, 0.9)',
            'rgba(251, 252, 252, 0.825)',
            'rgba(247, 249, 249, 0.75)',
            'rgba(244, 246, 247, 0.675)',
            'rgba(240, 243, 244, 0.6)',
            'rgba(236, 240, 241, 0.525)'],
        'Black':
            ['rgba(120, 120, 120, 0.7)',
            'rgba(100, 100, 100, 0.7)',
            'rgba(80, 80, 80, 0.7)',
            'rgba(60, 60, 60, 0.7)',
            'rgba(40, 40, 40, 0.7)',
            'rgba(20, 20, 20, 0.7)']
        
    }[colorway]

    # Defines depths that trigger color shade changes
    colors = []
    for index in range(len(disasterFile1[str(time)])):
        if disasterFile1[str(time)][index] > 15:
            colors.append(spectrum[5])
        elif disasterFile1[str(time)][index] > 10:
            colors.append(spectrum[4])
        elif disasterFile1[str(time)][index] > 5:
            colors.append(spectrum[3])
        elif disasterFile1[str(time)][index] > 1:
            colors.append(spectrum[2])
        else:
            colors.append(spectrum[1])
            
    marker=dict(
        sizemode = 'area',
        size=sizes,
        color=colors,
    )
    
    return marker


# Adjusts color and size of nodes to visualize fire location at a given timestep for wildfire scenario
# Returns 'marker' dictionary
def getFireNodeMarker1(time,colorway):
    sizes = []
    if colorway is None:
        colorway = 'Red'
    spectrum = {
        'Red':'rgba(170, 0, 0, 0.7)',
        'Yellow':'rgba(154, 125, 10, 0.7)',
        'Green':'rgba(24, 106, 59, 0.7)',
        'Blue':'rgba(21, 67, 96, 0.7)',
        'White':'rgba(236, 240, 241, 0.525)',
        'Black':'rgba(20, 20, 20, 0.7)'
    }[colorway]

    # Sets marker size to 70 if fire is present at node (disasterFile for fire is binary)
    for index in range(len(disasterFile1[str(time)])):
        if disasterFile1[str(time)][index] == 0:
            sizes.append(0)
        else:
            sizes.append(70)
    
    # Only one color shade available for fire--no varying depths
    colors = []
    for index in range(len(disasterFile1[str(time)])):
        if disasterFile1[str(time)][index] > 0:
            colors.append(spectrum)
        else:
            colors.append('rgba(255,255,255,0.7)')
    
    marker=dict(
        sizemode = 'area',
        size=sizes,
        color=colors
    )
    
    return marker


# Selects the appropriate data to display on the map
# Returns 'data' argument for scattermapbox map
def getData1(time, selection, agentColorScale, disasterColorScale):
    nf=nodesFile1
    tf=agentFile1
    df=disasterFile1
    
    # Set appropriate disaster marker type for the given location
    if location1.lower() == 'oroville' or location1.lower() == 'mosul':
        disasterMarker = getFloodNodeMarker1(time,disasterColorScale)
    elif location1.lower() == 'santamaria':
        disasterMarker = getFireNodeMarker1(time,disasterColorScale)
    else:   # general marker
        disasterMarker = dict(
            sizemode = 'area',
            color = 'rgba(255,255,255,0.7)',
            size = 1.75,
        )
    
    # Plot the nodes representing street intersections on the map
    nodeData = dict(
        type='scattermapbox',
        lon=nf['POINT_X'],
        lat=nf['POINT_Y'],
        text=nf['OBJECTID'],    # Node number, aligns with number assigned by ArcGIS
        hoverinfo = 'text',
        customdata=nf['OBJECTID'], # Used for hoverdata
        marker=dict(
            sizemode = 'area',
            size=1.75,
            color='rgba(255,255,255,0.5)',
        )
    )
    
    # Plot additional points with color, size based on the number of people (on top of nodeData)
    peopleData = dict(
        type='scattermapbox',
        lon=nf['POINT_X'],
        lat=nf['POINT_Y'],
        hoverinfo = 'skip',
        marker=getPeopleNodeMarker1(time, agentColorScale)
    )
    
    # Plot disaster data
    disasterData = dict(
        type='scattermapbox',
        lon=df['POINT_X'],
        lat=df['POINT_Y'],
        hoverinfo = 'skip',
        marker=disasterMarker
    )
    
    # Generates lat and lon list for nodes that were overtaken by the disaster while occupied by agents
    tff=tf[tf['TIME']==time]
    tfff=tff.groupby('CURRENT_NODE')['AGENT_ID'].count()
    impassible=tff[tff['ACTIVITY']==False]
    impassible = sorted(list(impassible['CURRENT_NODE'].unique()))
    impassibleLat = []
    impassibleLon = []
    for node in nf['OBJECTID']:
        if node in impassible and tfff[node] > 0:
            impassibleLat.append(float(nf[nf['OBJECTID']==node]['POINT_Y']))
            impassibleLon.append(float(nf[nf['OBJECTID']==node]['POINT_X']))
        else:
            pass
    
    # Plot red cross marker for nodes overtaken while occupied
    impassibleData = dict(
        type='scattermapbox',
        lon=impassibleLon,
        lat=impassibleLat,
        hoverinfo = 'skip',
        marker=dict(
            size=10,
            color='#ffffff',
            symbol='hospital'
        )
    )
    
    # Adjust which data shows on map based on the dropdown selection   
    if selection == 'both':
        data = [nodeData, peopleData, disasterData, impassibleData]
    elif selection == 'people':
        data = [nodeData, peopleData, impassibleData]
    elif selection == 'disaster':
        data = [nodeData, disasterData, impassibleData]
    else:
        data = [nodeData]
    return data


# Generates the layout for the map based on preloaded location and selected mapstyle
def getLayout1(mapStyle):
    # location1 variable pulled from preloadFile
    if location1.lower() == 'oroville':
        lat=39.5
        lon=-121.59
        zoom=11.1
    elif location1.lower() == 'mosul':
        lat=36.3566
        lon=43.164
        zoom=11
    elif location1.lower() == 'santamaria':
        lat=34.9353
        lon=-120.438626
        zoom=11.15
    else:
        lat=15
        lon=0
        zoom=0.6
    
    layout = dict(
        autosize=True,
        height=506,
        margin=go.Margin(l=0, r=0, t=0, b=0),
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(
                lat=lat,
                lon=lon 
            ),
            style=mapStyle, # Alters the map coloration/style based on dropdown
            bearing=0,
            zoom=zoom # Assigned from if/elif above
        )
    )
    return layout


#======================================================= Callbacks =================================================================

# Utilize prior functions to assign user input to appropriate action

# Generate comprehensive description of map based on location and data selection
# Outputs description to Map Header
@app.callback(
    dash.dependencies.Output('mapHeader1', 'children'),
    [dash.dependencies.Input('dataSelect1', 'value')]
)
def update_map_header1(data):
    # Proper location name
    locationName = {
        'oroville' : 'Oroville, CA, USA',
        'mosul': 'Mosul, Iraq',
        'santamaria': 'Santa Maria, CA, USA'
    }[location1.lower()]

    # Associated disaster type
    disasterName = {
        'oroville' : 'flood',
        'mosul': 'flood',
        'santamaria': 'wildfire'
    }[location1.lower()]
    
    # Selected data
    if data == 'both':
        header = 'Map of {}, showing movement of the disaster and people in the event of a {}.'.format(locationName, disasterName)
    elif data == 'people':
        header = 'Map of {}, showing people\'s movement in the event of a {}.'.format(locationName, disasterName)
    elif data == 'disaster':
        header = 'Map of {}, showing disaster movement in the event of a {}'.format(locationName, disasterName)
    else:
        header = 'Map of {}'.format(locationName)
    return header


# Generate the map
# Outputs map figure
@app.callback(
    dash.dependencies.Output('graphWithSlider1', 'figure'), # Main map
    [dash.dependencies.Input('timestepSlider1', 'value'), # Time slider
    dash.dependencies.Input('dataSelect1', 'value'), # Data selection dropdown ('both', 'people', 'disaster')
    dash.dependencies.Input('mapstyleDropdown1', 'value'), # Map style dropdown
    dash.dependencies.Input('agentColorDropdown1', 'value'), # Agent colorway selection dropdown
    dash.dependencies.Input('disasterColorDropdown1', 'value')] # Disaster colorway selection dropdown
)

def update_figure1(time,selection,mapStyle,agentColorScale,disasterColorScale):
    data = getData1(time, selection, agentColorScale, disasterColorScale)
    layout = getLayout1(mapStyle)  
    figure = dict(data=data, layout=layout)
    return figure


# Generate graph of number of agents that have arrived at the defined safezone at the given time
# Outputs graph figure
@app.callback(
    dash.dependencies.Output('safePeople-graph1', 'figure'),    # Bottom left graph
    [dash.dependencies.Input('timestepSlider1', 'value')]   # Time slider
)

def safegraph_update1(time):
    tf=agentFile1

    # Narrow dataframe down to current time and safe agents
    tff=tf[tf['TIME']<=time]
    tfff = tff[tff['IS_SAFE']==1]

    # Create list for time axis up to current time
    xList = list(tff['TIME'].unique())  
    # Create list of number of safe agents for each time point up to current time
    yList = []
    for x in xList:
        yList.append(len(tfff[tfff['TIME']==x]))       

    # Create scatterplot of number of people at safety vs time
    data = [dict(
        type = 'scatter',
        mode='lines+markers',
        x = xList,
        y = yList,
        line=dict(
            shape="spline",
            smoothing=1,    # arbitrary
            width=1,    # arbitrary
            color='#a9bb95' # arbitrary
        ),
        marker=dict(symbol='diamond-open')
    )]

    # Define appearance of scatterplot
    layout = dict(
        autosize=True,
        height=300,
        title='Number of people at safety:',
        xaxis={'title': 'Seconds'},
        yaxis={'title': 'Number of People'})

    figure = dict(data=data, layout=layout)
    
    return figure


# Generates graph of the number of agents at the specified node at given time
# Specify node by hovering mouse over node on map
# Outputs graph figure
@app.callback(
    dash.dependencies.Output('numPeople-graph1', 'figure'), # Top right graph
    [dash.dependencies.Input('graphWithSlider1', 'hoverData'), # Pulls which node is being hovered over
    dash.dependencies.Input('timestepSlider1', 'value')]    # Time slider
)

def hovergraph_update1(hoverData, time):
    tf=agentFile1
    hoverNode = hoverData['points'][0]['customdata'] # Syntax to access node number stored in map 'customdata'

    # Narrow dataframe to current time and node
    tff=tf[tf['TIME']<=time]
    tfff = tff[tff['CURRENT_NODE']==hoverNode]

    # Create list of times up to currrent time
    xList = list(tff['TIME'].unique())
    # Create list of number of agents at node at each time
    yList = []
    for x in xList:
        yList.append(len(tfff[tfff['TIME']==x]))       

    # Create scatterplot of number of people at node vs time
    data = [dict(
        type = 'scatter',
        mode='lines+markers',
        x = xList,
        y = yList,
        line=dict(
            shape="spline",
            smoothing=1,
            width=1,
            color='#a9bb95'
        ),
        marker=dict(symbol='diamond-open')
    )]

    # Define appearance of scatterplot
    layout = dict(
        autosize=True,
        height=243,
        title='Number of people at node %d:'% hoverNode,
        xaxis={'title': 'Seconds'},
        yaxis={'title': 'Number of People'})

    figure = dict(data=data, layout=layout)
    
    return figure


# Generate graph of average panic level of agents at given node
# Outputs graph figure
@app.callback(
    dash.dependencies.Output('second-graph1', 'figure'),    # Bottom right graph
    [dash.dependencies.Input('graphWithSlider1', 'hoverData'),  # Pulls which node is being hovered over
    dash.dependencies.Input('timestepSlider1', 'value')]    # Time slider
)

def secondhovergraph_update1(hoverData, time):
    tf=agentFile1
    hoverNode = hoverData['points'][0]['customdata']    # Syntax to access node number stored in map 'customdata'

    # Narrow dataframe to current time and node
    tff=tf[tf['TIME']<=time]
    tfff = tff[tff['CURRENT_NODE']==hoverNode]

    # Create list of times up to currrent time
    xList = list(tff['TIME'].unique())
    # Create list of average panic level at node at each time
    yList = list(tfff.groupby('TIME').mean()['PANIC'])

    for i in range(len(xList)):
        try:
            yList[i]
        except:
            try:
                yList.append(yList[-1])
            except:
                yList.append(0)

    # Create scatterplot of panic level at node vs time
    data = [dict(
        type = 'scatter',
        mode='lines+markers',
        x = xList,
        y = yList,
        line=dict(
            shape="spline",
            smoothing=1,
            width=1,
            color='#fac1b7'
        ),
        marker=dict(symbol='diamond-open')
    )]

    # Define appearance of scatterplot
    layout = dict(
        autosize=True,
        height=243,
        title='Average panic level at node %d:' % hoverNode,
        xaxis={'title': 'Seconds'},
        yaxis={'title': 'Panic Level (0-1)'})

    figure = dict(data=data, layout=layout)

    return figure


#===========================================================================================================================
#==================================================Simulation Inputs Page===================================================
#===========================================================================================================================

# Allows the user to adjust the available variables and run the simulation with the new "situation".
# CURRENTLY 'simulates' running the simulation by only adjusting the referenced simulation files. We have not yet figured
# out how to: 1) have dash reload the file without stopping and restarting the program, and 2) run the simulation in the 
# background with the selected inputs.

maxNumGroups = 10    # Max number of distinct groups with different attributes that the user can create

inputs_layout = html.Div([
    html.Div([

        # Top of page div
        html.Div([
            # Dash logo
            html.Div([
                html.Img(src=dashPlotly,
                    style={
                        'height': '55px',
                        'float': 'left',
                        'position': 'absolute',
                        'top': '23px',
                        'left': '15px'
                    },
                )],
            ),
            # Header
            html.Div([
                html.H2('Simulation Setup', 
                    style={
                        'textAlign': 'center',
                        'fontFamily': 'verdana'
                       }),
                # Homepage link
                html.Div([
                    html.Div([
                        dcc.Link('Return Home',
                            href='/home',
                            style = {'color':'#004F98',
                                'textDecoration':'underline',
                                 'cursor':'pointer'}
                        )],
                    style={
                        'padding': '0px 0px 20px 0px',
                        'display': 'inline-block'
                    })
                ],
                style={
                    'textAlign': 'center',
                    'fontSize': '9pt',
                    'fontFamily': 'verdana'
                }),
            ]),
            # Booz Allen Logo
            html.Div([
                html.Img(src=boozAllen,
                    style={
                        'height': '30px',
                        'float': 'right',
                        'position': 'absolute',
                        'top': '35px',
                        'right': '25px'

                    },
                )],
            )],
            style={
                'padding': '5px 5px 0px 5px',
            }
        ),

        # Main page content div
        html.Div([
            html.Div([

                # Instructions header
                html.Div([
                    html.Div([
                        html.P('Please select simulation inputs, then click Run Simulation:',
                            style={
                                'textAlign': 'center',
                                'fontFamily': 'verdana',
                                'fontSize': '10pt'
                            }),
                    ]),
                ],
                style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '5px 5px 5px 5px',
                }),
                html.Br(),

                # Primary trait selection box -- Location dropdown through destination node input box -- gray background
                # Portion of inputs that write to SimInputs file
                html.Div([
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(
                            id='locationDropdown',
                            options=[
                                {'label': 'Location: Flood in Mosul, Iraq', 'value': 'mosul'},
                                {'label': 'Location: Flood in Oroville, CA', 'value': 'oroville'},
                                {'label': 'Location: Wildfire in Santa Maria, CA', 'value': 'santaMaria'},
                            ],
                            value='oroville',
                            placeholder='Select a location...',)],
                        style={
                            'width': '70%',
                            'padding': '0% 15% 0% 15%'
                        }
                    ),
                    html.Br(),
                    html.Div([
                        dcc.Dropdown(
                            id='situationSelect',
                            options=[
                                {'label': 'Disaster Magnitude: Major', 'value': 'major'},
                                {'label': 'Disaster Magnitude: Moderate', 'value': 'moderate'},
                                {'label': 'Disaster Magnitude: Minor', 'value': 'minor'},
                            ],
                            value='major',
                            placeholder='Select disaster magnitude...',)],
                        style={
                            'width': '70%',
                            'padding': '0% 15% 0% 15%'
                        }
                    ),
                    html.Div([
                        html.P('Simulation Length (hours): '),
                        dcc.Input(
                            id='simLengthInput',
                            value=2,
                            placeholder='(2 hours)',
                            style={
                                'display': 'inline-block',
                                'padding': '5px 10px 5px 5px',
                            }
                        ), 
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 10px',
                    }),
                    html.Div([
                        html.P('Simulation Resolution (seconds): '),
                        dcc.Input(
                            id='resolutionInput',
                            value=1,
                            placeholder='(1 second)',
                            style={
                                'display': 'inline-block',
                                'padding': '5px 10px 5px 5px',
                            }
                        ),  
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 10px',
                    }),
                    html.Div([
                        html.P('Data Extract Interval (seconds): '),
                        dcc.Input(
                            id='extractIntervalInput',
                            value=100,
                            placeholder='(100 seconds)',
                            style={
                                'display': 'inline-block',
                                'padding': '5px 10px 5px 5px',
                            }
                        ),  
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 10px',
                    }),
                    html.Div([
                        html.P('Agents\' Notice Time Before Event (hours): '),
                        dcc.Input(
                            id='noticeTimeInput',
                            value=1,
                            placeholder='(1 hour)',
                            style={
                                'display': 'inline-block',
                                'padding': '5px 10px 5px 5px',
                            }
                        ),
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 10px',
                    }),
                    html.Div([
                        html.P('Number of Groups with Different Attributes: '),
                        dcc.Input(
                            id='numAgentGroupsInput',
                            value=1,
                            placeholder='Max of %s'% maxNumGroups,
                            style={
                                'display': 'inline-block',
                                'padding': '5px 10px 5px 5px',
                            }
                        ),
                    ],
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 10px',
                    }
                    ),
                    html.Div(
                        children=0,
                        id='validNumGroups',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.Div([
                        html.Div([
                            html.Br(),
                            dcc.Dropdown(
                                id='destinationInput',
                                options=[
                                    {'label': 'Use Evacuation Zone Destinations', 'value': 'y'},
                                    {'label': 'Use Defined Destinations', 'value': 'n'},

                                ],
                                value='y',
                                placeholder='Select agent destinations...',
                            ),],
                            style={
                                'width': '70%',
                                'padding': '0% 15% 0% 15%',
                            }
                        ),],
                        style={
                            'textAlign':'center'
                        }
                    ),
                    html.P('Destination node numbers to use if \'Defined Destinations\' is selected: ',
                        style={
                            'display': 'inline-block',
                            'padding': '5px 5px 5px 10px',
                        }
                    ),
                    dcc.Input(
                        id='destinationNodeInput',
                        value=[],
                        placeholder='[ ]',
                        style={
                            'display': 'inline-block',
                            'padding': '5px 10px 5px 5px',
                        }
                    ),
                ],
                    style={
                        'width': '100%',
                        'float': 'left',
                        'backgroundColor': 'rgb(250, 250, 250)',
                        'border': 'thin lightgrey solid'
                    }
                ),
                
                html.Div([
                    html.Div([
                        html.Button(
                            'Define Group Traits',
                            id='groupTraitsButton',
                            n_clicks=0
                        )],
                        id='groupTraitsButtonDiv',
                        style={
                            'width': '100%',
                            'float': 'left',
                            'padding': '20px 5px 20px 5px',
                        }
                    )],
                    id='groupTraitsButtonDivWrapper'
                ),

                # Div for procedurally generated group trait input boxes
                html.Div(
                    id='groupTraitDiv'
                ),
                html.Br(),

                # Hidden div used for writing sim inputs to csv
                html.Div(
                    id='outputDiv',
                    style={'display': 'none'}
                ),

                # Hidden div used for writing EmMA inputs to csv
                html.Div(
                    id='outputDiv2',
                    style={'display': 'none'}
                ),

                html.Div(
                    id='EmMAInputsDiv',
                    style={'display': 'none'}
                )
                
            ],
            style={
                'width': '100%',
                'float': 'left',
                'textAlign': 'center',
                'fontFamily': 'verdana',
                'fontSize': '10pt'
            }),
        ]),
    ]),

    # Bottom page div
    html.Div([
        # Run button
        html.Div([
            html.Button(
                dcc.Link(
                    'Run Simulation',
                    href='/simulationrunning'
                ),
                id='runSimButton',
                n_clicks=0
            )],
            id='runSimButtonDiv',
            style={
                'width': '100%',
                'float': 'left',
                'padding': '20px 5px 20px 5px',
            }
        ),
        # Placeholder for simulation status text
        html.Div(id='simStatusDiv'),
        ],
        style={
            'width': '100%',
            'textAlign': 'center'
        }
    )
])


#================================================= Callbacks ===================================================

@app.callback(
    dash.dependencies.Output('validNumGroups', 'children'),  # Placeholder div to store valid number of groups
    [dash.dependencies.Input('groupTraitsButton', 'n_clicks')],
    [dash.dependencies.State('numAgentGroupsInput', 'value')])  # User-defined number of groups

def verifyNumGroups(n_clicks,numAgentGroups):
    # Updates every time user adjusts number of groups, so the try and except account for when the box is
    # empty/an invalid entry occurs, and only stores valid numbers
    # CURRENTLY updates field to NoneType object when entry is invalid--want it to not update when invalid
    if n_clicks != 0:
        try:
            numGroups = int(numAgentGroups)
        except:
            pass
        else:
            return numGroups
    else:
        pass


# Creates the inputs boxes for characteristics of the distinct groups--will be written to EmMAInputs.csv
# Shows/hides boxes based on how many groups the user specifies
# Returns layout
@app.callback(
    dash.dependencies.Output('groupTraitDiv', 'children'),  # Layout div for group traits
    [dash.dependencies.Input('validNumGroups', 'children')])  # Validated number of groups

def groupTraits(numGroups):
    # Account for current NoneType error
    if numGroups is None:
        numGroups = 0

    groupTraitList = [] # Initialize list of divs for group traits

    # Add a box with inputs to the layout for each group
    for group in range(1,numGroups+1):

        # Adjust box width depending on number of boxes
        if numGroups == 1:
            divWidth = '100%'
        else:
            divWidth = '49%'

        # Add top padding only for top 2 boxes
        if group == 1 or group == 2:
            pad = '2% 0% 2% 0%'
        else:
            pad = '0% 0% 2% 0%'

        # Odd number boxes on left, even on right
        if group % 2 != 0:
            divFloat = 'left'
        elif group % 2 == 0:
            divFloat = 'right'

        # Layout to be appended for each group with group-specific IDs
        groupTraitList.append(
            html.Div([
                html.Div([
                html.U('Group %s'%(group)),
                html.Br(),
                html.P('Number of People in this Group: ',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 5px 5px 10px',
                    }
                ),
                dcc.Input(
                    id='numAgentsInput%s'%(group),
                    value=5000,
                    placeholder='(5000 people)',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                ),
                html.Br(),
                html.P('Mobilization Curve Coefficient 1: ',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 10px',
                    }
                ),
                dcc.Input(
                    id='B0Input%s'%(group),
                    value=-5,
                    placeholder='(-5)',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                ),
                html.Br(),
                html.P('Mobilization Curve Coefficient 2: ',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 20px',
                    }
                ),
                dcc.Input(
                    id='B1Input%s'%(group),
                    value=0.05,
                    placeholder='(0.05)',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                ),
                html.Br(),
                html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id='distributionInput%s'%(group),
                            options=[
                                {'label': 'Initialize Census Distribution', 'value': 'y'},
                                {'label': 'Initialize Defined Start Nodes', 'value': 'n'}
                            ],
                            value='y',
                            placeholder='Select agent distribution...',
                        ),],
                        style={
                            'width': '70%',
                            'padding': '0% 15% 0% 15%',
                        }
                    ),],
                    style={
                        'textAlign':'center'
                    }
                ),
                html.P('Start node numbers to use if \'Defined Start Nodes\' is selected: ',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 5px 5px 10px',
                    }
                ),
                dcc.Input(
                    id='startNodeInput%s'%(group),
                    value=[],
                    placeholder='[ ]',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                ),
                html.Br(),
                html.P('Proportion of People Familiar with the City: ',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 5px 5px 10px',
                    }
                ),
                dcc.Input(
                    id='familiarityInput%s'%(group), 
                    value=0.9,
                    placeholder='(0.9)',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                ),
                html.Br(),
                html.P('Proportion of Panicked People: ',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 5px 5px 10px',
                    }
                ),
                dcc.Input(
                    id='panicInput%s'%(group),
                    value=0.05,
                    placeholder='(0.05)',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                ),
                html.Br(),
                html.P('Probability of Recalculating Route in Traffic:',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 5px 5px 10px',
                    }
                ),
                dcc.Input(
                    id='recalcInput%s'%(group),
                    value=0.5,
                    placeholder='(0.5)',
                    style={
                        'display': 'inline-block',
                        'padding': '5px 10px 5px 5px',
                    }
                )
            ],
                style={
                    'textAlign': 'center',
                    'border': 'thin lightgrey solid',
                    'backgroundColor': 'rgb(250, 250, 250)',
                    'padding': '5px 5px 5px 5px',
                }
            )],
            style={
                'width': divWidth,
                'float': divFloat,
                'padding': pad,
            })
        )

    for group in range(numGroups+1,maxNumGroups+1):

            divWidth = '49%'

            # Add top padding only for top 2 boxes
            if group == 1 or group == 2:
                pad = '2% 0% 2% 0%'
            else:
                pad = '0% 0% 2% 0%'

            # Odd number boxes on left, even on right
            if group % 2 != 0:
                divFloat = 'left'
            elif group % 2 == 0:
                divFloat = 'right'

            # Layout to be appended for each HIDDEN group with group-specific IDs
            groupTraitList.append(
                html.Div([
                    html.Div([
                    html.U('Group %s'%(group)),
                    html.Br(),
                    html.P('Number of People in this Group: ',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='numAgentsInput%s'%(group),
                        value='',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.P('Mobilization Curve Coefficient 1: ',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='B0Input%s'%(group),
                        value='',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.P('Mobilization Curve Coefficient 2: ',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='B1Input%s'%(group),
                        value='',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='distributionInput%s'%(group),
                                options=[
                                    {'label': 'Initialize Census Distribution', 'value': 'y'},
                                    {'label': 'Initialize Defined Start Nodes', 'value': 'n'}
                                ],
                                value='',
                            ),],
                            style={
                                'display': 'none'
                            }
                        ),],
                        style={
                            'display': 'none'
                        }
                    ),
                    html.P('Start node numbers to use if \'Defined Start Nodes\' is selected: ',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='startNodeInput%s'%(group),
                        value='',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.P('Proportion of People Familiar with the City: ',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='familiarityInput%s'%(group), 
                        value='',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.P('Proportion of Panicked People: ',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='panicInput%s'%(group),
                        value='',
                        style={
                            'display': 'none'
                        }
                    ),
                    html.Br(),
                    html.P('Probability of Recalculating Route in Traffic:',
                        style={
                            'display': 'none'
                        }
                    ),
                    dcc.Input(
                        id='recalcInput%s'%(group),
                        value='',
                        style={
                            'display': 'none'
                        }
                    )
                ],
                    style={
                        'display': 'none'
                    }
                )],
                style={
                    'display': 'none'
                })
            )

    return groupTraitList


# Hides the Group Trait button after it is clicked
# Returns nothing
@app.callback(
    dash.dependencies.Output('groupTraitsButtonDiv','children'),
    events=[dash.dependencies.Event('groupTraitsButton', 'click')])

def hideGroupTraitButton():
    return

# Shows the Group Trait button after changes are made to the number of groups
# Returns re-initialized Group Trait button
@app.callback(
    dash.dependencies.Output('groupTraitsButtonDivWrapper','children'),
    [dash.dependencies.Input('numAgentGroupsInput', 'value')])

def showGroupTraitButton(numAgentGroups):
    layout = html.Div([
            html.Button(
                'Define Group Traits',
                id='groupTraitsButton',
                n_clicks=0
            )],
            id='groupTraitsButtonDiv',
            style={
                'width': '100%',
                'float': 'left',
                'padding': '20px 5px 20px 5px',
            }
        )
    return layout


# Write the sim input parameters to sim input file once the Run Simulation button is clicked
# Returns nothing
@app.callback(
    dash.dependencies.Output('outputDiv', 'children'),
    [dash.dependencies.Input('runSimButton', 'n_clicks')],
    [dash.dependencies.State('locationDropdown', 'value'),
    dash.dependencies.State('simLengthInput', 'value'),
    dash.dependencies.State('resolutionInput', 'value'),
    dash.dependencies.State('extractIntervalInput', 'value'),
    dash.dependencies.State('noticeTimeInput', 'value'),
    dash.dependencies.State('destinationInput', 'value'),
    dash.dependencies.State('destinationNodeInput', 'value'),
    dash.dependencies.State('situationSelect', 'value'),
    dash.dependencies.State('numAgentGroupsInput', 'value')])

def createSimInCSV(n_clicks,location,simLength,resolution,extractInterval,noticeTime,destination,destinationNodes,situation,numAgentGroups):
    locationName = {
        'oroville' : 'OrovilleCalifornia',
        'mosul': 'MosulIraq',
        'santamaria': 'SantamariaCalifornia'
    }[location.lower()]

    disasterName = {
        'oroville' : 'flood',
        'mosul': 'flood',
        'santamaria': 'wildfire'
    }[location.lower()]
    
    # Uses inputs to generate filepath according to set file naming convention
    disasterFileName = '../Disasters/%s%s%s.csv'%(locationName,situation,disasterName)
    nodeSource = '../Networks/%sDijkstra.csv'%(locationName)
    roadSource = '../Networks/%sRoads.csv'%(locationName)
    agentOut = '../Outputs/%sAgent_%s.csv'%(locationName,situation)
    roadOut = '../Outputs/%sRoad_%s.csv'%(locationName,situation)
    
    simIn = [location,simLength,resolution,extractInterval,noticeTime,destination,destinationNodes,nodeSource,roadSource,disasterFileName,agentOut,roadOut]
    simInCol = ['REGION','SIM_LENGTH[hr]','SIM_STEP_RESOL[sec]','DATA_EXTRACT_INTERVAL[sec]','NOTICE_TIME[hr]',\
                'USE_EVAC_ZONE','GOAL_NODES','NODE_SOURCE_FILE','ROAD_SOURCE_FILE','HZRD_SOURCE_FILE',\
                'AGENT_OUTPUT_FILENAME','ROAD_OUTPUT_FILENAME']
    simInputs=pd.DataFrame(columns=simInCol)
    simIn = pd.Series(simIn, simInCol)
    simInputs=simInputs.append([simIn],ignore_index=True)
    simInputs.to_csv(r'../Inputs/SimInput.csv', index = False)
    print('SimInput file updated.')
    return


# Generates the list of dash.dependencies.State variables for the number of groups. Not based on user-defined number, just simplifies the callback.
values=['numAgentsInput','B0Input','B1Input','distributionInput','startNodeInput','familiarityInput','panicInput','recalcInput']

stateList = [dash.dependencies.State('validNumGroups','children')]+[dash.dependencies.State('%s%s'%(value,group),'value')\
				for group in range(1, maxNumGroups+1) for value in values]


# Write the different group parameters to EmMA input file
# Returns nothing
@app.callback(
    dash.dependencies.Output('outputDiv2', 'children'),
    [dash.dependencies.Input('runSimButton', 'n_clicks')],
    stateList    # List of State objects procedurally generated to match the user-defined number of groups
)

def createEmmaInCSV(n_clicks,numGroups,*args):
    numGroups = int(numGroups)
    agentTraitList = [] # Initialize list of lists of group traits
    for i in range(0,numGroups*8,8):
        groupList=[(i/8)+1] # Add group number to groupList
        traits = [args[j] for j in range((i),((i+8)))] # List of eight attributes
        groupList.extend(traits) # Add each trait from traits list to groupList as individual items
        agentTraitList.append(groupList) # Add groupList to list

    # Create Dataframe out of list of lists and write to EmMA Input csv
    emmaInCol = ['GROUP','NUM_AGENTS','B0','B1','DIST_BY_CENSUS','START_NODES','PERCENT_FAMILIAR',\
                 'PERCENT_PANIC','PERCENT_RECALC']
    emmaInputs=pd.DataFrame(agentTraitList,columns=emmaInCol)
    emmaInputs.to_csv(r'../Inputs/EmMAInput.csv', index = False)
    print('EmMAInput file updated.')
    return


"""# Hide the run button after it is clicked
# Returns nothing
@app.callback(
    dash.dependencies.Output('runSimButtonDiv','children'),
    events=[dash.dependencies.Event('runSimButton', 'click')]
)

def hideRunButton():
    return"""


# Provide status of simulation after run button is clicked
# CURRENTLY JUST FOR LOOKS--not based on actual simulation status
# Returns status text
"""@app.callback(
    dash.dependencies.Output('simStatusDiv','children'),
    [dash.dependencies.Input('runSimButton', 'n_clicks')]
)

def simulationStatus(n_clicks):
    if n_clicks != 0:
        status = html.P('Running simulation with the defined inputs...',
            style={
                'textAlign': 'center',
                'fontFamily': 'verdana',
                'fontSize': '10pt'
            })
    else:
        status = None
    return status"""


#==========================================================================================================================
#================================================== Loading Screen ========================================================
#==========================================================================================================================

# Layout to be displayed while the simulation is running
loading_layout = html.Div([
    html.Div([
        html.Div([
            html.Br(),
            html.P('Simulation may take some time to run. Continue?'),
            html.Button(
                'Yes',
                id='continueButton',
                n_clicks=0
                ),
            html.Button(
                dcc.Link(
                    'No',
                    href='/inputs'
                    )
                ),
        ],
        id='confirmationWrapper'),
        html.Div(id='loading_page_content')],
    style={
        'fontFamily': 'verdana',
        'textAlign': 'center'
    }),
    # Placeholder for simulation status boolean
    html.Div(0,id='simulationDoneDiv',style={'display': 'none'})
])


@app.callback(
    dash.dependencies.Output('loading_page_content','children'),
    events=[dash.dependencies.Event('continueButton', 'click')])

def continueSimulation():
    layout = [
        html.Br(),
        html.Br(),
        html.Br(),
        html.H2('Simulation is currently running...'),
        html.Br(),
        html.H4('Please be patient. Page will redirect when simulation completes.')
    ]
    return layout

@app.callback(
    dash.dependencies.Output('confirmationWrapper','style'),
    events=[dash.dependencies.Event('continueButton', 'click')])

def hideConfirmation():
    return {'display': 'none'}


# Prevents delay in displaying the "Simulation Running" text by providing a buffer step
# Without this buffer the text would not display until after the simulation finished
# Returns Boolean
@app.callback(
    dash.dependencies.Output('simulationDoneDiv','children'),
    events=[dash.dependencies.Event('continueButton', 'click')])

def continueConfirmation():
    return 1


# Launches visualization screen to view the results of the new user-defined scenario
# CURRENTLY JUST FOR LOOKS--uses sleep function to cause delay and does not run simulation
# Returns url pathname
@app.callback(
    dash.dependencies.Output('url','pathname'),
    [dash.dependencies.Input('simulationDoneDiv', 'children')])

def redirectPage(done):
    if done == 0:
    	pass
    elif done == 1:
    	import EmMAUniverseFinal
    	link = '/viz'
    	return link


#===========================================================================================================================
#===================================================Input Visual Page========================================================
#===========================================================================================================================

# Same code as the Preloaded Visuals page, but using the user input file's data. Repeated functions are most likely 
# unnecessary, but the layout IDs and callbacks are necessary because if they are not different from their "preload" 
# counterparts then it will not output the graphs/info to the right location. All callbacks on every page are active no 
# matter what page you are on--each link simply changes which divs are visible.

# simInFile is written to by the user input page, but the file is only loaded into the script once, and it does not check
# for changes to the file on page refresh. For demonstration purposes, the input page could write to a hidden div instead,
# but the end goal is to have it write to a file, use that file to run the simulation, then use the simulation outputs for
# the visual.


#============================================================= Layout ============================================================

# Defines the page content for '/viz'
visuals_layout = html.Div([
    html.Div([

        # Top of page div (Logos, Headers, Links)
        html.Div([
            html.Div([
                # Dash logo
                html.Img(src=dashPlotly,
                    style={
                        'height': '55px',
                        'float': 'left',
                        'position': 'absolute',
                        'top': '23px',
                        'left': '15px'
                    },
                )],
            ),
            # Header and links
            html.Div([
                html.H2('Evacuation Movement', 
                    style={
                        'textAlign': 'center',
                        'fontFamily': 'verdana'
                       }),
                html.Div([
                    # Link to inputs page
                    html.Div([
                        dcc.Link('Define Inputs',
                            href='/inputs',
                            style = {'color':'#004F98',
                                'textDecoration':'underline',
                                'cursor':'pointer'}
                        )],
                    style={
                        'padding': '0px 15px 0px 2px',
                        'display': 'inline-block'
                    }),
                    # Link to home page
                    html.Div([
                        dcc.Link('Return Home',
                            href='/home',
                            style = {'color':'#004F98',
                                'textDecoration':'underline',
                                 'cursor':'pointer'}
                        )],
                    style={
                        'padding': '0px 2px 0px 15px',
                        'display': 'inline-block'
                    })
                ],
                style={
                    'textAlign': 'center',
                    'fontSize': '9pt',
                    'fontFamily': 'verdana'
                }),
            ]),
            # Booz Allen logo
            html.Div([
                html.Img(src=boozAllen,
                    style={
                        'height': '30px',
                        'float': 'right',
                        'position': 'absolute',
                        'top': '35px',
                        'right': '25px'

                    },
                )],
            )],
            style={
                'padding': '5px 5px 0px 5px',
            }
        ),
        html.Br(),
        # Middle of page split into two divs: 74% and 25%

        # Left div (Dropdowns, Safe Graph, Map)
        html.Div([
            # 74% div split into two divs: dropdowns=33% (~24% of whole page width), map=66% (~49% of page)

            # Left div (Dropdowns/Visualization Options)
            html.Div([

                # Header
                html.Div([
                    html.Div([
                        html.P('Visualization Options:',
                            style={
                                'textAlign': 'center',
                                'fontFamily': 'verdana',
                                'fontSize': '10pt'
                            }),
                    ]),
                ],
                style={
                'borderBottom': 'thin lightgrey solid',
                'backgroundColor': 'rgb(250, 250, 250)',
                'padding': '5px 5px 5px 5px',
                }),
                html.Br(),

                # Dropdowns
                dcc.Dropdown(
                    id='dataSelect',
                    options=[
                        {'label': 'Show disaster and people\'s movement', 'value': 'both'},
                        {'label': 'Show people\'s movement', 'value': 'people'},
                        {'label': 'Show disaster\'s movement', 'value': 'disaster'},
                    ],
                    value='both',
                    placeholder='Select data of interest...',
                ),
                html.Br(),
                dcc.Dropdown(
                    id='mapstyleDropdown',
                    options=[
                        {'label': 'Map style: Outdoors', 'value': 'outdoors'},
                        {'label': 'Map style: Dark', 'value': 'dark'},
                        {'label': 'Map style: Satellite', 'value': 'satellite'},
                        {'label': 'Map style: Streets', 'value': 'streets'}
                    ],
                    value='outdoors',
                    placeholder='Select a map style...'
                ),
                html.Br(),
                dcc.Dropdown(id='agentColorDropdown',
                    options=[
                        {'label': 'Agent colorscale: ' + i, 'value': i}\
                        for i in ['Blackbody','Bluered','Blues','Earth','Electric',\
                                  'Greens','Greys','Hot','Jet','Picnic','Portland',\
                                  'Rainbow','RdBu','Reds','Viridis','YlGnBu','YlOrRd']
                    ],
                    value='Reds',
                    placeholder='Select agent colorscale...'
                ),
                html.Br(),
                dcc.Dropdown(id='disasterColorDropdown',
                    options=[
                        {'label': 'Disaster colorscale: ' + i, 'value': i}\
                        for i in ['Blue', 'Green', 'Yellow', 'Red', 'White', 'Black']
                    ],
                    value='Blue',
                    placeholder='Select disaster colorscale...'
                ),
                html.Br(),

                # Graph showing number of agents that have reached the defined safe zones
                dcc.Graph(id='safePeople-graph',
                         config = {'displayModeBar': False})
            ],
            style={
                'width': '33%',
                'float': 'left',
                'textAlign': 'center',
                'fontFamily': 'verdana',
                'fontSize': '10pt'
            }),

            # Right div (Map)
            html.Div([

                # Header
                html.Div([
                    html.Div([
                        html.P(
                            id='mapHeader',
                            style={
                                'textAlign': 'center',
                                'fontFamily': 'verdana',
                                'fontSize': '10pt'
                            }),
                    ]),
                ],
                style={
                    'borderBottom': 'thin lightgrey solid',
                    'backgroundColor': 'rgb(250, 250, 250)',
                    'padding': '5px 5px 5px 5px',
                }),
                html.Br(),

                # Map
                dcc.Graph(
                    id='graphWithSlider',
                    animate=True,
                    hoverData = {'points':[{'customdata': 3}]},
                    config = {'displayModeBar': False}
                ),
            ],
            style={
                'width': '66%',
                'float': 'right'
            })
        ],
        style={
            'width': '74%',
            'float': 'left'
        }),

        # Right div (Hover Info Graphs)
        html.Div([

            # Header
            html.Div([
                html.P('Hover over points for more information.',
                    style={
                        'textAlign': 'center',
                        'fontFamily': 'verdana',
                        'fontSize': '10pt'
                   })
            ],
            style={
            'borderBottom': 'thin lightgrey solid',
            'backgroundColor': 'rgb(250, 250, 250)',
            'padding': '5px 5px 5px 5px',
            }),
            html.Br(),

            # Graphs showing information relevant to node mouse is hovering over
            html.Div([
                dcc.Graph(id='numPeople-graph',
                         config = {'displayModeBar': False}),
                html.Br(),
                dcc.Graph(id='second-graph',
                         config = {'displayModeBar': False})
            ])
        ],
        style={
            'width': '25%',
            'float': 'right'
        }),

        # Bottom of page div (Time Slider)
        html.Div([
            html.Div([
                html.Br(),
                html.Div([
                    dcc.Slider(
                        id='timestepSlider',
                        min=0,
                        max=7500,
                        step = 500,
                        value=0
                    )],
                    id='sliderDiv',
                )
            ],
            style={
                'width': '85%',
                'align': 'center',
                'display': 'inline-block'
            })
        ],
        style={
            'textAlign': 'center',
        }),
    ]),
])

#======================================================= Callbacks =================================================================

@app.callback(
    dash.dependencies.Output('loadVizPageSignal','children'),
    [dash.dependencies.Input('url','pathname')]
    )

def signal(url):
	if url == '/viz':
		return 1


# Set time slider max to the length of the simulation in seconds
@app.callback(
    dash.dependencies.Output('sliderDiv','children'),
    [dash.dependencies.Input('loadVizPageSignal','children')]
    )
def getSlider(signal):
    simInFile = pd.read_csv(r'../Inputs/SimInput.csv')
    simIn = list(simInFile.values[0])

    valMax = int(simIn[1])*60*60
    step = int(simIn[3])
    marks = {}

    # Starts at time=0, goes to slider max + 1 so that the max is included
    # Arbitrary decision to have a mark every 5 timesteps for spacing--doesn't always include the max value
    for i in range(0, valMax+1, step*5):
        # Includes units for start and end marks only
        if(i==0 or i==valMax):
            marks.update({i: '{} {}'.format(i, 'Seconds')})
        # All other marks do not include units
        else:
            marks.update({i: '{}'.format(i)})

    sliderDict = dcc.Slider(
            id='timestepSlider',
            min=0,
            max=valMax,
            step=step,
            marks=marks,
            value=0,
            updatemode='drag'
            )
    

    return sliderDict



# Generate comprehensive description of map based on location and data selection
# Outputs description to Map Header
@app.callback(
    dash.dependencies.Output('mapHeader', 'children'),  # Map description
    [dash.dependencies.Input('loadVizPageSignal','children'),
    dash.dependencies.Input('dataSelect', 'value')]    # Data selection dropdown   
)
def update_map_header(signal,data):
    simInFile = pd.read_csv(r'../Inputs/SimInput.csv')
    simIn = list(simInFile.values[0])
    location = simIn[0]


    # Proper location name
    locationName = {
        'oroville' : 'Oroville, CA, USA',
        'mosul': 'Mosul, Iraq',
        'santamaria': 'Santa Maria, CA, USA'
    }[location.lower()]

    # Associated disaster type
    disasterName = {
        'oroville' : 'flood',
        'mosul': 'flood',
        'santamaria': 'wildfire'
    }[location.lower()]
    
    # Selected data
    if data == 'both':
        header = 'Map of {}, showing movement of the disaster and people in the event of a {}.'.format(locationName, disasterName)
    elif data == 'people':
        header = 'Map of {}, showing people\'s movement in the event of a {}.'.format(locationName, disasterName)
    elif data == 'disaster':
        header = 'Map of {}, showing disaster movement in the event of a {}'.format(locationName, disasterName)
    else:
        header = 'Map of {}'.format(locationName)
    return header


# Generate the map
# Outputs map figure
@app.callback(
    dash.dependencies.Output('graphWithSlider', 'figure'),  # Main map
    [dash.dependencies.Input('loadVizPageSignal','children'),
    dash.dependencies.Input('timestepSlider', 'value'),    # Time slider
    dash.dependencies.Input('dataSelect', 'value'), # Data selection dropdown
    dash.dependencies.Input('mapstyleDropdown', 'value'),   # Map style dropdown
    dash.dependencies.Input('agentColorDropdown', 'value'), # Agent colorway selection dropdown
    dash.dependencies.Input('disasterColorDropdown', 'value')]  # Disaster colorway selection dropdown
)

def update_figure(signal,time,selection,mapStyle,agentColorScale,disasterColorScale):
    simInFile = pd.read_csv(r'../Inputs/SimInput.csv')
    simIn = list(simInFile.values[0])
    location = simIn[0]

    nodesFile = pd.read_csv(simIn[7])
    disasterFile = pd.read_csv(simIn[9])
    agentFile = pd.read_csv(simIn[10])

    nf=nodesFile
    tf=agentFile
    df=disasterFile
    
    # Marker definitions
    tff=tf[tf['TIME']==time]    # Create dataframe with only agent locations at given time
    tfff=tff.groupby('CURRENT_NODE')['AGENT_ID'].count()    # Translate tff to number of agents at each node

    impassible=tff[tff['ACTIVITY']==False]  # Identify impassible nodes at timestep by their 'Activity' status
    impassible = sorted(list(impassible['CURRENT_NODE'].unique()))  # Generate list of impassible nodes w/o duplicates
    
    # Creates list of number of agents at each node with zeroes at impassible nodes
    numVisitors=[]
    for node in nf['OBJECTID']:
        if node not in impassible:
            try:
                numVisitors.append(tfff[node])
            except:
                numVisitors.append(0)  
        else:
            numVisitors.append(0)

    # Arbitrary scaling of node size distribution to look better
    peopleNodeSize = numVisitors
    for i in range(len(peopleNodeSize)):
        peopleNodeSize[int(i)] = (peopleNodeSize[int(i)]**0.45)*4
    
    peopleNodeMarker = dict(
        size=peopleNodeSize,
        color=numVisitors,
        colorscale=agentColorScale,
        opacity=0.8,
    )


    # Set appropriate disaster marker type for the given location
    if location.lower() == 'oroville' or location.lower() == 'mosul':
        sizes = []
        # Sets marker size = 70 if there is any water at the node (disasterFile measurements not binary; shows depth)
        for index in range(len(disasterFile[str(time)])):
            if disasterFile[str(time)][index] == 0:
                sizes.append(0)
            else:
                sizes.append(70)
        
        # Sets default flood color to blue colorway
        if disasterColorScale is None:
            disasterColorScale = 'Blue'

        # Defines shades of each color to represent varying water depths
        spectrum = {
            'Red':
                ['rgba(253, 237, 236, 0.7)',
                'rgba(250, 219, 216, 0.7)',
                'rgba(241, 148, 138, 0.7)',
                'rgba(231, 76, 60, 0.7)',
                'rgba(176, 58, 46, 0.7)',
                'rgba(120, 40, 31, 0.7)'],
            'Yellow':
                ['rgba(249, 231, 159, 0.7)',
                'rgba(247, 220, 111, 0.7)',
                'rgba(241, 196, 15, 0.7)',
                'rgba(212, 172, 13, 0.7)',
                'rgba(183, 149, 11, 0.7)',
                'rgba(154, 125, 10, 0.7)'],
            'Green':
                ['rgba(234, 250, 241, 0.7)',
                'rgba(171, 235, 198, 0.7)',
                'rgba(88, 214, 141, 0.7)',
                'rgba(40, 180, 99, 0.7)',
                'rgba(29, 131, 72, 0.7)',
                'rgba(24, 106, 59, 0.7)'],
            'Blue':
                ['rgba(234, 242, 248, 0.7)',
                'rgba(212, 230, 241, 0.7)',
                'rgba(127, 179, 213, 0.7)',
                'rgba(41, 128, 185, 0.7)',
                'rgba(31, 97, 141, 0.7)',
                'rgba(21, 67, 96, 0.7)'],
            'White':
                ['rgba(253, 254, 254, 0.9)',
                'rgba(251, 252, 252, 0.825)',
                'rgba(247, 249, 249, 0.75)',
                'rgba(244, 246, 247, 0.675)',
                'rgba(240, 243, 244, 0.6)',
                'rgba(236, 240, 241, 0.525)'],
            'Black':
                ['rgba(120, 120, 120, 0.7)',
                'rgba(100, 100, 100, 0.7)',
                'rgba(80, 80, 80, 0.7)',
                'rgba(60, 60, 60, 0.7)',
                'rgba(40, 40, 40, 0.7)',
                'rgba(20, 20, 20, 0.7)']
            
        }[disasterColorScale]
        
        # Defines depths that trigger color shade changes
        colors = []
        for index in range(len(disasterFile[str(time)])):
            if disasterFile[str(time)][index] > 15:
                colors.append(spectrum[5])
            elif disasterFile[str(time)][index] > 10:
                colors.append(spectrum[4])
            elif disasterFile[str(time)][index] > 5:
                colors.append(spectrum[3])
            elif disasterFile[str(time)][index] > 1:
                colors.append(spectrum[2])
            else:
                colors.append(spectrum[1])
                
        floodNodeMarker=dict(
            sizemode = 'area',
            size=sizes,
            color=colors,
        )
        disasterMarker = floodNodeMarker
    elif location.lower() == 'santamaria':
        sizes = []
        if disasterColorScale is None:
            disasterColorScale = 'Red'
        spectrum = {
            'Red':'rgba(170, 0, 0, 0.7)',
            'Yellow':'rgba(154, 125, 10, 0.7)',
            'Green':'rgba(24, 106, 59, 0.7)',
            'Blue':'rgba(21, 67, 96, 0.7)',
            'White':'rgba(236, 240, 241, 0.525)',
            'Black':'rgba(20, 20, 20, 0.7)'
        }[disasterColorScale]
        
        # Sets marker size to 70 if fire is present at node (disasterFile for fire is binary)
        for index in range(len(disasterFile[str(time)])):
            if disasterFile[str(time)][index] == 0:
                sizes.append(0)
            else:
                sizes.append(70)
        
        # Only one color shade available for fire--no varying depths
        colors = []
        for index in range(len(disasterFile[str(time)])):
            if disasterFile[str(time)][index] > 0:
                colors.append(spectrum)
            else:
                colors.append('rgba(255,255,255,0.7)')
        
        fireNodeMarker=dict(
            sizemode = 'area',
            size=sizes,
            color=colors
        )
        disasterMarker = fireNodeMarker
    else:   # general marker
        disasterMarker = dict(
            sizemode = 'area',
            color = 'rgba(255,255,255,0.7)',
            size = 1.75,
        )
    
    # Plot the nodes representing street intersections on the map
    nodeData = dict(
        type='scattermapbox',
        lon=nf['POINT_X'],
        lat=nf['POINT_Y'],
        text=nf['OBJECTID'],    # Node number, aligns with number assigned by ArcGIS
        hoverinfo = 'text',
        customdata=nf['OBJECTID'],  # Used for hoverdata
        marker=dict(
            sizemode = 'area',
            size=1.75,
            color='rgba(255,255,255,0.5)',
        )
    )
    
    # Plot additional points with color, size based on the number of people (on top of nodeData)
    peopleData = dict(
        type='scattermapbox',
        lon=nf['POINT_X'],
        lat=nf['POINT_Y'],
        hoverinfo = 'skip',
        marker=peopleNodeMarker
    )
    
    # Plot disaster data
    disasterData = dict(
        type='scattermapbox',
        lon=df['POINT_X'],
        lat=df['POINT_Y'],
        hoverinfo = 'skip',
        marker=disasterMarker
    )
    
    # Generates lat and lon list for nodes that were overtaken by the disaster while occupied by agents
    tff=tf[tf['TIME']==time]
    tfff=tff.groupby('CURRENT_NODE')['AGENT_ID'].count()
    impassible=tff[tff['ACTIVITY']==False]
    impassible = sorted(list(impassible['CURRENT_NODE'].unique()))
    impassibleLat = []
    impassibleLon = []
    for node in nf['OBJECTID']:
        if node in impassible and tfff[node] > 0:
            impassibleLat.append(float(nf[nf['OBJECTID']==node]['POINT_Y']))
            impassibleLon.append(float(nf[nf['OBJECTID']==node]['POINT_X']))
        else:
            pass
    
    # Plot red cross marker for nodes overtaken while occupied
    impassibleData = dict(
        type='scattermapbox',
        lon=impassibleLon,
        lat=impassibleLat,
        hoverinfo = 'skip',
        marker=dict(
            size=10,
            color='#ffffff',
            symbol='hospital'
        )
    )
        
    # Adjust which data shows on map based on the dropdown selection   
    if selection == 'both':
        data = [nodeData, peopleData, disasterData, impassibleData]
    elif selection == 'people':
        data = [nodeData, peopleData, impassibleData]
    elif selection == 'disaster':
        data = [nodeData, disasterData]
    else:
        data = [nodeData]


    if location.lower() == 'oroville':
        lat=39.5
        lon=-121.59
        zoom=11.1
    elif location.lower() == 'mosul':
        lat=36.3566
        lon=43.164
        zoom=11
    elif location.lower() == 'santamaria':
        lat=34.9353
        lon=-120.438626
        zoom=11.15
    else:
        lat=15
        lon=0
        zoom=0.6
    
    layout = dict(
        autosize=True,
        height=506,
        margin=go.Margin(l=0, r=0, t=0, b=0),
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_access_token,
            center=dict(
                lat=lat,
                lon=lon 
            ),
            style=mapStyle, # Alters the map coloration/style based on dropdown
            bearing=0,
            zoom=zoom   # Assigned from if/elif above
        )
    )
 
    figure = dict(data=data, layout=layout)
    return figure


# Generate graph of number of agents that have arrived at the defined safezone at the given time
# Outputs graph figure
@app.callback(
    dash.dependencies.Output('safePeople-graph', 'figure'), # Bottom left graph
    [dash.dependencies.Input('loadVizPageSignal','children'),
    dash.dependencies.Input('timestepSlider', 'value')]    # Time slider
)

def safegraph_update(signal,time):
    simInFile = pd.read_csv(r'../Inputs/SimInput.csv')
    simIn = list(simInFile.values[0])
    agentFile = pd.read_csv(simIn[10])
    tf = agentFile

    # Narrow dataframe down to current time and safe agents
    tff=tf[tf['TIME']<=time]
    tfff = tff[tff['IS_SAFE']==1]

    # Create list for time axis up to current time
    xList = list(tff['TIME'].unique())
    # Create list of number of safe agents for each time point up to current time
    yList = []
    for x in xList:
        yList.append(len(tfff[tfff['TIME']==x]))       

    # Create scatterplot of number of people at safety vs time
    data = [dict(
        type = 'scatter',
        mode='lines+markers',
        x = xList,
        y = yList,
        line=dict(
            shape="spline",
            smoothing=1,    # arbitrary
            width=1,    # arbitrary
            color='#a9bb95' # arbitrary
        ),
        marker=dict(symbol='diamond-open')
    )]

    # Define appearance of scatterplot
    layout = dict(
        autosize=True,
        height=300,
        title='Number of people at safety:',
        xaxis={'title': 'Seconds'},
        yaxis={'title': 'Number of People'})

    figure = dict(data=data, layout=layout)
    
    return figure


# Generates graph of the number of agents at the specified node at given time
# Specify node by hovering mouse over node on map
# Outputs graph figure
@app.callback(
    dash.dependencies.Output('numPeople-graph', 'figure'),  # Top right graph
    [dash.dependencies.Input('loadVizPageSignal','children'),
    dash.dependencies.Input('graphWithSlider', 'hoverData'),   # Pulls which node is being hovered over
    dash.dependencies.Input('timestepSlider', 'value')] # Time slider
)

def hovergraph_update(signal,hoverData, time):
    simInFile = pd.read_csv(r'../Inputs/SimInput.csv')
    simIn = list(simInFile.values[0])
    agentFile = pd.read_csv(simIn[10])
    tf=agentFile
    hoverNode = hoverData['points'][0]['customdata']    # Syntax to access node number stored in map 'customdata'

    # Narrow dataframe to current time and node
    tff=tf[tf['TIME']<=time]
    tfff = tff[tff['CURRENT_NODE']==hoverNode]

    # Create list of times up to currrent time
    xList = list(tff['TIME'].unique())
    # Create list of number of agents at node at each time
    yList = []
    for x in xList:
        yList.append(len(tfff[tfff['TIME']==x]))       

    # Create scatterplot of number of people at node vs time
    data = [dict(
        type = 'scatter',
        mode='lines+markers',
        x = xList,
        y = yList,
        line=dict(
            shape="spline",
            smoothing=1,
            width=1,
            color='#a9bb95'
        ),
        marker=dict(symbol='diamond-open')
    )]

    # Define appearance of scatterplot
    layout = dict(
        autosize=True,
        height=243,
        title='Number of people at node %d:' % hoverNode,
        xaxis={'title': 'Seconds'},
        yaxis={'title': 'Number of People'})

    figure = dict(data=data, layout=layout)
    
    return figure


# Generate graph of average panic level of agents at given node
# Outputs graph figure
@app.callback(
    dash.dependencies.Output('second-graph', 'figure'), # Bottom right graph
    [dash.dependencies.Input('loadVizPageSignal','children'),
    dash.dependencies.Input('graphWithSlider', 'hoverData'),   # Pulls which node is being hovered over
    dash.dependencies.Input('timestepSlider', 'value')] # Time slider
)

def secondhovergraph_update(signal,hoverData, time):
    simInFile = pd.read_csv(r'../Inputs/SimInput.csv')
    simIn = list(simInFile.values[0])
    agentFile = pd.read_csv(simIn[10])
    tf=agentFile
    hoverNode = hoverData['points'][0]['customdata']    # Syntax to access node number stored in map 'customdata'

    # Narrow dataframe to current time and node
    tff=tf[tf['TIME']<=time]
    tfff = tff[tff['CURRENT_NODE']==hoverNode]

    # Create list of times up to currrent time
    xList = list(tff['TIME'].unique())
    # Create list of average panic level at node at each time
    yList = list(tfff.groupby('TIME').mean()['PANIC'])

    for i in range(len(xList)):
        try:
            yList[i]
        except:
            try:
                yList.append(yList[-1])
            except:
                yList.append(0)

    # Create scatterplot of panic level at node vs time
    data = [dict(
        type = 'scatter',
        mode='lines+markers',
        x = xList,
        y = yList,
        line=dict(
            shape="spline",
            smoothing=1,
            width=1,
            color='#fac1b7'
        ),
        marker=dict(symbol='diamond-open')
    )]

    # Define appearance of scatterplot
    layout = dict(
        autosize=True,
        height=243,
        title='Average panic level at node %d:' % hoverNode,
        xaxis={'title': 'Seconds'},
        yaxis={'title': 'Panic Level (0-1)'})

    figure = dict(data=data, layout=layout)

    return figure


#==========================================================================================================================
#==========================================================================================================================
#==========================================================================================================================

# Adjust page contents based on url pathname
# Returns page layout
@app.callback(
    dash.dependencies.Output('page-content', 'children'),
    [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/preloadedviz':
        return preloadedvisuals_layout
    elif pathname == '/inputs':
        return inputs_layout
    elif pathname == '/simulationrunning':
        return loading_layout
    elif pathname == '/viz':
        return visuals_layout
    else:
        return index_layout


# Run application (adjust debug status)
if __name__ == '__main__':
    app.run_server(port=8050,threaded=True,debug=False)