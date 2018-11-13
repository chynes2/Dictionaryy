import pandas as pd 

import dash 
from dash.dependencies import Input, Output   #used in the call backs
import dash_core_components as dcc            #contians all of the widgets you desire. 
import dash_html_components as html           #used for html commands e.g. headers and Divs.

app = dash.Dash()

d = {'x':[1,2,3,4],'y':[10,5,1,7],'z':['dog','dog','cat','cat']}
d1 = {'x':[1,2,3,4],'y':[10,5,1,7],'z':['pig','wolf','pig','wolf']}
df1 = pd.DataFrame(data = d)
df2 = pd.DataFrame(data = d1)

app = dash.Dash()
app.title = 'Add_Links'
app.config.supress_callback_exceptions = True
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

#==============================================================================
page_1_layout = html.Div([
	html.H1('Page1'),
    #here we create the link
	dcc.Link(
		children ='Go to page2', 
		href='/page2',#where the url will be sent to 
		style={'color':'#FF0000','cursor':'pointer'} #cursor changes on hover
		),
    
    dcc.Dropdown(
        id='my_dropdown',
        options=[
            {'label': 'Kitty Cat', 'value': 'cat'},
            {'label': 'Dog', 'value': 'dog'}
        ],
        value='dog'
    ),
    dcc.Graph(id='my_graph',config={'displayModeBar': False})
])

@app.callback(Output('my_graph', 'figure'), [Input('my_dropdown', 'value')])
def update_graph(dropdown_value):
    df = df1[df1.z==dropdown_value]
    return {
        'data': [{
            'x': df.x,
            'y': df.y,
            'type':'bar'
        }]
    }

#==============================================================================
page_2_layout = html.Div([
	html.H1('Page2'),
    
	dcc.Link(
		children ='Go to page1',
		href='/',
		style={'color':'#3587EA','cursor':'pointer','fontSize':'40'} 
		),
    
    dcc.Dropdown(
        id='my_dropdown2',
        options=[
            {'label': 'Pig', 'value': 'pig'},
            {'label': 'Wolf', 'value': 'wolf'}
        ],
        value='pig'
    ),
    dcc.Graph(id='my_graph2')
])


@app.callback(Output('my_graph2', 'figure'), [Input('my_dropdown2', 'value')])
def update_graph2(dropdown_value):
    df = df2[df2.z==dropdown_value]
    return {
        'data': [{
            'x': df.x,
            'y': df.y,
            'type':'bar'
        }]
    }


@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page2': #href and this must match.
        return page_2_layout
    else:
        return page_1_layout


if __name__ == '__main__':
    app.run_server(debug = False)