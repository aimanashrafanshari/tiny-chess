import json,os,urllib.request
V=(0,100,320,330,500,900,20000)
D=((),(),(14,18,31,33,-14,-18,-31,-33),(15,17,-15,-17),(1,16,-1,-16),(1,16,-1,-16,15,17,-15,-17),(1,16,-1,-16,15,17,-15,-17))
S=tuple(i for i in range(128)if not i&136)
def attack(b,s,c):
 for d in D[6]:
  t=s+d;n=1
  while not t&136:
   p=b[t]
   if p:
    if p*c>0:
     k=abs(p)
     if k==5 or k==6 and n==1 or k==1 and n==1 and d in(-16*c-1,-16*c+1) or k==3 and abs(d)in(15,17) or k==4 and abs(d)in(1,16):return True
    break
   n+=1;t+=d
 for d in D[2]:
  t=s+d
  if not t&136 and b[t]==2*c:return True
 return False
def check(b,c):return attack(b,b.index(6*c),-c)
def play(b,c,r,e,m):
 s,t,p=m;a=b[:];k=a[s];a[s]=0;a[t]=p*c if p else k
 if abs(k)==1 and t==e:a[t-16*c]=0
 if abs(k)==6:
  r=r.replace('K'if c==1 else'k','').replace('Q'if c==1 else'q','')
  if abs(t-s)==2:
   u=s+3 if t>s else s-4;a[s+(1 if t>s else-1)]=a[u];a[u]=0
 for x,z in ((0,'Q'),(7,'K'),(112,'q'),(119,'k')):
  if x in(s,t):r=r.replace(z,'')
 return a,-c,r,(s+t)//2 if abs(k)==1 and abs(t-s)==32 else-1
def moves(b,c,r,e):
 for s in S:
  k=b[s]*c
  if k<=0:continue
  ts=[]
  if k==1:
   t=s+16*c
   if not t&136 and not b[t]:
    ts.append(t)
    if s//16==(1 if c==1 else 6) and not b[t+16*c]:ts.append(t+16*c)
   for t in(s+15*c,s+17*c):
    if not t&136 and (b[t]*c<0 or t==e):ts.append(t)
  else:
   for d in D[k]:
    t=s+d
    while not t&136:
     if b[t]*c>0:break
     ts.append(t)
     if b[t] or k in(2,6):break
     t+=d
   if k==6 and not check(b,c):
    for d,z in((1,'K'if c==1 else'k'),(-1,'Q'if c==1 else'q')):
     if z in r and not any(b[s+d*j]for j in range(1,3 if d==1 else 4)) and not attack(b,s+d,-c) and not attack(b,s+2*d,-c):ts.append(s+2*d)
  for t in ts:
   for p in((5,4,3,2)if k==1 and t//16 in(0,7)else(0,)):
    m=s,t,p
    if not check(play(b,c,r,e,m)[0],c):yield m
def ev(b,c):
 score=0;ph=sum(1<abs(p)<6 for p in b)
 for s in S:
  p=b[s]
  if not p:continue
  k=abs(p);side=1 if p>0 else-1;f=s%16;r=s//16;adv=r if p>0 else 7-r
  ct=7-abs(2*f-7)-abs(2*r-7);v=V[k]
  if k==1:v+=adv*10+adv*adv*2
  if k in(2,3,5):v+=ct*(5 if k==2 else 3 if k==3 else 1)
  if k==4:v+=adv*4+18*(not any(abs(b[t])==1 for t in range(f,128,16)))
  if k==6:
   if ph>4:v+=-adv*14+12*sum(not(s+16*side+d)&136 and b[s+16*side+d]==side for d in(-1,0,1))
   else:v+=ct*5-12*attack(b,s,-side)
  score+=v*side
 return score*c
def order(b,e,m):return -(V[abs(b[m[1]])]if b[m[1]]else 100 if abs(b[m[0]])==1 and m[1]==e else 0),-V[m[2]],m
def search(b,c,r,e,d,lo,hi):
 global nodes
 if nodes>=9000:raise StopIteration
 nodes+=1;ic=check(b,c)
 ms=sorted(moves(b,c,r,e),key=lambda m:order(b,e,m))
 if not ms:return -30000-d if ic else 0
 if d<=0 and not ic:
  v=ev(b,c)
  if v>=hi:return v
  lo=max(lo,v)
  ms=[m for m in ms if b[m[1]] or abs(b[m[0]])==1 and m[1]==e]
 for m in ms:
  v=-search(*play(b,c,r,e,m),d-1,-hi,-lo)
  if v>=hi:return v
  lo=max(lo,v)
 return lo
def sq(s):return chr(97+s%16)+str(s//16+1)
def uci(m):return sq(m[0])+sq(m[1])+(' pnbrqk'[m[2]]if m[2]else'')
def choose(fen,legal):
 global nodes
 b=[0]*128;f=fen.split()
 for y,row in enumerate(f[0].split('/')):
  x=0
  for p in row:
   if p.isdigit():x+=int(p)
   else:b[(7-y)*16+x]=(' pnbrqk'.index(p.lower()))*(1 if p.isupper()else-1);x+=1
 c=1 if f[1]=='w'else-1;r=f[2];e=-1 if f[3]=='-'else(ord(f[3][0])-97)+16*(int(f[3][1])-1)
 ms=sorted(moves(b,c,r,e),key=lambda m:order(b,e,m));nodes=0;best=legal[0]
 for depth in range(1,7):
  score=-40000;pick=best
  try:
   for m in ms:
    v=-search(*play(b,c,r,e,m),depth-1,-40000,-score)
    if v>score:score=v;pick=uci(m)
  except StopIteration:break
  if pick in legal:best=pick
  ms.sort(key=lambda m:uci(m)!=best)
 return best
def post(path,b):
 req=urllib.request.Request(os.environ['MAKEFUN_ENV_URL']+path,data=json.dumps(b).encode(),headers={'Content-Type':'application/json'})
 return json.load(urllib.request.urlopen(req))
if __name__=='__main__':
 while True:
  g=post('/game',{})
  if g['status']=='done':break
  while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
