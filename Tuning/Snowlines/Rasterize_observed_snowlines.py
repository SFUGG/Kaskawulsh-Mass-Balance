# -*- coding: utf-8 -*-
"""
Created on Thu Mar  2 17:06:32 2023

A script for plotting picked snowlines on KW

@author: katierobinson
"""

import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import pandas as pd
import sys
from netCDF4 import Dataset
sys.path.insert(1,'F:\Mass Balance Model\Kaskawulsh-Mass-Balance\RunModel')
from Model_functions_ver4 import regridXY_something
from Model_functions_ver4 import KWtributaries

# load in one file at a time (loop through the list of images that are completed)
# change this: load the list of files within each directory in the main dorectory:
# if tehe folder is verified,, open it and get the csv snowlines out.

filepath = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/Tuning/Snowlines/Snowlines_FINAL'
#get list of files in this directory:


# =============================================================================
# Function to load snowline info from csv files and convert to lists
# =============================================================================
def snowlines_from_csv(filepath):
    '''
    filepath is the path the the main directory where all the snowlines are stored.
    '''
    # set up containers to hold outputs from each snowline
    snowline_name = []
    easting = []
    northing = []
    elevation = []
    sfc_type = []
    
    folderlist = os.listdir(filepath)
    for folder in folderlist:
        if folder[-8:] == 'Verified':
            # go inside that folder 
            folderpath = os.path.join(filepath,folder)
            # get all csv files (# of csv's?)
            filelist = os.listdir(folderpath)
            # for each of the csv's, save the name, x, y, z, sfc type. 
            for file in filelist:
                if '.csv' in file:
                    #print(file)
                    snowline_name.append(file[:-4])
                    
                    csvfile = os.path.join(folderpath,file)
                    snowlinedata = np.loadtxt(csvfile,delimiter=',',skiprows=1,dtype='str')
                    x = np.array(snowlinedata[:,0],dtype=float)
                    easting.append(x)
                    
                    y = np.array(snowlinedata[:,1],dtype=float)
                    northing.append(y)
                    
                    z = np.array(snowlinedata[:,2],dtype=float)
                    elevation.append(z)
                    
                    sfc = np.array(snowlinedata[:,3])
                    sfc_type.append(sfc)
                    # add line to delete off-glacier cells from all arrays
                
            
        else:
            pass
        
    return np.array(snowline_name), easting, northing, elevation, sfc_type
   
# =============================================================================
# Get coordinate info about each snowline
# =============================================================================
snowline_name, easting, northing, elevation, snowline_sfc_type = snowlines_from_csv(filepath)


# =============================================================================
# Load coordinate info for modelling grid
# =============================================================================
Glacier_ID = 'KRH'

Easting_grid = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/Downscaling/KRH_Xgrid.txt' # Paths to text files defining Easting/Northing coords of every model gridcell
Northing_grid = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/Downscaling/KRH_Ygrid.txt'
Sfc_grid = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/RunModel/KRH_SfcType.txt'      # Path to text file where 1 = off-glacier, 0 = on-glacier, NaN = not in the domain.
Elev_inputs = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SurfaceZ/Zgrids'

Xgrid = np.loadtxt(Easting_grid)
Ygrid = np.loadtxt(Northing_grid)
Sfc = np.loadtxt(Sfc_grid)
Zgrid = np.loadtxt(os.path.join(Elev_inputs,'DEM_' + str(Glacier_ID) + '_' + str(2018) + '.txt'))
    

Catchmentoutline = np.array(Sfc)
Catchmentoutline[np.where(np.isfinite(Sfc))] = 0
Catchmentoutline[np.where(np.isnan(Sfc))] = 1

KRH_tributaries = np.loadtxt('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/RunModel/KRH_Tributaries.txt')
nanlocs = np.where(np.isnan(KRH_tributaries))

# =============================================================================
# Plot ALL snowlines that were delineated
# =============================================================================

def plot_KW_Zgrid():
    plt.contourf(Xgrid,Ygrid,Zgrid,cmap = 'Greys_r',levels=np.linspace(600,4000,35))
    legend = plt.colorbar()
    plt.axis('equal') 
    legend.ax.set_ylabel('Elevation (m a.s.l.)', rotation=270,fontsize=14,labelpad=20)
    plt.xlabel('Easting',fontsize=14)
    plt.ylabel('Northing',fontsize=14)
    plt.show

plt.figure(figsize=(10,6))
plt.title('All Snowlines',fontsize=14)
plot_KW_Zgrid()
colors = plt.cm.Blues(np.linspace(0,1,len(snowline_name)))
for i in range(0,len(snowline_name)):
    plt.scatter(easting[i],northing[i],s=3,label=snowline_name[i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
#plt.savefig('allsnowlines.png',bbox_inches='tight')

# =============================================================================
# Function to get a subset of snowlines from any years, tributaries, U/L bounds, months, etc.
# =============================================================================

def get_subset_of_snowlines(years,trib,UL,month='Any'):
    '''
    run snowlines_from_csv function first to get list of snowlines, easting, northing, etc.
    year = desired year(s)
    trib = (string) desired tributary: 'NA', 'CA', 'SW', 'SA'
    U/L = Upper (U) or Lower (L) snowline: 'U', 'L'
    '''
    snowline_subset = []
    x = []
    y = []
    z = []
    sfc = []
    date = []
    
    if month == 'Any':
        for year in years:
            #print(y)
            for n in snowline_name:
                if n[:4] == str(year):
                    #print(n)
                    if n[11:13] == trib:
                        #print(n)
                        if n[14] == UL:
                            #print(n)
                            index = np.where(snowline_name == n)[0][0]
                            snowline_subset.append(n)
                            x.append(easting[index])
                            y.append(northing[index])
                            z.append(elevation[index])
                            sfc.append(snowline_sfc_type[index])
                            date.append(n[0:10])
                            
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
    else:
        for year in years:
            for n in snowline_name:
                if n[:4] == str(year):
                    #print(n)
                    if int(n[5:7]) == month:
                        if n[11:13] == trib:
                            #print(n)
                            if n[14] == UL:
                                #print(n)
                                index = np.where(snowline_name == n)[0][0]
                                snowline_subset.append(n)
                                x.append(easting[index])
                                y.append(northing[index])
                                z.append(elevation[index])
                                sfc.append(snowline_sfc_type[index])
                                date.append(n[0:10])
                                
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
        
    return snowline_subset, x, y, z, date, sfc
    
# Plotting all SA_L snowlines
snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'SA','L')
plt.figure(figsize=(10,6))
plt.title('South Arm Upper Snowlines (2013-2019)',fontsize=14)
plot_KW_Zgrid()
colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
for i in range(0,len(snowlines_subset[0])):
    plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(2.0, 1.15))

# Plotting just the snowlines for a specific tributary, month and year (July 2018)
snowlines_subset = get_subset_of_snowlines([2018],'SA','L',7)
plt.figure(figsize=(10,6))
plt.title('South Arm Lower Snowlines (2018)',fontsize=14)
plot_KW_Zgrid()
colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
for i in range(0,len(snowlines_subset[0])):
    plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))

# Plotting all the upper bounds for a specific month in any year:
plt.figure(figsize=(10,6))
plt.title('August Upper Snowlines (2013--2019)',fontsize=14)
plot_KW_Zgrid()
snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'SA','U',8)
colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
for i in range(0,len(snowlines_subset[0])):
    plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'SW','U',8)
colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
for i in range(0,len(snowlines_subset[0])):
    plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'NA','U',8)
colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
for i in range(0,len(snowlines_subset[0])):
    plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'CA','U',8)
colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
for i in range(0,len(snowlines_subset[0])):
    plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[i])
plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))


plt.figure(figsize=(10,6))
plt.title('Upper Snowlines (2013--2019)',fontsize=14)
plot_KW_Zgrid()
colors = ['red','gold','lime','turquoise','blue','blueviolet']
for month in range(5,11):
    snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'SA','U',month)
    #colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
    for i in range(0,len(snowlines_subset[0])):
        plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[month-5])
    plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
    snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'SW','U',month)
    #colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
    for i in range(0,len(snowlines_subset[0])):
        plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[month-5])
    plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
    snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'NA','U',month)
    #colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
    for i in range(0,len(snowlines_subset[0])):
        plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[month-5])
    plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))
    snowlines_subset = get_subset_of_snowlines(np.arange(2007,2020),'CA','U',month)
    #colors = plt.cm.Blues(np.linspace(0,0.5,len(snowlines_subset[0])))
    for i in range(0,len(snowlines_subset[0])):
        plt.scatter(snowlines_subset[1][i],snowlines_subset[2][i],s=3,label=snowlines_subset[0][i],color=colors[month-5])
    plt.legend(ncol=3,bbox_to_anchor=(1.25, 1.15))

# =============================================================================
# Get mean elevation of each snowline (upper and lower bounds) for each tributary
# =============================================================================

def mean_snowline(snowlines_subset):
# Get mean snowline elevation:
    snowline_names = snowlines_subset[0]
    elevation = snowlines_subset[3]
    mean_snowline_z = []
    dates = []
    sfc_type = []
    
    # get sfc type bool:
    for sfc in snowlines_subset[5]:
        sfc_list = []
        for i in sfc:
            if len(i) > 1:
                sfc_list.append(int(i[1]))
            else:
                sfc_list.append(int(i))
        sfc_type.append(sfc_list)
    
    i = 0
    for z in elevation:
        zz = np.array(z)
        offglacier = np.where(np.array(sfc_type[i][0])==1)
        zz[offglacier] = np.nan
        mean_z = np.nanmean(zz)
        mean_snowline_z.append(mean_z)
        i += 1
        
    for date in snowline_names:
        dates.append(np.datetime64(date[:10]))
        
    return snowline_names, dates, mean_snowline_z

z_SW_L = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'SW','L'))
z_SW_U = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'SW','U'))

z_SA_L = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'SA','L'))
z_SA_U = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'SA','U'))

z_CA_L = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'CA','L'))
z_CA_U = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'CA','U'))

z_NA_L = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'NA','L'))
z_NA_U = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'NA','U'))

z_TR_L = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'TR','L'))
z_TR_U = mean_snowline(get_subset_of_snowlines(np.arange(2013,2020),'TR','U'))

# =============================================================================
# Plot the mean snowline elevations for each trib for all dates 
# =============================================================================

def combined_dates_barplot(z_U,z_L,AllDates=False):
    if AllDates == False:
        dates = list( dict.fromkeys(sorted(z_U[1]+z_L[1])) )
        width = 0.8
    else:
        dates = list( dict.fromkeys(sorted(z_SW_L[1]+z_SW_U[1]+z_SA_L[1]+z_SA_U[1]+z_CA_L[1]+z_CA_U[1]+z_NA_L[1]+z_NA_U[1]+z_TR_L[1]+z_TR_U[1])) )
        width = 0.7
    
    new_z_L = np.zeros(len(dates))
    new_z_U = np.zeros(len(dates))
    for i in range(0,len(dates)):
        date = dates[i]
        Upper_ind = np.where(z_U[1]==date)[0]
        if len(Upper_ind) == 0:
            pass
        else:
            new_z_U[i] = z_U[2][Upper_ind[0]]
            
        Lower_ind = np.where(z_L[1]==date)[0]
        if len(Lower_ind) == 0:
            pass
        else:
            new_z_L[i] = z_L[2][Lower_ind[0]]
    
    plt.bar(np.arange(0,len(dates)),new_z_U,width=width,label='Upper Boundary',color='lightskyblue')
    plt.bar(np.arange(0,len(dates)),new_z_L,width=width,label='Lower Boundary',color='grey')
    plt.xlim(-1,len(dates))
    plt.ylim(650,2600)
    plt.xticks(ticks=np.arange(0,len(dates),4),labels=dates[::4],rotation=45)
    plt.ylabel('Elevation (m a.s.l.)',fontsize=13)
    #plt.plot([dates[0],dates[-1]],[2000,2000])

fig = plt.figure(figsize=(12,8))
plt.subplot(2,3,1)
plt.title('North Arm',fontsize=14)
combined_dates_barplot(z_NA_U,z_NA_L)
fig.legend(bbox_to_anchor=(0.9,0.4),fontsize=15)
plt.subplot(2,3,2)
plt.title('Central Arm',fontsize=14)
combined_dates_barplot(z_CA_U,z_CA_L)
plt.subplot(2,3,3)
plt.title('Stairway Glacier',fontsize=14)
combined_dates_barplot(z_SW_U,z_SW_L)
plt.subplot(2,3,4)
plt.title('South Arm',fontsize=14)
combined_dates_barplot(z_SA_U,z_SA_L)
plt.subplot(2,3,5)
plt.title('Trunk',fontsize=14)
combined_dates_barplot(z_TR_U,z_TR_L)
plt.tight_layout()
#plt.savefig('Snowlines_histogram_combined_dates.png')

fig = plt.figure(figsize=(12,8))
plt.subplot(2,3,1)
plt.title('North Arm',fontsize=14)
combined_dates_barplot(z_NA_U,z_NA_L,AllDates=True)
fig.legend(bbox_to_anchor=(0.9,0.4),fontsize=15)
plt.subplot(2,3,2)
plt.title('Central Arm',fontsize=14)
combined_dates_barplot(z_CA_U,z_CA_L,AllDates=True)
plt.subplot(2,3,3)
plt.title('Stairway Glacier',fontsize=14)
combined_dates_barplot(z_SW_U,z_SW_L,AllDates=True)
plt.subplot(2,3,4)
plt.title('South Arm',fontsize=14)
combined_dates_barplot(z_SA_U,z_SA_L,AllDates=True)
plt.subplot(2,3,5)
plt.title('Trunk',fontsize=14)
combined_dates_barplot(z_TR_U,z_TR_L,AllDates=True)
plt.tight_layout()
#plt.savefig('Snowlines_histogram_all_dates.png')

# =============================================================================
# Plot mean (2013--2019) monthly snowline elevations
# =============================================================================

# Calculate mean monthly snowline
# get mean monthly elev:
def mean_monthly_snowline(meansnowlines_list):
    mean_monthly_elev = []
    mean_monthly_std = []
    for m in range(3,12):
        mean_sl_elevs = []
        for d in range(0,len(meansnowlines_list[1])):
            date = meansnowlines_list[1][d]
            if date.astype(object).month == m:
                mean_sl_elevs.append(meansnowlines_list[2][d])
            else:
                pass
        
        mean_monthly_elev.append(np.mean(mean_sl_elevs))
        mean_monthly_std.append(np.std(mean_sl_elevs))

    return mean_monthly_elev, mean_monthly_std

plt.figure(figsize=(8,6))
plt.title('Mean (2013--2019) Monthly Snowline Elevation',fontsize=14)
x = np.arange(1,10)
width = 0.16
plt.bar(x-0.32,mean_monthly_snowline(z_TR_U)[0],width=width,color='mediumpurple')
plt.bar(x-0.32,mean_monthly_snowline(z_TR_L)[0],width=width,color='rebeccapurple',label='Trunk')
plt.bar(x-0.16,mean_monthly_snowline(z_SA_U)[0],width=width,color='lightskyblue')
plt.bar(x-0.16,mean_monthly_snowline(z_SA_L)[0],width=width,color='steelblue',label='South Arm')
plt.bar(x,mean_monthly_snowline(z_SW_U)[0],width=width,color='pink')
plt.bar(x,mean_monthly_snowline(z_SW_L)[0],width=width,color='palevioletred',label='Stairway')
plt.bar(x+0.16,mean_monthly_snowline(z_CA_U)[0],width=width,color='gold')
plt.bar(x+0.16,mean_monthly_snowline(z_CA_L)[0],width=width,color='goldenrod',label='Central Arm')
plt.bar(x+0.32,mean_monthly_snowline(z_NA_U)[0],width=width,color='mediumseagreen')
plt.bar(x+0.32,mean_monthly_snowline(z_NA_L)[0],width=width,color='green',label='North Arm')
plt.xticks(x,labels=['Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov'],fontsize=14,rotation=45)
plt.legend(fontsize=14,bbox_to_anchor=(1.05,1))
plt.ylim(650,2600)
plt.yticks(fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
#plt.savefig('Mean_monthly_snowline_elevation.png',bbox_inches='tight')

# =============================================================================
# Find images where all 4 tributaries have snowlines delineated
# =============================================================================

plottingcsv = np.loadtxt('C:/Users/agribbon/OneDrive - Simon Fraser University (1sfu)/Mantek_Snowlines/Plotting_CSV/Plotting_data.csv',delimiter=',',skiprows=1,dtype='str')
dates_with_all_tribs = []
for row in plottingcsv:
    if row[2] == '1':
        if row[3] == '1':
            if row[4] == '1':
                if row[5] == '1':
                    print(row[0])
                    dates_with_all_tribs.append(row[0])
                else:
                    pass
            else:
                pass
        else:
            pass
    else:
        pass

def get_snowlines_for_date(dates):
    '''
    function to rasterize a satellite image with delineated snowlines.
    Returns raster that can be used to compare with modelled snowlines.
    Key for output raster:
    2 = snow covered
    1 = transition zone
    0 = ice
    nan = off glacier
    -0.5 = NO INFORMATION - DO NOT COUNT IN MOD VS OBS COMPARISON
    '''
    NAu_list = []
    NAl_list = []
    CAu_list = []
    CAl_list = []
    SWu_list = []
    SWl_list = []
    SAu_list = []
    SAl_list = []
    for date in dates:
        
        if len(np.where(snowline_name == date + '_NA_U')[0]) == 0:
            NAu = np.nan
        else:
            NAu = np.nanmean(elevation[np.where(snowline_name == date + '_NA_U')[0][0]])
        
        if len(np.where(snowline_name == date + '_NA_L')[0]) == 0:
            NAl = np.nan
        else:
            NAl = np.nanmean(elevation[np.where(snowline_name == date + '_NA_L')[0][0]])
        
        if len(np.where(snowline_name == date + '_CA_U')[0]) == 0:
            CAu = np.nan
        else:
            CAu = np.nanmean(elevation[np.where(snowline_name == date + '_CA_U')[0][0]])
        
        if len(np.where(snowline_name == date + '_CA_L')[0]) == 0:
            CAl = np.nan
        else:
            CAl = np.nanmean(elevation[np.where(snowline_name == date + '_CA_L')[0][0]])
        
        if len(np.where(snowline_name == date + '_SW_U')[0]) == 0:
            SWu = np.nan
        else:
            SWu = np.nanmean(elevation[np.where(snowline_name == date + '_SW_U')[0][0]])
            
        if len(np.where(snowline_name == date + '_SW_L')[0]) == 0:
            SWl = np.nan
        else:
            SWl = np.nanmean(elevation[np.where(snowline_name == date + '_SW_L')[0][0]])
        
        if len(np.where(snowline_name == date + '_SA_U')[0]) == 0:
            SAu = np.nan
        else:
            SAu = np.nanmean(elevation[np.where(snowline_name == date + '_SA_U')[0][0]])
            
        if len(np.where(snowline_name == date + '_SA_L')[0]) == 0:
            SAl = np.nan
        else:
            SAl = np.nanmean(elevation[np.where(snowline_name == date + '_SA_L')[0][0]])
            
        NAu_list.append(NAu)
        NAl_list.append(NAl)
        CAu_list.append(CAu)
        CAl_list.append(CAl)
        SWu_list.append(SWu)
        SWl_list.append(SWl)
        SAu_list.append(SAu)
        SAl_list.append(SAl)
        
        
    return NAu_list,NAl_list,CAu_list,CAl_list,SWu_list,SWl_list,SAu_list,SAl_list

plt.figure(figsize=(8,6))
data = get_snowlines_for_date(dates_with_all_tribs)
x = np.arange(0,len(dates_with_all_tribs))
width = 0.2
for date in dates_with_all_tribs:
    z = get_snowlines_for_date(date)
    plt.bar(x-0.3,data[6],width=width,color='lightskyblue')
    plt.bar(x-0.3,data[7],width=width,color='steelblue',label='South Arm')
    plt.bar(x-0.1,data[4],width=width,color='pink')
    plt.bar(x-0.1,data[5],width=width,color='palevioletred',label='Stairway')
    plt.bar(x+0.1,data[2],width=width,color='gold')
    plt.bar(x+0.1,data[3],width=width,color='goldenrod',label='Central Arm')
    plt.bar(x+0.3,data[0],width=width,color='mediumseagreen')
    plt.bar(x+0.3,data[1],width=width,color='green',label='North Arm')
    if date==dates_with_all_tribs[0]:
        plt.legend(fontsize=14,bbox_to_anchor=(1.06,1))
    else:
        pass
plt.ylim(1500,2500)
plt.yticks(fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.xticks(x,dates_with_all_tribs,rotation=270,fontsize=14)

# =============================================================================
# Calculate area of each tributary:
# =============================================================================

#SA = 1
#SW = 2
#CA = 3
#NA = 4
#Trunk = 5
totalarea = len(np.where(~np.isnan(KRH_tributaries))[0])*(0.2*0.2) # km^2
SAarea = np.round(len(np.where(KRH_tributaries==1)[0])*(0.2*0.2),1) # km^2
SWarea = np.round(len(np.where(KRH_tributaries==2)[0])*(0.2*0.2),1) # km^2
CAarea = np.round(len(np.where(KRH_tributaries==3)[0])*(0.2*0.2),1) # km^2
NAarea = np.round(len(np.where(KRH_tributaries==4)[0])*(0.2*0.2),1) # km^2
TRarea = np.round(len(np.where(KRH_tributaries==5)[0])*(0.2*0.2),1) # km^2

def area_percent(tribarea):
    percent = np.round(((tribarea/totalarea)*100),1)
    return '(' + str(percent) + ' %)'


plt.figure(figsize=(9,6))
plt.contourf(Xgrid,Ygrid,KRH_tributaries,cmap='Accent',levels=np.arange(0,6))
#plt.colorbar()
plt.axis('equal')
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.tight_layout()
plt.text(568000,6715000,'North Arm = ' + str(NAarea) + ' km$^2$ ' + area_percent(NAarea),fontsize=14,color='deeppink')
plt.text(568000,6713000,'Central Arm = ' + str(CAarea) + ' km$^2$ ' + area_percent(CAarea),fontsize=14,color='mediumblue')
plt.text(568000,6711000,'Stairway = ' + str(SWarea) + ' km$^2$ ' + area_percent(SWarea),fontsize=14,color='sandybrown')
plt.text(568000,6709000,'South Arm = ' + str(SAarea) + ' km$^2$ ' + area_percent(SAarea),fontsize=14,color='lightgreen')
plt.text(568000,6707000,'Trunk = ' + str(TRarea) + ' km$^2$ ' + area_percent(TRarea),fontsize=14,color='dimgrey')
#plt.savefig('KW_tributaries.png')


plt.figure(figsize=(8,6))
plt.contourf(Xgrid,Ygrid,Sfc)
plt.contourf(Xgrid,Ygrid,KRH_tributaries,cmap='Accent',levels=np.arange(0,6))
plt.axis('equal')
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
#plt.savefig('Catchment_tributaries.png')

# =============================================================================
# GET RASTERIZED OBSERVED SNOWLINES
# =============================================================================

def rasterize_observed_snowline(Zgrid,date):
    '''
    function to rasterize a satellite image with delineated snowlines.
    Returns raster that can be used to compare with modelled snowlines.
    Key for output raster:
    2 = snow covered
    1 = transition zone
    0 = ice
    nan = off glacier
    -0.5 = NO INFORMATION - DO NOT COUNT IN MOD VS OBS COMPARISON
    '''
    Zgrid[nanlocs] = np.nan
    
    if len(np.where(snowline_name == date + '_NA_U')[0]) == 0:
        NAu = np.nan
    else:
        NAu = np.nanmean(elevation[np.where(snowline_name == date + '_NA_U')[0][0]])
    
    if len(np.where(snowline_name == date + '_NA_L')[0]) == 0:
        NAl = np.nan
    else:
        NAl = np.nanmean(elevation[np.where(snowline_name == date + '_NA_L')[0][0]])
    
    if len(np.where(snowline_name == date + '_CA_U')[0]) == 0:
        CAu = np.nan
    else:
        CAu = np.nanmean(elevation[np.where(snowline_name == date + '_CA_U')[0][0]])
    
    if len(np.where(snowline_name == date + '_CA_L')[0]) == 0:
        CAl = np.nan
    else:
        CAl = np.nanmean(elevation[np.where(snowline_name == date + '_CA_L')[0][0]])
    
    if len(np.where(snowline_name == date + '_SW_U')[0]) == 0:
        SWu = np.nan
    else:
        SWu = np.nanmean(elevation[np.where(snowline_name == date + '_SW_U')[0][0]])
        
    if len(np.where(snowline_name == date + '_SW_L')[0]) == 0:
        SWl = np.nan
    else:
        SWl = np.nanmean(elevation[np.where(snowline_name == date + '_SW_L')[0][0]])
    
    if len(np.where(snowline_name == date + '_SA_U')[0]) == 0:
        SAu = np.nan
    else:
        SAu = np.nanmean(elevation[np.where(snowline_name == date + '_SA_U')[0][0]])
        
    if len(np.where(snowline_name == date + '_SA_L')[0]) == 0:
        SAl = np.nan
    else:
        SAl = np.nanmean(elevation[np.where(snowline_name == date + '_SA_L')[0][0]])
        
    if len(np.where(snowline_name == date + '_TR_U')[0]) == 0:
        TRu = np.nan
        TRu_min = np.nan
    else:
        TRu = np.nanmean(elevation[np.where(snowline_name == date + '_TR_U')[0][0]])
        TRu_min = np.nanmin(elevation[np.where(snowline_name == date + '_TR_U')[0][0]])
        
    if len(np.where(snowline_name == date + '_TR_L')[0]) == 0:
        TRl = np.nan
        TRl_min = np.nan
    else:
        TRl = np.nanmean(elevation[np.where(snowline_name == date + '_TR_L')[0][0]])
        TRl_min = np.nanmin(elevation[np.where(snowline_name == date + '_TR_L')[0][0]])
    
    obs_snowline = np.empty(Zgrid.shape)
    obs_snowline[:] = -0.5
    # 2 = snow covered
    # 1 = transition zone
    # 0 = ice
    # nan = off glacier
    # -0.5 = NO INFORMATION - DO NOT COUNT IN MOD VS OBS COMPARISON

    for i in range(0,len(Zgrid)): # For every cell in the domain
        for j in range(0,len(Zgrid[1])):
            if np.isnan(KRH_tributaries[i][j]): # If the cell is off glacier, skip.
                pass
            
            elif KRH_tributaries[i][j] == 1: #If the cell is in South Arm:
                upperbound = SAu
                if np.isnan(upperbound): # If there's no upper bound on SA but there is on TR:
                    if ~np.isnan(TRu): 
                        if (TRu_min < np.min(Zgrid[KRH_tributaries==1])): # And if the min elev of TR_U is below SA:
                            upperbound = TRu_min  # Set SA_U = min(TR_U)
                    else:
                        pass
                else:
                    pass
                
                
                lowerbound = SAl
                if np.isnan(lowerbound): # If there is no lower bound on SA but there is on TR:
                    if ~np.isnan(TRl):
                        if (TRl_min < np.min(Zgrid[KRH_tributaries==1])): # And if the min elev of TR_L is below SA
                            lowerbound = TRl_min # Set SA_L = min(TR_L)
                    else:
                        pass
                else:
                    pass      
                
            elif KRH_tributaries[i][j] == 2: #If the cell is in Stairway:
                upperbound = SWu
                if np.isnan(upperbound): # If there's no upper bound on SW but there is on TR:
                    if ~np.isnan(TRu): 
                        if (TRu_min < np.min(Zgrid[KRH_tributaries==2])): # And if the min elev of TR_U is below SW:
                            upperbound = TRu_min  # Set SW_U = min(TR_U)
                    else:
                        pass
                else:
                    pass
                
                
                lowerbound = SWl
                if np.isnan(lowerbound): # If there is no lower bound on SW but there is on TR:
                    if ~np.isnan(TRl):
                        if (TRl_min < np.min(Zgrid[KRH_tributaries==2])): # And if the min elev of TR_L is below SW
                            lowerbound = TRl_min # Set SW_L = min(TR_L)
                    else:
                        pass
                else:
                    pass                    
                
            elif KRH_tributaries[i][j] == 3: #CA
                upperbound = CAu
                if np.isnan(upperbound): # If no upper bound on CA, but there is on TR:
                    if ~np.isnan(TRu):
                        if (TRu_min < np.min(Zgrid[KRH_tributaries==3])): # And if the min elev of TR_U is below CA:
                            upperbound = TRu_min  # Set CA_U = min(TR_U)
                    else:
                        pass
                else:
                    pass
                
                lowerbound = CAl
                if np.isnan(lowerbound): # If there is no lower bound on CA but there is on TR:
                    if ~np.isnan(TRl):
                        if (TRl_min < np.min(Zgrid[KRH_tributaries==3])): # And if the min elev of TR_L is below CA
                            lowerbound = TRl_min # Set CA_L = min(TR_L)
                    else:
                        pass
                else:
                    pass    

            elif KRH_tributaries[i][j] == 4: #NA
                upperbound = NAu 
                if np.isnan(upperbound): # If no upper bound on NA, but there is on TR:
                    if ~np.isnan(TRu):
                        if (TRu_min < np.min(Zgrid[KRH_tributaries==4])): # And if the min elev of TR_U is below NA:
                            upperbound = TRu_min  # Set NA_U = min(TR_U)
                    else:
                        pass
                else:
                    pass
                
                lowerbound = NAl
                if np.isnan(lowerbound): # If there is no lower bound on NA but there is on TR:
                    if ~np.isnan(TRl):
                        if (TRl_min < np.min(Zgrid[KRH_tributaries==4])): # And if the min elev of TR_L is below NA
                            lowerbound = TRl_min # Set NA_L = min(TR_L)
                    else:
                        pass
                else:
                    pass                          
                
            elif KRH_tributaries[i][j] == 5: # TRUNK
                lowerbound = TRl
                upperbound = TRu
                if np.isnan(lowerbound): 
                    if np.isnan(upperbound): # If there is no info for the trunk (e.g. all snowlines are on the tribs
                        if ~np.isnan(NAl):
                            lowerbound = np.nanmin([NAl,CAl]) # If there is a lower bound on NA or CA, then TR_L = the minimum of the two
                        elif ~np.isnan(CAl):
                            lowerbound = np.nanmin([NAl,CAl])  
                        else:
                            lowerbound = np.nanmin([NAl,CAl,SWl,SAl]) # Otherwise TR_L is just the minimum LB between SW and SA
                
                if np.isnan(upperbound): # If there's no upper bound on TR but there is one on NA or CA, then TR_U = max(CA_U,NA_U)
                    if ~np.isnan(NAu):
                        upperbound = np.nanmax([NAu,CAu]) 
                    elif ~np.isnan(CAu):
                        upperbound = np.nanmax([NAu,CAu])  
                    else:
                        pass
                else:
                    pass
                
                # another special case:
                # if there is an upper bound on the trunk, any trib without an upper bound can assume that
                # any area above the upper bound of the trunk is also snow covered.
             
            # determine if the cell is above the upper bound (snow = 2), below the lower bound (ice = 0), or in between (transition = 1)
            z = Zgrid[i][j]
            if ~np.isnan(z):
                # if cell is above upper bound, set to snow
                if ~np.isnan(upperbound):
                    if z >= upperbound:
                        obs_snowline[i][j] = 2
                    else:
                        pass
                else:
                    pass
                # if cell is below lower bound, set to ice
                if ~np.isnan(lowerbound):
                    if z <= lowerbound:
                        obs_snowline[i][j] = 0
                    else:
                        pass
                else:
                    pass
                
                # if cell is between upper and lower bounds, set to transition zone
                # there is only a transition zone if BOTH upper and lower bounds exist
                if ~np.isnan(upperbound):
                    if ~np.isnan(lowerbound):
                        if z > lowerbound:
                            if z < upperbound:
                                obs_snowline[i][j] = 1
                            
    obs_snowline[nanlocs] = np.nan
    np.save('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/Tuning/Snowlines/Rasterized_Observed_Snowlines/SnowlineTarget_' + date + '.npy',obs_snowline)
        
    plt.figure(figsize=(8,6))
    plt.pcolor(Xgrid,Ygrid,obs_snowline,cmap='terrain_r',vmin=-0.75,vmax=2.6)
    #plt.colorbar()
    plt.axis('equal')
    plt.xlabel('Easting',fontsize=14)
    plt.ylabel('Northing',fontsize=14)
    plt.title('Observed Snowline: ' + date,fontsize=14)
    plt.tight_layout()
    plt.savefig('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/Tuning/Snowlines/Rasterized_Observed_Snowlines/SnowlineTarget_' + date + '.png')
    plt.show()
    plt.close()

    
    return obs_snowline

dates = list( dict.fromkeys(sorted(z_SW_L[1]+z_SW_U[1]+z_SA_L[1]+z_SA_U[1]+z_CA_L[1]+z_CA_U[1]+z_NA_L[1]+z_NA_U[1]+z_TR_L[1]+z_TR_U[1])) )
for day in dates:
    print(day)
    Zgrid_y = np.loadtxt(os.path.join(Elev_inputs,'DEM_' + str(Glacier_ID) + '_' + str(day)[0:4] + '.txt'))
    rasterize_observed_snowline(Zgrid_y,str(day))
    sys.stdout.flush()


# =============================================================================
# # =============================================================================
# # GET MODELLED SNOWLINES FOR EACH SIM
# # =============================================================================
# 
# for sim in range(0,12):
#     MB_2015_file = 'D:/Model Runs/Debris Tests/VariableThicknessTest_2007-2018/MB2015' + str(sim) + '.nc'
#     MB_2016_file = 'D:/Model Runs/Debris Tests/VariableThicknessTest_2007-2018/MB2016' + str(sim) + '.nc'
#     MB_in_2015 = Dataset(MB_2015_file, "r")
#     MB_in_2016 = Dataset(MB_2016_file, "r")
#     
#     MB_var = 'MB'
#     
#     MB_2015 = MB_in_2015.variables[MB_var][:]
#     MB_2016 = MB_in_2016.variables[MB_var][:]
#     
#     dates_2015 = pd.date_range(start="2015-01-01",end="2015-12-31 21:00:00",freq='3H')
#     dates_2016 = pd.date_range(start="2016-01-01",end="2016-12-31 21:00:00",freq='3H')
#     
#     snow_depth = np.zeros(MB_2015[0].shape)
#     snow_depth[nanlocs_1] = np.nan
#     
#     start_date = np.where(dates_2015 == '2015-09-01')[0][0]
#     end_date = np.where(dates_2016 == '2016-07-17')[0][0]
#     
#     for i in range(start_date,len(dates_2015)):
#         snow_depth += MB_2015[i]
#         snow_depth[np.where(snow_depth < 0)] = 0
#     for i in range(0,end_date):
#         snow_depth += MB_2016[i]
#         snow_depth[np.where(snow_depth < 0)] = 0
# 
#     #plt.figure(figsize=(9,6))
#     #plt.contourf(Xgrid1,Ygrid1,np.flipud(snow_depth),cmap='BuPu')
#     #legend = plt.colorbar()
#     #legend.ax.set_ylabel('Snow Depth (m w.e.)', rotation=270,fontsize=14,labelpad=20)
#     #plt.axis('equal')
#     #plt.contour(np.flipud(snow_depth), colors = 'black', levels = 0.1)
#     #plt.xlabel('Easting',fontsize=14)
#     #plt.ylabel('Northing',fontsize=14)
#     #plt.title('Modelled Snow Depth\n2015-09-01 - 2016-07-17',fontsize=14)
#     #plt.savefig('ModelledSnowdepth_2016-07-17.png')
#     
#     modelled_snowline = np.zeros(MB_2015[0].shape)
#     
#     modelled_snowline[np.where(snow_depth <=0)] = 0
#     modelled_snowline[np.where(snow_depth >0)] = 2
#     modelled_snowline[nanlocs_1] = np.nan
#     
#     #plt.figure(figsize=(8,6))
#     #plt.pcolor(Xgrid,Ygrid,np.flipud(modelled_snowline),cmap='terrain_r',vmin=-0.75,vmax=2.6)
#     #plt.colorbar()
#     #plt.axis('equal')
#     #plt.xlabel('Easting',fontsize=14)
#     #plt.ylabel('Northing',fontsize=14)
#     #plt.title('Modelled Snowline: 2016-07-17',fontsize=14)
#     #plt.savefig('Modelled_Snowline_2016-07-17.png')
#     
#     # Compare % of matching cells:
#     diff = obs_snowline - modelled_snowline
#     passing_cells = (len(np.where(diff == -1)[0]) + len(np.where(diff == 1)[0]) + len(np.where(diff == 0)[0]))
#     percent = (passing_cells/26314)*100
#     print(percent)
# 
# =============================================================================
