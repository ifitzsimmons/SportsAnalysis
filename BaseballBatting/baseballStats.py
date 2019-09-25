#!/usr/local/bin/python3.7

import argparse
import pandas as pd
import sys

def add_arguments():
	name_group = parser.add_mutually_exclusive_group()
	name_group.add_argument("-i", "--player-id", 
					help=("Print the player id in the output. This is "
					"the default."),
                    			action="store_true")
	name_group.add_argument("-n", "--name", 
					help=('Print the player name as "nameFirst nameLast" '
					'instead of the player id.'),
			                action="store_true")
	name_group.add_argument("-g", "--given-name", 
					help=('Print the player name  as "nameGiven" instead '
					'of the player id'),
                    			action="store_true")

	stat_group = parser.add_mutually_exclusive_group()
	stat_group.add_argument("-b", "--batting-avg",
					help=("Print the player batting average. This is the"
					" default"),
  					action="store_true")
	stat_group.add_argument("-a", "--at-bats-per-home-run", 
					help="Print the player at bats per home run.",
                    			action="store_true")

	parser.add_argument("-t", "--top", type=int, default=5,
					help=("Print the top NUM players for the given statistic. "
					"The default is 5."))
	parser.add_argument("-s", "--skip", type=int, default=0,
					help=("Skip the top NUM players before printing. The default"
					" is 0."))
	parser.add_argument("-m", "--minimum-at-bats", type=int, default=3000,
					help=("The minimum NUM of at bats for a player to have a "
					"qualifying score. The default is 3000."))

def validate_career_stats():
	'''This function ensures that the data grouping occured without error 
		 (number of grouped rows = number of unique players) and that the skip+top 
		 number of results is less that the total number of players
	'''
	num_players = len(career_stats)
	
	if (num_players != batting_data.playerID.nunique()):
		print('Grouping on playerID in Batting.csv failed')
		sys.exit(1)	

	if (args.skip + args.top) >= len(career_stats):
			print(f'ERROR: Sum of skip ({args.skip}) and top ({args.top}) is greater '
						f'than the total number of unique players ({num_players})')
			sys.exit(1)

def import_people_csv():
	if args.name:
		return pd.read_csv('./People.csv')[['playerID', 'nameLast', 'nameFirst']]
	else:
		return pd.read_csv('./People.csv')[['playerID', 'nameGiven', 'nameLast']]

def add_supplementary_data(col_name, numerator, denominator):
	''' This function provides the new column
				BA (batting average): numerator = H,  denominator = AB
				AB_per_HR           : numerator = AB, denominator = HR
			
			==========
			PARAMATERS:
				col_name:    str, name of cloumn to be created
				numerator:   str, H or AB depending on the request
				denominator: str, AB or HR depending on the request

			======
			OUTPUT:
				Pandas database of career batting statistics with new column
	'''

	career_stats[col_name] = career_stats[numerator] / career_stats[denominator]

def print_data(statIn, all_data):
	''' This function prints data to the console

	==========
	Paramaters
		statIn: str, Column name that will either be 'BA' or 'AB_per_HR'
	'''

	identifier = []
	stat_category = [] 

	if args.name:
		# this line combines the first and last name row by row into one item
		identifier = list(all_data['nameFirst'] + ' ' + all_data['nameLast'])
	elif args.given_name:
		identifier = list(all_data['nameGiven'] + ' ' + all_data['nameLast'])
	else:
		identifier = all_data['playerID'].tolist()

	stat_category = list(all_data[stat])

	for name, statistic in zip(identifier, stat_category):
		 print(f'{name} {statistic}')

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	
	add_arguments()
	args = parser.parse_args()

	batting_data = pd.read_csv('./Batting.csv')[['playerID', 'AB', 'H', 'HR']]
	
	#Sum AB, H, HR across all seasons for each player 
	career_stats = batting_data.groupby('playerID').agg('sum')

	validate_career_stats()
	
	career_stats = career_stats[career_stats['AB'] > args.minimum_at_bats]
	if len(career_stats) < 1:
		print(f'There are no players with {args.minimum_at_bats} career at bats.')
		sys.exit(1)
	
	stat = ''
	if args.at_bats_per_home_run:
		stat = 'AB_per_HR'
		add_supplementary_data(stat, 'AB', 'HR')
		# Sort in ascending order (higher is better for BA)
		career_stats.sort_values(by='AB_per_HR', axis=0, ascending=True, inplace=True)
	else:
		stat = 'BA'
		add_supplementary_data(stat, 'H', 'AB')
		# Sort in descending order (lower number is better)
		career_stats.sort_values(by='BA', axis=0, ascending=False, inplace=True)

	skip_rows    = args.skip
	top_results  = args.top + skip_rows
	career_stats = career_stats.iloc[skip_rows:top_results]

	if args.name or args.given_name:
		player_data  = import_people_csv()
		career_stats = career_stats.merge(player_data, on='playerID', how='inner')

	print_data(stat, career_stats.reset_index())

