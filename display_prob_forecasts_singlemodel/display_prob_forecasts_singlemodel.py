""" this python script is intended to display precipitation analysis
    and forecast information at the 1/8-degree grid mesh scale.  This
    routine is capable of generating plots of quantile mapped
    and dressed, quantile mapped only, and raw ensemble 
    probability forecasts.
"""
# --- import library routines

from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap
import matplotlib
import pygrib
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
from numpy import ma
import os, sys
from dateutils import daterange, dateshift, dayofyear, splitdate
from read_prob_forecasts_weighted import read_prob_forecasts_weighted

# --- setting up font sizes for the display

rcParams['legend.fontsize']='small'
rcParams['legend.fancybox']=True
rcParams['xtick.labelsize']='small'
rcParams['axes.labelsize']='small'
rcParams['contour.negative_linestyle']='solid'

# ---- read inputs from command line

cyyyymmddhh = sys.argv[1] # initial time in YYYYMMDDHH format
cmodel = sys.argv[2]
cleade = sys.argv[3] # end lead time in hours
cthresh = sys.argv[4] # threshold amount
ileade = int(cleade)

if cthresh == 'POP':
    ithresh = 0
    cthresh_title = 'POP'
elif cthresh == '1mm':
    ithresh = 1
    cthresh_title = '$\geq$ 1 mm'
elif cthresh == '2p5mm':
    ithresh = 2
    cthresh_title = '$\geq$ 2.5 mm'
elif cthresh == '5mm':
    ithresh = 3
    cthresh_title = '$\geq$ 5 mm'
elif cthresh == '10mm':
    ithresh = 4
    cthresh_title = '$\geq$ 10 mm'
elif cthresh == '25mm':
    ithresh = 5
    cthresh_title = '$\geq$ 25 mm'
elif cthresh == '50mm':
    ithresh = 6
    cthresh_title = '$\geq$ 50 mm'
else:
    print 'Invalid threshold', cthresh
    print 'Please use POP, 1mm, 2p5mm, 5mm, 10mm, 25mm, 50mm'
    print 'Exiting.'
    sys.exit()

yyyy,mm,dd,hh = splitdate(cyyyymmddhh)
cyyyy = str(yyyy)
cdd = str(dd)
chh = str(hh)
cmonths = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
cmonth = cmonths[mm-1]
iyyyymmddhh = int(cyyyymmddhh)


# ---- read in precipitation analysis

nxa = 464
nya = 224
apcp_anal_t = np.zeros((nya,nxa), dtype=np.float32)
mninetynine = -99.99*np.ones((nya,nxa), dtype=np.float32)

date_fearly = dateshift(cyyyymmddhh, ileade-6)
date_flate = dateshift(cyyyymmddhh, ileade)
infile1 = '/Users/thamill/ccpa_v1/ccpa.'+date_fearly[0:8]+'/06/ccpa.t06z.06h.0p125.conus'
infile2 = '/Users/thamill/ccpa_v1/ccpa.'+date_flate[0:8]+'/12/ccpa.t12z.06h.0p125.conus'


fexist1 = os.path.exists(infile1)
if fexist1:
    afile1 = pygrib.open(infile1)
    grb2 = afile1.select()[0]
    apcp_anal_t1 = grb2.values
else:
    print 'no analysis data for this date'
    apcp_anal_t1 = -99.99*np.ones((nya,nxa),dtype=np.float32)

fexist2 = os.path.exists(infile2)
if fexist2:
    afile2 = pygrib.open(infile2)
    grb2 = afile2.select()[0]
    lats_small_t, lons_small_t = grb2.latlons()
    apcp_anal_t = apcp_anal_t1 + grb2.values
    apcp_anal_t = np.where(apcp_anal_t > 500., mninetynine, apcp_anal_t)
else:
    print 'no analysis data for this date'
    apcp_anal_t = -99.99*np.ones((nya,nxa),dtype=np.float32)
#print 'min, max apcp_anal_t = ', np.min(apcp_anal_t), np.max(apcp_anal_t)

afile2.close()

data_directory = '/Users/thamill/precip/ecmwf_data/'
infile = data_directory+cmodel+'_'+cleade+'h_IC'+cyyyymmddhh+'.nc'
print infile
nc = Dataset(infile)
pthreshes = nc.variables['pthreshes'][:]
conusmask = nc.variables['conusmask'][:,:]
rlonsa = nc.variables['rlonsa'][:,:]
rlatsa = nc.variables['rlatsa'][:,:]
prob_forecast_raw = nc.variables['prob_forecast_raw'][:,:,:]
prob_forecast_qmapped = nc.variables['prob_forecast_qmapped'][:,:,:]
prob_forecast = nc.variables['prob_forecast'][:,:,:]


print 'prob_forecast(0,nya/4,0:nxa:10) = ', prob_forecast[0,nya/4,0:nxa:10]


climo_prob = nc.variables['climo_prob'][:,:,:]
nc.close()

# ======================================================================

# ---- plot a four-panel figure with raw, qmapped, final, verif

fig1 = plt.figure(figsize=(7.8,6.5))
plt.suptitle(r''+cleade+'-h forecasts of '+cthresh_title+' from '+cmodel+\
    '+ analysis,\ninitialized 00 UTC '+cdd+' '+cmonth+' '+cyyyy,fontsize=16)

for ifield in range(4):
    if ifield == 0:
        prob_forecast_display = prob_forecast_raw[ithresh,:,:]
        position = [0.02, 0.55, 0.46, 0.33]
        position_legend = [0.02, 0.52, 0.46, 0.02]
        ctitle = '(a) Raw ensemble'
        colorst = ['White','#E4FFFF','#C4E8FF','#8FB3FF','#D8F9D8','#A6ECA6','#42F742','Yellow','Gold',\
            'Orange','#FCD5D9','#F6A3AE','#FB4246','Red','#AD8ADB','#A449FF','LightGray'] #'#AD8ADB
        colorstblack=['White','Black','Black','Black','Black', 'Black','Black','Black',\
            'Black','Black','Black','Black','Black','Black','Black','Black','Black']
        colorstwhite=['White','Black','Black','White','White','White','White',\
            'White','White','White','Black','White','White','White','White','White']
        clevs = [0.0, 0.03, 0.05,0.1, 0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95,0.99,1.0]
        #linewidths = [0.2,0.2, 0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2,0.2]
        linewidths = [0.1,0.1, 0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
        legend_title = 'Probability'
    elif ifield == 1:
        prob_forecast_display = prob_forecast_qmapped[ithresh,:,:]
        position = [0.52, 0.55, 0.46, 0.33]
        position_legend = [0.52, 0.52, 0.46, 0.02]
        ctitle = '(b) After quantile mapping with 5x5 stencil'
    elif ifield == 2:
        prob_forecast_display = prob_forecast[ithresh,:,:]
        position = [0.02, 0.09, 0.46, 0.33]
        position_legend = [0.02, 0.06, 0.46, 0.02]
        ctitle = '(c) Final quantile-mapped and dressed'
    elif ifield == 3:        
        prob_forecast_display = apcp_anal_t # climo_prob[ithresh,:,:] #
        position = [0.52, 0.09, 0.46, 0.33]
        position_legend = [0.52, 0.06, 0.46, 0.02]
        ctitle = '(d) CCPA precipitation analysis' # Climatological probability' #
        colorst = ['White','#E4FFFF','#C4E8FF','#8FB3FF','#D8F9D8','#A6ECA6','#42F742','Yellow','Gold',\
            'Orange','#FCD5D9','#F6A3AE','#FA5257','Red','Maroon','#A449FF','LightGray'] #'#AD8ADB
        colorstblack=['White','Black','White','White', 'White','White',\
            'White','White','White', 'White','White','White','White','White','White']
        clevs = [0.0, 0.254,1,2,3,4,5,7,10,15,20,30,50,100]
        linewidths = [0.1,0.4,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1,0.1]
        legend_title = 'Precipitation amount (mm)'

    ax = fig1.add_axes(position)
    ax.set_title(ctitle,fontsize=11)
    m = Basemap(projection='mill',llcrnrlon=rlonsa[0,0],llcrnrlat=rlatsa[0,0],\
        urcrnrlon=rlonsa[-1,-1],urcrnrlat=rlatsa[-1,-1],resolution='l')
    x,y = m(rlonsa,rlatsa)
    prob_forecast_m = ma.array(prob_forecast_display)
    CS1 = m.contour(x,y,prob_forecast_m,clevs,colors=colorstblack,cmap=None,linewidths = linewidths)
    CS2 = m.contourf(x,y,prob_forecast_m,clevs,colors=colorst,cmap=None,extend='neither')
    m.drawcoastlines(linewidth=.5)
    m.drawstates(linewidth=.5)
    m.drawcountries(linewidth=.5)

    cax = fig1.add_axes(position_legend)
    cbar = fig1.colorbar(CS2,extend='neither', \
        orientation='horizontal',cax=cax,drawedges=True,ticks=clevs,format='%g')
    cax.set_xlabel(legend_title,fontsize=9)
    cbar.ax.tick_params(labelsize=6)

# ---- set plot title, save to pdf file

plot_title = cmodel+'_'+cthresh+'_'+cyyyymmddhh+'_'+cleade+'h.pdf'
fig1.savefig(plot_title)
print 'saving plot to file = ',plot_title

