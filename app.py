# -*- coding: utf-8 -*-
import math
from datetime import date, datetime
from pytz import timezone
import geojson
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


#
# Get the data
#
url = "https://raw.githubusercontent.com/cormacbon/covid19-cases-switzerland/master/covid19_cases_switzerland.csv"
# url = "C:/Users/cbon/PycharmProjects/covid19-cases-switzerland/covid19_cases_switzerland.csv"
df = pd.read_csv(url, error_bad_lines=False)

accr_categories = "https://raw.githubusercontent.com/cormacbon/covid19-cases-switzerland/master/accr_categories.csv"
# accr_categories = "C:/Users/cbon/PycharmProjects/covid19-cases-switzerland/accr_categories.csv"
df_accr_categories = pd.read_csv(accr_categories, error_bad_lines=False)

euro_2020_venues = "https://raw.githubusercontent.com/cormacbon/covid19-cases-switzerland/master/euro2020_venues.csv"
# euro_2020_venues = "C:/Users/cbon/PycharmProjects/covid19-cases-switzerland/euro2020_venues.csv"
df_euro_2020_venues = pd.read_csv(euro_2020_venues, error_bad_lines=False)
df_euro_2020_venues = df_euro_2020_venues.sort_values(by=['Venue'])

url_fatalities = "https://raw.githubusercontent.com/cormacbon/covid19-cases-switzerland/master/covid19_fatalities_switzerland.csv"
# url_fatalities = "C:/Users/cbon/PycharmProjects/covid19-cases-switzerland/covid19_fatalities_switzerland.csv"
df_fatalities = pd.read_csv(url_fatalities, error_bad_lines=False)

url_pred = "https://raw.githubusercontent.com/cormacbon/covid19-cases-switzerland/master/predicted.csv"
# url_pred = "C:/Users/cbon/PycharmProjects/covid19-cases-switzerland/predicted.csv"
df_pred = pd.read_csv(url_pred, error_bad_lines=False)

url_demo = "https://raw.githubusercontent.com/cormacbon/covid19-cases-switzerland/master/demographics.csv"
# url_demo = "C:/Users/cbon/PycharmProjects/covid19-cases-switzerland/demographics.csv"
df_demo = pd.read_csv(url_demo, error_bad_lines=False, index_col=0)

df_map = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv"
)

url_world = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
df_world = pd.read_csv(url_world)

url_world_fatalities = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
df_world_fatalities = pd.read_csv(url_world_fatalities)

#
# Load boundaries for the cantons
#
#canton_boundaries = geojson.load(open("assets/switzerland.geojson", "r"))

#
# Centres of cantons
#
centres_venues = {

    "Baku": {"lat": 40.395, "lon": 49.43},
    "Copenhagen": {"lat": 55.6711876, "lon": 12.4537421},
    "Bilbao": {"lat": 43.2633534, "lon": -2.951074},
    "Munich": {"lat": 48.155004, "lon": 11.4717963},
    "Dublin": {"lat": 53.3239919, "lon": -6.5258808},
    "London": {"lat": 51.5287718, "lon": -0.2416802},
    "Glasgow": {"lat": 55.8553807, "lon": -4.3725403},
    "Budapest": {"lat": 47.4813602, "lon": 18.9902209},
    "Bucharest": {"lat": 44.4379269, "lon": 26.024598},
    "St. Petersburg": {"lat": 59.940461, "lon": 29.8145014},
    "Rome": {"lat": 41.9102415, "lon": 12.3959153},
    "Amsterdam": {"lat": 52.3547498, "lon": 4.8339211},
    "EURO 2021": {"lat": 40.395, "lon": 49.43}
}

#
# Wrangle the data
#

accr_categories_dict = df_accr_categories.to_dict("list")
for i, j in accr_categories_dict.items():
    accr_categories_labels = j

euro_2020_venues_dict = df_euro_2020_venues.to_dict("list")

for i, j in euro_2020_venues_dict.items():
    if i == 'Venue':
        euro_2020_venues_labels = j

df_by_date = df.set_index("Date")
df_fatalities_by_date = df_fatalities.set_index("Date")
latest_date = df.iloc[len(df) - 1]["Date"]

# Get the cantons that were updated today to display below the map
cantons_updated_today = [
    canton
    for canton in df_by_date.iloc[len(df_by_date) - 1][
        df_by_date.iloc[len(df_by_date) - 1].notnull()
    ].index
]

cases_new = (
    df_by_date.diff().iloc[len(df_by_date) - 1].sum()
    - df_by_date.diff().iloc[len(df_by_date) - 1]["EURO 2021"]
)

# If a new day starts and there is no info yet, show no new cases
if date.fromisoformat(latest_date) != datetime.now(timezone("Europe/Zurich")).date():
    cases_new = 0

# Fill all the missing data by previously reported data
df_by_date = df_by_date.fillna(method="ffill", axis=0)
df_by_date_pc = df_by_date.copy()
for column in df_by_date_pc:
    df_by_date_pc[column] = (
        df_by_date_pc[column] / df_demo["Population"][column] * 10000
    )

cases_total = (
    df_by_date.iloc[len(df_by_date) - 1].sum()
    - df_by_date.iloc[len(df_by_date) - 1]["EURO 2021"]
)

fatalities_total = (
    df_fatalities_by_date.iloc[len(df_fatalities_by_date) - 1].sum()
    - df_fatalities_by_date.iloc[len(df_fatalities_by_date) - 1]["EURO 2021"]
)


# Get the data in list form and normalize it
data = df.to_dict("list")
canton_labels = [canton for canton in data if canton != "EURO 2021" and canton != "Date"]
data_norm = {
    str(canton): [
        round(i, 2) for i in data[canton] / df_demo["Population"][canton] * 10000
    ]
    for canton in data
    if canton != "Date"
}
data_norm["Date"] = data["Date"]

#
# World data
#
df_world.drop(columns=["Lat", "Long"], inplace=True)
df_world["Province/State"].fillna("", inplace=True)
df_world = df_world.rename(columns={"Country/Region": "Day"})
df_world = df_world.groupby("Day").sum()
df_world = df_world.T
df_world.drop(
    df_world.columns.difference(
        ["France", "Germany", "Italy", "Spain", "United Kingdom", "US"]
    ),
    1,
    inplace=True,
)

df_world.index = range(0, len(df_world))

# Shift the data to the start (remove leading zeros in columns)
df_world["Switzerland"] = pd.Series(data["EURO 2021"])
pop_world = {
    "France": 65273511,
    "Germany": 83783942,
    "Italy": 60461826,
    "Spain": 46754778,
    "US": 331002651,
    "United Kingdom": 67886011,
    "Switzerland": 8654622,
}

for column in df_world:
    df_world[column] = df_world[column] / pop_world[column] * 10000

df_world[df_world < 0.4] = 0
for column in df_world:
    while df_world[column].iloc[0] == 0:
        df_world[column] = df_world[column].shift(-1)
df_world.dropna(how="all", inplace=True)

#
# The predicted data
#
data_pred = df_pred.to_dict("list")
data_pred_norm = {
    str(canton): [
        round(i, 2) for i in data_pred[canton] / df_demo["Population"][canton] * 10000
    ]
    for canton in data_pred
    if canton != "Date"
}
data_pred_norm["Date"] = data_pred["Date"]

#
# Some nice differentiable colors for the cantons + EUR
#

colors = [
    "#7a8871",
    "#a359e3",
    "#91e63f",
    "#dd47ba",
    "#5ad358",
    "#6e7edc",
    "#d9dd3d",
    "#c376bc",
    "#a8cc5f",
    "#d95479",
    "#63de9f",
    "#de4f37",
    "#74deda",
    "#dd892d",
    "#71adcf",
    "#dbbd59",
    "#797ca6",
    "#4e9648",
    "#d4b7d8",
    "#8a873d",
    "#489889",
    "#b1743d",
    "#a8d5a2",
    "#a87575",
    "#d6cead",
    "#e59780",
    "#000000",
]

color_scale = [
    "#f2fffb",
    "#bbffeb",
    "#98ffe0",
    "#79ffd6",
    "#6df0c8",
    "#69e7c0",
    "#59dab2",
    "#45d0a5",
    "#31c194",
    "#2bb489",
    "#25a27b",
    "#1e906d",
    "#188463",
    "#157658",
    "#11684d",
    "#10523e",
]

theme = {"background": "#252e3f", "foreground": "#4bbdcf", "accent": "#7fafdf"}

#
# General app settings
#
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "ACCR Stats"

rows = [
    'Broadcast Partner - RADIO', 'Broadcast Partner - TV', 'COMMERCIAL PARTNERS / HOST CITIES',
    'HB', 'MEDIA', 'PNA MEDIA', 'NRH', 'ORG', 'RESIDENTS', 'SAFETY & SECURITY', 'Stewards',
    'Public Authority Passes', 'TEAMS', 'VOLUNTEERS', 'SERVICE & SUPPLIERS', 'Stadium', 'Ceremonies',
    'Catering', 'Transport', 'Hospitality'
]
columns = [
    'Tournament Pass', '2PP', 'Setup Pass', 'Resident Pass', 'OC Pass', 'CC Pass'
]
#
# Show the data
#

app.layout = html.Div(
    id="main",
    children=[
        html.H4(children="Accreditation Stats - Per Venue"),
        html.Div(
            id="header",
            children=[
                #html.H4(children="Accreditations Stats - Per Venue"),
                html.P(
                    id="description",
                    children=[
                        dcc.Markdown(
                            """
                        Number of accreditations delivered, broken down by category 
                        Data source is a CSV table, could be app in future (ERT)
                        """
                        )
                    ],
                ),
            ],
        ),
        html.H4(children="Select Venue"),
        html.Div(
            children=[
                # html.P(
                #     className="total-title", children="Venue Selector"
                # ),
                # html.H4(children="Select Venue"),
                dcc.Dropdown(
                    id="dropdown-venues",
                    options=[
                        {"label": venue, "value": venue} for venue in euro_2020_venues_labels
                    ],
                    #value=euro_2020_venues_labels,
                    multi=True,
                ),
            ],
        ),

        dcc.Tabs(id="tabs-example", value='tab-1-example', parent_className='custom-tabs', className='custom-tabs-container', children=[
            dcc.Tab(className="tab-content", selected_className='custom-tab--selected', label='Cockpit', value='tab-1-example', children=[
                html.Div(id='tabs-content-example'),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="twelve columns",
                                children=[
                                    html.Div(
                                        className="total-container",
                                        children=[
                                            html.P(className="total-title", children="Total Delivered"),
                                            html.Div(id='total_cases', className="total-content", children=str(int(cases_total)),),
                                        ],
                                    ),
                                    html.Div(
                                        className="total-container",
                                        children=[
                                            html.P(
                                                className="total-title", children="New Requests Today"
                                            ),
                                            html.Div(id='total_new_requests', className="total-content", children="+" + str(int(cases_new)),
                                            ),
                                        ],
                                    ),
                                    html.Div(
                                        className="total-container",
                                        children=[
                                            html.P(
                                                className="total-title", children="Total to Deliver (%)"
                                            ),
                                            html.Div(id='total_to_deliver', className="total-content", children=str(int(fatalities_total)),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            html.Div(className="six columns"),
                            html.Div(className="six columns"),
                        ],
                    ),
                    html.Br(),
                    html.Div(
                        id="slider-container",
                        children=[
                            html.P(
                                id="slider-text", children="Drag the slider to change the date:",
                            ),
                            dcc.Slider(
                                id="slider-date",
                                min=0,
                                max=len(df["Date"]) - 1,
                                marks={i: d for i, d in enumerate(df["Date"])},
                                value=len(df["Date"]) - 1,
                            ),
                            html.Br(),
                            dcc.RadioItems(
                                id="radio-prevalence",
                                options=[
                                    {"label": "Delivered", "value": "number"},
                                    {"label": "To be delivered", "value": "prevalence"},
                                    {"label": "Total", "value": "fatalities"},
                                ],
                                value="number",
                                labelStyle={
                                    "display": "inline-block",
                                    "color": theme["foreground"],
                                },
                            ),
                        ],
                    ),
                    html.Div(children=[dcc.Graph(id="graph-map", config={"staticPlot": True},),]),
                    html.Div(
                        children=[
                            "Cantons updated today: ",
                            html.Span(", ".join(cantons_updated_today)),
                        ]
                    ),
                    html.Br(),
                    html.H4(id='dd-output-container', children="Data for Venue" + str(Input("dropdown-venues", "value")), style={"color": theme["accent"]}),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="six columns", children=[dcc.Graph(id="case-ch-graph")]
                            ),
                            html.Div(
                                className="six columns",
                                children=[dcc.Graph(id="case-world-graph")],
                            ),
                        ],
                    ),
                    # html.Div(
                    #     className="row",
                    #     children=[
                    #         html.Div(
                    #             className="six columns",
                    #             children=[dcc.Graph(id="fatalities-ch-graph")],
                    #         ),
                    #         html.Div(
                    #             className="six columns",
                    #             children=[dcc.Graph(id="fatalities-world-graph")],
                    #         ),
                    #     ],
                    # ),
                    html.Br(),
                    html.H4(children="Data per Venue", style={"color": theme["accent"]}),
                    html.Div(
                        id="plot-settings-container",
                        children=[
                            html.P(
                                id="plot-settings-text",
                                children="Select scale and cantons to show in the plots:",
                            ),
                            dcc.RadioItems(
                                id="radio-scale",
                                options=[
                                    {"label": "Linear Scale", "value": "linear"},
                                    {"label": "Logarithmic Scale", "value": "log"},
                                ],
                                value="linear",
                                labelStyle={
                                    "display": "inline-block",
                                    "color": theme["foreground"],
                                },
                            ),
                            html.Br(),
                            dcc.Dropdown(
                                id="dropdown-cantons",
                                options=[
                                    {"label": canton, "value": canton} for canton in canton_labels
                                ],
                                value=canton_labels,
                                multi=True,
                            ),
                        ],
                    ),
                    html.Br(),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="six columns", children=[dcc.Graph(id="case-graph")]
                            ),
                            html.Div(
                                className="six columns", children=[dcc.Graph(id="case-pc-graph"),],
                            ),
                        ],
                    ),
                    html.Br(),
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="twelve columns",
                                children=[dcc.Graph(id="case-graph-diff")],
                            ),
                        ],
                    ),
                    html.Br(),
                    # html.H4(
                    #     children="Interpolated and Predicted Data", style={"color": theme["accent"]}
                    # ),
                    # html.Div(
                    #     className="row",
                    #     children=[
                    #         html.Div(
                    #             className="six columns", children=[dcc.Graph(id="case-graph-pred")]
                    #         ),
                    #         html.Div(
                    #             className="six columns",
                    #             children=[dcc.Graph(id="case-pc-graph-pred"),],
                    #         ),
                    #     ],
                    # ),
                    html.H4(children="Raw Data", style={"color": theme["accent"]}),
                    dash_table.DataTable(
                        id="table",
                        columns=[{"name": i, "id": i} for i in df.columns],
                        data=df.to_dict("records"),
                    ),
                    html.H4(children="Raw Data (Predicted)", style={"color": theme["accent"]}),
                    dash_table.DataTable(
                        id="table_pred",
                        columns=[{"name": i, "id": i} for i in df_pred.columns],
                        data=df_pred.to_dict("records"),
                    ),

            ]),
            dcc.Tab(className="tab-content", selected_className='custom-tab--selected', label='Data Entry', value='tab-2-example', children=[
                dash_table.DataTable(
                    id='table-editing-simple',
                    columns=([
                        {"name": ["", "Category"], "id": "category", "clearable": "first"},
                        {"name": ["Delivered", "Tournament Pass"], "id": "delivered_tournament_pass", "deletable": [False, True]},
                        {"name": ["Delivered", "2PP"], "id": "delivered_2pp", "renamable": True },
                        {"name": ["Delivered", "Setup Pass"], "id": "delivered_setup_pass", "hideable": "last"},
                        {"name": ["Delivered", "Resident Pass"], "id": "delivered_resident_pass", "clearable": True, "renamable": True, "hideable": True, "deletable": True },
                        {"name": ["Delivered", "OC Pass"], "id": "delivered_oc_pass", "clearable": True, "renamable": True, "hideable": True, "deletable": True },
                        {"name": ["Delivered", "CC Pass"], "id": "delivered_cc_pass", "clearable": True, "renamable": True, "hideable": True, "deletable": True },
                        {"name": ["Still to deliver", "Tournament Pass"], "id": "to_deliver_tournament_pass", "deletable": [False, True]},
                        {"name": ["Still to deliver", "2PP"], "id": "to_deliver_2pp", "renamable": True },
                        {"name": ["Still to deliver", "Setup Pass"], "id": "to_deliver_setup_pass", "hideable": "last"},
                        {"name": ["Still to deliver", "Resident Pass"], "id": "to_deliver_resident_pass", "clearable": True, "renamable": True, "hideable": True, "deletable": True },
                        {"name": ["Still to deliver", "OC Pass"], "id": "to_deliver_oc_pass", "clearable": True, "renamable": True, "hideable": True, "deletable": True },
                        {"name": ["Still to deliver", "CC Pass"], "id": "to_deliver_cc_pass", "clearable": True, "renamable": True, "hideable": True, "deletable": True }
                        ]
                    ),
                    # data=[
                    #     dict(Model=i, **{column: 0 for column in columns})
                    #     for i in range(1, )
                    # ],
                    data=[
                        {
                            "category": i,
                        }
                        for i in accr_categories_labels
                    ],
                    editable=True
                )
            ]),

        ]),
    ],
)

# -------------------------------------------------------------------------------
# Callbacks
# -------------------------------------------------------------------------------
# @app.callback(
#     Output('table-editing-simple-output', 'figure'),
#     [Input('table-editing-simple', 'data'),
#      Input('table-editing-simple', 'columns')])
# def display_output(rows, columns):
#     df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
#     return {
#         'data': [{
#             'type': 'parcoords',
#             'dimensions': [{
#                 'label': col['name'],
#                 'values': df[col['id']]
#             } for col in columns]
#         }]
#     }
# @app.callback(Output('tabs-content-example', 'children'),
#               [Input('tabs-example', 'value')])
# def render_content(tab):
#     if tab == 'tab-2-example':
#         return html.Div([
#             html.H3('Data entry'),
#             dash_table.DataTable(
#                 id='table-editing-simple',
#                 columns=(
#                         [{'id': 'Model', 'name': 'Model'}] +
#                         [{'id': p, 'name': p} for p in params]
#                 ),
#                 data=[
#                     dict(Model=i, **{param: 0 for param in params})
#                     for i in range(1, 5)
#                 ],
#                 editable=True
#             ),
#             #dcc.Graph(id='table-editing-simple-output')
#         ])
#     elif tab == 'tab-2-example':
#         return html.Div([
#             html.H3('Tab content 2'),
#             # dcc.Graph(
#             #     id='graph-2-tabs',
#             #     figure={
#             #         'data': [{
#             #             'x': [1, 2, 3],
#             #             'y': [5, 10, 6],
#             #             'type': 'bar'
#             #         }]
#             #     }
#             # )
#         ])

@app.callback(
    Output('dd-output-container', 'children'),
    [dash.dependencies.Input('dropdown-venues', 'value')])
def update_output(value):
    return 'Data for venue "{}"'.format(value)

@app.callback(
    [Output("total_cases", "children"), Output("total_new_requests", "children"), Output("total_to_deliver", "children")],
    [Input("slider-date", "value"), Input("dropdown-venues", "value")],
)
def update_totals_boxes(selected_date_index, selected_venues):
    date = df["Date"].iloc[selected_date_index]
    #date_cases_new = df["Date"].iloc[selected_date_index]
    cases_total = 0
    cases_new = 0
    fatalities_total = 0

    for venue in selected_venues:
        cases_total = cases_total + int(df_by_date[venue][date])
        #cases_new = cases_new + int(df_by_date[venue][date])
        fatalities_total = fatalities_total + int(df_fatalities_by_date[venue][date])

    return cases_total, cases_new, fatalities_total

@app.callback(
    Output("graph-map", "figure"),
    [Input("slider-date", "value"), Input("radio-prevalence", "value"), Input("dropdown-venues", "value")],
)
def update_graph_map(selected_date_index, mode, selected_venues):
    date = df["Date"].iloc[selected_date_index]
    if selected_venues is None:
        selected_venues = centres_venues
        labelz = canton_labels
    elif selected_venues is not None:
        labelz = selected_venues

    temp_dict = {}
    new_dict = {}
    for venue in selected_venues:
        for i, j in euro_2020_venues_dict.items():
            if venue in j:
                num = (j.index(venue))
                temp_dict = {'lat': euro_2020_venues_dict['lat'][num], 'lon': euro_2020_venues_dict['lon'][num]}
                new_dict[venue] = temp_dict


    selected_venues = new_dict

    map_data = df_by_date
    labels = [
        venue + ": " + str(int(map_data[venue][date])) for venue in selected_venues
    ]

    if mode == "prevalence":
        map_data = df_by_date_pc
        labels = [
            venue + ": " + str(round((map_data[venue][date]), 1))
            for venue in selected_venues
        ]
    elif mode == "fatalities":
        map_data = df_fatalities_by_date
        labels = [
            venue + ": " + str(int(map_data[venue][date]))
            if not math.isnan(float(map_data[venue][date]))
            else ""
            for venue in selected_venues
        ]

    return {
        "data": [
            {
                "lat": [selected_venues[venue]["lat"] for venue in selected_venues],
                "lon": [selected_venues[venue]["lon"] for venue in selected_venues],
                "text": labels,
                "mode": "text",
                "type": "scattermapbox",
                "textfont": {
                    "family": "sans serif",
                    "size": 18,
                    "color": "white",
                    "weight": "bold",
                },
            },
            {
                "type": "choroplethmapbox",
                "locations": labelz, #canton_labels,
                "z": [map_data[canton][date] for canton in map_data if canton != "EURO 2021"],
                "colorscale": [(0, "#007aBc"), (1, "#4bbdcf")],
                "geojson": "/assets/europe5.geojson",
                "marker": {"line": {"width": 0.0, "color": "#08302A"}},
                "colorbar": {
                    "thickness": 10,
                    "bgcolor": "#1f2630",
                    "tickfont": {"color": "white"},
                },
            },
        ],
        "layout": {
            "mapbox": {
                "accesstoken": "pk.eyJ1IjoiZGFlbnVwcm9ic3QiLCJhIjoiY2s3eDR2dmRyMDg0ajN0cDlkaDNmM3J0NyJ9.tcJPFQkbsVGlWpyQaKPtiw",
                "style": "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz",
                "center": {"lat": 50.00, "lon": 20.00},
                "pitch": 0,
                "zoom": 3.2,
            },
            "margin": {"l": 0, "r": 0, "t": 0, "b": 0},
            "height": 600,
            "plot_bgcolor": "#1f2630",
            "paper_bgcolor": "#1f2630",
        },
    }


#
# Total cases Switzerland
#
@app.callback(
    Output("case-ch-graph", "figure"), [Input("radio-scale", "value")],
)
def update_case_ch_graph(selected_scale):
    return {
        "data": [
            {
                "x": data["Date"],
                "y": data["EURO 2021"],
                "name": "EURO 2021",
                "marker": {"color": theme["foreground"]},
                "type": "bar",
            }
        ],
        "layout": {
            "title": "Total Delivered",
            "height": 400,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {
                "type": selected_scale,
                "showgrid": True,
                "color": "#ffffff",
                "rangemode": "tozero",
            },
            "plot_bgcolor": theme["background"],
            "paper_bgcolor": theme["background"],
            "font": {"color": theme["foreground"]},
        },
    }


# @app.callback(
#     Output("fatalities-ch-graph", "figure"), [Input("radio-scale", "value")],
# )
# def update_fatalities_ch_graph(selected_scale):
#     return {
#         "data": [
#             {
#                 "x": df_fatalities["Date"],
#                 "y": df_fatalities["EURO 2021"],
#                 "name": "EURO 2021",
#                 "marker": {"color": theme["foreground"]},
#                 "type": "bar",
#             }
#         ],
#         "layout": {
#             "title": "Total Fatalities Switzerland",
#             "height": 400,
#             "xaxis": {"showgrid": True, "color": "#ffffff"},
#             "yaxis": {
#                 "type": selected_scale,
#                 "showgrid": True,
#                 "color": "#ffffff",
#                 "rangemode": "tozero",
#             },
#             "plot_bgcolor": theme["background"],
#             "paper_bgcolor": theme["background"],
#             "font": {"color": theme["foreground"]},
#         },
#     }


#
# Total cases world
#
@app.callback(
    Output("case-world-graph", "figure"), [Input("radio-scale", "value")],
)

def update_case_world_graph(selected_scale):
    return {
        "data": [
            {
                "x": df_world.index.values,
                "y": df_world[country],
                "name": country,
                # "marker": {"color": theme["foreground"]},
                # "type": "bar",
            }
            for country in df_world
            if country != "Day"
        ],
        "layout": {
            "title": "Per venue timeline",
            "height": 400,
            "xaxis": {
                "showgrid": True,
                "color": "#ffffff",
                "title": "No. of requests per Venue",
            },
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff",},
            "plot_bgcolor": theme["background"],
            "paper_bgcolor": theme["background"],
            "font": {"color": theme["foreground"]},
        },
    }


#
# Cantonal Data
#
@app.callback(
    Output("case-graph", "figure"),
    [Input("dropdown-cantons", "value"), Input("radio-scale", "value")],
)
def update_case_graph(selected_cantons, selected_scale):
    return {
        "data": [
            {
                "x": data["Date"],
                "y": data[canton],
                "name": canton,
                "marker": {"color": colors[i - 1]},
            }
            for i, canton in enumerate(data)
            if canton in selected_cantons
        ],
        "layout": {
            "title": "Delivered per Venue",
            "height": 750,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
            "plot_bgcolor": theme["background"],
            "paper_bgcolor": theme["background"],
            "font": {"color": theme["foreground"]},
        },
    }


@app.callback(
    Output("case-pc-graph", "figure"),
    [Input("dropdown-cantons", "value"), Input("radio-scale", "value")],
)
def update_case_pc_graph(selected_cantons, selected_scale):
    return {
        "data": [
            {
                "x": data_norm["Date"],
                "y": data_norm[canton],
                "name": canton,
                "marker": {"color": colors[i - 1]},
            }
            for i, canton in enumerate(data)
            if canton in selected_cantons
        ],
        "layout": {
            "title": "To be Delivered per Venue",
            "height": 750,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
            "plot_bgcolor": theme["background"],
            "paper_bgcolor": theme["background"],
            "font": {"color": theme["foreground"]},
        },
    }


@app.callback(
    Output("case-graph-diff", "figure"),
    [Input("dropdown-cantons", "value"), Input("radio-scale", "value")],
)
def update_case_graph_diff(selected_cantons, selected_scale):
    return {
        "data": [
            {
                "x": data["Date"],
                "y": [0] + [j - i for i, j in zip(data[canton][:-1], data[canton][1:])],
                "name": canton,
                "marker": {"color": colors[i - 1]},
                "type": "bar",
            }
            for i, canton in enumerate(data)
            if canton in selected_cantons
        ],
        "layout": {
            "title": "New Requests per Venue",
            "height": 750,
            "xaxis": {"showgrid": True, "color": "#ffffff"},
            "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
            "plot_bgcolor": theme["background"],
            "paper_bgcolor": theme["background"],
            "font": {"color": theme["foreground"]},
            "barmode": "stack",
        },
    }


# #
# # Predictions: cases per canton
# #
# @app.callback(
#     Output("case-graph-pred", "figure"),
#     [Input("dropdown-cantons", "value"), Input("radio-scale", "value")],
# )
# def update_case_graph_pred(selected_cantons, selected_scale):
#     return {
#         "data": [
#             {
#                 "x": data_pred["Date"],
#                 "y": data_pred[canton],
#                 "name": canton,
#                 "marker": {"color": colors[i - 1]},
#             }
#             for i, canton in enumerate(data_pred)
#             if canton in selected_cantons
#         ],
#         "layout": {
#             "title": "Cases per Canton",
#             "height": 750,
#             "xaxis": {"showgrid": True, "color": "#ffffff"},
#             "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
#             "plot_bgcolor": theme["background"],
#             "paper_bgcolor": theme["background"],
#             "font": {"color": theme["foreground"]},
#         },
#     }


# #
# # Predictions: cases per canton (per 10'000 inhabitants)
# #
# @app.callback(
#     Output("case-pc-graph-pred", "figure"),
#     [Input("dropdown-cantons", "value"), Input("radio-scale", "value")],
# )
# def update_case_pc_graph_pred(selected_cantons, selected_scale):
#     return {
#         "data": [
#             {
#                 "x": data_pred_norm["Date"],
#                 "y": data_pred_norm[canton],
#                 "name": canton,
#                 "marker": {"color": colors[i - 1]},
#             }
#             for i, canton in enumerate(data_pred)
#             if canton in selected_cantons
#         ],
#         "layout": {
#             "title": "Cases per Canton (per 10,000 Inhabitants)",
#             "height": 750,
#             "xaxis": {"showgrid": True, "color": "#ffffff"},
#             "yaxis": {"type": selected_scale, "showgrid": True, "color": "#ffffff"},
#             "plot_bgcolor": theme["background"],
#             "paper_bgcolor": theme["background"],
#             "font": {"color": theme["foreground"]},
#         },
#    }


if __name__ == "__main__":
    app.run_server(
        # debug=True,
        # dev_tools_hot_reload=True,
        # dev_tools_hot_reload_interval=50,
        # dev_tools_hot_reload_max_retry=30,
    )
