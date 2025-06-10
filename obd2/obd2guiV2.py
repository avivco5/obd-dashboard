import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_daq as daq
import random
import datetime
import obd

initial_speed = 40  # אפשר לשנות לערך אחר

# התחברות ל-OBD בפורט ידני
try:
    connection = obd.OBD(portstr="/dev/rfcomm0")  # נסה פורט קבוע
    is_connected = connection.is_connected()
except:
    connection = None
    is_connected = False

# אתחול נתוני סימולציה
current_values = {
    "speed": initial_speed,
    "rpm": 800,
    "coolant_temp": 90,
    "throttle": 10
}

speed_history = []

app = dash.Dash(__name__)
app.title = "OBD2 Dashboard"

app.layout = html.Div(style={'backgroundColor': '#1e1e1e', 'color': 'white', 'fontFamily': 'Arial'}, children=[
    html.H1("OBD2 Dashboard", style={'textAlign': 'center'}),
    html.Div(id='clock', style={'textAlign': 'center', 'fontSize': '28px'}),

    html.Div([
        html.Label("בחר מקור נתונים:"),
        dcc.RadioItems(
            id='mode',
            options=[
                {'label': 'OBD2', 'value': 'obd'},
                {'label': 'סימולציה', 'value': 'sim'}
            ],
            value='sim',
            labelStyle={'display': 'inline-block', 'margin-right': '20px'}
        ),
        daq.Indicator(
            id='obd-status',
            label="OBD Connection",
            color="grey",
            value=False,
            style={'marginTop': '10px'}
        ),
        html.Div(id='mode-warning', style={'color': 'orange', 'marginTop': '10px'}),
    ], style={'textAlign': 'center', 'paddingBottom': '20px'}),

    html.Div([
        html.Div([
            html.H3("Speed (km/h)"),
            daq.Gauge(id='speed', min=0, max=140, showCurrentValue=True, color="#00cc96", label="Speed")
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.H3("RPM"),
            daq.Gauge(id='rpm', min=0, max=7000, showCurrentValue=True, color="#EF553B", label="RPM")
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.H3("Coolant Temp (°C)"),
            daq.Gauge(id='coolant_temp', min=50, max=130, showCurrentValue=True, color="#636EFA", label="Coolant Temp")
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.H3("Throttle Position:"),
            daq.GraduatedBar(
                id='throttle',
                min=0,
                max=100,
                value=10,
                color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 75], "red": [75, 100]}},
                showCurrentValue=True,
                label="%",
                step=1,
                vertical=True,
                style={'height': '200px'}
            )
        ], style={'width': '10%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '20px'}),
    ], style={'display': 'flex', 'justifyContent': 'space-around'}),

    html.Div([
        html.H3("Gear Estimate:"),
        html.Div(id='gear', style={'fontSize': '40px'}),
    ], style={'textAlign': 'center'}),

    html.Div([
        dcc.Graph(id='speed-history', style={'backgroundColor': '#1e1e1e'})
    ], style={'padding': '20px'}),

    dcc.Interval(id='interval', interval=1000, n_intervals=0)
])


@app.callback(
    Output('clock', 'children'),
    Output('speed', 'value'),
    Output('rpm', 'value'),
    Output('coolant_temp', 'value'),
    Output('throttle', 'value'),
    Output('gear', 'children'),
    Output('speed-history', 'figure'),
    Output('mode-warning', 'children'),
    Output('obd-status', 'color'),      # ← חדש
    Output('obd-status', 'value'),      # ← חדש
    Input('interval', 'n_intervals'),
    State('mode', 'value')
)

def update_dashboard(n, mode):
    global current_values, speed_history
    obd_color = "grey"
    obd_value = False

    now = datetime.datetime.now().strftime("%H:%M:%S")
    warning = ""

    if mode == 'obd':
        if is_connected:
            try:
                speed = connection.query(obd.commands.SPEED).value.magnitude
                rpm = connection.query(obd.commands.RPM).value.magnitude
                temp = connection.query(obd.commands.COOLANT_TEMP).value.magnitude
                throttle = connection.query(obd.commands.THROTTLE_POS).value.magnitude
                obd_color = "green"
                obd_value = True
            except:
                speed = rpm = temp = throttle = 0
                warning = "⚠️ שגיאה בקריאת נתונים מה-OBD"
                obd_color = "orange"
                obd_value = False
        else:
            speed = rpm = temp = throttle = 0
            warning = "❌ OBD לא מחובר – מציג אפסים בלבד"
            obd_color = "red"
            obd_value = False

    else:
        speed = max(0, min(current_values["speed"] + random.uniform(-2, 2), 140))
        rpm = max(800, min(current_values["rpm"] + random.uniform(-300, 300), 7000))
        temp = max(70, min(current_values["coolant_temp"] + random.uniform(-1, 1), 130))
        throttle = max(0, min(current_values["throttle"] + random.uniform(-5, 5), 100))
        obd_color = "grey"
        obd_value = False

        current_values = {
        "speed": speed,
        "rpm": rpm,
        "coolant_temp": temp,
        "throttle": throttle
    }
    speed_history.append((datetime.datetime.now(), speed))
    if len(speed_history) > 60:
        speed_history = speed_history[-60:]

    # הילוך
    if speed < 1 and rpm > 1500:
        gear_display = "N"
    elif random.random() < 0.01:
        gear_display = "R"
    else:
        ratio = rpm / max(speed, 1)
        if ratio > 100:
            gear_display = "1"
        elif ratio > 70:
            gear_display = "2"
        elif ratio > 50:
            gear_display = "3"
        elif ratio > 30:
            gear_display = "4"
        elif ratio > 20:
            gear_display = "5"
        else:
            gear_display = "6"

    if len(speed_history) > 60:
        speed_history = speed_history[-60:]

    fig = {
        'data': [
            {
                'x': [t[0].strftime('%H:%M:%S') for t in speed_history],
                'y': [t[1] for t in speed_history],
                'type': 'line',
                'name': 'Speed',
                'line': {'color': '#00cc96'}
            }
        ],
        'layout': {
            'paper_bgcolor': '#1e1e1e',
            'plot_bgcolor': '#1e1e1e',
            'font': {'color': 'white'},
            'xaxis': {'title': 'Time'},
            'yaxis': {'title': 'Speed (km/h)', 'range': [0, 140]}
        }
    }

    # return now, round(speed, 2), round(rpm, 2), round(temp, 2), round(throttle, 2), gear_display, fig, warning
    return now, round(speed, 2), round(rpm, 2), round(temp, 2), round(throttle,
                                                                      2), gear_display, fig, warning, obd_color, obd_value


if __name__ == '__main__':
    app.run(debug=True)
