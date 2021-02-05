import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import scipy.stats
from datetime import datetime, date, time

# Hitting data from Baseball Cube
cube_hit = pd.read_csv('C:/users/teddy/onedrive/documents/statstak/d1_hitting_cube_stats.csv')
cube_hit_draft = cube_hit[cube_hit['draft_year'] != 0]

# Clean / modify / select data for upcoming linear regression

# Remove high school draft picks
lrdf = cube_hit_draft[cube_hit_draft['draft_year'] >= cube_hit_draft['year']]

# Only consider players drafted in, or since, 2015
lrdf = lrdf[lrdf['draft_year'] >= 2015]

# Remove POs
lrdf = lrdf[lrdf['posit'] != 'P']

# Remove any players who played at multiple DI schools, or schools that changed leagues. This will make ensuing regression easier
for i in lrdf['playerid'].drop_duplicates():
    plyr_df = lrdf[lrdf['playerid'] == i]
    for j in range(len(plyr_df)):
        if plyr_df['teamName'].iloc[j] != plyr_df['teamName'].iloc[0]:
            lrdf = lrdf[lrdf['playerid'] != i]
        if plyr_df['leagueName'].iloc[j] != plyr_df['leagueName'].iloc[0]:
            lrdf = lrdf[lrdf['playerid'] != i]

# Remove basically any cumulative stats

# Add ISO as a stat
lrdf['iso'] = (lrdf['Dbl'] + 2*lrdf['Tpl'] + 3*lrdf['HR']) / lrdf['AB']

# HR per AB
lrdf['hr_per_ab'] = lrdf['HR'] / lrdf['AB']

# SB per PA
lrdf['sb_per_pa'] = lrdf['SB'] / (lrdf['AB'] + lrdf['BB'] + lrdf['IBB'] + lrdf['HBP'] + lrdf['SH'] + lrdf['SF'])

# Add walk rate (BB%) and strikeout rate (K%)
lrdf['bb_rate'] = (lrdf['BB'] + lrdf['IBB'] + lrdf['HBP']) / (lrdf['AB'] + lrdf['BB'] + lrdf['IBB'] + lrdf['HBP'] + lrdf['SH'] + lrdf['SF'])
lrdf['k_rate'] = (lrdf['SO']) / (lrdf['AB'] + lrdf['BB'] + lrdf['IBB'] + lrdf['HBP'] + lrdf['SH'] + lrdf['SF'])

# Create column that tells how many years prior to a draft selection a certain season is
lrdf['years_before_drafted'] = lrdf['draft_year'] - lrdf['year']

# Convert team names to RPI rankings (we want only numerical variables in the upcoming regression!)
for i in range(len(lrdf)):
    df_tm = lrdf['teamName'].iloc[i]
    draft_yr = lrdf['draft_year'].iloc[i]
    rpi = pd.read_excel('C:/users/teddy/onedrive/documents/statstak/d1_rankings/rpi/rpi_'+str(draft_yr)+'.xlsx')

    if df_tm == 'Ark-Little Rock':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Arkansas-Little Rock', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Bethune-Cookman':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Bethune Cookman', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Bowling Green State':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Bowling Green', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Bryant University':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Bryant', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'University at Buffalo':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Buffalo', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Brigham Young':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'BYU', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Canisius College':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Canisius', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Central Ct State':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Central Connecticut State', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'East Tennessee State':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'East Tennessee state', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Florida Intl':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Florida International', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Long Island-Brooklyn':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Long Island', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Manhattan College':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Manhattan', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Middle Tenn State':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Middle Tenn', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Miss. Valley St':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Mississippi Valley State', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Nebraska at Omaha':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Nebraska-Omaha', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Mississippi':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Ole Miss', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Pennsylvania':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Penn', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Siena College':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Siena', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'SE Missouri State':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Southeast Missouri State', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'SE Louisiana':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Southeastern Louisiana', ['Rank']]['Rank'].iloc[0]
    elif df_tm == "St. Mary's (CA)":
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == "St. Mary's College", ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Texas A&M-Corpus Christi':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Texas A&M Corpus Christi', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Louisiana-Lafayette':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UL Lafayette', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Massachusetts-Lowell':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Mass-Lowell', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'UMD-Baltimore Cty':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UMBC', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'UNC-Greensboro':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UNC Greensboro', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'USC-Upstate':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'USC Upstate', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Texas-Arlington':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UT Arlington', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Texas-Pan American':
        try:
            lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UT Pan American', ['Rank']]['Rank'].iloc[0]
        except IndexError: # the program merged with Rio Grande Valley at some point
            lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UT Rio Grande Valley', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Texas-San Antonio':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'UT San Antonio', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Va. Commonwealth':
        try:
            lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'VCU', ['Rank']]['Rank'].iloc[0]
        except IndexError:
            lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Virginia Commonwealth', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'Va Military Inst.':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'VMI', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'UW Milwaukee':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Wisconsin-Milwaukee', ['Rank']]['Rank'].iloc[0]
    elif df_tm == 'California Baptist':
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == 'Cal Baptist', ['Rank']]['Rank'].iloc[0]
    else:
        lrdf['teamName'].iloc[i] = rpi.loc[rpi['College'] == df_tm, ['Rank']]['Rank'].iloc[0]

# Condense several seasons into "one" stat line for each player. This is subtle; let's see if it works.
lrdf_condensed = pd.DataFrame(columns=['playerid', 'teamName', 'LeagueAbbr', 
                                            'Bavg', 
                                            'iso', 
                                            'hr_per_ab', 
                                            'sb_per_pa', 
                                            'bb_rate', 
                                            'k_rate', 
                                            'obp', 
                                            'OPS', 
                                            'Slg', 
                                            'Age', 
                                            'HT', 
                                            'WT', 
                                            'Bats', 
                                            'Throws', 
                                            'posit', 
                                            'draft_overall'])

decay = 0.6
for i in lrdf['playerid'].drop_duplicates():
    plyr_df = lrdf[lrdf['playerid'] == i]
    playerid = plyr_df['playerid'].iloc[0]
    team = plyr_df['teamName'].iloc[0]
    league = plyr_df['LeagueAbbr'].iloc[0]
    bats = plyr_df['Bats'].iloc[0]
    throws = plyr_df['Throws'].iloc[0]
    
    plyr_df['weights'] = (decay**(plyr_df['years_before_drafted'])) * np.sqrt(plyr_df['AB'] + plyr_df['BB'] + plyr_df['IBB'] + plyr_df['HBP'] + plyr_df['SH'] + plyr_df['SF'])

    b_avg = np.dot(plyr_df['weights'], plyr_df['Bavg']) / (plyr_df['weights'].sum())
    iso = np.dot(plyr_df['weights'], plyr_df['iso']) / (plyr_df['weights'].sum())
    hr_per_ab = np.dot(plyr_df['weights'], plyr_df['hr_per_ab']) / (plyr_df['weights'].sum())
    sb_per_pa = np.dot(plyr_df['weights'], plyr_df['sb_per_pa']) / (plyr_df['weights'].sum())
    bb_rate = np.dot(plyr_df['weights'], plyr_df['bb_rate']) / (plyr_df['weights'].sum())
    k_rate = np.dot(plyr_df['weights'], plyr_df['k_rate']) / (plyr_df['weights'].sum())
    obp = np.dot(plyr_df['weights'], plyr_df['obp']) / (plyr_df['weights'].sum())
    ops = np.dot(plyr_df['weights'], plyr_df['OPS']) / (plyr_df['weights'].sum())
    slg = np.dot(plyr_df['weights'], plyr_df['Slg']) / (plyr_df['weights'].sum())
    
    draftyr_df = plyr_df.iloc[plyr_df['years_before_drafted'].argmin()]
    
    age = draftyr_df['Age']
    height = draftyr_df['HT']
    weight = draftyr_df['WT']
    pos = draftyr_df['posit']
    draft_ovrl = draftyr_df['draft_overall']
    
    lrdf_condensed = lrdf_condensed.append({'playerid': playerid, 
                                            'teamName': team, 
                                            'LeagueAbbr': league, 
                                            'Bavg': b_avg, 
                                            'iso': iso, 
                                            'hr_per_ab': hr_per_ab, 
                                            'sb_per_pa': sb_per_pa, 
                                            'bb_rate': bb_rate, 
                                            'k_rate': k_rate, 
                                            'obp': obp, 
                                            'OPS': ops, 
                                            'Slg': slg, 
                                            'Age': age, 
                                            'HT': height, 
                                            'WT': weight, 
                                            'Bats': bats, 
                                            'Throws': throws, 
                                            'posit': pos, 
                                            'draft_overall': draft_ovrl}, ignore_index=True)
    

# Excel, and therefore pandas, recognizes height as a date format (6-1 is read as June 1st!). We must fix that
for i in range(len(lrdf_condensed)):
    if lrdf_condensed['HT'].iloc[i] == 'Jun-00':
        lrdf_condensed['HT'].iloc[i] = 6*12
    else:
        try:
            lrdf_condensed['HT'].iloc[i] = datetime.strptime(lrdf_condensed['HT'].iloc[i], '%d-%b')
            lrdf_condensed['HT'].iloc[i] = lrdf_condensed['HT'].iloc[i].month*12 + lrdf_condensed['HT'].iloc[i].day
        except ValueError:
            lrdf_condensed['HT'].iloc[i] = 6*12
        
# Drop rows with np.nan
lrdf_condensed = lrdf_condensed.dropna()
# Drop rows with all zeros
lrdf_condensed = lrdf_condensed[(lrdf_condensed.T != 0).any()]

X = lrdf_condensed.drop(['LeagueAbbr', 'playerid', 'Age', 'draft_overall'], axis=1)
X['teamName'] = X['teamName'].astype(float)
X['WT'] = X['WT'].astype(float)
X['HT'] = X['HT'].astype(float)
X = pd.get_dummies(X)
X = X.astype(float)
X.dtypes

y = lrdf_condensed['draft_overall'].astype(float)

from sklearn.model_selection import train_test_split
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_regression

import matplotlib.pyplot as plt 

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25, random_state=1)

fs = SelectKBest(score_func=f_regression, k='all')
fs.fit(X_train, y_train)
X_train_fs = fs.transform(X_train)
X_test_fs = fs.transform(X_test)

scores = pd.DataFrame(columns=['col', 'score'])
for i in range(len(fs.scores_)):
    col = X_train.columns[i]
    score = fs.scores_[i]
    scores = scores.append({'col': col, 'score': score}, ignore_index=True)
    
plt.bar(scores['col'], scores['score'])
plt.show()

scores = scores.sort_values(by='score', ascending=False)
# The information yielded by this cell gives us feature selection

from sklearn.linear_model import LinearRegression

reg_cols = scores.sort_values(by='score', ascending=False)['col']
#['teamName', 'OPS', 'Slg', 'iso', 'Bavg', 'obp', 'hr_per_ab', 'k_rate', 'posit_SS', 'sb_per_pa', 'posit_2B']
X_gotime = X_train[reg_cols]

reg = LinearRegression(fit_intercept=True).fit(X_gotime, y_train)
((reg.predict(X_test[reg_cols]) - y_test)**2).sum() #MSE
