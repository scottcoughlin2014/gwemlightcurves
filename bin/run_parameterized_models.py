
import os, sys
import numpy as np
import optparse

from astropy.table import Table, Column
 
import matplotlib
#matplotlib.rc('text', usetex=True)
matplotlib.use('Agg')
matplotlib.rcParams.update({'font.size': 16})
import matplotlib.pyplot as plt

from gwemlightcurves.KNModels import KNTable
from gwemlightcurves import __version__

def parse_commandline():
    """
    Parse the options given on the command-line.
    """
    parser = optparse.OptionParser()

    parser.add_option("-o","--outputDir",default="../output")
    parser.add_option("-p","--plotDir",default="../plots") 
    parser.add_option("-b","--boxfitDir",default="../boxfit")
    parser.add_option("-m","--model",default="KaKy2016")
    parser.add_option("-e","--eos",default="H4")
    parser.add_option("-q","--massratio",default=3.0,type=float)
    parser.add_option("-a","--chi_eff",default=0.1,type=float) 
    parser.add_option("--mej",default=0.005,type=float)
    parser.add_option("--vej",default=0.2,type=float)
    parser.add_option("--m1",default=1.35,type=float)
    parser.add_option("--m2",default=1.35,type=float)
    parser.add_option("-z","--redshift",default=0.001,type=float)
    parser.add_option("--x0",default=1.0,type=float)
    parser.add_option("--x1",default=1.0,type=float)
    parser.add_option("-c","--c",default=1.0,type=float)
    parser.add_option("--doMasses",  action="store_true", default=False)
    parser.add_option("--doEjecta",  action="store_true", default=False)
    parser.add_option("--theta_0",default=0.1,type=float)
    parser.add_option("--E",default=1e53,type=float)
    parser.add_option("--n",default=1.0,type=float)
    parser.add_option("--theta_obs",default=0.0,type=float)
    parser.add_option("--beta",default=3.0,type=float)
    parser.add_option("--kappa_r",default=0.1,type=float)
    parser.add_option("--slope_r",default=-1.2,type=float)
    
    opts, args = parser.parse_args()
 
    return opts

# Parse command line
opts = parse_commandline()

boxfitDir = opts.boxfitDir

m1 = opts.m1
m2 = opts.m2
q = opts.massratio
chi_eff = opts.chi_eff
mej = opts.mej
vej = opts.vej
theta_0 = opts.theta_0
E = opts.E
n = opts.n
theta_obs = opts.theta_obs
beta = opts.beta
kappa_r = opts.kappa_r
slope_r = opts.slope_r

if opts.eos == "APR4":
    c = 0.180
    mb = 1.50
elif opts.eos == "ALF2":
    c = 0.161
    mb = 1.49
elif opts.eos == "H4":
    c = 0.147
    mb = 1.47
elif opts.eos == "MS1":
    c = 0.138
    mb = 1.46

mns = 1.35

tini = 0.1
tmax = 14.0
dt = 0.1

vave = 0.267
vmin = 0.02
th = 0.2
ph = 3.14
kappa = 10.0
eps = 1.58*(10**10)
alp = 1.2
eth = 0.5
flgbct = 1

p = 2.5    
epsilon_B = 1e-2 
epsilon_E = 1e-1
ksi_N = 1

#add default values from above to table
samples = {}
samples['tini'] = tini
samples['tmax'] = tmax
samples['dt'] = dt
samples['vmin'] = vmin
samples['th'] = th
samples['ph'] = ph
samples['kappa'] = kappa
samples['eps'] = eps
samples['alp'] = alp
samples['eth'] = eth
samples['flgbct'] = flgbct
samples['beta'] = beta
samples['kappa_r'] = kappa_r
samples['slope_r'] = slope_r

samples['m1'] = opts.m1
samples['m2'] = opts.m2
samples['q'] = opts.massratio
samples['chi_eff'] = opts.chi_eff
samples['mej'] = opts.mej
samples['vej'] = opts.vej
samples['theta_0'] = opts.theta_0
samples['E'] = opts.E
samples['n'] = opts.n
samples['theta_obs'] = opts.theta_obs
samples['beta'] = opts.beta
samples['kappa_r'] = opts.kappa_r
samples['slope_r'] = opts.slope_r
samples['c1'] = c
samples['c2'] = c
samples['mb1'] = mb
samples['mb2'] = mb
t = Table()
for key, val in samples.iteritems():
    t.add_column(Column(data=[val],name=key))
samples = t
model_table = KNTable.model(opts.model, samples)
t, lbol, mag = model_table["t"][0], model_table["lbol"][0], model_table["mag"][0] 

if opts.model == "KaKy2016":
    if opts.doEjecta:
        name = "KaKy2016_%sM%03dV%02d"%(opts.eos,opts.mej*1000,opts.vej*100)
    elif opts.doMasses:
        name = "%sQ%.0fa%.0f"%(opts.eos,opts.massratio,opts.chi_eff*100)
    else:
        print "Enable --doEjecta or --doMasses"
        exit(0)
elif opts.model == "DiUj2017":
    if opts.doEjecta:
        name = "DiUj2017_%sM%03dV%02d"%(opts.eos,opts.mej*1000,opts.vej*100)
    elif opts.doMasses:
        name = "%sM%.0fm%.0f"%(opts.eos,opts.m1*100,opts.m2*100)
    else:
        print "Enable --doEjecta or --doMasses"
        exit(0)
elif opts.model == "Me2017":
    if opts.doEjecta:
        name = "Me2017_%sM%03dV%02d"%(opts.eos,opts.mej*1000,opts.vej*100)
    elif opts.doMasses:
        name = "%sM%.0fm%.0f"%(opts.eos,opts.m1*100,opts.m2*100)
    else:
        print "Enable --doEjecta or --doMasses"
        exit(0)
elif opts.model == "SmCh2017":
    if opts.doEjecta:
        name = "SmCh2017_%sM%03dV%02d"%(opts.eos,opts.mej*1000,opts.vej*100)
    elif opts.doMasses:
        name = "%sM%.0fm%.0f"%(opts.eos,opts.m1*100,opts.m2*100)
    else:
        print "Enable --doEjecta or --doMasses"
        exit(0)
elif opts.model == "WoKo2017":
    if opts.doEjecta:
        name = "WoKo2017_%sM%03dV%02d"%(opts.eos,opts.mej*1000,opts.vej*100)
    elif opts.doMasses:
        name = "%sM%.0fm%.0f"%(opts.eos,opts.m1*100,opts.m2*100)
    else:
        print "Enable --doEjecta or --doMasses"
        exit(0)
elif opts.model == "SN":
    t0 = (tini+tmax)/2.0
    t0 = 0.0
    t, lbol, mag = SALT2.lightcurve(tini,tmax,dt,opts.redshift,t0,opts.x0,opts.x1,opts.c)
    name = "z%.0fx0%.0fx1%.0fc%.0f"%(opts.redshift*100,opts.x0*10000,opts.x1*10000,opts.c*10000)

elif opts.model == "Afterglow":
    tini = 0.0
    tmax = 10.0
    dt = 0.1
    p = 2.5
    epsilon_B = 1e-2
    epsilon_E = 1e-1
    ksi_N = 1

    t, lbol, mag = BOXFit.lightcurve(boxfitDir,tini,tmax,dt,theta_0,E,n,theta_obs,p,epsilon_B,epsilon_E,ksi_N)

    name = "theta0%.0fE0%.0en%.0fthetaobs%.0f"%(theta_0*100,E,n*10,theta_obs*100)

else:
   print "Model must be either: BHNS, BNS, Blue, SN, Afterglow"
   exit(0)

if np.sum(lbol) == 0.0:
    print "No luminosity..."
    exit(0)

baseoutputDir = opts.outputDir
if not os.path.isdir(baseoutputDir):
    os.mkdir(baseoutputDir)
outputDir = os.path.join(baseoutputDir,opts.model)
if not os.path.isdir(outputDir):
    os.mkdir(outputDir)

baseplotDir = opts.plotDir
if not os.path.isdir(baseplotDir):
    os.mkdir(baseplotDir)
plotDir = os.path.join(baseplotDir,opts.model)
if not os.path.isdir(plotDir):
    os.mkdir(plotDir)

#filename = 'bhns/%s.txt'%name
#fid = open(filename,'w')
#fid.write('# t[days]   Lbol[erg/s]  u-band  g-band  r-band i-band  z-band  J-band  H-band  K-band\n')
#for ii in xrange(len(t)):
#    fid.write("%.2f "%t[ii])
#    fid.write("%.3e "%lbol[ii])
#    for jj in xrange(8):
#        fid.write("%.3f "%mag[jj][ii])
#    fid.write("\n")
#fid.close()

filename = "%s/%s.dat"%(outputDir,name)
fid = open(filename,'w')
#fid.write('# t[days] g-band r-band  i-band z-band\n')
fid.write('# t[days] u g r i z y J H K\n')
for ii in xrange(len(t)):
    fid.write("%.2f "%t[ii])
    for jj in np.arange(0,9):
        fid.write("%.3f "%mag[jj][ii])
    fid.write("\n")
fid.close()

plotName = "%s/%s.pdf"%(plotDir,name)
plt.figure()
plt.plot(t,mag[0],'r',label='u-band')
plt.plot(t,mag[1],'y',label='g-band')
plt.plot(t,mag[2],'g',label='r-band')
plt.plot(t,mag[3],'b',label='i-band')
plt.plot(t,mag[4],'c',label='z-band')
plt.xlabel('Time [days]')
plt.ylabel('Absolute AB Magnitude')
plt.legend(loc="best")
plt.gca().invert_yaxis()
plt.savefig(plotName)
plt.close()

filename = "%s/%s_Lbol.dat"%(outputDir,name)
fid = open(filename,'w')
fid.write('# t[days] Lbol[erg/s]\n')
for ii in xrange(len(t)):
    fid.write("%.5f %.5e\n"%(t[ii],lbol[ii]))
fid.close()

Lbol_ds = np.loadtxt(filename)
t = Lbol_ds[:,0]
Lbol = Lbol_ds[:,1]

plotName = "%s/%s_Lbol.pdf"%(plotDir,name)
plt.figure()
plt.semilogy(t,Lbol,'k--')
plt.xlabel('Time [days]')
plt.ylabel('Bolometric Luminosity [erg/s]')
plt.savefig(plotName)
plt.close()
