"""Draw every sample from the two exports; no filtering or normalization."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from read_data import ROOT, read_record


def main():
    records = json.loads((ROOT/'data/manifest.json').read_text(encoding='utf-8'))['records']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'path.simplify':False})
    fig, axes = plt.subplots(2,1,figsize=(12,7.3),sharex=True,sharey=True)
    fig.patch.set_facecolor('#f6f8fa')
    fig.subplots_adjust(left=.095,right=.965,top=.80,bottom=.13,hspace=.34)
    fig.text(.095,.925,'Pavement velocity / two ballast states',fontsize=22,weight='bold',color='#142f3b')
    fig.text(.095,.868,'45 m measurement distance  ·  40 km/h vehicle speed  ·  complete exported records',fontsize=11,color='#526975')
    for ax,r,color in zip(axes,records,['#147d92','#b26b30']):
        _,v = read_record(ROOT/r['path'])
        ax.set_facecolor('#ffffff')
        ax.plot(range(len(v)),v,color=color,lw=.65,alpha=.9)
        label='No added ballast' if r['condition']=='unballasted' else 'Added ballast'
        ax.set_title(f"{label}    /    {len(v):,} samples",loc='left',fontsize=12,pad=10,color='#243d49',weight='bold')
        ax.set_ylabel('Velocity (mm/s)',color='#526975',labelpad=12)
        ax.set_ylim(-1.15,1.15)
        ax.set_xlim(0,max(x['sample_count'] for x in records)-1)
        ax.set_yticks([-1,-.5,0,.5,1])
        ax.grid(axis='y',color='#e4eaee',lw=.7)
        ax.set_axisbelow(True)
        ax.spines[['top','right']].set_visible(False)
        for side in ['left','bottom']: ax.spines[side].set_color('#cad5dc')
        ax.tick_params(colors='#526975',length=3)
    axes[-1].xaxis.set_major_formatter(FuncFormatter(lambda x,pos:f'{int(x):,}'))
    axes[-1].set_xlabel('Sample index (zero-based)',color='#526975',labelpad=10)
    fig.text(.095,.025,'Original export values  •  No filtering or normalization  •  Records are not event-aligned',fontsize=10,color='#526975')
    fig.savefig(ROOT/'assets/signals.png',dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)
    print('Saved assets/signals.png')


if __name__=='__main__':
    main()
