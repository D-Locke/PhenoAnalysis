import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as cols
import itertools
import numpy as np
import csv
import pandas as pd
import math

def getLabel(observable):
    plotLabel={}
    plotLabel['NoCuts']="No cuts"
    plotLabel['Mmiss']="$M_{miss} [GeV]$"
    plotLabel['Mmiss_m']="$M_{miss}(p_\mu^{z(-)}) [GeV]$"
    plotLabel['Mmiss_p']="$M_{miss}(p_\mu^{z(+)}) [GeV]$"
    plotLabel['PTmiss']="$p_T^{miss} [GeV]$"
    plotLabel['Mjj']="$M_{jj}$ [GeV]"
    plotLabel['Mjets']="$M_{jets}$ [GeV]"
    plotLabel['Ejj']="$E_{jj}$ [GeV]"
    plotLabel['PTjj']="$p^T_{jj}$ [GeV]"
    plotLabel['Etajj']="$\\eta_{jj}$"
    plotLabel['CosThetajj']="$\\cos{\\theta_{jj}}$"
    plotLabel['Ew']="$E_{w}$ [GeV]"
    plotLabel['Emu']="$E_{\\mu}$ [GeV]"
    plotLabel['PTmu']="$p_T^{\\mu}$ [GeV]"
    plotLabel['Etamu']="$\\eta_{\\mu}$"
    plotLabel['CosThetamu']="$\\cos{\\theta_{\\mu}}$"
    plotLabel['Tracks']="$N_{{tracks}}$"
    plotLabel['Sum_CosTheta']="$\sum_{{vis}} |\\cos{\\theta_{\\mu}}|$"
    plotLabel['P_WW']="$M_{{WW}}$ [GeV]"
    plotLabel['deltaR_Jmu_min']="$\\Delta R_{{j\mu}}^{{min}}$"
    if observable in plotLabel:
        return plotLabel[observable]
    else:
        return observable

def getRange(observable):
    """ only needed when binning is given as an integer """
    plotRange={}
    plotRange['Mmiss']=(0,500)
    plotRange['Mmiss_m']=(0,500)
    plotRange['Mmiss_p']=(0,500)
    plotRange['PTmiss']=(0,500)
    plotRange['Ejj']=(0,500)
    plotRange['Ejets']=(0,500)
    plotRange['Mjj']=(0,500)
    plotRange['Mjets']=(0,500)
    plotRange['PTjj']=(0,500)
    plotRange['Etajj']=(-50.0,50.0)
    plotRange['CosThetajj']=(-1.0,1.0)
    plotRange['Ew']=(0,500)
    plotRange['Emu']=(0,250)
    plotRange['PTmu']=(0,500)
    plotRange['Etamu']=(-50.0,50.0)
    plotRange['CosThetamu']=(-1.0,1.0)
    plotRange['Tracks']=(0,40.0)
    plotRange['Sum_CosTheta']=(0,5.0)
    plotRange['P_WW']=(0,500)
    plotRange['deltaR_Jmu_min']=(0.0,5.0)
    plotRange['deltaPhi_jj_mu']=(-5.0,5.0)
    if observable in plotRange:
        return plotRange[observable]
    else:
        return (0,500)

def getBinCenters(plot):
    x,binning=plot["label"],plot["binning"]
    if np.size(binning)==1:
        nbins=binning
        min,max=getRange(x)
        min=float(min)
        max=float(max)
        return [min+(max-min)/nbins*(0.5+n) for n in range(0,nbins)]
    else:
        binning=[float(i) for i in binning]
        return [binning[i]+(binning[i+1]-binning[i])/2 for i in range(0,len(binning)-1)]



# def writeEmuInfo(bincenters,sig,bg_total,model,filetype,obs):
#     with open('./cutNplot/'+str(filetype)+'/EmuPlots/'+model+'_'+obs+'_'+filetype+'.dat', 'w') as f:
#         f.write('BIN_CENTRE,SIG,BG\n')
#         writer = csv.writer(f)#, delimiter='\t')
#         writer.writerows(zip(bincenters,sig,bg_total))


# def EmuPlot(objects, nbins):
#     """ made for outputting correct info on Emu dist for fitting later"""
#     observables=[key for key in objects[0].obs.keys()]
#     observables.remove("EventWeight")
#     x="Emu"
#     #plt.title('$e^+e^- \\to j,j,\\mu,\\nu(+D,D)$ at '+str(objects[0].luminosity)+'$fb^{-1}$ (AFTER '+cutlabel+')')
#     #plt.yscale('log')
#     plt.xlabel(getLabel(x))
#     plt.ylabel('entries / bin')

#     for x in ["Emu"]:#,"Ejj"]:
#         for obj in objects:
#             if obj.type=="signal":
#                 bg_total=np.zeros(nbins)
#                 for bg in objects:
#                     if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model)):
#                        (bgv, bins, patches) = plt.hist(bg.obs[x], nbins, range=(0,250),weights=bg.obs['EventWeight'], label=bg.label, histtype = 'step', linestyle=bg.plotStyle['linestyle'],color=bg.plotStyle['color'])
#                        bg_total=bg_total+bgv 
#                 (sig, bins, patches) = plt.hist(obj.obs[x], nbins, range=(0,250),weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
#                 writeEmuInfo(getBinCenters(nbins,0.0,250.0),sig,bg_total,obj.model, obj.filetype, x)

#                 plt.legend(loc='upper left', prop={'size':6}, bbox_to_anchor=(1,1))
#                 plt.tight_layout()
#                 plt.savefig('./cutNplot/'+str(objects[0].filetype)+'/EmuPlots/'+str(objects[0].filetype)+'_plot_'+obj.model+'_'+x+'.pdf')
#                 plt.close()
  

    #axes[1].scatter(df[x],df[y], c=df['OMEGA'],cmap='jet',s=0.1,rasterized=True,norm=norm)

# def CompPlot(objects, cutlabel):
#     observables=[key for key in objects[0].obs.keys()]
#     observables.remove("EventWeight")
#     for x in observables:
#     #plt.title('$e^+e^- \\to j,j,\\mu,\\nu(+D,D)$ at '+str(objects[0].luminosity)+'$fb^{-1}$ (AFTER '+cutlabel+')')
#     #plt.yscale('log')
#         plt.xlabel(getLabel(x))
#         plt.ylabel('entries / bin')
#         nbins=20
#         bgs=[]
#         for obj in objects:
#             if obj.type=="signal":
#                 plt.hist(obj.obs[x], nbins, range=getRange(x),density=True, label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
#         plt.legend(loc='upper left', prop={'size':6}, bbox_to_anchor=(1,1))
#         plt.tight_layout()
#         plt.savefig('./cutNplot/'+str(objects[0].filetype)+'/CompPlots/'+str(objects[0].filetype)+'_plot_'+obj.model+'_'+x+'_'+cutlabel+'.pdf')
#         plt.close()

def Significance(SIG,SMtot):
    """ use total from SM here """
    sig=[]
    for S,BG in zip(SIG,SMtot):
        if BG > 0.0:
            sig.append(S/math.sqrt(BG))
        else:
            sig.append(float('nan'))
    return sig

def HistPlot(objects, plots, cutlabel):

    observables=plots
    for plot in plots:
        fig, (ax1, ax2) = plt.subplots(2, sharex=True, gridspec_kw = {'height_ratios':[3, 1]})
        fig.subplots_adjust(hspace=0)
        x=plot["label"]
        df=pd.DataFrame({'BIN_CENTRE':getBinCenters(plot)})
        #plt.title('$e^+e^- \\to j,j,\\mu,\\nu(+D,D)$ at '+str(objects[0].luminosity)+'$fb^{-1}$ (AFTER '+cutlabel+')')
        ax1.set_yscale(plot["yscale"])
        ax1.set_xlabel(getLabel(x))
        ax1.set_ylabel('Events / Bin')
        hists={}       
        for obj in objects:
            if np.size(plot["binning"])==1:
                hists[obj.flabel] = ax1.hist(obj.obs[x], bins=plot["binning"],range=getRange(x),weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
            else:
                hists[obj.flabel] = ax1.hist(obj.obs[x], bins=plot["binning"],weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])               
            df[obj.flabel]=hists[obj.flabel][0]
            #plt.hist(obj.obs[x], nbins, range=getRange(x),weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
        #axes[1].scatter(df[x],df[y], c=df['OMEGA'],cmap='jet',s=0.1,rasterized=True,norm=norm)
        ax1.legend()#loc='upper left', prop={'size':6}, bbox_to_anchor=(1,1))
        ax1.set_ylim(ymin=0.1)#,ymax=400)
        #ax1.tight_layout()
        ax1.yaxis.get_major_ticks()[1].set_visible(False)

        # SIGNIFICANCE
        SMevents=[]
        for obj in objects:
            if obj.type=="signal":
                for i in range(0,len(hists[obj.flabel][0])):
                    #print sum([df[bg.flabel][i] for bg in objects if (bg.type=="background" and (bg.model=="SM" or bg.model==obj.model))])
                    SMevents.append(sum([df[bg.flabel][i] for bg in objects if (bg.type=="background" and (bg.model=="SM"))]))# or bg.model==obj.model))]))
                
                ax2.step(hists[obj.flabel][1],[0.0]+Significance(df[obj.flabel],SMevents),color=obj.plotStyle['color'],linestyle=obj.plotStyle['linestyle'])


        ax2.set_ylabel("Significance")
        ax2.set_xlabel(getLabel(x))
        fig.savefig('./cutNplot/'+str(objects[0].filetype)+'/Plots/'+str(objects[0].filetype)+'_plot_'+x+'_'+cutlabel+'.pdf')
        df.to_csv('./cutNplot/'+str(objects[0].filetype)+'/Plots/dat/'+str(objects[0].filetype)+'_plot_'+x+'_'+cutlabel+'.dat', sep='\t', encoding='utf-8')
        plt.close(fig)
        #return df



# def HistPlot(objects, plots,cutlabel):
#     observables=plots#[key for key in objects[0].obs.keys()]
#     #observables.remove("EventWeight")
#     for plot in plots:
#         x,binning=plot["label"],plot["binning"]
#         df=pd.DataFrame({'BIN_CENTRE':getBinCenters(plot)})
#         #plt.title('$e^+e^- \\to j,j,\\mu,\\nu(+D,D)$ at '+str(objects[0].luminosity)+'$fb^{-1}$ (AFTER '+cutlabel+')')
#         plt.yscale('log')
#         plt.xlabel(getLabel(x))
#         plt.ylabel('Events / Bin')       
#         for obj in objects:
#             if np.size(binning)==1:
#                 (bgv, bins, patches) = plt.hist(obj.obs[x], bins=binning,range=getRange(x),weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
#             else:
#                  (bgv, bins, patches) = plt.hist(obj.obs[x], bins=binning,weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])               
#             df[obj.flabel]=bgv
#             #plt.hist(obj.obs[x], nbins, range=getRange(x),weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
#         #axes[1].scatter(df[x],df[y], c=df['OMEGA'],cmap='jet',s=0.1,rasterized=True,norm=norm)
#         plt.legend(loc='upper left', prop={'size':6}, bbox_to_anchor=(1,1))
#         plt.ylim(ymin=0.1)
#         plt.tight_layout()
#         plt.savefig('./cutNplot/'+str(objects[0].filetype)+'/Plots/'+str(objects[0].filetype)+'_plot_'+x+'_'+cutlabel+'.pdf')
#         df.to_csv('./cutNplot/'+str(objects[0].filetype)+'/Plots/'+str(objects[0].filetype)+'_plot_'+x+'_'+cutlabel+'.dat', sep='\t', encoding='utf-8')        
#         plt.close()

def Dalitz(objects, plots, cutlabel):
    observables=plots#[key for key in objects[0].obs.keys()]
    observables.remove("EventWeight")
    if len(observables)<2: return 0
    for x,y in itertools.combinations(observables,2):
        fig, axes = plt.subplots(1, len(objects), sharey=True,figsize=(16,4))
        fig.subplots_adjust(wspace=0.2,top=0.8,bottom=0.2)
        cbar_ax = fig.add_axes([0.84, 0.1, 0.015, 0.8])
        
        #axes[0].set_ylabel(getLabel(y),fontsize=16)
        if len(objects) == 1:
            axes=[axes]
        for ax in axes:       
          ax.set_xlabel(getLabel(x),fontsize=16)
          ax.set_xlim(getRange(x))
          ax.set_ylim(getRange(y))

        #cmaps=['Reds','Greens','Blues']
        NORM=cols.LogNorm(vmin=0.1,vmax=100000)
        nbins=20
        xedges = np.linspace(getRange(x)[0],getRange(x)[1],nbins)
        yedges = np.linspace(getRange(y)[0],getRange(y)[1],nbins)


        hists2d={}
        for i,obj in enumerate(objects):
            axes[i].set_title(obj.label)
            hists2d[obj.label]=np.histogram2d(obj.obs[x],obj.obs[y],bins=(xedges, yedges),weights=obj.obs['EventWeight'])
            img = axes[i].imshow(hists2d[obj.label][0].T, interpolation='nearest', origin='low', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]],aspect='auto',norm=NORM)

        fig.subplots_adjust(right=0.8)
        cb_ticks=[10**(j) for j in range(0,5)]
        cb=fig.colorbar(img, cax=cbar_ax)#,ticks=cb_ticks)
        cb.set_label('N entries / bin', fontsize=18)
        fig.savefig('./cutNplot/'+str(objects[0].filetype)+'/Dalitz/'+str(objects[0].filetype)+'_Dalitz_'+x+'_'+y+'_'+cutlabel+'.pdf')
        plt.close(fig)