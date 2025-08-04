import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px
import random

# Generate mock data
def generate_mock_data():
    dates = pd.date_range("2025-01-01", "2025-08-01", freq="MS")
    data = {
        "Date": dates,
        "Revenue": [random.randint(800, 2000) for _ in dates],
        "Users": [random.randint(150, 300) for _ in dates],
        "Conversions": [random.randint(10, 50) for _ in dates],
    }
    return pd.DataFrame(data)

df = generate_mock_data()

# Start app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
app.title = "ADmyBRAND Insights"

# Layout
app.layout = dbc.Container([
    html.H1("ADmyBRAND Insights Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Date Range:"),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=df['Date'].min(),
                max_date_allowed=df['Date'].max(),
                start_date=df['Date'].min(),
                end_date=df['Date'].max()
            ),
        ], md=6),
        dbc.Col([
            html.Br(),
            dbc.Button("Export CSV", id="export-btn", color="info"),
            dcc.Download(id="download-dataframe-csv")
        ], md=6, className="text-end"),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dbc.Card([html.H4("Revenue"), html.H2(id="rev-card")]), md=3),
        dbc.Col(dbc.Card([html.H4("Users"), html.H2(id="user-card")]), md=3),
        dbc.Col(dbc.Card([html.H4("Conversions"), html.H2(id="conv-card")]), md=3),
        dbc.Col(dbc.Card([html.H4("Growth %"), html.H2("12%")]), md=3),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="line-chart"), md=6),
        dbc.Col(dcc.Graph(id="bar-chart"), md=6),
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="pie-chart"), md=12),
    ]),
    dcc.Interval(id="update-interval", interval=60000, n_intervals=0)  # updates every 60s
], fluid=True)

# Update visuals
@app.callback(
    Output("line-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("rev-card", "children"),
    Output("user-card", "children"),
    Output("conv-card", "children"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
    Input("update-interval", "n_intervals")
)
def update_dashboard(start_date, end_date, _):
    filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    line_fig = px.line(filtered_df, x="Date", y="Revenue", title="Revenue Over Time")
    bar_fig = px.bar(filtered_df, x="Date", y="Users", title="Users Over Time")
    pie_fig = px.pie(filtered_df, names=filtered_df["Date"].dt.strftime('%b-%Y'), values="Conversions", title="Conversion Share")
    return line_fig, bar_fig, pie_fig, f"${filtered_df['Revenue'].sum():,}", f"{filtered_df['Users'].sum():,}", f"{filtered_df['Conversions'].sum():,}"

# Export data
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-btn", "n_clicks"),
    State("date-picker", "start_date"),
    State("date-picker", "end_date"),
    prevent_initial_call=True
)
def export_csv(n_clicks, start_date, end_date):
    filtered_df = df[(df["Date"] >= pd.to_datetime(start_date)) & (df["Date"] <= pd.to_datetime(end_date))]
    return dcc.send_data_frame(filtered_df.to_csv, filename="dashboard_export.csv")

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
