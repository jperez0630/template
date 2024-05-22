from pybaseball import statcast, pitching_stats
import time, datetime
import pandas as pd
import os
from pathlib import Path
import duckdb

con = duckdb.connect(f'{Path.cwd()}/marinerds_data.duckdb')
local_con = con.cursor()

def get_most_recent_date():
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    return yesterday

def get_pitching_stats():
    data = pitching_stats(2024)
    filtered_data = data[['Name','Team','WHIP','ERA','xERA','HardHit%','H/9','BB/9','BABIP']].copy()
    filtered_data.rename(columns={'HardHit%':'Hard_Hit_Percent','H/9':'H_per_9','BB/9':'BB_per_9'},inplace=True)
    return filtered_data

df_filtered_pitching_stats = get_pitching_stats()

def get_league_median_stats():
    league_median_whip = df_filtered_pitching_stats.WHIP.median()
    league_median_era = df_filtered_pitching_stats.ERA.median()
    league_median_xera = df_filtered_pitching_stats.xERA.median()
    league_median_hits_per_9 = df_filtered_pitching_stats.H_per_9.median()
    league_median_bb_per_9 = df_filtered_pitching_stats.BB_per_9.median()
    league_median_hard_hit_percent = df_filtered_pitching_stats.Hard_Hit_Percent.median()
    league_median_babip = df_filtered_pitching_stats.BABIP.median()
    league_median_dict = {
        'Name':'League Median',
        'Team':'N/A',
        'WHIP':league_median_whip,
        'ERA':league_median_era,
        'xERA':league_median_xera,
        'H_per_9':league_median_hits_per_9,
        'BB_per_9':league_median_bb_per_9,
        'Hard_Hit_Percent':league_median_hard_hit_percent,
        'BABIP':league_median_babip
    }
    return league_median_dict

def get_league_min_stats():    
    league_min_whip = df_filtered_pitching_stats.WHIP.min()
    league_min_era = df_filtered_pitching_stats.ERA.min()
    league_min_xera = df_filtered_pitching_stats.xERA.min()
    league_min_hits_per_9 = df_filtered_pitching_stats.H_per_9.min()
    league_min_bb_per_9 = df_filtered_pitching_stats.BB_per_9.min()
    league_min_hard_hit_percent = df_filtered_pitching_stats.Hard_Hit_Percent.min()
    league_min_babip = df_filtered_pitching_stats.BABIP.min()
    league_min_dict = {
        'Name':'League Minimum',
        'Team':'N/A',
        'WHIP':league_min_whip,
        'ERA':league_min_era,
        'xERA':league_min_xera,
        'H_per_9':league_min_hits_per_9,
        'BB_per_9':league_min_bb_per_9,
        'Hard_Hit_Percent':league_min_hard_hit_percent,
        'BABIP':league_min_babip
    }
    return league_min_dict

df_filtered_pitching_stats = get_pitching_stats()

def add_league_median_min_stats(df_filtered_pitching_stats):
    df_filtered_pitching_stats = pd.concat([df_filtered_pitching_stats, pd.DataFrame([get_league_median_stats()])], ignore_index=True)
    df_filtered_pitching_stats = pd.concat([df_filtered_pitching_stats, pd.DataFrame([get_league_min_stats()])], ignore_index=True)
    return df_filtered_pitching_stats

df_filtered_pitching_stats = add_league_median_min_stats(df_filtered_pitching_stats)

def add_rank():
    df_filtered_pitching_stats['ERA_Rank'] = df_filtered_pitching_stats['ERA'].rank()
    df_filtered_pitching_stats['xERA_Rank'] = df_filtered_pitching_stats['xERA'].rank()
    df_filtered_pitching_stats['WHIP_Rank'] = df_filtered_pitching_stats['WHIP'].rank()
    df_filtered_pitching_stats['Hard_Hit_Percent_Rank'] = df_filtered_pitching_stats['Hard_Hit_Percent'].rank()
    df_filtered_pitching_stats['H_per_9_Rank'] = df_filtered_pitching_stats['H_per_9'].rank()
    df_filtered_pitching_stats['BB_per_9_Rank'] = df_filtered_pitching_stats['BB_per_9'].rank()
    df_filtered_pitching_stats['BABIP_Rank'] = df_filtered_pitching_stats['BABIP'].rank()
    return df_filtered_pitching_stats

add_rank()

def get_mariners_staff_data():
    mariners_staff_data = df_filtered_pitching_stats.loc[df_filtered_pitching_stats['Team'].str.contains('SEA')| df_filtered_pitching_stats['Team'].str.contains('N/A')]
    return mariners_staff_data

df_mariners_staff = get_mariners_staff_data()

local_con.sql('''
CREATE OR REPLACE TABLE mariners_pitching_data AS
SELECT * FROM df_mariners_staff
''')

local_con.sql('''
CREATE OR REPLACE TABLE mlb_pitching_data AS
SELECT * from df_filtered_pitching_stats
''')