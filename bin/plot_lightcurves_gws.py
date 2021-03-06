
import os, sys, glob
import optparse
import numpy as np
from scipy.interpolate import interpolate as interp
import scipy.stats

import matplotlib
#matplotlib.rc('text', usetex=True)
matplotlib.use('Agg')
#matplotlib.rcParams.update({'font.size': 20})
import matplotlib.pyplot as plt

import corner

from gwemlightcurves import BHNSKilonovaLightcurve, BNSKilonovaLightcurve, BlueKilonovaLightcurve, SALT2
from gwemlightcurves import lightcurve_utils

def parse_commandline():
    """
    Parse the options given on the command-line.
    """
    parser = optparse.OptionParser()

    parser.add_option("-o","--outputDir",default="../output")
    parser.add_option("-p","--plotDir",default="../plots")
    parser.add_option("-d","--dataDir",default="../lightcurves")
    #parser.add_option("-n","--name",default="../plots/gws/Blue/u_g_r_i_z_y_J_H_K/0_14/ejecta/G298048_PS1_GROND_SOFI/1.00,../plots/gws/BNS/y_J_H_K/5_14/ejecta/G298048_PS1_GROND_SOFI/1.00")
    parser.add_option("--outputName",default="G298048_PS1_GROND_SOFI")
    parser.add_option("--doMasses",  action="store_true", default=False)
    parser.add_option("--doEjecta",  action="store_true", default=False)

    parser.add_option("-n","--name",default="../plots/gws/Blue_EOSFit/u_g_r_i_z_y_J_H_K/0_14/masses/G298048_PS1_GROND_SOFI/1.00,../plots/gws/BNS_EOSFit/y_J_H_K/5_14/masses/G298048_PS1_GROND_SOFI/1.00")

    #parser.add_option("-l","--labelType",default="errorbar")
    parser.add_option("-l","--labelType",default="name")

    opts, args = parser.parse_args()

    return opts

def q2eta(q):
    return q/(1+q)**2

def mc2ms(mc,eta):
    """
    Utility function for converting mchirp,eta to component masses. The
    masses are defined so that m1>m2. The rvalue is a tuple (m1,m2).
    """
    root = np.sqrt(0.25-eta)
    fraction = (0.5+root) / (0.5-root)
    invfraction = 1/fraction

    m2= mc * np.power((1+fraction),0.2) / np.power(fraction,0.6)

    m1= mc* np.power(1+invfraction,0.2) / np.power(invfraction,0.6)
    return (m1,m2)

def ms2mc(m1,m2):
    eta = m1*m2/( (m1+m2)*(m1+m2) )
    mchirp = ((m1*m2)**(3./5.)) * ((m1 + m2)**(-1./5.))
    q = m2/m1

    return (mchirp,eta,q)

def hist_results(samples,Nbins=16,bounds=None):

    if not bounds==None:
        bins = np.linspace(bounds[0],bounds[1],Nbins)
    else:
        bins = np.linspace(np.min(samples),np.max(samples),Nbins)
    hist1, bin_edges = np.histogram(samples, bins=bins, density=True)
    hist1[hist1==0.0] = 1e-3
    #hist1 = hist1 / float(np.sum(hist1))
    bins = (bins[1:] + bins[:-1])/2.0

    return bins, hist1

def get_post_file(basedir):
    filenames = glob.glob(os.path.join(basedir,'2-post*'))
    if len(filenames)>0:
        filename = filenames[0]
    else:
        filename = []
    return filename

def get_labels(label):
    models = ["barnes_kilonova_spectra","ns_merger_spectra","kilonova_wind_spectra","ns_precursor_Lbol","BHNS","BNS","SN","tanaka_compactmergers","macronovae-rosswog","Afterglow","metzger_rprocess","korobkin_kilonova","Blue"]
    models_ref = ["Barnes et al. (2016)","Barnes and Kasen (2013)","Kasen et al. (2014)","Metzger et al. (2015)","Kawaguchi et al. (2016)","Dietrich and Ujevic (2017)","Guy et al. (2007)","Tanaka and Hotokezaka (2013)","Rosswog et al. (2017)","Van Eerten et al. (2012)","Metzger et al. (2010)","Wollaeger et al. (2017)","Metzger (2017)"]

    idx = models.index(label)
    return models_ref[idx]

# Parse command line
opts = parse_commandline()

if not (opts.doEjecta or opts.doMasses):
    print "Enable --doEjecta or --doMasses"
    exit(0)

names = opts.name.split(",")
post = {}
for plotDir in names:
    plotDirSplit = plotDir.split("/")
    name = plotDirSplit[-6]
    nameSplit = name.split("_")
    name = nameSplit[0] 
    if len(nameSplit) == 2:
        EOSFit = 1
    else:
        EOSFit = 0
     
    errorbudget = float(plotDirSplit[-1])
    post[name] = {}
        
    multifile = get_post_file(plotDir)
    if not multifile: continue
    data = np.loadtxt(multifile)

    post[name][errorbudget] = {}
    if name == "BHNS":
        if opts.doMasses:
            if EOSFit:
                t0 = data[:,0]
                q = data[:,1]
                chi_eff = data[:,2]
                mns = data[:,3]
                c = data[:,4]
                th = data[:,5]
                ph = data[:,6]
                zp = data[:,7]
                loglikelihood = data[:,8]

                mchirp,eta,q = ms2mc(data[:,1]*data[:,3],data[:,3])

                post[name][errorbudget]["mchirp"] = mchirp
                post[name][errorbudget]["q"] = q
            else:
                t0 = data[:,0]
                q = data[:,1]
                chi_eff = data[:,2]
                mns = data[:,3]
                mb = data[:,4]
                c = data[:,5]
                th = data[:,6]
                ph = data[:,7]
                zp = data[:,8]
                loglikelihood = data[:,9]

                mchirp,eta,q = ms2mc(data[:,1]*data[:,3],data[:,3])

                post[name][errorbudget]["mchirp"] = mchirp
                post[name][errorbudget]["q"] = q

        elif opts.doEjecta:
            t0 = data[:,0]
            mej = 10**data[:,1]
            vej = data[:,2]
            th = data[:,3]
            ph = data[:,4]
            zp = data[:,5]
            loglikelihood = data[:,6]

            post[name][errorbudget]["mej"] = mej
            post[name][errorbudget]["vej"] = vej

    elif name == "BNS": 
        if opts.doMasses:
            if EOSFit:
                t0 = data[:,0]
                m1 = data[:,1]
                c1 = data[:,2]
                m2 = data[:,3]
                c2 = data[:,4]
                th = data[:,5]
                ph = data[:,6]
                zp = data[:,7]
 
                mchirp,eta,q = ms2mc(m1,m2)
 
                post[name][errorbudget]["mchirp"] = mchirp
                post[name][errorbudget]["q"] = 1/q
            else:
                t0 = data[:,0]
                m1 = data[:,1]
                mb1 = data[:,2]
                c1 = data[:,3]
                m2 = data[:,4]
                mb2 = data[:,5]
                c2 = data[:,6]
                th = data[:,7]
                ph = data[:,8]
                zp = data[:,9]
    
                mchirp,eta,q = ms2mc(m1,m2)
    
                post[name][errorbudget]["mchirp"] = mchirp
                post[name][errorbudget]["q"] = 1/q

        elif opts.doEjecta:
            t0 = data[:,0]
            mej = 10**data[:,1]
            vej = data[:,2]
            th = data[:,3]
            ph = data[:,4]
            zp = data[:,5]
            loglikelihood = data[:,6]

            post[name][errorbudget]["mej"] = mej
            post[name][errorbudget]["vej"] = vej

    elif name == "Blue":
        if opts.doMasses:
            if EOSFit:
                t0 = data[:,0]
                m1 = data[:,1]
                c1 = data[:,2]
                m2 = data[:,3]
                c2 = data[:,4]
                beta = data[:,5]
                kappa_r = data[:,6]
                zp = data[:,7]
 
                mchirp,eta,q = ms2mc(m1,m2)
 
                post[name][errorbudget]["mchirp"] = mchirp
                post[name][errorbudget]["q"] = 1/q
            else:
                t0 = data[:,0]
                m1 = data[:,1]
                mb1 = data[:,2]
                c1 = data[:,3]
                m2 = data[:,4]
                mb2 = data[:,5]
                c2 = data[:,6]
                beta = data[:,7]
                kappa_r = data[:,8]
                zp = data[:,9]
    
                mchirp,eta,q = ms2mc(m1,m2)
    
                post[name][errorbudget]["mchirp"] = mchirp
                post[name][errorbudget]["q"] = 1/q

        elif opts.doEjecta:
            t0 = data[:,0]
            mej = 10**data[:,1]
            vej = data[:,2]
            beta = data[:,3]
            kappa_r = data[:,4]
            zp = data[:,5]
            loglikelihood = data[:,6]

            post[name][errorbudget]["mej"] = mej
            post[name][errorbudget]["vej"] = vej

    elif name == "SN":
        t0 = data[:,0]
        z = data[:,1]
        x0 = data[:,2]
        x1 = data[:,3]
        c = data[:,4]
        zp = data[:,5]
        loglikelihood = data[:,6]

baseplotDir = opts.plotDir
if not os.path.isdir(baseplotDir):
    os.mkdir(baseplotDir)
plotDir = os.path.join(baseplotDir,'gws')
plotDir = os.path.join(plotDir,opts.outputName)
if opts.doMasses:
    plotDir = os.path.join(plotDir,'masses')
elif opts.doEjecta:
    plotDir = os.path.join(plotDir,'ejecta')
if not os.path.isdir(plotDir):
    os.makedirs(plotDir)

colors = ['b','g','r','m','c']
linestyles = ['-', '-.', ':','--']

if opts.doEjecta:

    bounds = [-3.0,0.0]
    xlims = [-3.0,0.0]
    ylims = [1e-1,10]

    plotName = "%s/mej.pdf"%(plotDir)
    plt.figure(figsize=(10,8))
    maxhist = -1
    for ii,name in enumerate(sorted(post.keys())):
        for jj,errorbudget in enumerate(sorted(post[name].keys())):
            if opts.labelType == "errorbar":
                label = r"$\Delta$m: %.2f"%float(errorbudget)
            elif opts.labelType == "name":
                label = get_labels(name)
            else:
                label = []
            if opts.labelType == "errorbar":
                color = colors[jj]
                colortrue = 'k'
                linestyle = '-'
            elif opts.labelType == "name":
                color = colors[ii]
                colortrue = colors[ii]
                linestyle = linestyles[jj]
            else:
                color = 'b'
                colortrue = 'k'
                linestyle = '-'
    
            samples = np.log10(post[name][errorbudget]["mej"])
            print samples
          
            bins, hist1 = hist_results(samples,Nbins=25,bounds=bounds) 
    
            if opts.labelType == "name" and jj > 0:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),linewidth=3)
            else:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),label=label,linewidth=3)
    
            maxhist = np.max([maxhist,np.max(hist1)])
    
    plt.xlabel(r"${\rm log}_{10} (M_{\rm ej})$",fontsize=24)
    plt.ylabel('Probability Density Function',fontsize=24)
    plt.legend(loc="best",prop={'size':24})
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.savefig(plotName)
    plt.close()

    bounds = [0.0,1.0]
    xlims = [0.0,1.0]
    ylims = [1e-1,20]
    
    plotName = "%s/vej.pdf"%(plotDir)
    plt.figure(figsize=(10,8))
    maxhist = -1
    for ii,name in enumerate(sorted(post.keys())):
        for jj,errorbudget in enumerate(sorted(post[name].keys())):
            if opts.labelType == "errorbar":
                label = r"$\Delta$m: %.2f"%float(errorbudget)
            elif opts.labelType == "name":
                label = get_labels(name)
            else:
                label = []
            if opts.labelType == "errorbar":
                color = colors[jj]
                colortrue = 'k'
                linestyle = '-'
            elif opts.labelType == "name":
                color = colors[ii]
                colortrue = colors[ii]
                linestyle = linestyles[jj]
            else:
                color = 'b'
                colortrue = 'k'
                linestyle = '-'
    
            samples = post[name][errorbudget]["vej"]
            bins, hist1 = hist_results(samples,Nbins=25,bounds=bounds)
    
            if opts.labelType == "name" and jj > 0:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),linewidth=3)
            else:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),label=label,linewidth=3)
    
            maxhist = np.max([maxhist,np.max(hist1)])
    
    plt.xlabel(r"$v_{\rm ej}$",fontsize=24)
    plt.ylabel('Probability Density Function',fontsize=24)
    plt.legend(loc="best",prop={'size':24})
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.savefig(plotName)
    plt.close()

elif opts.doMasses:

    bounds = [0.8,4.0]
    xlims = [0.8,4.0]
    ylims = [1e-1,10]

    plotName = "%s/mchirp.pdf"%(plotDir)
    plt.figure(figsize=(10,8))
    maxhist = -1

    for ii,name in enumerate(sorted(post.keys())):
        for jj,errorbudget in enumerate(sorted(post[name].keys())):

            if opts.labelType == "errorbar":
                label = r"$\Delta$m: %.2f"%float(errorbudget)
            elif opts.labelType == "name":
                label = get_labels(name)
            else:
                label = []
            if opts.labelType == "errorbar":
                color = colors[jj]
                colortrue = 'k'
                linestyle = '-'
            elif opts.labelType == "name":
                color = colors[ii]
                colortrue = colors[ii]
                linestyle = linestyles[jj]
            else:
                color = 'b'
                colortrue = 'k'
                linestyle = '-'

            samples = post[name][errorbudget]["mchirp"]
            print samples
            bins, hist1 = hist_results(samples,Nbins=25,bounds=bounds)

            if opts.labelType == "name" and jj > 0:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),linewidth=3)
            else:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),label=label,linewidth=3)

            maxhist = np.max([maxhist,np.max(hist1)])

    plt.xlabel(r"${\rm M}_{\rm c}$",fontsize=24)
    plt.ylabel('Probability Density Function',fontsize=24)
    plt.legend(loc="best",prop={'size':24})
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.savefig(plotName)
    plt.close()

    bounds = [0.0,2.0]
    xlims = [0.9,2.0]
    ylims = [1e-1,10]

    plotName = "%s/q.pdf"%(plotDir)
    plt.figure(figsize=(10,8))
    maxhist = -1
    for ii,name in enumerate(sorted(post.keys())):
        for jj,errorbudget in enumerate(sorted(post[name].keys())):

            if opts.labelType == "errorbar":
                label = r"$\Delta$m: %.2f"%float(errorbudget)
            elif opts.labelType == "name":
                label = get_labels(name)
            else:
                label = []
            if opts.labelType == "errorbar":
                color = colors[jj]
                colortrue = 'k'
                linestyle = '-'
            elif opts.labelType == "name":
                color = colors[ii]
                colortrue = colors[ii]
                linestyle = linestyles[jj]
            else:
                color = 'b'
                colortrue = 'k'
                linestyle = '-'

            samples = post[name][errorbudget]["q"]
            bins, hist1 = hist_results(samples,Nbins=25,bounds=bounds)

            if opts.labelType == "name" and jj > 0:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),linewidth=3)
            else:
                plt.semilogy(bins,hist1,'%s%s'%(color,linestyle),label=label,linewidth=3)

            maxhist = np.max([maxhist,np.max(hist1)])

    plt.xlabel(r"$q$",fontsize=24)
    plt.ylabel('Probability Density Function',fontsize=24)
    plt.legend(loc="best",prop={'size':24})
    plt.xticks(fontsize=24)
    plt.yticks(fontsize=24)
    plt.xlim(xlims)
    plt.ylim(ylims)
    plt.savefig(plotName)
    plt.close()
