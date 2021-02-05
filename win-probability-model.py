import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly as ply
from bs4 import BeautifulSoup
import requests

# Team sites were added one at a time, but this can be automated by creating a spreadsheet of teams and sites and then reading it into Python as a pandas DataFrame
sites = pd.Series()
sites['Duke'] = 'https://goduke.com/sports/baseball/'
sites['Yale'] = 'https://yalebulldogs.com/sports/baseball/'
sites['Stanford'] = 'https://gostanford.com/sports/baseball/'
sites['Cal'] = 'https://calbears.com/sports/baseball/'
sites['Boston College'] = 'https://bceagles.com/sports/baseball/'
sites['Texas A&M'] = 'https://12thman.com/sports/baseball/'
sites['Michigan'] = 'https://mgoblue.com/sports/baseball/'
sites['Florida'] = 'https://floridagators.com/sports/baseball/'
sites['Texas'] = 'https://texassports.com/sports/baseball/'
team = input("Team: ").title()
year = input("Year (YYYY): ")

opponent = input("Opponent: ")
opp_url = '-'.join(c.lower() for c in opponent.split() if c.isalpha())

gameid = input("Game ID (in URL, e.g. xxxxx): ")

team_is_home = input("Is {team} the home team (write 'Yes' or 'No')? ".format(team=team))
if team_is_home == 'Yes':
    home_team = team
    away_team = opponent
else:
    home_team = opponent
    away_team = team
    
url = sites[team]+'stats/'+year+'/'+opp_url+'/boxscore/'+gameid

url_text = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}).text

soup = BeautifulSoup(url_text, 'lxml')

play_by_play = soup.find_all('section', id='play-by-play')[0]

inn = play_by_play.find_all('table', attrs={'class': 'sidearm-table play-by-play'})

# Create dataframe to store play-by-play data
df = pd.DataFrame(columns=['Team', 'Play', '1B Result', '2B Result', '3B Result', 'Outs Result', 'Score Result'])

# Modelling the game.
outs_away = 0
runs_away = 0

outs_home = 0
runs_home = 0

first = 0
second = 0
third = 0

# Away team
for i in range(0, len(inn), 2): # Half-innings during which the home team is up
    
    first = 0
    second = 0
    third = 0
    
    if runs_away < runs_home:
        if outs_away >= 27:
            break
            
    if runs_away > runs_home:
        if outs_home >= 27:
            break

    print('{away_team} is up to bat.'.format(away_team = away_team))
    pbp = inn[i].find_all('th', scope='row')
    for play in pbp:
        # Get the hitter's last name
        hitter = None 
        if '.' in play.get_text().split()[0]:
            if len(play.get_text().split()[0]) == 2:
                hitter = play.get_text().split()[0] + ' ' + play.get_text().split()[1]
                print(hitter)
            else:
                hitter = play.get_text().split()[0]
                print(hitter)
        elif ',' in play.get_text().split()[0]:
            if '.' in play.get_text().split()[1]:
                hitter = play.get_text().split('.')[0]
                print(hitter)
            elif len(play.get_text().split(';')[0].split()[0].split(',')) == 2:
                hitter = play.get_text().split()[0]
                print(hitter)
            else:
                hitter = play.get_text().split()[0] + ' ' + play.get_text().split()[1]
                print(hitter)
        else:
            hitter = play.get_text().split()[0]
            print(hitter)
            
        # Pinch runners
        if 'pinch ran' in play.get_text().split(';')[0]:
            player = input("Who did {hitter} pinch run for? (Type in same format that appears in play-by-play)".format(hitter=hitter))
            if first == player:
                first = hitter
            if second == player:
                second = hitter
            if third == player:
                third = hitter       

        #Outs    
        if any([bool(third != 0 and third != hitter and third in j and ' out ' in j and 'caught stealing' not in j) for j in play.get_text().split(';')]):
            outs_away = outs_away + 1
            third = 0
        if any([bool(second != 0 and second != hitter and second in j and ' out ' in j and 'caught stealing' not in j) for j in play.get_text().split(';')]):
            outs_away = outs_away + 1
            second = 0
        if any([bool(first != 0 and first != hitter and first in j and ' out ' in j and 'caught stealing' not in j) for j in play.get_text().split(';')]):
            outs_away = outs_away + 1
            first = 0
        if hitter in play.get_text().split(';')[0] and ' out ' in play.get_text().split(';')[0] and 'caught stealing' not in play.get_text().split(';')[0] and 'picked off' not in play.get_text().split(';')[0]:
            if 'reached first' in play.get_text().split(';')[0] and 'struck out' in play.get_text().split(';')[0]:
                outs_away = outs_away
            elif 'out at second c to 2b' in play.get_text().split(';')[0]:
                outs_away = outs_away + 1
            elif 'out at third c to 3b' in play.get_text().split(';')[0]:
                outs_away = outs_away + 1
            elif 'under review' in play.get_text() and 'stands' in play.get_text():
                outs_away = outs_away
            elif 'under review' in play.get_text(): # if call is reversed
                print('The call during this play was reversed. Input the following.')
                first = input('Who is at first after this play (0 if nobody)? ')
                second = input('Who is at second after this play (0 if nobody)? ')
                third = input('Who is at third after this play (0 if nobody)? ')
                outs_away = outs_away + input('How many outs should be added/subracted because of this call reversal (0 if none)? ')
            else:
                outs_away = outs_away + 1
        # We need to tell Python that 'popped up' is an out.
        if hitter in play.get_text().split(';')[0] and 'popped up' in play.get_text().split(';')[0]:
            outs_away = outs_away + 1

        if any([bool(hitter in j and 'double play' in j) for j in play.get_text().split(';')]):
            outs_away = outs_away + 1
        if hitter in play.get_text().split(';')[0] and 'infield fly' in play.get_text().split(';')[0]:
            outs_away = outs_away + 1
        
        #Stolen bases
        if any([bool(third != 0 and third in j and ' scored' not in j and 'stole home' in j) for j in play.get_text().split(';')]):
            runs_away = runs_away + 1
            third = 0
        if any([bool(second != 0 and second in j and ' scored' not in j and 'stole third' in j) for j in play.get_text().split(';')]):
            third = second
            second = 0
        if any([bool(first != 0 and first in j and ' scored' not in j and 'advanced to third' not in j and 'stole second' in j) for j in play.get_text().split(';')]):
            second = first
            first = 0
            
        #Caught stealing
        if any([bool(third != 0 and third in j and ' scored' not in j and ('caught stealing' in j or 'picked off' in j)) for j in play.get_text().split(';')[1:]]):
            outs_away = outs_away + 1
            third = 0
        if any([bool(second != 0 and second in j and ' scored' not in j and ('caught stealing' in j or 'picked off' in j)) for j in play.get_text().split(';')[1:]]):
            outs_away = outs_away + 1
            second = 0
        if any([bool(first != 0 and first in j and ' scored' not in j and 'advanced to third' not in j and ('caught stealing' in j or 'picked off' in j)) for j in play.get_text().split(';')[1:]]):
            outs_away = outs_away + 1
            first = 0
        if hitter in play.get_text().split(';')[0]:
            if 'caught stealing' in play.get_text().split(';')[0]:
                if first == hitter:
                    first = 0
                    outs_away = outs_away + 1
                if second == hitter:
                    second = 0
                    outs_away = outs_away + 1
                if third == hitter:
                    third = 0
                    outs_away = outs_away + 1
            if 'picked off' in play.get_text().split(';')[0]:
                if first == hitter:
                    first = 0
                    outs_away = outs_away + 1
                if second == hitter:
                    second = 0
                    outs_away = outs_away + 1
                if third == hitter:
                    third = 0
                    outs_away = outs_away + 1
        
        #Runs scored / baserunning
        if any([bool(third != 0 and third in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_away = runs_away + 1
            third = 0
        if any([bool(second != 0 and second in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_away = runs_away + 1
            second = 0
        if any([bool(first != 0 and first in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_away = runs_away + 1
            first = 0
        if any([bool(hitter in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_away = runs_away + 1
            first = 0
            second = 0
            third = 0 
        
        #Baserunning
        if any([bool(second != 0 and second in j and 'advanced to third' in j and ' scored' not in j) for j in play.get_text().split(';')]):
            third = second
            second = 0
        if any([bool(first != 0 and first in j and 'advanced to third' in j and ' scored' not in j) for j in play.get_text().split(';')]):
            third = first
            first = 0
        if any([bool(first != 0 and first in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j) for j in play.get_text().split(';')]):
            second = first
            first = 0
        if any([bool(hitter in j and 'advanced to third' in j and ' scored' not in j) for j in play.get_text().split(';')]):
            third = hitter
            second = 0
            first = 0      
        if any([bool(hitter in j and 'advanced to second' in j and ' scored' not in j and 'advanced to third' not in j) for j in play.get_text().split(';')]):
            second = hitter
            first = 0
    
        #Single
        if hitter in play.get_text().split(';')[0] and ' singled' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        
        #Double
        if hitter in play.get_text().split(';')[0] and ' doubled' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            second = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        
        #Triple
        if hitter in play.get_text().split(';')[0] and ' tripled' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            third = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        
        #homerun
        if hitter in play.get_text() and 'homered' in play.get_text() and ' out ' not in play.get_text():
            runs_away = runs_away + 1
            first = 0
            second = 0
            third = 0
        
        #Walk
        if hitter in play.get_text().split(';')[0] and ' walked' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        #HBP         
        if hitter in play.get_text().split(';')[0] and 'hit by pitch' in play.get_text().split(';')[0]  and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        #Catcher's interference        
        if hitter in play.get_text().split(';')[0] and "reached on catcher's interference" in play.get_text().split(';')[0]  and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        
        #Reached on error        
        if hitter in play.get_text().split(';')[0] and 'reached on' in play.get_text().split(';')[0] and 'error' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        
        #Dropped third strike
        if hitter in play.get_text().split(';')[0] and 'struck out' in play.get_text().split(';')[0] and 'reached first' in play.get_text().split(';')[0]:
            first = hitter
            outs_away = outs_away # compensate
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
                
        #Fielder's choice
        if hitter in play.get_text().split(';')[0] and "reached on a fielder's choice" in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_away = runs_away + 1
        
        df = df.append({'Team': away_team, 'Play': play.get_text(), '1B Result': bool(first != 0), '2B Result': bool(second != 0), '3B Result': bool(third != 0), 'Outs Result': outs_away, 'Score Result': runs_away}, ignore_index=True)
      
    # Bases cleared for the start of new half-inning
                
    first = 0
    second = 0
    third = 0
       
    # Home team    
    if runs_away < runs_home:
        if outs_home == 24:
            break 
        
    print('{home_team} is up to bat.'.format(home_team = home_team))
    pbp = inn[i+1].find_all('th', scope='row')
    for play in pbp:
        # Get the hitter's last name
        hitter = None 
        if '.' in play.get_text().split()[0]:
            if len(play.get_text().split()[0]) == 2:
                hitter = play.get_text().split()[0] + ' ' + play.get_text().split()[1]
                print(hitter)
            else:
                hitter = play.get_text().split()[0]
                print(hitter)
        elif ',' in play.get_text().split()[0]:
            if '.' in play.get_text().split()[1]:
                hitter = play.get_text().split('.')[0]
                print(hitter)
            elif len(play.get_text().split(';')[0].split()[0].split(',')) == 2:
                hitter = play.get_text().split()[0]
                print(hitter)
            else:
                hitter = play.get_text().split()[0] + ' ' + play.get_text().split()[1]
                print(hitter)
        else:
            hitter = play.get_text().split()[0]
            print(hitter)
            
        # Pinch runners
        if 'pinch ran' in play.get_text().split(';')[0]:
            player = input("Who did {hitter} pinch run for? (Type in same format that appears in play-by-play)".format(hitter=hitter))
            if first == player:
                first = hitter
            if second == player:
                second = hitter
            if third == player:
                third = hitter 
    
        #Outs
        if any([bool(third != 0 and third != hitter and third in j and ' out ' in j and 'caught stealing' not in j) for j in play.get_text().split(';')]):
            outs_home = outs_home + 1
            third = 0
        if any([bool(second != 0 and second != hitter and second in j and ' out ' in j and 'caught stealing' not in j) for j in play.get_text().split(';')]):
            outs_home = outs_home + 1
            second = 0
        if any([bool(first != 0 and first != hitter and first in j and ' out ' in j and 'caught stealing' not in j) for j in play.get_text().split(';')]):
            outs_home = outs_home + 1
            first = 0
        if hitter in play.get_text().split(';')[0] and ' out ' in play.get_text().split(';')[0] and 'caught stealing' not in play.get_text().split(';')[0] and 'picked off' not in play.get_text().split(';')[0]:
            if 'reached first' in play.get_text().split(';')[0] and 'struck out' in play.get_text().split(';')[0]:
                outs_home = outs_home
            elif 'out at second c to 2b' in play.get_text().split(';')[0]:
                outs_home = outs_home + 1
            elif 'out at third c to 3b' in play.get_text().split(';')[0]:
                outs_home = outs_home + 1
            elif 'under review' in play.get_text() and 'stands' in play.get_text():
                outs_home = outs_home
            elif 'under review' in play.get_text(): # if call is reversed
                print('The call during this play was reversed. Input the following.')
                first = input('Who is at first after this play (0 if nobody)? ')
                second = input('Who is at second after this play (0 if nobody)? ')
                third = input('Who is at third after this play (0 if nobody)? ')
                outs_home = outs_home + input('How many outs should be added/subracted because of this call reversal (0 if none)? ')
            else:
                outs_home = outs_home + 1
        # We need to tell Python that 'popped up' is an out.
        if hitter in play.get_text().split(';')[0] and 'popped up' in play.get_text().split(';')[0]:
            print('Yeah python got this far too')
            print(outs_home)
            outs_home = outs_home + 1

        if any([bool(hitter in j and 'double play' in j) for j in play.get_text().split(';')]):
            outs_home = outs_home + 1
        if hitter in play.get_text().split(';')[0] and 'infield fly' in play.get_text().split(';')[0]:
            outs_home = outs_home + 1
        
        #Stolen bases
        if any([bool(third != 0 and third in j and ' scored' not in j and 'stole home' in j) for j in play.get_text().split(';')]):
            runs_home = runs_home + 1
            third = 0
        if any([bool(second != 0 and second in j and ' scored' not in j and 'stole third' in j) for j in play.get_text().split(';')]):
            third = second
            second = 0
        if any([bool(first != 0 and first in j and ' scored' not in j and 'advanced to third' not in j and 'stole second' in j) for j in play.get_text().split(';')]):
            second = first
            first = 0
            
        #Caught stealing
        if any([bool(third != 0 and third in j and ' scored' not in j and ('caught stealing' in j or 'picked off' in j)) for j in play.get_text().split(';')[1:]]):
            outs_home = outs_home + 1
            third = 0
        if any([bool(second != 0 and second in j and ' scored' not in j and ('caught stealing' in j or 'picked off' in j)) for j in play.get_text().split(';')[1:]]):
            outs_home = outs_home + 1
            second = 0
        if any([bool(first != 0 and first in j and ' scored' not in j and 'advanced to third' not in j and ('caught stealing' in j or 'picked off' in j)) for j in play.get_text().split(';')[1:]]):
            outs_home = outs_home + 1
            first = 0
        if hitter in play.get_text().split(';')[0]:
            if 'caught stealing' in play.get_text().split(';')[0]:
                if first == hitter:
                    first = 0
                    outs_home = outs_home + 1
                if second == hitter:
                    second = 0
                    outs_home = outs_home + 1
                if third == hitter:
                    third = 0
                    outs_home = outs_home + 1
            if 'picked off' in play.get_text().split(';')[0]:
                if first == hitter:
                    first = 0
                    outs_home = outs_home + 1
                if second == hitter:
                    second = 0
                    outs_home = outs_home + 1
                if third == hitter:
                    third = 0
                    outs_home = outs_home + 1
        
        #Runs scored / baserunning
        if any([bool(third != 0 and third in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_home = runs_home + 1
            third = 0
        if any([bool(second != 0 and second in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_home = runs_home + 1
            second = 0
        if any([bool(first != 0 and first in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_home = runs_home + 1
            first = 0
        if any([bool(hitter in j and ' scored' in j) for j in play.get_text().split(';')]):
            runs_home = runs_home + 1
            first = 0
            second = 0
            third = 0 
        
        #Baserunning
        if any([bool(second != 0 and second in j and 'advanced to third' in j and ' scored' not in j) for j in play.get_text().split(';')]):
            third = second
            second = 0
        if any([bool(first != 0 and first in j and 'advanced to third' in j and ' scored' not in j) for j in play.get_text().split(';')]):
            third = first
            first = 0
        if any([bool(first != 0 and first in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j) for j in play.get_text().split(';')]):
            second = first
            first = 0
        if any([bool(hitter in j and 'advanced to third' in j and ' scored' not in j) for j in play.get_text().split(';')]):
            third = hitter
            second = 0
            first = 0      
        if any([bool(hitter in j and 'advanced to second' in j and ' scored' not in j and 'advanced to third' not in j) for j in play.get_text().split(';')]):
            second = hitter
            first = 0
    
        #Single
        if hitter in play.get_text().split(';')[0] and ' singled' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        
        #Double
        if hitter in play.get_text().split(';')[0] and ' doubled' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            second = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        
        #Triple
        if hitter in play.get_text().split(';')[0] and ' tripled' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            third = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        
        #Homerun
        if hitter in play.get_text() and 'homered' in play.get_text() and ' out ' not in play.get_text():
            runs_home = runs_home + 1
            first = 0
            second = 0
            third = 0
        
        #Walk
        if hitter in play.get_text().split(';')[0] and ' walked' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        #HBP         
        if hitter in play.get_text().split(';')[0] and 'hit by pitch' in play.get_text().split(';')[0]  and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        #Catcher's interference        
        if hitter in play.get_text().split(';')[0] and "reached on catcher's interference" in play.get_text().split(';')[0]  and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        
        #Reached on error        
        if hitter in play.get_text().split(';')[0] and 'reached on' in play.get_text().split(';')[0] and 'error' in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
        
        #Dropped third strike
        if hitter in play.get_text().split(';')[0] and 'struck out' in play.get_text().split(';')[0] and 'reached first' in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            outs_home = outs_home  # compensate
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
                
        #Fielder's choice
        if hitter in play.get_text().split(';')[0] and "reached on a fielder's choice" in play.get_text().split(';')[0] and ' out ' not in play.get_text().split(';')[0]:
            first = hitter
            j = play.get_text().split(';')[0]
            if hitter in j and 'advanced to second' in j and 'advanced to third' not in j and ' scored' not in j:
                second = hitter
                first = 0
            if hitter in j and 'advanced to third' in j and ' scored' not in j:
                third = hitter
                second = 0
                first = 0
            if hitter in j and ' scored' in j:
                first = 0
                second = 0
                third = 0
                runs_home = runs_home + 1
                
        print(first)
        print(second)
        print(third)
        
        df = df.append({'Team': home_team, 'Play': play.get_text(), '1B Result': bool(first != 0), '2B Result': bool(second != 0), '3B Result': bool(third != 0), 'Outs Result': outs_home, 'Score Result': runs_home}, ignore_index=True)
    
# Now we use a run expectancy matrix from FanGraphs to basically weight RBIs
# RE End state - RE Begin state + Runs actually scored

# Stats source: https://library.fangraphs.com/misc/re24/
re_matrix = pd.read_excel('C:/users/teddy/onedrive/desktop/statstak/run_ex_matrix_2019d1.xlsx')
re_matrix = re_matrix.set_index('Runners')

# Create column that gives outs in the inning
df['Inn Outs Result'] = df['Outs Result'] % 3
df['Inn Outs Result'].iloc[-1] = 3

df['RE'] = None

for i in range(len(df)-1):
    if df['Inn Outs Result'].iloc[i] == 0 and df['Team'].iloc[i] != df['Team'].iloc[i+1]:
        df['Inn Outs Result'].iloc[i] = 3

# Determine RE of rows...
if df['Outs Result'].iloc[0] == 0:
    df['RE'].iloc[0] = 0.831
elif df['Outs Result'].iloc[0] == 1:
    df['RE'].iloc[0] = 0.243

for i in range(len(df)-1):
    if df['Inn Outs Result'].iloc[i+1] == 0:
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['Empty', '0 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['1 _ _', '0 Outs']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['_ 2 _', '0 Outs']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['_ _ 3', '0 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['1 2 _', '0 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['1 _ 3', '0 Outs']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['_ 2 3', '0 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['1 2 3', '0 Outs']
    if df['Inn Outs Result'].iloc[i+1] == 1:
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['Empty', '1 Out']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['1 _ _', '1 Out']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['_ 2 _', '1 Out']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['_ _ 3', '1 Out']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['1 2 _', '1 Out']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['1 _ 3', '1 Out']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['_ 2 3', '1 Out']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['1 2 3', '1 Out']
    if df['Inn Outs Result'].iloc[i+1] == 2:
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['Empty', '2 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['1 _ _', '2 Outs']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['_ 2 _', '2 Outs']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['_ _ 3', '2 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == False:
            df['RE'].iloc[i+1] = re_matrix.loc['1 2 _', '2 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == False and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['1 _ 3', '2 Outs']
        if df['1B Result'].iloc[i+1] == False and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['_ 2 3', '2 Outs']
        if df['1B Result'].iloc[i+1] == True and df['2B Result'].iloc[i+1] == True and df['3B Result'].iloc[i+1] == True:
            df['RE'].iloc[i+1] = re_matrix.loc['1 2 3', '2 Outs']
    if df['Inn Outs Result'].iloc[i+1] == 3:
        df['RE'].iloc[i+1] = 0
        df['1B Result'].iloc[i+1] = False
        df['2B Result'].iloc[i+1] = False
        df['3B Result'].iloc[i+1] = False

# Now we make a column summing actual runs and expected runs at every point.
df['RE + Runs'] = df['RE'] + df['Score Result']

# 2018 average runs per game per team: 5.64
#df['Expected Runs'] = None

# Key question to answer: how much does game score vary (i.e. standard deviation) as fewer and fewer outs remain for a team??

std_outs_left = pd.DataFrame([[27, 3.575737686]])
std_outs_left = std_outs_left.append([[26, 3.57566258]])
std_outs_left = std_outs_left.append([[25, 3.1906112267]])
std_outs_left = std_outs_left.append([[24, 3.0608985608804486]])
std_outs_left = std_outs_left.append([[23, 2.9106013124438737]])
std_outs_left = std_outs_left.append([[22, 3.175909318604673]])
std_outs_left = std_outs_left.append([[21, 2.7981958473273454]])
std_outs_left = std_outs_left.append([[20, 2.831960451701259]])
std_outs_left = std_outs_left.append([[19, 2.7076927447552093]])
std_outs_left = std_outs_left.append([[18, 2.6019223662515376]])
std_outs_left = std_outs_left.append([[17, 2.7505635786143903]])
std_outs_left = std_outs_left.append([[16, 2.398728830026437]])
std_outs_left = std_outs_left.append([[15, 2.742261840160418]])
std_outs_left = std_outs_left.append([[14, 2.3932195887548637]])
std_outs_left = std_outs_left.append([[13, 2.473863375370596]])
std_outs_left = std_outs_left.append([[12, 2.8655889447022926]])
std_outs_left = std_outs_left.append([[11, 2.1170498340851593]])
std_outs_left = std_outs_left.append([[10, 2.324198786678971]])
std_outs_left = std_outs_left.append([[9, 2.0448960853794014]])
std_outs_left = std_outs_left.append([[8, 1.804882267628556]])
std_outs_left = std_outs_left.append([[7, 1.1288932633336068]])
std_outs_left = std_outs_left.append([[6, 1.4849579118614775]])
std_outs_left = std_outs_left.append([[5, 1.0934349546269315]])
std_outs_left = std_outs_left.append([[4, 1.3190905958272918]])
std_outs_left = std_outs_left.append([[3, 0.9630680142129111]])
#std_outs_left = std_outs_left.append([[0, 0]])

std_outs_left['std^2'] = std_outs_left[1]**2

std_outs_left['const'] = 1

import matplotlib.pyplot as plt

best_fit_slope = 0.4373
best_fit_int = -0.1910

# outs left * slope + int = model std**2

std_outs_left = std_outs_left.append({0: 2}, ignore_index=True)
std_outs_left = std_outs_left.append({0: 1}, ignore_index=True)
std_outs_left = std_outs_left.append({0: 0}, ignore_index=True)

std_outs_left['model std'] = np.sqrt(std_outs_left[0]*best_fit_slope + best_fit_int)
std_outs_left['model std'].iloc[-1] = 0.00001
std_outs_left

df['Home RE + Runs'] = np.where(df['Team'] == home_team, df['RE + Runs'], np.nan)
df['Home RE + Runs'].iloc[0] = 0
df['Away RE + Runs'] = np.where(df['Team'] == away_team, df['RE + Runs'], np.nan)
df['Home RE + Runs'] = df['Home RE + Runs'].ffill()
df['Away RE + Runs'] = df['Away RE + Runs'].ffill()
df['STD Runs Away'] = np.nan
df['STD Runs Home'] = np.nan
for i in range(len(df)):
    if df['Team'].iloc[i] == home_team:
        if outs_home <= 27:
            df['STD Runs Home'].iloc[i] = std_outs_left['model std'].iloc[df['Outs Result'].iloc[i]]
        else:
            df['STD Runs Home'].iloc[i] = std_outs_left['model std'].iloc[df['Outs Result'].iloc[i] % 3 + 24]
    if df['Team'].iloc[i] == away_team:
        if outs_away <= 27:
            df['STD Runs Away'].iloc[i] = std_outs_left['model std'].iloc[df['Outs Result'].iloc[i]]
        else:
            df['STD Runs Away'].iloc[i] = std_outs_left['model std'].iloc[df['Outs Result'].iloc[i] % 3 + 24]
    
df['STD Runs Home'].iloc[0] = 3.408240
df['STD Runs Home'] = df['STD Runs Home'].fillna(method='ffill')
df['STD Runs Away'] = df['STD Runs Away'].fillna(method='ffill')

import scipy.stats

df['Prob {Away} Win'.format(Away=away_team)] = scipy.stats.norm(df['Home RE + Runs'] - df['Away RE + Runs'], (df['STD Runs Away']**2 + df['STD Runs Home']**2)**0.5).cdf(0)
df['Prob {Home} Win'.format(Home=home_team)] = 1 - df['Prob {Away} Win'.format(Away=away_team)]

# This piece of code accounts for walk-off hits/wins etc.
if outs_home >= 24: 
    if outs_away >= 27: #If we are in the bottom of the ninth inning or later
        if runs_home > runs_away:
            df['Prob {Home} Win'.format(Home=home_team)].iloc[-1] = 1
            df['Prob {Away} Win'.format(Away=away_team)].iloc[-1] = 0
            
import plotly.express as plx

fig = plx.line(df, x=df.index, y=[df['Prob {Away} Win'.format(Away=away_team)], df['Prob {Home} Win'.format(Home=home_team)]], hover_name=df['Play'])
fig.show()
