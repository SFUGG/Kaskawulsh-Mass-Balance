# -*- coding: utf-8 -*-
"""
Created on Wed May 18 16:08:00 2022

Download and plot data from NASA Icebride snow radar flyover of the Kaskawulsh May 3 2021
Data is available at https://data.cresis.ku.edu/data/snow/2021_Alaska_SO

@author: katierobinson
"""

import numpy as np
import h5py 
import scipy.io
import mat4py
import matplotlib.pyplot as plt
import utm
import os
import sys
import mat73
sys.path.insert(1,'F:\Mass Balance Model\Kaskawulsh-Mass-Balance\RunModel')
from Model_functions_ver4 import regridXY_something
from Model_functions_ver4 import KWtributaries
from netCDF4 import Dataset


# load .csv file with radar data
radardata = np.loadtxt('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/Data_20210510_03.csv',delimiter=',',skiprows=1)
# load individual variables from the .csv file, eliminate last line since it is a Null value
lat = radardata[:,0][:-1]
lon = radardata[:,1][:-1]
elevation = radardata[:,4][:-1]
depth = radardata[:,6][:-1]/100
frame = radardata[:,5][:-1]

# convert lat/lon to easting/northing:
easting = []
northing = []
for i in range(0,len(lat)):
    x = utm.from_latlon(lat[i],lon[i])
    easting.append(x[0])
    northing.append(x[1])

# get easting, northing, elevation, and accumulation data from Kask model domain
#load easting, northing, elevation:
Path2KWoutline = 'F:\Mass Balance Model\Kaskawulsh-Mass-Balance\RunModel'
File_glacier_in = os.path.join(Path2KWoutline,'kaskonly_deb.txt')
glacier = np.genfromtxt(File_glacier_in, skip_header=1, delimiter=',')
Ix = glacier[:,3] 
Iy = glacier[:,4] 
Ih = glacier[:,2] 
debris_array = glacier[:,6]

#-------Turn vectors into 3D gridded inputs--------------------

Zgrid, Xgrid, Ygrid, xbounds, ybounds = regridXY_something(Ix, Iy, Ih)
nanlocs = np.where(np.isnan(Zgrid))
#Xgrid[nanlocs] = np.nan
#Ygrid[nanlocs] = np.nan
Ygrid_flipped = np.flipud(Ygrid)

#Load final model accumulation field (averaged over all years, sims)
KW_accumulation = 'F:/Mass Balance Model/OUTPUTS/Plots/BaselineDebris/allrunAccumulations_BaselineDebris.npy'
uncorrected_accumulation_file = 'F:/Mass Balance Model/Kaskonly_Downscaled_NoBC/UncorrectedAccumulation.npy'

# plotting code from the PlotOutputs.py file
overall_Accumulation = np.load(KW_accumulation)
distributed_accumulation = np.nanmean(overall_Accumulation, axis = 0)
#distributed_accumulation_flipped = np.flipud(distributed_accumulation)

uncorrected_acc = np.load(uncorrected_accumulation_file)


#PLOT MEAN MASS BALANCE OVER ENTIRE SIMULATION PERIOD:    
plt.figure(figsize=(12,7))
plt.contourf(np.flipud(distributed_accumulation), cmap = 'BuPu', levels = np.linspace(0,10,41))
#plt.contourf((distributed_accumulation_flipped), cmap = 'BuPu', levels = np.linspace(0,10,41))
#plt.contourf(np.flipud(Topo), cmap = 'PuRd', levels = np.linspace(0,4, 20))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.xticks(ticks=[0,50,100,150,200,250,300],labels=[int(Xgrid[0][0]),int(Xgrid[0][50]),int(Xgrid[0][100]),int(Xgrid[0][150]),int(Xgrid[0][200]),int(Xgrid[0][250]),int(Xgrid[0][300])],fontsize=10,rotation=20)
plt.yticks(ticks=[0,50,100,150,200],labels=[int(Ygrid[:,0][0]),int(Ygrid[:,0][50]),int(Ygrid[:,0][100]),int(Ygrid[:,0][150]),int(Ygrid[:,0][200])],fontsize=10,rotation=20)
plt.title('Downscaled & Bias Corrected NARR Accumulation (2007-2018)',fontsize=14)
#plt.savefig('NARRAccumulation.png',bbox_inches = 'tight')

plt.figure(figsize=(12,7))
plt.scatter(easting,northing,c=depth, cmap="BuPu") #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar (2021)',fontsize=14)
#plt.savefig('CReSISAccumulation.png',bbox_inches = 'tight')

NARR_elevation = []
NARR_accumulation = []
NARR_uncorrected_acc = []
NARR_easting = []
NARR_northing = []
for i in range(0,len(Xgrid)):
    for j in range(0,len(Xgrid[1])):
        if np.isnan(Zgrid[i,j]):
            pass
        else:
            NARR_elevation.append(Zgrid[i,j])
            NARR_accumulation.append(distributed_accumulation[i,j])
            NARR_uncorrected_acc.append(uncorrected_acc[i,j])
            NARR_easting.append(Xgrid[i,j])
            NARR_northing.append(Ygrid[i,j])
            #print(Ygrid[i,j])
            #what is wrong with this code!!
    
#----------------------------------------------------------------------------#
# REMOVE WEIRD RADAR POINTS
# METHOD 1: REMOVE THE FULL CROSS SECTION FROM NORTH TO WEST ACROSS THE DOMAIN
s=41000 #this is where wierdness starts
plt.scatter(easting[:s],northing[:s],c=depth[:s], cmap="BuPu") #levels = np.linspace(0,4.5,19))
    
e = 61000 #this is where wierdness ends
plt.scatter(easting[:e],northing[:e],c=depth[:e], cmap="BuPu") #levels = np.linspace(0,4.5,19))    
    
plt.scatter(easting[s:e],northing[s:e],c=depth[s:e], cmap="BuPu") #levels = np.linspace(0,4.5,19))        

badradar_flightpath = depth[s:e]
badradar_flightpath_E = easting[s:e]
badradar_flightpath_N = northing[s:e]    
plt.figure(figsize=(12,7))
plt.scatter(badradar_flightpath_E,badradar_flightpath_N,c=badradar_flightpath, cmap="BuPu") #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar (2021) \n where it flies NW across the domain',fontsize=14)

# change points on the cross KW flight path to NaNs
depth_fixed = np.array(depth)
elevation_fixed = np.array(elevation)
easting_fixed = np.array(easting)
northing_fixed = np.array(northing)

depth_fixed[s:e] = np.nan
elevation_fixed[s:e] = np.nan
easting_fixed[s:e] = np.nan
northing_fixed[s:e] = np.nan

plt.figure(figsize=(12,7))
plt.scatter(easting_fixed,northing_fixed,c=depth_fixed, cmap="BuPu") #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar (2021) \n without the NW cross-section',fontsize=14)
#plt.savefig('CReSISAccumulation.png',bbox_inches = 'tight')

plt.figure(figsize=(10,8))
plt.subplot(1,2,1)
plt.scatter(depth_fixed,elevation)

# METHOD 2: MANUALLY REMOVE FRAMES THAT LOOK WIERD IN THE ECHO: https://data.cresis.ku.edu/data/snow/2021_Alaska_SO/images/20210510_03/
bad_indices = np.array([11,12,13,14,15,25,26,27,28,29,30,31,32,33,34,35,36])
questionable_indices = [16,17,37] #check these ones with gwenn

frame0 = 2021051003000
bad_frames = bad_indices + frame0

for i in bad_frames:
    badpoints = np.where(frame == i)
    depth[badpoints] = np.nan
    elevation[badpoints] = np.nan
    frame[badpoints] = np.nan
    
plt.figure(figsize=(12,7))
plt.scatter(easting,northing,c=depth, cmap="BuPu") #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar (2021)',fontsize=14)
#plt.savefig('CReSISAccumulation.png',bbox_inches = 'tight')
    
plt.figure(figsize=(12,6))
plt.subplot(1,3,1)
plt.scatter(depth,elevation,marker='.')
plt.title('CReSIS Snow Radar (2021)',fontsize=12)
plt.xlabel('Accumulation (m w.e.)',fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.xlim(0,4.5)
plt.ylim(500,3500)
plt.subplot(1,3,2)
plt.scatter(NARR_accumulation,NARR_elevation,marker='.')
plt.title('NARR Accumulation (2007-2018) \n Downscaled + Bias Corrected',fontsize=12)
plt.xlabel('Accumulation (m w.e.)',fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.xlim(0,4.5)
plt.ylim(500,3500)
plt.subplot(1,3,3)
plt.scatter(NARR_uncorrected_acc,NARR_elevation,marker='.')
plt.title('NARR Accumulation (2007-2018) \n Uncorrected',fontsize=12)
plt.xlabel('Accumulation (m w.e.)',fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.xlim(0,4.5)
plt.ylim(500,3500)
#plt.savefig('NARR_CReSISvsElevation.png',bbox_inches = 'tight')

# PLOT THE CRESIS ACC. OVERLAYED ON THE NARR ACCUMULATION
#plt.figure(figsize=(14,7))
#plt.scatter(NARR_easting,np.flipud(NARR_northing),c=NARR_accumulation, cmap="BuPu")
#legend1 = plt.colorbar()
#legend1.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
#plt.scatter(easting,northing,c=depth, facecolor='k',marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
#legend2 = plt.colorbar()
#legend2.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
#plt.xlabel('Easting',fontsize=14)
#plt.ylabel('Northing',fontsize=14)
#plt.title('CReSIS Snow Radar Compared to NARR Accumulation',fontsize=14)
#plt.savefig('NARR_CReSIS_diffcolour.png',bbox_inches = 'tight')

#plt.figure(figsize=(8,5))
#plt.scatter(NARR_easting,np.flipud(NARR_northing),c=NARR_accumulation,cmap="BuPu")
#plt.scatter(easting,northing,c=depth, cmap="BuPu",marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
#legend = plt.colorbar()
#legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
#plt.xlabel('Easting',fontsize=14)
#plt.ylabel('Northing',fontsize=14)
#plt.title('CReSIS Snow Radar Compared to NARR Accumulation',fontsize=14)
#plt.savefig('NARR_CReSIS_samecolours.png',bbox_inches = 'tight')


plt.figure(figsize=(5,7))
plt.scatter(NARR_accumulation,NARR_elevation,marker='.',color='purple')
plt.scatter(depth,elevation,marker='.',color='turquoise')
plt.title('CReSIS Snow Radar (2021)',fontsize=12)
plt.xlabel('Accumulation (m w.e.)',fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.legend(['NARR Accumulation','CReSIS Snow Radar'])
plt.xlim(0,4.5)
plt.ylim(500,4000)
#plt.savefig('NARR_CReSIS_vs_elevation.png',bbox_inches = 'tight')

###########################################################################
Zgrid, EY_Xgrid, EY_Ygrid, xbounds, ybounds = regridXY_something(Ix, Iy, Ih)
nanlocs = np.where(np.isnan(Zgrid))

#Setup debris mask for use in radiation parameters
debris_grid, EY_Xgrid, EY_Ygrid, xbounds, ybounds = regridXY_something(Ix, Iy, debris_array)
debris_m = np.zeros(debris_grid.shape)
debris_m[np.where(debris_grid > 100)] = 1
debris_m[np.where(debris_grid <= 100)] = np.nan
debris_m[nanlocs] = np.nan

EY_Ygrid_flipped = np.flipud(EY_Ygrid) # EY_Ygrid is originally upside down (values decreasing south to north)

def calculate_XYZAcc(Xgrid,Ygrid,Zgrid,Acc_array):
    easting_EY = []
    northing_EY = []
    elevation_EY = []
    acc_EY = []
    for i in range(0,len(Xgrid)):
        for j in range(0,len(Xgrid[1])):
            if np.isnan(Zgrid[i,j]):
                pass
            else:
                easting_EY.append(Xgrid[i,j])
                northing_EY.append(EY_Ygrid_flipped[i,j])
                elevation_EY.append(Zgrid[i,j])
                acc_EY.append(distributed_accumulation[i,j])
    
    return easting_EY,northing_EY,elevation_EY,acc_EY
                
easting_EY = calculate_XYZAcc(Xgrid,EY_Ygrid_flipped,Zgrid,distributed_accumulation)[0]
northing_EY = calculate_XYZAcc(Xgrid,EY_Ygrid_flipped,Zgrid,distributed_accumulation)[1]
elevation_EY = calculate_XYZAcc(Xgrid,EY_Ygrid_flipped,Zgrid,distributed_accumulation)[2]
acc_EY = calculate_XYZAcc(Xgrid,EY_Ygrid_flipped,Zgrid,distributed_accumulation)[3]

plt.figure(figsize=(14,7))
plt.scatter(easting_EY,northing_EY,c=acc_EY,cmap="BuPu")
legend1 = plt.colorbar()
legend1.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.scatter(easting,northing,c=depth, facecolor='k',marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
legend2 = plt.colorbar()
#legend2.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar Compared to NARR Accumulation',fontsize=14)
#plt.savefig('NARR_CReSIS_diffcolour.png',bbox_inches = 'tight')

plt.figure(figsize=(12,7))
plt.scatter(easting_EY,northing_EY,c=acc_EY,cmap="BuPu")
plt.scatter(easting,northing,c=depth, cmap="BuPu",marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar Compared to NARR Accumulation',fontsize=14)
#plt.savefig('NARR_CReSIS_samecolours.png',bbox_inches = 'tight')
        
###############################################################################
# look at 2021 accumulation season only: (Oct1 2020-May 10 2022)
# also check --> how much accumulation in august, september. 
# test: with netsnow2014 and netsnow2011 and netsnow2012

# 1. load net snow 2011 and 2012
def seasonalaccumulation(year1,year2,BC):
    if BC == False:
        Fvar = 'Precipitation'
    else:
        Fvar = 'Net snow'
        
    inF1 = Dataset(year1,'r')
    snowyr1 = inF1.variables[Fvar][:] # has shape (time,y,x)
    
    inF2 = Dataset(year2,'r')
    snowyr2 = inF2.variables[Fvar][:] # has shape (time,y,x)
    
    # calculate total accumulation from oct - jan of year 1
    #use np.nansum(axis=0) to get sum through time
    
    #formula = 8*(DOY-1)
    oct1_DOY= 274 
    oct1 = 8*(oct1_DOY-1)
    
    may10_DOY = 132
    may10 = 8*(may10_DOY-1)
    
    snowoct = np.nansum(snowyr1[oct1:,:,:],axis=0) #units are m.w.e.
    snowmay = np.nansum(snowyr2[:may10,:,:],axis=0)
    
    totalsnow = np.add(snowoct,snowmay)
    nanlocs = np.where(totalsnow == 0)
    totalsnow[nanlocs] = np.nan 
    
    return totalsnow

#snow20112012_noBC = seasonalaccumulation('F:/Mass Balance Model/DownscaledNARR/netSnowkaskonly2011.nc','F:/Mass Balance Model/DownscaledNARR/netSnowkaskonly2012.nc',False)
#snow20112012_BC = seasonalaccumulation('F:/Mass Balance Model/BiasCorrectedInputs/Kaskonly_R2S=1/Prcpkaskonly_BC_2011.nc','F:/Mass Balance Model/BiasCorrectedInputs/Kaskonly_R2S=1/Prcpkaskonly_BC_2011.nc',True)


def accumulationvselevation(Zgrid,Accumulation_Array):
    elevation = []
    accumulation = []
    for i in range(0,len(Zgrid)):
        for j in range(0,len(Zgrid[1])):
            if np.isnan(Zgrid[i,j]):
                pass
            else:
                elevation.append(Zgrid[i,j])
                accumulation.append(Accumulation_Array[i,j])
    
    return accumulation,elevation

#noBC2011 = accumulationvselevation(Zgrid,snow20112012_noBC)
#BC2011 = accumulationvselevation(Zgrid,snow20112012_BC)

# COMPARISON SCATTER PLOT
#plt.figure(figsize=(5,7))
#plt.scatter(noBC2011[0],noBC2011[1],marker='.',color='purple')
#plt.scatter(BC2011[0],BC2011[1],marker='.',color='green')
#plt.scatter(depth,elevation,marker='.',color='turquoise')
#plt.title('Kaskawulsh Accumulation',fontsize=12)
#plt.xlabel('Accumulation (m w.e.)',fontsize=14)
#plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
#plt.legend(['NARR Accumulation (2011) No BC','NARR Accumulation (2011) BC','CReSIS Snow Radar'])
#plt.xlim(0,4.5)
#plt.ylim(500,4000)

# compare cell by cell NARR and Icebridge:
# means we need to calculate nearest neighbour
# icebridge covers less area so it is the "limiting factor"
# for every cell in icebridge, calculate who is the nearest NARR neighbour and record in a list

def nearestneighbour(NARRsnowarray,NASAsnowlist=depth,NASAeasting=easting,NASAnorthing=northing,xgrid=Xgrid,ygrid=EY_Ygrid_flipped):    
    distance_to_NN = []
    NARRaccumulation = []
    for i in range(0,len(NASAeasting)):
        if np.isnan(NASAsnowlist[i]):
            NARRaccumulation.append(np.nan)
        else:
            x_dist = xgrid - NASAeasting[i]
            y_dist = ygrid - NASAnorthing[i]
            distance = np.sqrt((x_dist**2)+(y_dist**2))
            closest_cell = np.where(distance == np.nanmin(distance))
            distance_to_NN.append(np.nanmin(distance))
            NARRaccumulation.append(NARRsnowarray[closest_cell])
        
    return NARRaccumulation

#snow2011_BC_list = nearestneighbour(snow20112012_BC)

#plt.figure(figsize=(5,5))
#plt.scatter(depth,snow2011_BC_list)
#plt.xlim(0,3.5)
#plt.ylim(0,3.5)

###############################################################################
# load 2020/2021 data
snow2021_nobc = seasonalaccumulation('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/downscaled2021acc/netSnowkaskonly2020.nc','F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/downscaled2021acc/netSnowkaskonly2021.nc',False)
snow2021_bc = seasonalaccumulation('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/downscaled2021acc/Prcpkaskonly_BC_2020.nc','F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/downscaled2021acc/Prcpkaskonly_BC_2021.nc',True)

snow2021_bc_list = calculate_XYZAcc(Xgrid,EY_Ygrid_flipped,Zgrid,snow2021_bc)[3]

# compare to NASA snow data
plt.figure(figsize=(14,7))
plt.scatter(easting_EY,northing_EY,c=snow2021_bc_list,cmap="BuPu")
legend1 = plt.colorbar()
legend1.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.scatter(easting,northing,c=depth, facecolor='k',marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
legend2 = plt.colorbar()
#legend2.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar (May2021) Compared to NARR Accumulation (Oct2020-May2021)',fontsize=14)
#plt.savefig('NARR_CReSIS_2021_diffcolour.png',bbox_inches = 'tight')

plt.figure(figsize=(12,7))
plt.scatter(easting_EY,northing_EY,c=snow2021_bc_list,cmap="BuPu")
plt.scatter(easting,northing,c=depth, cmap="BuPu",marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Accumulation (m w.e. $a^{-1}$)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('CReSIS Snow Radar (May2021) Compared to NARR Accumulation (Oct2020-May2021)',fontsize=14)
#plt.savefig('NARR_CReSIS_2021_samecolours.png',bbox_inches = 'tight')

plt.figure(figsize=(6,8))
plt.scatter(accumulationvselevation(Zgrid,snow2021_nobc)[0],accumulationvselevation(Zgrid,snow2021_nobc)[1],marker='.',color='orange')
plt.scatter(accumulationvselevation(Zgrid,snow2021_bc)[0],accumulationvselevation(Zgrid,snow2021_bc)[1],marker='.',color='purple')
plt.scatter(depth,elevation,marker='.',color='turquoise')
plt.title('Kaskawulsh Accumulation',fontsize=12)
plt.xlabel('Accumulation (m w.e.)',fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.legend(['NARR Accumulation (Oct2020-May2021) Uncorrected','NARR Accumulation (Oct2020-May2021) Bias Corrected','CReSIS Snow Radar (2021)'])
plt.xlim(0,4.5)
plt.ylim(500,4000)
#plt.savefig('NARRCresis2021_AccvsElev.png',bbox_inches = 'tight')

def howmuchsnowinlatesummer(year1file,BC):
    if BC == False:
        Fvar = 'Precipitation'
    else:
        Fvar = 'Net snow'
        
    inF1 = Dataset(year1file,'r')
    snowyr1 = inF1.variables[Fvar][:] # has shape (time,y,x)
    
    #inF2 = Dataset(year2,'r')
    #snowyr2 = inF2.variables[Fvar][:] # has shape (time,y,x)
    
    # calculate total accumulation from oct - jan of year 1
    #use np.nansum(axis=0) to get sum through time
    
    #formula = 8*(DOY-1)
    aug1_DOY= 214
    aug1 = 8*(aug1_DOY-1)
    
    sept30_DOY = 274
    sept30 = 8*(sept30_DOY-1)
    
    summersnow = np.nansum(snowyr1[aug1:sept30,:,:],axis=0) #units are m.w.e.
    
    nanlocs = np.where(summersnow == 0)
    summersnow[nanlocs] = np.nan 
    
    return summersnow

summersnow_2020_bc = howmuchsnowinlatesummer('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/downscaled2021acc/Prcpkaskonly_BC_2020.nc',True)
snow2021_bc_plussummersnow = np.add(snow2021_bc,summersnow_2020_bc)

summersnow_2020_Nobc = howmuchsnowinlatesummer('F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/downscaled2021acc/netSnowkaskonly2020.nc',False)
snow2021_nobc_plussummersnow = np.add(snow2021_nobc,summersnow_2020_Nobc)

    
plt.figure(figsize=(6,8))
plt.scatter(accumulationvselevation(Zgrid,snow2021_nobc_plussummersnow)[0],accumulationvselevation(Zgrid,snow2021_nobc_plussummersnow)[1],marker='.',color='orange')
plt.scatter(accumulationvselevation(Zgrid,snow2021_bc_plussummersnow)[0],accumulationvselevation(Zgrid,snow2021_bc_plussummersnow)[1],marker='.',color='purple')
plt.scatter(depth,elevation,marker='.',color='turquoise')
plt.title('Kaskawulsh Accumulation',fontsize=12)
plt.xlabel('Accumulation (m w.e.)',fontsize=14)
plt.ylabel('Elevation (m a.s.l.)',fontsize=14)
plt.legend(['NARR Accumulation (Aug2020-May2021) Uncorrected','NARR Accumulation (Aug2020-May2021) Bias Corrected','CReSIS Snow Radar (2021)'])
plt.xlim(0,4.5)
plt.ylim(500,4000)
#plt.savefig('NARRCresis2021_AccvsElev_summersnowincl.png',bbox_inches = 'tight')

# compare directly: nearest neighbour NARR (BC) to NASA accumulation
snow2021_bc_NN_NASAcells = nearestneighbour(snow2021_bc_plussummersnow)
snow2021_nobc_NN_NASAcells = nearestneighbour(snow2021_nobc_plussummersnow)

plt.figure(figsize=(12,6))
plt.subplot(1,2,1)
plt.scatter(depth,snow2021_nobc_NN_NASAcells)
plt.title('Nearest Neighbour Comparison \n NARR (Aug2020-May2021) Uncorrected vs CReSIS (2021)')
plt.xlim(0,3)
plt.ylim(0,3)
plt.plot([0,3],[0,3],linestyle='--',color='k')
plt.xlabel('CReSIS Snow Radar (m w.e.)',fontsize=14)
plt.ylabel('NARR Accumulation (m.w.e.)',fontsize=14)
plt.subplot(1,2,2)
plt.scatter(depth,snow2021_bc_NN_NASAcells)
plt.title('Nearest Neighbour Comparison \n NARR (Aug2020-May2021) Bias Corrected vs CReSIS (2021)')
plt.xlim(0,3)
plt.ylim(0,3)
plt.plot([0,3],[0,3],linestyle='--',color='k')
plt.xlabel('CReSIS Snow Radar (m w.e.)',fontsize=14)
plt.ylabel('NARR Accumulation (m.w.e.)',fontsize=14)
#plt.savefig('NNComparison_NARRvsCReSIS_2021.png',bbox_inches = 'tight')

#get spatially distributed plot of the differences between NARR and NASA
difference_2021bc = depth - snow2021_bc_NN_NASAcells

plt.figure(figsize=(12,7))
plt.scatter(easting_EY,northing_EY,color='lightslategrey')#,c=acc_EY)#,cmap="Greys")
plt.scatter(easting,northing,c=difference_2021bc, cmap="BuPu",marker='o',linewidth=3) #levels = np.linspace(0,4.5,19))
legend = plt.colorbar()
legend.ax.set_ylabel('Difference in Accumulation (m w.e.)', rotation=270,fontsize=14,labelpad=20)
plt.xlabel('Easting',fontsize=14)
plt.ylabel('Northing',fontsize=14)
plt.title('Difference between CReSIS and NARR (Aug2020-May2021) Bias Corrected Accumulation',fontsize=14)
#plt.savefig('Spatialdiffs_NARRvsCReSIS.png',bbox_inches = 'tight')

# segment the NASA data into the diff tributaries:
tribarray = KWtributaries('file:///F:/Mass Balance Model/Kaskawulsh-Mass-Balance/RunModel/KWTributaries.csv',Zgrid)
nanlocs = np.where(np.isnan(Zgrid))
tribarray[nanlocs] = np.nan

def tributary_accvselev(tribarray,Zgrid,snowarray):
    SAs = []
    SAz = []
    SWs = []
    SWz = []
    NAs = []
    NAz = []
    CAs = []
    CAz = []
    Trs = []
    Trz = []
    
    for i in range(0,len(Zgrid)):
        for j in range(0,len(Zgrid[0])):
            if np.isnan(Zgrid[i][j]):
                pass
            else:
                if tribarray[i][j] == 1:
                    SAs.append(snowarray[i][j])
                    SAz.append(Zgrid[i][j])
                elif tribarray[i][j] == 2:
                    SWs.append(snowarray[i][j])
                    SWz.append(Zgrid[i][j])
                elif tribarray[i][j] == 3:
                    CAs.append(snowarray[i][j])
                    CAz.append(Zgrid[i][j])
                elif tribarray[i][j] == 4:
                    NAs.append(snowarray[i][j])
                    NAz.append(Zgrid[i][j])
                elif tribarray[i][j] == 5:
                    Trs.append(snowarray[i][j])
                    Trz.append(Zgrid[i][j])
                else:
                    pass
                
    return [SAs,SAz],[SWs,SWz],[CAs,CAz],[NAs,NAz],[Trs,Trz]

#get tributary data from NASA snow radar:

NAs_nasa = depth[0:9000]
NAz_nasa = elevation[0:9000]

Trs_nasa = depth[9000:31000]
Trz_nasa = elevation[9000:31000]

SAs_nasa = depth[31000:45000]
SAz_nasa = elevation[31000:45000]

CAs_nasa = depth[50000:76203]
CAz_nasa = elevation[50000:76203]
                    
plt.figure(figsize=(10,12))
plt.subplot(2,2,1)
plt.title('South Arm',fontsize=14)
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[0][0],tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[0][1],color='purple')
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[0][0],tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[0][1],color='orange')
plt.scatter(SAs_nasa,SAz_nasa,color='turquoise')
plt.xlabel('Accumulation (m w.e.)',fontsize=12)
plt.ylabel('Elevation (m a.s.l.)',fontsize=12)
plt.legend(['NARR (Aug2020-May2021) Bias Corrected','NARR (Aug2020-May2021) Uncorrected','CReSIS Snow Radar (2021)'])
plt.ylim(700,3700)
plt.xlim(0,4)
plt.subplot(2,2,2)
plt.title('Stairway Glacier',fontsize=14)
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[1][0],tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[1][1],color='purple')
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[1][0],tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[1][1],color='orange')
plt.xlabel('Accumulation (m w.e.)',fontsize=12)
plt.ylabel('Elevation (m a.s.l.)',fontsize=12)
plt.legend(['NARR (Aug2020-May2021) Bias Corrected','NARR (Aug2020-May2021) Uncorrected','CReSIS Snow Radar (2021)'])
plt.ylim(700,3700)
plt.xlim(0,4)
plt.subplot(2,2,3)
plt.title('Central Arm',fontsize=14)
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[2][0],tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[2][1],color='purple')
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[2][0],tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[2][1],color='orange')
plt.scatter(CAs_nasa,CAz_nasa,color='turquoise')
plt.xlabel('Accumulation (m w.e.)',fontsize=12)
plt.ylabel('Elevation (m a.s.l.)',fontsize=12)
plt.legend(['NARR (Aug2020-May2021) Bias Corrected','NARR (Aug2020-May2021) Uncorrected','CReSIS Snow Radar (2021)'])
plt.ylim(700,3700)
plt.xlim(0,4)
plt.subplot(2,2,4)
plt.title('North Arm',fontsize=14)
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[3][0],tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[3][1],color='purple')
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[3][0],tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[3][1],color='orange')
plt.scatter(NAs_nasa,NAz_nasa,color='turquoise')
plt.xlabel('Accumulation (m w.e.)',fontsize=12)
plt.ylabel('Elevation (m a.s.l.)',fontsize=12)
plt.legend(['NARR (Aug2020-May2021) Bias Corrected','NARR (Aug2020-May2021) Uncorrected','CReSIS Snow Radar (2021)'])
plt.ylim(700,3700)
plt.xlim(0,4)
plt.tight_layout()
#plt.savefig('Tributaries_SnowvsZ.png',bbox_inches = 'tight')

plt.figure(figsize=(6,8))
plt.title('Trunk',fontsize=14)
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[4][0],tributary_accvselev(tribarray,Zgrid,snow2021_bc_plussummersnow)[4][1],color='purple')
plt.scatter(tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[4][0],tributary_accvselev(tribarray,Zgrid,snow2021_nobc_plussummersnow)[4][1],color='orange')
plt.scatter(Trs_nasa,Trz_nasa,color='turquoise')
plt.xlabel('Accumulation (m w.e.)',fontsize=12)
plt.ylabel('Elevation (m a.s.l.)',fontsize=12)
plt.legend(['NARR (Aug2020-May2021) Bias Corrected','NARR (Aug2020-May2021) Uncorrected','CReSIS Snow Radar (2021)'])
plt.ylim(700,3700)
plt.xlim(0,4)
#plt.savefig('Trunk_SnowvsZ.png',bbox_inches = 'tight')

plt.figure(figsize=(8,6))
plt.contourf(np.flipud(tribarray),levels=(-1,0,1,2,3,4,5,6,),cmap='tab10')
#plt.colorbar()
plt.legend(['grey = trunk','pink = NA','brown = CA','red = SW','green = SA','blue = none'])
plt.tight_layout()
#plt.savefig('KWTributaries.png',bbox_inches = 'tight')


#####IMPORT THE NASA DATA FROM THE MATLAB FILE#################################
#matfile = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/Data_20210510_03_001.mat' #from CSARP_layer
matfile002 = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/Data_20210510_03_002.mat' #this one came from CSARP_qlook
matfile009 = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/Data_20210510_03_009.mat'
matfile041 = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/Data_20210510_03_041.mat'

#data_dict = mat73.loadmat(matfile) # print this to see the variables
radar_data002 = mat73.loadmat(matfile002) # print this to see the variables
radar_data009 = mat73.loadmat(matfile009)
# looks like matfile2 has the variables in documentation except for Depth


f = h5py.File(matfile002,'r')
data = f.get('Surface') 
surface002 = np.array(data)

f = h5py.File(matfile002,'r')
data = f.get('Time') 
time002 = np.array(data)

f = h5py.File(matfile009,'r')
data = f.get('Surface') 
surface009 = np.array(data)

f = h5py.File(matfile009,'r')
data = f.get('Time') 
time009 = np.array(data)

f = h5py.File(matfile009,'r')
data = f.get('Depth') 
depth009 = np.array(data) #does not exist :(

f = h5py.File(matfile041,'r')
data = f.get('Surface') 
surface041 = np.array(data)

f = h5py.File(matfile041,'r')
data = f.get('Time') 
time041 = np.array(data)
tb = f.get('Truncate_Bins')
truncate_bins041 = np.array(tb)

e = 1.53
c = 3e8

#D = (time[0,-1] - np.median(surface))*c/2/np.sqrt(e) 

D002 = (time002[0] - np.median(surface002))*c/2/np.sqrt(e) #closest point to origin = D002[5071] = 0.0273 m
D009 = (time009[0] - np.median(surface009))*c/2/np.sqrt(e) #closest point to origin = D009[2803] = 0.0037 m
D041 = (time041[0] - np.median(surface041))*c/2/np.sqrt(e) #closest point to origin = D041[5967] = 0.0132 m

picks_file = 'F:/Mass Balance Model/Kaskawulsh-Mass-Balance/SnowRadar2021/2021_Alaska_seasonal_snow.mat'
seasonalsnow = scipy.io.loadmat(picks_file)
elevs = seasonalsnow['Elev']
lats = seasonalsnow['Lat']
lons = seasonalsnow['Lon']
thickness = seasonalsnow['Thickness']



plt.figure()
plt.scatter(lons[0],lats[0],c=thickness[0],cmap="BuPu", vmin = 0, vmax=5)
plt.colorbar()

kw_lats = []
kw_lons = []
kw_thickness = []

        
