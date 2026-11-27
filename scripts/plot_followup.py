"""Reproduce follow-up research figures from public aggregates, without model calls."""
from pathlib import Path
import json, os
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
D=json.loads((ROOT/'results/decision_review.json').read_text())
G=json.loads((ROOT/'results/theme_guardrail.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none','axes.titlesize':10,'axes.labelsize':9,'pdf.fonttype':42})
BLUE='#245778';GRAY='#777777';LIGHT='#dddddd'

def decision_figure():
    fig,axes=plt.subplots(1,2,figsize=(9,3.45))
    curves=D['results']['primary']['curves'];x=[r['reviews'] for r in curves]
    for ax,key,title,ylabel in zip(axes,['slot_errors','score_shortfall_pp'],['a  Priority-set mismatch','b  Priority-score shortfall'],['Remaining mismatched priority slots','Mean school-normalized shortfall (pp)']):
        ys=[r['random'][key]['mean'] for r in curves]
        ax.fill_between(x,[r['random'][key]['p025'] for r in curves],[r['random'][key]['p975'] for r in curves],color=LIGHT,alpha=.8,label='Random: 95% order envelope')
        ax.plot(x,ys,'--',color=GRAY,lw=1.5,label='Random: mean')
        ax.plot(x,[r['impact'][key] for r in curves],'-o',color=BLUE,lw=1.6,ms=3.2,label='Impact-first')
        ax.axvline(20,color='#aaa',lw=.7,ls=':');ax.set_title(title,loc='left',fontweight='bold',pad=12)
        ax.set(xlabel='Unique inputs reviewed',ylabel=ylabel,xlim=(0,102),ylim=(0,None),xticks=[0,20,50,100])
        ax.grid(axis='y',color='#eee',lw=.7);ax.set_axisbelow(True)
    axes[0].annotate('Primary budget',xy=(20,2.6),xytext=(24,2.6),color='#666',fontsize=8)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,frameon=False,fontsize=8,bbox_to_anchor=(.5,.005))
    fig.subplots_adjust(left=.075,right=.985,top=.88,bottom=.23,wspace=.29)
    return fig

def guard_figure():
    fig,axes=plt.subplots(1,2,figsize=(9,3.45))
    labels=['Improved\nclassifier','Whole-comment\ngate','Per-theme\ngate'];x=np.arange(3)
    axes[0].bar(x-.17,[G['real'][k]['no_difficulty_false_alarms'] for k in 'BCD'],width=.32,color=GRAY,label='False alarms / 20 negatives')
    axes[0].bar(x+.17,[G['real'][k]['true_difficulties_retained'] for k in 'BCD'],width=.32,color=BLUE,label='Retained signals / 15 positives')
    axes[0].set(xticks=x,xticklabels=labels,ylim=(0,15),ylabel='Targeted cases',yticks=[0,5,10,15]);axes[0].set_title('a  Diagnostic set (40 cases)',loc='left',fontweight='bold',pad=12)
    for offset,values in [(-.17,[4,1,1]),(.17,[10,5,6])]:
        for i,v in enumerate(values):axes[0].text(i+offset,v+.3,str(v),ha='center',fontsize=8)
    x=np.arange(2);axes[1].bar(x,[329,329],color=BLUE,width=.5,label='Complete output')
    axes[1].bar(x,[0,6],bottom=[329,329],color='#83a4bb',width=.5,label='Partial; still needs review')
    axes[1].bar(x,[104,98],bottom=[329,335],color='#e3e3e3',width=.5,label='No usable binary output')
    axes[1].set(xticks=x,xticklabels=['Whole-comment gate','Per-theme gate'],ylim=(0,445),ylabel='Unique inputs',yticks=[0,100,200,300,433]);axes[1].set_title('b  Coverage replay (433 inputs)',loc='left',fontweight='bold',pad=12)
    for i in range(2):axes[1].text(i,164.5,'329 complete',ha='center',va='center',color='white',fontsize=9)
    axes[1].annotate('6 partial',xy=(1,332),xytext=(.45,365),arrowprops={'arrowstyle':'-','lw':.6},fontsize=8)
    for ax in axes:ax.legend(loc='upper center',bbox_to_anchor=(.5,-.22),frameon=False,fontsize=7.5);ax.grid(axis='y',color='#eee',lw=.7);ax.set_axisbelow(True)
    fig.subplots_adjust(left=.065,right=.965,top=.88,bottom=.30,wspace=.27)
    return fig

if __name__=='__main__':
    with PdfPages(OUT/'followup-figures.pdf',metadata={'Title':'Evidence gates and decision-aware review','Author':'Daniel (Heedong) Jang'}) as pdf:
        for stem,build in [('decision-review',decision_figure),('theme-guardrail',guard_figure)]:
            fig=build();fig.savefig(OUT/(stem+'.png'),dpi=240);fig.savefig(OUT/(stem+'.svg'),metadata={'Date':None});pdf.savefig(fig);plt.close(fig)
    print('Generated two follow-up figures from released aggregates.')
