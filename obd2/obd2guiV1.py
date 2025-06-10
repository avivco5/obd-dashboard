import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_daq as daq
import random
import datetime


current_values = {
    "speed": 0,
    "rpm": 800,
    "coolant_temp": 70,
    "throttle": 10,
}

app = dash.Dash(__name__)
app.title = "OBD2 Dashboard"

app.layout = html.Div(style={'backgroundColor': '#1e1e1e', 'color': 'white', 'fontFamily': 'Arial', 'padding': '20px'}, children=[

    html.H1("OBD2 Dashboard", style={'textAlign': 'center'}),
    html.Div(id='clock', style={'textAlign': 'center', 'fontSize': '32px', 'marginBottom': '30px'}),

    html.Div(style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}, children=[
        # שלושת העיגולים
        html.Div(style={'display': 'flex', 'gap': '40px'}, children=[
            daq.Gauge(id='speed', min=0, max=140, showCurrentValue=True, color="#00cc96", label="Speed (km/h)"),
            daq.Gauge(id='rpm', min=0, max=7000, showCurrentValue=True, color="#EF553B", label="RPM"),
            daq.Gauge(id='coolant_temp', min=50, max=130, showCurrentValue=True, color="#636EFA", label="Coolant Temp"),
        ]),

        # בר אנכי של דוושת הגז
        html.Div([
            daq.GraduatedBar(
                id='throttle',
                min=0,
                max=100,
                value=10,
                vertical=True,  # ✅ נתמך בגרסה שלך
                color={"gradient": True, "ranges": {"green": [0, 50], "yellow": [50, 75], "red": [75, 100]}},
                showCurrentValue=True,
                label="Throttle %",
                step=1,
                size=220
            )

        ], style={'marginLeft': '60px'})
    ]),

    html.Div([
        html.H3("Gear Estimate:", style={'textAlign': 'center', 'marginTop': '40px'}),
        html.Div(id='gear', style={'fontSize': '40px', 'textAlign': 'center'}),
    ]),

    dcc.Interval(id='interval', interval=1000, n_intervals=0)
])
@app.callback(
    Output('clock', 'children'),
    Output('speed', 'value'),
    Output('rpm', 'value'),
    Output('coolant_temp', 'value'),
    Output('throttle', 'value'),
    Output('gear', 'children'),
    Input('interval', 'n_intervals')
)
def update_dashboard(n):
    now = datetime.datetime.now().strftime("%H:%M:%S")

    # ערכים חדשים רנדומליים (יעד)
    target_speed = random.uniform(0, 120)
    target_rpm = random.uniform(800, 5000)
    target_temp = random.uniform(70, 100)
    target_throttle = random.uniform(10, 80)

    # קצב התקרבות (ככל שקרוב ל-1 זה יותר חלק)
    smoothing_factor = 0.1

    # החלקה בין ערכים
    current_values["speed"] += (target_speed - current_values["speed"]) * smoothing_factor
    current_values["rpm"] += (target_rpm - current_values["rpm"]) * smoothing_factor
    current_values["coolant_temp"] += (target_temp - current_values["coolant_temp"]) * smoothing_factor
    current_values["throttle"] += (target_throttle - current_values["throttle"]) * smoothing_factor

    # חישוב הילוך
    # תנאים לרברס / ניוטרל
    if current_values["speed"] < 1 and current_values["rpm"] > 1500:
        gear_display = "N"  # ניוטרל
    elif random.random() < 0.01:
        gear_display = "R"  # סימולציה רנדומלית לרברס (לבדיקה)
    else:
        gear_ratio = current_values["speed"] / current_values["rpm"]
        gear = round(gear_ratio * 20)
        gear_display = str(max(1, min(gear, 6)))  # הילוכים 1–6 בלבד

    return (
        now,
        round(current_values["speed"], 2),
        round(current_values["rpm"], 2),
        round(current_values["coolant_temp"], 2),
        round(current_values["throttle"], 2),
        gear_display  # ✅ מחזיר R / N / 1–6
    )


# Run
if __name__ == '__main__':
    app.run(debug=True)
