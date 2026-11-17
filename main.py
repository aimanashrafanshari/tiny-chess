#!/usr/bin/env python3
import json,os,sys,urllib.request
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("no env")
def P(p,b):
 r=urllib.request.Request(E+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
 return json.load(urllib.request.urlopen(r,timeout=15))
KN=(-33,-31,-18,-14,14,18,31,33);KB=(-17,-15,15,17);KR=(-16,-1,1,16);KQ=KB+KR
V={'P':100,'N':320,'B':335,'R':500,'Q':900,'K':20000};F="abcdefgh"
def PS(fen):
 b=[None]*128;p,stm,cs,ep=(fen.split()+['-'])[:4]
 for i,r in enumerate(p.split('/')):
  f=0
  for c in r:
   if c.isdigit():f+=int(c)
   else:b[(7-i)*16+f]=c;f+=1
 return b,stm=='w',cs,ep
def US(sq):return F[sq&7]+str((sq>>4)+1)
def UCI(m):f,t,pr,fl=m;return US(f)+US(t)+pr
def atk(b,sq,w):
 d=16 if w else-16
 for df in(-1,1):
  s=sq-d+df
  if 0<=s<128 and not(s&0x88)and b[s]==('P'if w else'p'):return 1
 for ds,pc in((KN,'Nn'),(KQ,'QqKk')):
  for st in ds:
   s=sq+st
   if s&0x88:continue
   c=b[s]
   if c:
    if c in pc:return 1
    break
   if ds is not KN:s+=st
 return 0
def ks(b,w):
 k='K'if w else'k'
 for s in range(128):
  if not(s&0x88)and b[s]==k:return s
 return-1
def chk(b,w):k=ks(b,w);return k>=0 and atk(b,k,not w)
def PV(p,sq,w):
 v=V[p.upper()];r,f=sq>>4,sq&7;cd=(7-r)if w else r
 if p in'Pp':v+=18*cd-8 if cd<6 else 900
 elif p in'Nn':v+=8*(3-abs(f-4))+8*(3-abs(r-4))
 elif p in'Bb':v+=8*(3-abs(f-4))+8*(3-abs(r-4))
 elif p in'Rr':v+=6*(3-abs(f-4))+6*cd
 elif p in'Qq':v+=6*(3-abs(f-4))+6*(3-abs(r-4))
 elif p in'Kk':v+=-50 if cd<3 else(30 if cd>5 else 0)
 return v if w else-v
def ev(b):
 s=0
 for sq in range(128):
  if b[sq]and not(sq&0x88):s+=PV(b[sq],sq,b[sq].isupper())
 return s
def gn(b,w,cs,ep,cp=0):
 o=[];ow=str.isupper if w else str.islower
 for s in range(128):
  if s&0x88 or not b[s]or not ow(b[s]):continue
  p=b[s];P=p.upper()
  if P=='P':
   d=16 if w else-16;o1=s+d;pr=7 if w else 0
   for df in(-1,1):
    t=o1+df
    if t&0x88:continue
    q=b[t]
    if q and not ow(q):
     for x in('q','r','b','n')if(t>>4)==pr else('',):o.append((s,t,x,''))
   if not cp and not b[o1]:
    if(o1>>4)==pr:
     for x in'qrn':o.append((s,o1,x,''))
    else:
     o.append((s,o1,'',''))
     st=1 if w else 6
     if(s>>4)==st and not b[o1+d]:o.append((s,o1+d,'',''))
  elif P=='N':
   for st in KN:
    t=s+st
    if t&0x88:continue
    q=b[t]
    if not q or not ow(q):
     if not cp or q:o.append((s,t,'',''))
  elif P=='K':
   for st in KQ:
    t=s+st
    if t&0x88:continue
    q=b[t]
    if not q or not ow(q):
     if not cp or q:o.append((s,t,'',''))
  else:
   ds=KB if P=='B'else KR if P=='R'else KQ
   for st in ds:
    t=s+st
    while not(t&0x88):
     q=b[t]
     if not q:
      if not cp:o.append((s,t,'',''))
     else:
      if not ow(q):o.append((s,t,'',''))
      break
     t+=st
 return o
def MK(b,m,w,cs):
 f,t,pr,fl=m;p=b[f];nb=b[:]
 nb[t]=(pr.upper()if w else pr)if pr else p;nb[f]=None
 if p in'Pp'and abs(t-f)==32:e=(f+t)//2
    
  
  
  
 return nb,cs
MT=90000;N=0;L=9000
def ab(b,w,cs,ep,d,a,bn):
 global N
 N+=1
 if N>L:return ev(b)if w else-ev(b)
 if d==0:return ev(b)if w else-ev(b)
 ms=gn(b,w,cs,ep)
 ms.sort(key=lambda m:-(V[b[m[1]].upper()]if b[m[1]]else 0))
 best=-MT*2;an=0
 for m in ms:
  nb,nc=MK(b,m,w,cs)
  if chk(nb,w):continue
  an=1
  sc=-ab(nb,not w,nc,0,d-1,-bn,-a)
  if sc>best:best=sc
  if sc>a:a=sc
  if a>=bn:break
 if not an:return-MT if chk(b,w)else 0
 return best
def BM(fen,bud):
 global N,L
 b,w,cs,ep=PS(fen);L=bud;N=0;d=6
 ms=gn(b,w,cs,ep)
 ms.sort(key=lambda m:-(V[b[m[1]].upper()]if b[m[1]]else 0))
 best,bm=-MT*2,None
 for m in ms:
  nb,nc=MK(b,m,w,cs)
  if chk(nb,w):continue
  sc=-ab(nb,not w,nc,0,d-1,-MT*2,MT*2)
  if sc>best:best,bm=sc,m
 return UCI(bm)if bm else None
def CH(fen,leg):
 mv=BM(fen,9000);return mv if mv in leg else leg[0]
g=P("/game",{})
while g["status"]!="done":
 while g["status"]=="your_move":
  g=P("/move",{"game":g["game"],"move":CH(g["fen"],g["legal_moves"])})
 print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
print(f"done: {g.get('wins')}W {g.get('draws')}D {g.get('losses')}L",file=sys.stderr)
