import pandas as pd
import numpy as np
import re
from scipy import stats
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 100)
pd.set_option('display.max_colwidth', 20)

handle = open(u'university_towns.txt', 'r')

data =[]
for line in handle :
    match = re.findall('([A-Za-z\s]*)\[edit\]', line)
    if len(match) > 0 :
        state = match
    match2 = re.findall(u'([.A-Za-z,\s"]*\u2014*-*[.A-Za-z,\s"]*)\s\([\s\S]*', line) or re.findall('^[\s\S]*:', line) or re.findall('^([A-Za-z,\s".-]*)\n', line)
    if len(match2) > 0 :
        region = match2
        data.append((state[0],region[0]))

uni_df = pd.DataFrame(data, columns=['State', 'RegionName'])

#Recession start
GDP = pd.read_excel('gdplev.xls', skiprows = 7).rename(columns=
                               {
                                'Unnamed: 4':'Quarter', 
                                'Unnamed: 6':'GDP'
                                })
dfGDP = GDP.filter(['Quarter','GDP']).set_index(['Quarter'])[212:]
dfGDP_diff = dfGDP.diff().mask(dfGDP.diff() < 0 , 0).mask(dfGDP.diff() > 0 , 1)
dfGDP_dd = dfGDP_diff.diff()

loci = dfGDP_dd['GDP'].iloc
for i in range(0, len(dfGDP_dd)) :
    if loci[i] == -1 and loci[i+1] == 0 :
        recession_start = dfGDP_dd['GDP'].index[i]
    if loci[i] == 1 and loci[i-1] == 0 and loci[i+1] == 0 :
        recession_end = dfGDP_dd['GDP'].index[i+1]

recession_low = dfGDP['GDP'].loc[recession_start : recession_end].idxmin()

allhomes = pd.read_csv('City_Zhvi_AllHomes.csv')

states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa',
          'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 
          'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 
          'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 
          'IL': 'Illinois', 'TN': 'Tennessee', 
          'DC': 'District of Columbia', 'VT': 'Vermont', 
          'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 
          'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 
          'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 
          'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 
          'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 
          'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 
          'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 
          'WV': 'West Virginia', 'SC': 'South Carolina', 
          'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 
          'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 
          'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 
          'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 
          'MN': 'Minnesota', 'VI': 'Virgin Islands', 
          'NH': 'New Hampshire', 'MA': 'Massachusetts', 
          'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'
          }
allhomes['State'].replace(states, inplace = True)
allhomes.set_index(["State","RegionName"],inplace=True)
allhomes = allhomes.iloc[:, 49:249]

homesbyQT = allhomes.groupby(pd.PeriodIndex(allhomes.columns, freq='q'), axis=1).mean()
homesbyQT = homesbyQT.sort_index().rename(columns=lambda x: str(x).lower())

#prep for t-test
#University housing, drop all except recession, difference:low-start
unidf = uni_df.set_index(["State","RegionName"]).sort_index()
uni_housing = pd.merge(unidf, homesbyQT, how = "inner",
                                  left_index = True, right_index = True)
uni_recess = uni_housing.filter([recession_start,recession_low]).dropna()

uni_recess['Ratio'] = uni_recess[recession_start]/uni_recess[recession_low]

#non-university housing, drop all except recession, difference:low-start
non_merge = pd.merge(unidf, homesbyQT, how = "right",
                                  left_index = True, right_index = True, indicator=True)
non_uni_housing = non_merge[(non_merge['_merge']=='right_only')].drop(['_merge'],axis=1)
non_uni_recess = non_uni_housing.filter([recession_start,recession_low]).dropna()

non_uni_recess['Ratio'] = non_uni_recess[recession_start]/non_uni_recess[recession_low]

def run_t_test():
    statistic, p = stats.ttest_ind(uni_recess['Ratio'],non_uni_recess['Ratio'])
    if p < 0.01 :
        different=True
    else:
        different=False
        
    if non_uni_recess['Ratio'].mean() > uni_recess['Ratio'].mean() :
        better = 'university town'
    else :
        better = 'non-university town'
    return (different, p, better)
a = run_t_test()

#for year in range(2000,2017) :
#    for quarter in range(1,5) :
#        print('{}q{}'.format(year,quarter))        
#for year in range(2000,2017) :
#    for month in range(1,13) :
#        column = '{}-{:02d}'.format(year,month)
#inv_states = {v: k for k, v in states.items()} 

 