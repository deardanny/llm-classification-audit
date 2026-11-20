"""Reproduce research figures using released aggregate counts. No model calls."""
from pathlib import Path
import json, os, textwrap
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'figures'
OUT.mkdir(exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.colors import LinearSegmentedColormap, Normalize
import numpy as np
D = json.loads((ROOT / 'results/aggregates.json').read_text())
BLUE = '#0072B2'
BLACK = '#222222'
GRAY = '#707070'
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 7.5,
    'axes.labelsize': 7.5, 'axes.titlesize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7,
    'legend.fontsize': 7, 'legend.frameon': False,
    'axes.linewidth': .6, 'lines.linewidth': .9,
    'xtick.major.width': .6, 'ytick.major.width': .6,
    'xtick.major.size': 3, 'ytick.major.size': 3,
    'axes.spines.top': False, 'axes.spines.right': False,
    'text.color': BLACK, 'axes.edgecolor': BLACK,
    'axes.labelcolor': BLACK, 'xtick.color': BLACK, 'ytick.color': BLACK,
    'figure.facecolor': 'white', 'axes.facecolor': 'white',
    'axes.grid': False, 'pdf.fonttype': 42, 'ps.fonttype': 42,
    'svg.fonttype': 'none', 'savefig.facecolor': 'white',
})


def panel(ax, letter, title):
    ax.set_title(title, loc='left', pad=10, weight='normal')
    ax.text(-.18, 1.04, letter, transform=ax.transAxes, fontsize=10,
            fontweight='bold', ha='left', va='bottom')


def matrix(ax, values, labels, xlabel, ylabel, vmax):
    cmap = LinearSegmentedColormap.from_list('paper_greys', ['#FFFFFF', '#C9C9C9', '#3B3B3B'])
    mesh = ax.pcolormesh(np.arange(len(labels)+1), np.arange(len(labels)+1),
                         values, cmap=cmap, vmin=0, vmax=vmax,
                         edgecolors='white', linewidth=.9, shading='flat', rasterized=False)
    ax.set_aspect('equal')
    ax.set_xlim(0, len(labels)); ax.set_ylim(len(labels), 0)
    ax.set_xticks(np.arange(len(labels))+.5, labels)
    ax.set_yticks(np.arange(len(labels))+.5, labels)
    ax.set_xlabel(xlabel, labelpad=6); ax.set_ylabel(ylabel, labelpad=7)
    ax.tick_params(axis='both', length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    norm=Normalize(0,vmax)
    for y in range(len(labels)):
        for x in range(len(labels)):
            rgb=cmap(norm(values[y,x]))[:3]
            luminance=sum(a*b for a,b in zip(rgb,[.2126,.7152,.0722]))
            ax.text(x+.5,y+.5,str(values[y,x]),ha='center',va='center',fontsize=9,
                    color='white' if luminance<.52 else BLACK)
    return mesh


def figure1():
    s = D['grouping']['results']
    keys=['two_off_topic','mixed','two_on_topic']
    vals=np.array([[s['state_pairs'].get(f'{a} -> {b}',0) for b in keys] for a in keys])
    assert vals.tolist()==[[44,7,79],[1,0,16],[1,0,2]]
    assert vals.sum()==s['rows']==150
    fig=plt.figure(figsize=(7.2,2.85))
    ax=fig.add_axes([.085,.215,.325,.65])
    matrix(ax,vals,['Off','Mixed','On'],'Singleton state','Batch state',80)
    panel(ax,'a','Joint decision states ($n=150$)')
    cax=fig.add_axes([.428,.30,.014,.45])
    cbar=fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(0,80),cmap=LinearSegmentedColormap.from_list('g',['white','#C9C9C9','#3B3B3B'])),cax=cax)
    cbar.set_ticks([0,40,80]);cbar.ax.set_ylabel('Responses (count)',rotation=90,labelpad=4,fontsize=7)
    cbar.outline.set_linewidth(.5)

    ax=fig.add_axes([.64,.215,.31,.65])
    n=s['rows']; colors=[BLACK,BLUE]; markers=['o','s']
    for r in range(2):
        counts=[s['batch_on_topic_by_repeat'][r],s['singleton_on_topic_by_repeat'][r]]
        rates=np.array(counts)/n*100
        offset=(-.025 if r==0 else .025)
        ax.plot(np.array([0,1])+offset,rates,color=colors[r],marker=markers[r],
                markersize=4,markerfacecolor='white' if r==0 else colors[r],
                linestyle='-' if r==0 else '--',label=f'Repetition {r+1}')
    ax.set_xlim(-.25,1.25);ax.set_ylim(0,100)
    ax.set_xticks([0,1],['Batch','Singleton']);ax.set_yticks([0,25,50,75,100])
    ax.set_ylabel('On-topic classifications (%)',labelpad=5)
    ax.legend(loc='upper left',handlelength=2.2,borderaxespad=.2)
    panel(ax,'b','Repeated classifications')
    return fig


def figure2():
    fig=plt.figure(figsize=(7.2,2.65))
    a=D['audit']['audit_verdicts'];n=D['audit']['source_rows']
    ax=fig.add_axes([.10,.24,.21,.60])
    names=['Supported','Hold','Contradicted'];counts=[a[k.lower()] for k in names]
    perc=np.array(counts)/n*100
    ax.hlines([2,1,0],0,perc,color='#AAAAAA',linewidth=.6)
    ax.plot(perc,[2,1,0],'o',color=BLACK,markersize=4)
    for x,y,c in zip(perc,[2,1,0],counts):
        ax.annotate(f'{c:,}',(x,y),xytext=(5,0),textcoords='offset points',va='center',fontsize=7)
    ax.set_yticks([2,1,0],names);ax.set_ylim(-.5,2.5);ax.set_xlim(0,110)
    ax.set_xticks([0,50,100]);ax.set_xlabel('Responses (%)')
    ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
    panel(ax,'a','Blind audit ($n=12{,}531$)')

    p=D['prompt']['target_row_statistics']['paired_transitions']
    mat=np.array([[p['off_topic -> off_topic'],p['off_topic -> on_topic']],
                  [p['on_topic -> off_topic'],p['on_topic -> on_topic']]])
    assert mat.sum()==201
    ax=fig.add_axes([.425,.24,.205,.60])
    # Exact cell counts are sufficient; no additional colour scale is needed.
    matrix(ax,mat,['Off','On'],'Revised prompt','Original-prompt control',160)
    ax.set_aspect('auto')
    panel(ax,'b','Prompt revision ($n=201$)')

    ax=fig.add_axes([.775,.24,.205,.60])
    m=D['masking']['primary_all_targets'];r=D['masking']['primary_change_repeat_patterns']
    first=[m['control_to_repair']['off_topic_to_on_topic'],m['control_to_repair']['on_topic_to_off_topic']]
    repeated=[r['stable_off_topic_to_on_topic'],r['stable_on_topic_to_off_topic']]
    xx=np.array([0,1])
    ax.bar(xx-.16,first,width=.30,facecolor='white',edgecolor=BLACK,linewidth=.7,label='First pair')
    ax.bar(xx+.16,repeated,width=.30,color=BLUE,label='Reproduced')
    for x,ns in [(xx-.16,first),(xx+.16,repeated)]:
        for xpos,value in zip(x,ns):ax.text(xpos,value+.5,str(value),ha='center',va='bottom',fontsize=7)
    ax.set_xticks(xx,['Off → on','On → off']);ax.set_ylim(0,25);ax.set_yticks([0,10,20])
    ax.set_ylabel('Changed responses (count)',labelpad=5)
    ax.legend(loc='upper right',fontsize=6.5,handlelength=1.2,borderaxespad=.1)
    panel(ax,'c','Mask repair ($n=1{,}171$)')
    return fig


CAPTIONS={
    'figure1': (
        'Figure 1. Sensitivity of topic classification to input grouping. '
        '(a) Joint decision states for 150 complete response pairs from 152 selected residual rows. '
        'Off and On denote identical labels in both repetitions; Mixed denotes disagreement between repetitions. '
        'Rows show batch states and columns show singleton states. '
        '(b) On-topic counts were 11 and 12 in batch calls, and 98 and 103 in singleton calls (denominator 150 each). '
        'Connectors link matching repetition indices, '
        'not independent experimental units. The model, prompt and target text were held fixed. '
        'Two rows remained unavailable after bounded format retries and are excluded. '
        'These selected-cohort results measure classification sensitivity, not accuracy. '
        'No inferential error bars are shown for two repetitions.'),
    'figure2': (
        'Figure 2. Audit outcomes and controlled interventions. '
        '(a) Jev audit-policy outcomes for 12,531 reconstructed Claude baseline labels; support and contradiction are not correctness labels. '
        '(b) Paired classifications under a fresh original-prompt control and a relevance-separated prompt for 201 selected disagreements. '
        'Cells report counts. (c) Directional changes between a fresh original-input control and repaired evaluation inputs '
        'among 1,171 rows affected by the ALL dictionary collision. '
        'Eighteen responses changed from off-topic to on-topic and four in the reverse direction; '
        '15 and four, respectively, reproduced in the follow-up paired calls. '
        'The other 1,149 labels were unchanged. Of the target rows, 23 had no change within their own 800-character model input. '
        'Follow-up repeats were outcome-selected; interventions may also affect neighboring batch responses. '
        'Cohorts overlap, and their changes cannot be added as verified corrections.'),
}


def write():
    pages=[]
    for name,stem,build in [('figure1','grouping',figure1),('figure2','interventions',figure2)]:
        fig=build()
        fig.savefig(OUT/(stem+'.png'),dpi=300)
        fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None})
        old_h=fig.get_figheight();new_h=4.25
        positions=[(ax,ax.get_position(original=True).frozen()) for ax in fig.axes]
        fig.set_figheight(new_h)
        for ax,box in positions:
            ax.set_position([box.x0,(box.y0*old_h+new_h-old_h)/new_h,box.width,box.height*old_h/new_h])
        fig.text(.045,(new_h-old_h+.18)/new_h,textwrap.fill(CAPTIONS[name],width=128),
                 ha='left',va='top',fontfamily='DejaVu Serif',fontsize=7.5,linespacing=1.25)
        pages.append(fig)
    with PdfPages(OUT/'research-figures.pdf',metadata={'Title':'Classification audit: aggregate research figures','Author':'Daniel Jang'}) as pdf:
        for fig in pages:pdf.savefig(fig)
    for fig in pages:plt.close(fig)
    (OUT/'captions.txt').write_text('\n\n'.join(CAPTIONS.values())+'\n')
    print('Reproduced two aggregate figures and captioned PDF.')

if __name__=='__main__':write()
