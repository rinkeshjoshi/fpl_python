# -*- coding: utf-8 -*-
"""
@author: Rineksh Joshi 
and other info project details, institute and course details and student id
"""

# import all the packages
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components

# list of Fantsay Premier League API Endpoints:
# General Information: https://fantasy.premierleague.com/api/bootstrap-static/
# Fixtures: https://fantasy.premierleague.com/api/fixtures/
# Player's detailed Data: https://fantasy.premierleague.com/api/element-summary/{element_id}/
# Game Week specific Data (Current Active Season): https://fantasy.premierleague.com/api/event/{event_id}/live/
# Manager Information Active Gameweek: https://fantasy.premierleague.com/api/entry/{manager_id}/
# Manager's Information Past Gameweeks and Past Seasons: https://fantasy.premierleague.com/api/entry/{manager_id}/history/
# Manager's Information And Gameweek: https://fantasy.premierleague.com/api/entry/{manager_id}/event/{event_id}/picks/
# Dream Team for Gameweek: https://fantasy.premierleague.com/api/dream-team/{event_id}/
# event_id: Gameweek and manager_id: Manager ID/Team ID

# accessing player data using API url
# get basic gameweek information: average score, highest score,
url_basic_gameweek = "https://fantasy.premierleague.com/api/bootstrap-static/"


def url_manager_gameweek(manager_id, gameweek_id):
    '''
    A function that returns the url to access data of manager_id for the active gameweek
    '''
    return("https://fantasy.premierleague.com/api/entry/"+manager_id+"/event/"+str(gameweek_id)+"/picks/")


def user_details():
    '''
    A function to print user details such as Team Name, Participating Country, Previous Season Rank using manager_id
    Returns
    -------
    None.
    '''
    request_url_basic_gameweek = requests.get(url_basic_gameweek)
    json_basic_gameweek = request_url_basic_gameweek.json()
    player_count_df = (json_basic_gameweek["total_players"])
    
    request_url_manager_history = requests.get("https://fantasy.premierleague.com/api/entry/"+manager_id+"/")
    json_manager_history = request_url_manager_history.json()
    # user_info_df = pd.DataFrame(json_manager_history["started_event", "player_region_name", "name"])
    
    st.markdown("-----")
    st.markdown("***Your Team Name: ***"+str(json_manager_history["name"]))
    st.markdown("***Participating Country: ***"+str(json_manager_history["player_region_name"])+" | ***You started in Gameweek: ***"+str(json_manager_history["started_event"]))
    st.markdown("***Total Number of FPL players: ***"+str(json_basic_gameweek["total_players"]))
    st.markdown("-----")
    st.markdown("### Your Performance Breakdown:")
    
def display_graphs():
    ''' 
    A function to generate various graphs
    Returns
    -------
    None.
    '''
    # get user specific information for active & previous gameweeks of the current season and past seasons of FPL
    url_manager_history = str("https://fantasy.premierleague.com/api/entry/"+manager_id+"/history/")
    
    # display a line graph comparing manger_id's total points vs average total points for the avtive season
    # using the requests package to make a GET request from the API endpoint:
    request_url_basic_gameweek = requests.get(url_basic_gameweek)
    request_url_manager_history = requests.get(url_manager_history)
    
    # transforing requests into a JSON object
    json_basic_gameweek = request_url_basic_gameweek.json()
    json_manager_history = request_url_manager_history.json()
    
    # required data:
    #   Points in a Gameweek, Average Points in a Gameweek
    #   Captain Points in a Gameweek
    #   Rank in a Gameweek, Overall Rank
    
    #-------------------------------------------------------------------------------------------------------------#
    
    # Building DataFrames from API request responses
    # we are only interested in the 'events' key of json_basic_gameweek object
    # evnts_df contains the average points of each gameweek
    events_df = pd.DataFrame(json_basic_gameweek["events"])
    
    # saving the average score of each gameweek in a slimmed down events_df
    # events_df_avergae_score is a DataFrame: {0:69, 1:55,...,37:0}
    events_df_average_score = events_df[["id", "average_entry_score"]]
    #removing the future gameweeks with value O
    events_df_average_score = events_df_average_score.loc[events_df_average_score["average_entry_score"] != 0]
    
    # similarly for gameweek specific score of manager_id
    currentGW_manager_df = pd.DataFrame(json_manager_history["current"])
    currentGW_manager_df_score = currentGW_manager_df[["event", "points"]]
    currentGW_manager_df_score.rename(columns={"event" : "id"}, inplace=True)
    
    #combining into a single dataframe
    events_df_average_score ["points"] = currentGW_manager_df_score["points"]
    
    # creating a line graph using plotly
    
    # # Points_figure = px.line(events_df_average_score, x = range(1,39), y = 
    # Points_figure = px.line(events_df_average_score, x="id", y=events_df_average_score.columns[1:],labels ={"id":"Game Week"}, markers=True, title = "Points")
    # Points_figure.update_traces({"line":{"color":"Blue"}}, marker = dict(size=12, line=dict(width=2, color='DarkSlateGrey')), marker_symbol = "circle-dot", marker_color = "lightBlue")
    # st.plotly_chart(Points_figure, use_container_width=True)
    
    Points_figure = go.Figure()
    # Create and style traces
    Points_figure.add_trace(go.Line(x = events_df_average_score["id"], y = events_df_average_score["average_entry_score"], name = "Average Scores", line = dict(color = "firebrick", width = 4),mode="lines+markers", marker_symbol="circle", marker_line_color="midnightblue", marker_color="lightskyblue", marker_line_width=2))
    Points_figure.add_trace(go.Line(x = events_df_average_score["id"], y = events_df_average_score["points"], name = "Score", line = dict(color = "royalblue", width =4), mode="lines+markers", marker_symbol="circle", marker_line_color="firebrick", marker_color="pink", marker_line_width=2))
    
    # edit the layout
    Points_figure.update_layout(title = "Average Score vs Your Score", xaxis_title = "Gameweek", yaxis_title = "Score")
    st.plotly_chart(Points_figure, use_container_width=True)
    
    #-------------------------------------------------------------------------------------------------------------#
    
    # display graph #2 Change in Rank Gameweek vs Overall
    rank_df = pd.DataFrame(json_manager_history["current"])
    rank_df = rank_df[["event", "rank", "overall_rank"]]
    
    Rank_figure = go.Figure()
    # Create and style traces
    Rank_figure.add_trace(go.Line(x = rank_df["event"], y = rank_df["rank"], name = "Gameweek Rank", line = dict(color = "#ff7f0e", width = 4), mode = "lines+markers", marker_symbol = "circle", marker_line_color = "royalblue", marker_color = "#17becf", marker_line_width = 2))
    Rank_figure.add_trace(go.Line(x = rank_df["event"], y = rank_df["overall_rank"], name = "Overall Rank", line = dict(color = "#1f77b4", width = 4), mode = "lines+markers", marker_symbol = "circle", marker_line_color = "firebrick", marker_color = "pink", marker_line_width = 2))
    
    # edit the layout
    Rank_figure.update_layout(title = "Overall Rank vs Gameweek Rank", xaxis_title = "Gameweek", yaxis_title = "Rank")
    st.plotly_chart(Rank_figure, use_container_width=True)
    
    #-------------------------------------------------------------------------------------------------------------#
    
    # display graph #3 Captain Points per Gameweek
    

def display_tables():
    '''
    A function to creates and display interactive tables using plotly

    Returns
    -------
    None.
    '''
    # get user specific information for active & previous gameweeks of the current season and past seasons of FPL
    url_manager_history = str("https://fantasy.premierleague.com/api/entry/"+manager_id+"/history/")
    request_url_manager_history = requests.get(url_manager_history)
    json_manager_history = request_url_manager_history.json()
    
    # Rank averages table #1
    ranks_df = pd.DataFrame(json_manager_history["current"])
    ranks_df = ranks_df[["points", "rank", "overall_rank"]]
    
    # current_rank = ranks_df.iloc[-1:, [2]]  last entry in the overall_rank column
    values = [["Current Rank", "Lowest Gameweek Rank", "Highest Gameweek Rank", "Average Gameweek Rank", "Highest Gameweek Score", "Lowest Gameweek Score"],
              [ranks_df.iloc[-1:, [2]], ranks_df["rank"].min(), ranks_df["rank"].max(), (ranks_df["rank"].mean().round()), ranks_df["points"].max(), ranks_df["points"].min()]]
    
    st.markdown("### Your Rank and Averages: ")
    Ranks_table = go.Figure(data=[go.Table(header=dict(values=["Title", "Rank and Score Averages"], line_color='darkslategray', fill_color='royalblue', align='center', font = dict(color = "white", size=20), height=40), cells=dict(values=values, line_color='darkslategray', fill_color='lightcyan', align='left', font = dict(color = "black", size=18), height=38))])
    st.plotly_chart(Ranks_table, use_container_width=True)
    
    #-------------------------------------------------------------------------------------------------------------#
    
    # # Captain points breakdown table #2
    # list_captains = []
    # for i in range(1,39):
    #     url_captain_gw = url_manager_gameweek(manager_id,i)
    #     request_captain_gw = requests.get(url_captain_gw)
    #     json_captain_gw = request_captain_gw.json()
        
    #     # dataframe from json
    #     captain_df = pd.DataFrame(json_captain_gw["picks"])
    #     captain_df = (captain_df.loc[captain_df["multiplier"] >= 2]) 
    #     list_captains.append(captain_df["element"].tolist()[0])
    
    # for i in list_captains:
    #     url_player_data = "https://fantasy.premierleague.com/api/bootstrap-static/"
    #     request_player_data = requests.get(url_player_data)
    #     json_player_data = request_player_data.json()
    #     player_df = pd.DataFrame(json_player_data["elements"])
    #     player_df = player_df["id", "web_name", "event_points"]
    #     if()
        
    # Just general idea about players # table 2
    url_player_data = "https://fantasy.premierleague.com/api/bootstrap-static/"
    request_player_data = requests.get(url_player_data)
    json_player_data = request_player_data.json()

    player_df = pd.DataFrame(json_player_data["elements"])
    player_df = player_df[["web_name", "event_points", "bonus", "ict_index_rank", "total_points", "points_per_game", "selected_by_percent"]]
    # print(player_df.head())
    player_df = player_df.sort_values("total_points", ascending= False)
    
    values = [player_df["web_name"], player_df["bonus"], player_df["ict_index_rank"], player_df["total_points"], player_df["points_per_game"], player_df["selected_by_percent"]]

    Player_details_table = go.Figure(data=[go.Table(header=dict(values=["Player Name", "Total Bonus Points", "ICT Index Rank (Lower is better)", "Total Points", "Points Per Game", "% Selected by users"], line_color='darkslategray', fill_color='royalblue', align='center', font = dict(color = "white", size=18), height=38), cells=dict(values=values, line_color='darkslategray', fill_color='lightcyan', align='left', font = dict(color = "black", size=18), height=38))])
    Player_details_table.update_layout(width=1200, height=1000)
    
    st.markdown("### Player Performance Details (Scroll for more information): (Arranged by Total Score!)")
    st.plotly_chart(Player_details_table, use_container_width=True)
    
    # Table for positional summary
    position_df = pd.DataFrame(json_player_data["element_types"])
    position_df = position_df[["element_count", "plural_name"]]
    
    values = [position_df["plural_name"], position_df["element_count"]]
    
    st.markdown("### Player Positional Details: ")
    position_table = go.Figure(data=[go.Table(header=dict(values=["Position", "Total Players"], line_color='darkslategray', fill_color='royalblue', align='center', font = dict(color = "white", size=20), height=40), cells=dict(values=values, line_color='darkslategray', fill_color='lightcyan', align='left', font = dict(color = "black", size=18), height=38))])
    st.plotly_chart(position_table, use_container_width=True)
    
    #-------------------------------------------------------------------------------------------------------------#
    
    # Total Transfers and Hit Points table #3
    transfers_df = pd.DataFrame(json_manager_history["current"])
    transfers_df = transfers_df[["event_transfers","event_transfers_cost"]]
    
    values = [["Total Transfers Made", "Hits incurred(-)"], [transfers_df["event_transfers"].sum(), transfers_df["event_transfers_cost"].sum()]]

    Transfers_table = go.Figure(data=[go.Table(header=dict(values=["Title", "Transfer Summary"], line_color='darkslategray', fill_color='royalblue', align='center', font = dict(color = "white", size=20), height=40), cells=dict(values=values, line_color='darkslategray', fill_color='lightcyan', align='left', font = dict(color = "black", size=18), height=38))])
    st.markdown("### Your Transfer Summary: ")
    st.plotly_chart(Transfers_table, use_container_width=True)
    
def main():
    '''
    The main() function that gets executed after a valid entry in mangaer_id 
    Returns
    -------
    None.
    '''
    user_details()
    display_graphs()
    display_tables()

def value_check(manager_id):
     ''' 
     A function to check the value of manager_id to raise an exception if invalid 
     '''
     if(manager_id.isalnum()):
         main()
     else:
         st.exception("Please enter a valid value in FPL Team ID box!!")

# markdowns for tool info and formatting

st.markdown("# StatsHub! :soccer: :bar_chart:")
st.markdown("----")
st.markdown("### Hello! Welcome to StatsHub \nUse this tool to see your FPL (Fantsay Premier League) team is performing during the current season! Simply enter your manager/team id in the text box below and hit enter!\nJust as an example, the following results are for the Team ID: 1")
st.markdown("----")

# get the user's manager_id usng streamlit's text input widget
# st.text_input(label, value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, args=None, kwargs=None, *, placeholder=None)
manager_id = st.text_input("Enter FPL Team ID","1", None, "user_id_key", "default", "Refer to the How-to section to find your Team ID. Scroll to the end")
value_check(manager_id) 

# markdowns for tool info and formatting
st.markdown("### How-to section: \nYou might be wondering: how to get the manager id? The answer is simple. Just go to official [Fantasy Premier League Website](https://fantasy.premierleague.com), sign in with your account, go to ‘Pick Team’ then ‘View Gameweek history’. You can find your id in the URL, right before the ‘/history’.")
st.markdown("-----")
st.markdown("### Hello! My name is Rinkesh Joshi :wave: \nI am a graduate student at Carleton University in the Systems and Computer Engineering Department. I created this tool to try out a few of Python libraries.")
st.markdown("\nCombining two things I absolutely love: Python :snake: + Fantasy Premier League :arrow_upper_right: :gem:")
st.markdown("\nFor more details, feel free to contact me at: \n:inbox_tray: [rinkeshjoshi@cmail.carleton.ca](mailto:rinkeshjoshi@cmail.carleton.ca)")
st.markdown("-----")

#[
#theme
#]
#base="#F9F7E8"



