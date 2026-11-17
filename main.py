import json,os,sys,urllib.request
U=os.environ.get('MAKEFUN_ENV_URL') or sys.exit('MAKEFUN_ENV_URL required')
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0};K=20000;LIMIT=8000;N=0
N8=(14,31,33,18,-14,-31,-33,-18);K8=(1,16,-1,-16,15,17,-15,-17)
def post(p,b):
 r=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={'content-type':'application/json'});return json.load(urllib.request.urlopen(r))
def parse(f):
 b=[None]*128;s=f.split()
 for r,row in enumerate(s[0].split('/')):
  i=(7-r)*16
  for c in row:
   if c.isdigit():i+=int(c)
   else:b[i]=c;i+=1
  return b,s[1]=='b',s[2],s[3]
def sq(x):return chr(97+(x&7))+str(8-(x>>4))
def name(m):return sq(m[0])+sq(m[1])+m[2]
def chk(b,w):return hit(b,b.index('K'if w else'k'),not w)
def hit(b,x,w):
 d=16 if w else-16
 for z in (x-d-1,x-d+1):
  if not z&0x88 and b[z]==('P'if w else'p'):return 1
 for ds,pcs in ((N8,'Nn'),(K8,'Kk'),((1,16,-1,-16),'RrQq'),((15,17,-15,-17),'BbQq')):
  for d in ds:
   q=x+d
   while not q&0x88:
    if b[q]:
     if b[q] in pcs:return 1
     break
    if ds in (N8,K8):break
    q+=d
 return 0
def gen(b,w,cs,ep):
 o=[];own=str.isupper if w else str.islower
 for s,p in enumerate(b):
  if s&0x88 or not p or not own(p):continue
  t=p.lower()
  if t=='p':
   d=16 if w else-16;last=7 if w else 0
   for z in (s+d-1,s+d+1):
    if not z&0x88 and ((b[z] and not own(b[z])) or z==ep):o.append((s,z,'q'if z>>4==last else'',z==ep and not b[z]))
   z=s+d
   if not z&0x88 and not b[z]:
    o.append((s,z,'q'if z>>4==last else'',False));zz=z+d
    if s>>4==(1 if w else 6) and not b[zz]:o.append((s,zz,'',False))
   continue
  ds=N8 if t=='n' else K8 if t=='k' else (15,17,-15,-17)if t=='b' else (1,16,-1,-16)if t=='r' else K8
  for d in ds:
   z=s+d
   while not z&0x88:
    if b[z]:
     if not own(b[z]):o.append((s,z,'',False))
     break
    o.append((s,z,'',False))
    if t in'nk':break
    z+=d
  if t=='k':
   for bit,mid,dest,rk in (('K'if w else'k',s+1,s+2,s+3),('Q'if w else'q',s-1,s-2,s-4)):
    if bit in cs and b[rk]==('R'if w else'r') and not b[mid] and not b[dest] and not chk(b,w) and not hit(b,mid,not w) and not hit(b,dest,not w):o.append((s,dest,'',False))
 return o
def move(b,m,w,cs,ep):
 s,z,pr,e=m;p=b[s];q=b[:];q[s]=None
 if e:q[z+(16 if w else-16)]=None
 q[z]=(pr.upper()if w else pr)if pr else p
 if p.lower()=='k' and abs(z-s)==2:
  r=s+(3 if z>s else-4);q[s+(1 if z>s else-1)]=q[r];q[r]=None
 c=cs
 if p.lower()=='k':c=c.replace('K','').replace('Q','').replace('k','').replace('q','')
 for x in (s,z):
  if x==0:c=c.replace('q','')
  if x==7:c=c.replace('k','')
  if x==112:c=c.replace('Q','')
  if x==119:c=c.replace('K','')
 e=(s+z)//2 if p.lower()=='p' and abs(z-s)==32 else -1
 return q,c,e
def pst(p,s):
 t=p.lower();r=s>>4;f=s&7;adv=r if p.isupper() else 7-r;cen=6-abs(3-f)-abs(3-r)
 return V[t]+(adv*12 if t=='p' else cen*8 if t=='n' else cen*5 if t=='b' else adv*4 if t=='r' else cen*2 if t=='q' else (-40 if adv<2 else 20 if adv>5 else 0))
def ev(b):return sum(pst(p,s)*(1 if p.isupper() else-1)for s,p in enumerate(b)if p and not s&0x88)
def order(b,m):
 s,z,p,e=m;v=b[z]
 return (-(10*V[v.lower()]-V[b[s].lower()]if v else 0),-V[p]if p else 0,s,z)
def ab(b,w,c,e,d,a,bb):
 global N
 N+=1
 if N>=LIMIT or d==0:return ev(b)if w else-ev(b)
 ms=gen(b,w,c,e);ms.sort(key=lambda m:order(b,m));best=-K;ok=0
 for m in ms:
  q,cc,ee=move(b,m,w,c,e)
  if chk(q,w):continue
  ok=1;x=-ab(q,not w,cc,ee,d-1,-bb,-a)
  if x>best:best=x
  if x>a:a=x
  if a>=bb:break
 return best if ok else(-K if chk(b,w)else 0)
def choose(f,legal):
 global N
 b,w,c,e=parse(f);e=-1 if e=='-' else(8-int(e[1]))*16+ord(e[0])-97;N=0
 ms=gen(b,w,c,e);ms.sort(key=lambda m:order(b,m));best=-K;ans=None
 for m in ms:
  q,cc,ee=move(b,m,w,c,e)
  if chk(q,w):continue
  x=-ab(q,not w,cc,ee,4,-K,K)
  if x>best:best=x;ans=name(m)
 return ans if ans in legal else legal[0]
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
 print(g['game'],g['outcome'],g['reason'],file=sys.stderr)
