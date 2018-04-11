import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as cols
import itertools
import numpy as np

def getLabel(observable):
    plotLabel={}
    plotLabel['Mmiss']="$M_{miss} [GeV]$"
    plotLabel['PTmiss']="$p_T^{miss} [GeV]$"
    plotLabel['Ejj']="$E_{jj}$ [GeV]"
    plotLabel['PTjj']="$p^T_{jj}$ [GeV]"
    plotLabel['Etajj']="$\\eta_{jj}$"
    plotLabel['CosThetajj']="$\\cos{\\theta_{jj}}$"
    plotLabel['Ew']="$E_{w}$ [GeV]"
    plotLabel['Emu']="$E_{\\mu}$ [GeV]"
    plotLabel['PTmu']="$p_T^{\\mu}$ [GeV]"
    plotLabel['Etamu']="$\\eta_{\\mu}$"
    plotLabel['CosThetamu']="$\\cos{\\theta_{\\mu}}$"
    return plotLabel[observable]

def getRange(observable):
    plotRange={}
    plotRange['Mmiss']=(0,500)
    plotRange['PTmiss']=(0,500)
    plotRange['Ejj']=(0,500)
    plotRange['PTjj']=(0,500)
    plotRange['Etajj']=(-50.0,50.0)
    plotRange['CosThetajj']=(-1.0,1.0)
    plotRange['Ew']=(0,500)
    plotRange['Emu']=(0,500)
    plotRange['PTmu']=(0,500)
    plotRange['Etamu']=(-50.0,50.0)
    plotRange['CosThetamu']=(-1.0,1.0)
    return plotRange[observable]

def quickPlot(objects, cutlabel):
    observables=[key for key in objects[0].obs.keys()]
    observables.remove("EventWeight")
    for x in observables:
        #plt.title('$e^+e^- \\to j,j,\\mu,\\nu(+D,D)$ at '+str(objects[0].luminosity)+'$fb^{-1}$ (AFTER '+cutlabel+')')
        plt.yscale('log')
        plt.xlabel(getLabel(x))
        plt.ylabel('entries / bin')
        nbins=20
        for obj in objects:
            plt.hist(obj.obs[x], nbins, range=getRange(x),weights=obj.obs['EventWeight'], label=obj.label, histtype = 'step', linestyle=obj.plotStyle['linestyle'],color=obj.plotStyle['color'])
        #axes[1].scatter(df[x],df[y], c=df['OMEGA'],cmap='jet',s=0.1,rasterized=True,norm=norm)
        plt.legend()
        plt.savefig('./cutNplot/'+str(objects[0].filetype)+'/'+str(objects[0].filetype)+'_plot_'+x+'_'+cutlabel+'.pdf')
        plt.close()

def Dalitz(objects, cutlabel):
    observables=[key for key in objects[0].obs.keys()]
    observables.remove("EventWeight")
    for x,y in itertools.combinations(observables,2):
        fig, axes = plt.subplots(1, len(objects), sharey=True,figsize=(16,4))
        fig.subplots_adjust(wspace=0.2,top=0.8,bottom=0.2)
        cbar_ax = fig.add_axes([0.84, 0.1, 0.015, 0.8])
        
        axes[0].set_ylabel(getLabel(y),fontsize=16)
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