import dash
from dash import html, dcc, Input, Output, State
import dash_leaflet as dl
import paho.mqtt.client as mqtt
import json

# Initialize Dash app
app = dash.Dash(__name__)

# MQTT setup
mqtt_broker_address = "localhost"  # Replace with your broker's address
mqtt_topic = "BotPatrol"
mqtt_client = mqtt.Client()

# Initial map setup
center = [40.1020, -88.2272]  # Center of the UIUC campus
zoom = 15

# Define shapes
siebel_center = [40.1138, -88.2249]

shapes = {
    'square': dl.Rectangle(bounds=[[siebel_center[0]-0.001, siebel_center[1]-0.001], [siebel_center[0]+0.001, siebel_center[1]+0.001]], color="blue"),
    'triangle': dl.Polygon(positions=[[siebel_center[0], siebel_center[1]-0.001], [siebel_center[0]-0.001, siebel_center[1]+0.001], [siebel_center[0]+0.001, siebel_center[1]+0.001]], color="red"),
    'line': dl.Polyline(positions=[[siebel_center[0]-0.001, siebel_center[1]-0.001], [siebel_center[0]+0.001, siebel_center[1]+0.001]], color="green")
}

app.layout = html.Div([
    html.H1("Bot Patrol", style={
        'text-align': 'center',
        'margin-top': '20px',
        'font-size': '2.5em',
        'color': '#333',
        'font-family': '"Helvetica Neue", Helvetica, Arial, sans-serif'
    }),
    dcc.ConfirmDialog(
        id='confirm-alert',
        message='Your area has been secured.',
    ),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='shape-selector',
                options=[
                    {'label': 'Line', 'value': 'line'},
                    {'label': 'Triangle', 'value': 'triangle'},
                    {'label': 'Square', 'value': 'square'}
                ],
                value='line',  # Default value
                clearable=False,
                style={
                    'color': '#333',
                    'font-size': '16px',
                }
            )
        ], style={
            'width': '20%',
            'padding': '20px',
            'background-color': '#f8f9fa',
            'border-radius': '8px',
            'box-shadow': '0 2px 4px rgba(0,0,0,.1)'
        }),
        html.Div([
            dl.Map(center=siebel_center, zoom=zoom, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="overlay-shape")
            ], style={'width': '1000px', 'height': '500px', 'border-radius': '8px'}),
        ], style={'width': '75%', 'padding': '20px'}),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'padding': '20px'}),
    html.Div([
        dcc.Input(
            id='sensitivity-input',
            type='number',
            value=0.5,  # Default value
            min=0.1,  # Minimum value
            max=0.9,  # Maximum value
            step=0.1,  # Increment step
            style={
                'margin-right': '10px',
                'width': '100px',
                'height': '40px',
                'text-align': 'center',
                'border-radius': '5px',
                'border': '1px solid #bbb',
                'font-size': '16px',
                'outline': 'none'
            }
        ),
        html.Button("Submit", id="submit-shape", style={
    'background-color': '#28a745',
    'color': 'white',
    'padding': '10px 24px',
    'border': 'none',
    'cursor': 'pointer',
    'border-radius': '5px',
    'font-size': '16px',
    'outline': 'none',
    'transition': 'background-color 0.3s',  # Smooth transition for background color
    ':hover': {
        'background-color': '#218838',  # Darker shade for hover
    },
    ':active': {
        'background-color': '#1e7e34',  # Even darker shade for active/click
    },
}),
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'padding-top': '20px'}),
    html.Div(id="status", style={'text-align': 'center', 'padding-top': '10px', 'font-size': '18px', 'color': '#333'})
], style={
    'background-color': '#e9ecef',
    'font-family': '"Helvetica Neue", Helvetica, Arial, sans-serif',
    'padding-bottom': '20px'
})


@app.callback(
    Output("overlay-shape", "children"),
    Input('shape-selector', 'value')
)
def overlay_selected_shape(selected_shape):
    # Overlay the selected shape on the map
    return shapes[selected_shape]

@app.callback(
    Output("status", "children"),
    Input("submit-shape", "n_clicks"),
    State('shape-selector', 'value'),
    State('sensitivity-input', 'value'),
    prevent_initial_call=True  # Prevents the callback from being triggered on app load
)
def submit_shape(n_clicks, selected_shape, sensitivity):
    if n_clicks > 0:
        payload = {'shape': selected_shape, 'sensitivity': sensitivity}
        json_payload = json.dumps(payload)
        mqtt_client.connect(mqtt_broker_address, 1883)
        mqtt_client.publish(mqtt_topic, json_payload)
        mqtt_client.disconnect()
        # Update the status message to indicate the area has been secured
        return "Your area has been secured."
    return "Select a shape, set sensitivity, and click 'Submit Shape'"

if __name__ == '__main__':
    app.run_server(debug=True)