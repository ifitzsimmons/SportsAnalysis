from bs4 import BeautifulSoup
from collections import Counter, defaultdict
from datetime import datetime as dt

import argparse
import pandas as pd
from pprint import pprint
import re
import requests

def fill_zeros(draft_dict_zeros, category_list):  
    """Fill zeros if supplementary data does not apply to player
    Offensive players will not have defensive statistics and 
    get_sup_info adds defensive statistics to the data available
    from the draft information.
    
    Parameters
    ----------
    draft_dict_zeros: defaultdict(list)
    ...

    Returns
    -------
    draft_dict_zeros: defaultdict(list)
        passed by reference and supplements data from draft 
        site with zeros

    """ 

    for cat in category_list:
        draft_dict_zeros[cat].append('0')
    draft_dict_zeros['def_tds'].append('0')

def get_sup_info(player_link, player_data):
    """Add defensive data for defensive players and zeros for
    offensive players. Add seasons played and games started
    for all players

    All offensive statitistics are in original table.
    The only stat that must be added is the number of games
    started
    
    Parameters
    ----------
    player_link: string
    Link to supplemental data

    player_data: defaultdict(list)
    Dictionary with keys as the column name and values are
    the individual players' statistics

    Returns
    -------
    player_data: defaultdict(list)
        add supplemental data to player_data

    """
    sup_request = requests.get(player_link)
    sup_soup = BeautifulSoup(sup_request.text, 'html.parser')

    t_body = None
    
    try:
        # Find table that contains season by season data.
        # Seasons played will account for any season in
        # which the player has statistical recorded
        t_body = sup_soup.find_all('tbody')[0]
        seasons_played = len(t_body.find_all('tr'))
        player_data['seasons_played'].append(seasons_played)
    except IndexError:
        # if table does not exist, player never recorded stats
        # fill all categories with zeros and return
        fill_zeros(player_data, supp_cats)
        return

    if t_body:
        # The table footer contains career totals
        career_stats = sup_soup.find('tfoot')

        # Checks to see if this is a defensive player
        defense = sup_soup.find('div', {'id': 'div_defense'})
        
        if defense:
            # Loop over everything but seasons played
            # and populate data
            for cat in supp_cats[1:]:
                stat = career_stats.find('td', {'data-stat': cat}).text
                player_data[cat].append(stat)

            def_int_tds = career_stats.find('td', {'data-stat': 'def_int_td'}).text
            fumble_rec_tds = career_stats.find('td', {'data-stat': 'fumbles_rec_td'}).text
            total_def_tds = def_int_tds + fumble_rec_tds
            player_data['def_tds'].append(total_def_tds)
        else:
            # If offense
            try:
                games_started = career_stats.find('td', {'data-stat': 'gs'})
                player_data['gs'].append(games_started.text)
                fill_zeros(player_data, supp_cats[2:])
            except:
                # Fill zeros for everything but seasons played
                fill_zeros(player_data, supp_cats[1:])

def get_year_draft_info(year):
    """Get all draft information and career statistics
        per player in a given year
    
    Parameters
    ----------
    year: int
        year in which draft data exists for 
        https://www.pro-football-reference.com

    Returns
    -------
    draft_year_data: pandas.DataFrame
        DataFrame containing draft information and career statistics
        per player in a given year

    """

    url = f'https://www.pro-football-reference.com/years/{year}/draft.htm'
    request = requests.get(url)

    soup = BeautifulSoup(request.text, 'html.parser')

    div = soup.find_all('div', {'class' : 'table_outer_container'})[0]
    tr = div.find_all('tr')
    
    # List of BeautifulSoup objects describing player info
    table_entries = [row for row in tr if 'class' not in row.attrs.keys()]
    # Row that describes column data
    table_header = table_entries[0]
    # The actual draft data
    drafted_players = table_entries[1:]
    
    draft_dict = defaultdict(list)

    # Look for correct link extension
    ext_pattern = re.compile('^/players')

    # This loop collects all the data for each player in 
    # the year's draft class
    for player_info in drafted_players:
        sup_called = False
        for tag in player_info:

            # Look for data-stat attribute in beautifulSoup object
            category = tag.attrs['data-stat']
            draft_dict[category].append(tag.text)
            
             try:
                # Check for a-tag
                a = tag.find('a')
                if a:
                    ext_string = (a.attrs['href'])
                    # Check that extension is for the player
                    # by searching for the `/player` extension
                    if re.search(ext_pattern, ext_string):
                        ext = ext_string
                    else:
                        continue
                    link = f'https://www.pro-football-reference.com{ext}'
                    sup_called = True
                    get_sup_info(link, draft_dict)
            except KeyError:
                continue
        if not sup_called:
            # If the player data does not have an ext id, 
            # fill all supplemental data with zeros
            fill_zeros(draft_dict, supp_cats)  
            
    draft_year_data = pd.DataFrame(draft_dict)
    draft_year_data.set_index(data.player, inplace=True)
    
    years_since_draft = dt.now().year - year

    # Adjust years in league to consider only the first 10 years
    years_in_league = years_since_draft if years_since_draft <= 10 else 10
    data = data[cols+supp_cats]
    data.insert(0, 'Year', str(year))
    data.insert(4, 'Years_in_League', str(years_in_league))
    
    
    return draft_year_data

if __name__ == '__main__':

    # TODO - use argparse to configure
    num_drafts = 20
    
    year = dt.now().year
    first_year = year - num_drafts

    draft_years = list(range(first_year, year))

    cols = [
        'pos', 'draft_round', 'draft_pick', 
        'all_pros_first_team', 'g', 'pass_att', 'pass_cmp', 
        'pass_int', 'pass_td', 'pass_yds', 'pro_bowls', 
        'rec', 'rec_td','rec_yds', 'rush_att', 'rush_td', 
        'rush_yds', 'sacks', 'tackles_solo', 
        'years_as_primary_starter'
    ]

    # Data that is not in original draft table
    supp_cats = [
        'seasons_played', 'gs', 'pass_defended', 'fumbles_forced', 
        'fumbles_rec', 'tackles_combined', 'tackles_assists', 
        'tackles_loss', 'qb_hits', 'safety_md'
    ]

    for i, year in enumerate(draft_years):
        result = get_year_draft_info(year)
        if i == 0:
            prev = result
        else:
            frames = [prev, result]
            prev = pd.concat(frames)

    file_name = f'./{str(first_year)}_{str(draft_years[-1])}_drafts.csv'
    prev.to_csv(file_name)
