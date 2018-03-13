import pandas as pd
import numpy as np
import re
pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_columns', 10000)
pd.set_option('display.width', 100)
pd.set_option('display.max_colwidth', 15)

#energy
energy = pd.read_excel('Energy Indicators.xls')[16:243]
energy = energy.drop(energy.columns[[0,1]],axis=1).rename(columns=
        {
        'Environmental Indicators: Energy' : 'Country',
        'Unnamed: 3' : 'Energy Supply',
        'Unnamed: 4' : 'Energy Supply per Capita',
        'Unnamed: 5' : '% Renewable'
        }).replace('...', np.nan)
energy['Energy Supply'] *= 1000000                  #peta to giga

for line in energy['Country'] :                    #regex num dlt.
    x = re.sub('\s\([A-Z\s,a-z]*\)','',line)
    energy.replace(line, x, inplace=True)
    y = re.sub('[^A-Z\s,a-z]*','',line)        
    energy.replace(line, y, inplace=True)

energy['Country'].replace(
        {
        'United States of America' : 'United States',
        'United Kingdom of Great Britain and '\
        'Northern Ireland' : 'United Kingdom',
        'Republic of Korea' : 'South Korea',
        'China, Hong Kong Special Administrative Region' : 'Hong Kong'
        },inplace=True)

#GDP
GDP = pd.read_csv('world_bank.csv',skiprows=4)
GDP.rename(columns=
        {
        'Country Name' : 'Country'
        }, inplace=True)

GDP['Country'].replace(
        {
        'Korea, Rep.' : 'South Korea', 
        'Iran, Islamic Rep.' : 'Iran', 
        'Hong Kong SAR, China' : 'Hong Kong'
        }, inplace=True)
#ScimEn, merge, & select
ScimEn = pd.read_excel('scimagojr-3.xlsx')

df = pd.merge(pd.merge(ScimEn, energy, on='Country'), 
              GDP, on='Country').set_index('Country')

df= df[[
        'Rank', 'Documents', 'Citable documents', 'Citations', 
        'Self-citations', 'Citations per document', 'H index', 
        'Energy Supply', 'Energy Supply per Capita', '% Renewable', 
        '2006', '2007', '2008', '2009', '2010', 
        '2011', '2012', '2013', '2014', '2015'
        ]]

df15 = df.loc[df['Rank'] <= 15]
print(df15)
#Union, intersect, and difference between
all = pd.merge(pd.merge(ScimEn, energy, on='Country', how='outer'),
                 GDP, on='Country', how='outer')
common = pd.merge(pd.merge(ScimEn, energy, on='Country', how='inner'),
                 GDP, on='Country', how='inner')
exclude = (all.shape[0]*all.shape[1])-(common.shape[0]*common.shape[1]) #num cells excluded
#exclude2 = (len(energy)+len(GDP)+len(ScimEn)) - len(df)
#exclude = len(all) - len(common)             #num rows excluded    

#Means of top 15 coountries, descending order
cols = [
        '2006', '2007', '2008', '2009', '2010', 
        '2011', '2012', '2013', '2014', '2015'
        ]
top15 = (df15[cols].mean(axis=1)).sort_values(ascending=False).rename('avgGDP')

#Change in GDP from 6th largest GDP
pos6 = top15.index[5]
diffGDP = abs(df15.at[pos6,'2015'] - df15.at[pos6,'2006'])

#Mean energy supply per capita (15)
mnpercap = df15['Energy Supply per Capita'].mean()

#Max % Renewable with country as tuple
tup_per_rnw = (df15['% Renewable'].idxmax(), df15['% Renewable'].max())

#Add column with citation/self-citation ratio, tuple with max
df15['Citation Ratio'] = df15['Self-citations']/df15['Citations']
tup_cit_rat = (df15['Citation Ratio'].idxmax(), df15['Citation Ratio'].max())

#Population estimate from energy ratio E/(E/p), 3rd most populous
df15['Population (est)'] = df15['Energy Supply']/df15['Energy Supply per Capita']
pop_est3 = df15.sort_values(by='Population (est)', ascending=False).index[2]

#Citable documents per cap, correlation btw citable docs/energy per cap
df15['Citable docs per Capita'] = df15['Citable documents'] / df15['Population (est)']
pearson = df15['Citable docs per Capita'].corr(df15['Energy Supply per Capita'])

#1 or 0 if
med = df15['% Renewable'].median()
df15['HighRenew'] = df15['% Renewable']
df15['HighRenew'] = df15['HighRenew'].apply(lambda x:1 if x >= med else 0)
df15.sort_values(by='Rank', inplace=True)

#Group by continent, population stats
ContinentDict  = {'China':'Asia', 
                  'United States':'North America', 
                  'Japan':'Asia', 
                  'United Kingdom':'Europe', 
                  'Russian Federation':'Europe', 
                  'Canada':'North America', 
                  'Germany':'Europe', 
                  'India':'Asia',
                  'France':'Europe', 
                  'South Korea':'Asia', 
                  'Italy':'Europe', 
                  'Spain':'Europe', 
                  'Iran':'Asia',
                  'Australia':'Australia', 
                  'Brazil':'South America'}

dfstats = pd.DataFrame({'sum' : df15.groupby(ContinentDict)['Population (est)'].sum(),
                     'size' : df15.groupby(ContinentDict)['Population (est)'].count(),
                     'mean' : df15.groupby(ContinentDict)['Population (est)'].mean(),
                     'std' : df15.groupby(ContinentDict)['Population (est)'].std()})
dfstats = dfstats[['size', 'sum', 'mean', 'std']]

#Cut %renew into 5 bins, group df15 by continent and by 5 new bins
df15 = df15.reset_index()
df15['Continent'] = [ContinentDict[country] for country in df15['Country']]
df15['bins'] = pd.cut(df15['% Renewable'],5)
df15.groupby(['Continent','bins']).size()

#Convert Population (est) format to include commas
df15.set_index('Country',inplace=True)
popest = df15['Population (est)'].apply(lambda x: '{0:,}'.format(x)).rename('PopEst',inplace=True)

#for line in energy['Country'] :
#    x = re.findall('(^[A-Z\s,a-z]*)[0-9]+$',line)
#    if len(x)>0 :
#        print(x)

#for line in energy['Country'] :
#    line = re.sub('[^A-Z\s,a-z]*','',line)

#groups = pd.DataFrame(columns = ['size', 'sum', 'mean', 'std'])
#for group, frame in df15.groupby(ContinentDict):
#    groups.loc[group] = [len(frame), frame['Estimate Population'].sum(),frame['Estimate Population'].mean(),frame['Estimate Population'].std()]