import re, json, subprocess
txt=open('voiceover_script.md').read()
paras=[]
for blk in re.split(r'\n\[.*?\]\n', txt)[1:]:
    p=blk.strip().split('\n\nElevenLabs')[0].strip()
    paras.append(p)
sec_names=['problem','what','demo1','demo2','results','honesty','close']
units=[];usec=[]
for si,p in enumerate(paras):
    for s in re.split(r'(?<=[.:])\s+', p):
        if s.strip(): units.append(s.strip()); usec.append(si)
out=subprocess.run(['ffmpeg','-hide_banner','-i','voice.mp3','-af','silencedetect=noise=-35dB:d=0.35','-f','null','-'],capture_output=True,text=True).stderr
starts=[float(x) for x in re.findall(r'silence_start: ([\d.]+)',out)]
ends=[float(x) for x in re.findall(r'silence_end: ([\d.]+)',out)]
total=133.146
# candidate boundaries: (speech_end, speech_start)
cands=[(s,e) for s,e in zip(starts,ends) if e<total-0.3 and s>0.3]
L=[len(u) for u in units]; n=len(units); m=len(cands)
first=0.0
lead=[e for s,e in zip(starts,ends) if s<0.3]
if lead: first=lead[0]
lastend=total-0.1
rate=sum(L)/ (lastend-first)
INF=1e18
# dp[i][j]: units 0..i end at cand j (j=-1 means start)
import math
dp=[[INF]*m for _ in range(n)]; bp=[[None]*m for _ in range(n)]
for j in range(m):
    d=cands[j][0]-first; dp[0][j]=(d-L[0]/rate)**2
for i in range(1,n-1):
    for j in range(m):
        best=INF;bj=None
        for k in range(j):
            c=dp[i-1][k]
            if c>=INF: continue
            d=cands[j][0]-cands[k][1]; v=c+(d-L[i]/rate)**2
            if v<best: best=v;bj=k
        dp[i][j]=best;bp[i][j]=bj
best=INF;bj=None
for k in range(m):
    if dp[n-2][k]<INF:
        v=dp[n-2][k]+(lastend-cands[k][1]-L[n-1]/rate)**2
        if v<best: best=v;bj=k
idx=[None]*(n-1); idx[n-2]=bj
for i in range(n-2,0,-1): idx[i-1]=bp[i][idx[i]]
times=[]
st=first
for i in range(n):
    en=cands[idx[i]][0] if i<n-1 else lastend
    times.append((st,en)); 
    if i<n-1: st=cands[idx[i]][1]
# caption chunks
def chunks(u):
    words=u.split(); out=[];cur=''
    for w in words:
        if len(cur)+len(w)+1>62 and cur: out.append(cur);cur=w
        else: cur=(cur+' '+w).strip()
    if cur: out.append(cur)
    return out
caps=[]
for u,(a,b),si in zip(units,times,usec):
    cs=chunks(u); tot=sum(len(c) for c in cs); t=a
    for c in cs:
        d=(b-a)*len(c)/tot; caps.append((t,t+d,c)); t+=d
def ts(x):
    h=int(x//3600);mi=int(x%3600//60);s=x%60
    return f"{h:02d}:{mi:02d}:{s:06.3f}".replace('.',',')
with open('build/captions.srt','w') as f:
    for k,(a,b,c) in enumerate(caps,1): f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{c}\n\n")
sec={}
for (a,b),si in zip(times,usec):
    nm=sec_names[si]; sec.setdefault(nm,[a,b]); sec[nm][1]=b
units_t=[dict(t0=round(a,2),t1=round(b,2),sec=sec_names[si],text=u) for u,(a,b),si in zip(units,times,usec)]
json.dump(dict(sections=sec,units=units_t),open('build/timing.json','w'),indent=1)
for u in units_t: print(u['t0'],u['t1'],u['sec'],u['text'][:60])
print(sec)
