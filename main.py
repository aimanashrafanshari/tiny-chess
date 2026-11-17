import json,os,sys,urllib.request
U=os.environ.get('MAKEFUN_ENV_URL') or sys.exit('MAKEFUN_ENV_URL is not set')
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':0}
N=0
def post(p,b):
 r=urllib.request.Request(U+p,data=json.dumps(b).encode(),headers={'content-type':'application/json'})
 return json.load(urllib.request.urlopen(r))
def parse(f):
 a=[None]*64;s=f.split();i=0
 for c in s[0]:
  if c=='/':continue
  if c.isdigit():i+=int(c)
  else:a[i]=c;i+=1
 return a,s[1],s[2],s[3]
def attacks(a,x,by):
 for i,p in enumerate(a):
  if not p or (p.isupper())!=by:continue
  d=x-i; t=p.lower()
  if t=='p' and d in ((-9,-7) if by else (7,9)) and abs(i%8-x%8)==1:return 1
  if t=='n' and sorted((abs(d)//8,abs(d)%8))==[1,2] and abs(i%8-x%8) in (1,2):return 1
  if t=='k' and max(abs(d)//8,abs(i%8-x%8))==1:return 1
  if t in 'brq':
   df=x%8-i%8; dr=x//8-i//8
   ok=(t in 'rq' and (df==0 or dr==0)) or (t in 'bq' and abs(df)==abs(dr))
   if ok:
    sf=(df>0)-(df<0);sr=(dr>0)-(dr<0);q=i+sr*8+sf
    while q!=x:
     if a[q]:break
     q+=sr*8+sf
    if q==x:return 1
 return 0
def moves(a,turn,castle,ep):
 out=[]; us=turn=='w'; dirs={'n':(17,15,10,6,-6,-10,-15,-17),'k':(1,-1,8,-8,9,7,-7,-9),'b':(9,7,-7,-9),'r':(1,-1,8,-8),'q':(1,-1,8,-8,9,7,-7,-9)}
 for i,p in enumerate(a):
  if not p or p.isupper()!=us:continue
  t=p.lower(); dest=[]
  if t=='p':
   z=i+(-8 if us else 8)
   if 0<=z<64 and not a[z]:
    dest.append(z)
    zz=z+(-8 if us else 8)
    if i//8==(6 if us else 1) and not a[zz]:dest.append(zz)
   for z in (i+(-9 if us else 7),i+(-7 if us else 9)):
    if 0<=z<64 and abs(z%8-i%8)==1 and ((a[z] and a[z].isupper()!=us) or str(z)==ep):dest.append(z)
  else:
   for d in dirs[t]:
    z=i
    while True:
     q=z+d
     if not 0<=q<64 or abs(q%8-z%8)>2 or (abs(d)==1 and q//8!=z//8):break
     z=q
     if a[z]:
      if a[z].isupper()!=us:dest.append(z)
      break
     dest.append(z)
     if t in 'nk':break
  if t=='k':
   for c,z,mid in (('K',6,5),('Q',2,3),('k',62,61),('q',58,59)):
    if c in castle and not a[z] and not a[mid] and (c not in 'Qq' or not a[i-3]):dest.append(z)
  for z in dest:
   b=a[:];b[z]=b[i];b[i]=None
   if t=='p' and z//8 in (0,7):b[z]='Q' if us else 'q'
   if t=='k' and abs(z-i)==2:
    r=z+1 if z>i else z-2;w=z-1 if z>i else z+1;b[w]=b[r];b[r]=None
   k=next(j for j,v in enumerate(b) if v==('K' if us else 'k'))
   if not attacks(b,k,not us):out.append((i,z,b))
 return out
def score(a,us):
 n=0
 for i,p in enumerate(a):
  if p:
   v=V[p.lower()]; advance=(6-i//8 if p.isupper() else i//8-1) if p.lower()=='p' else 0
   n+=(v+advance*9)*(1 if p.isupper()==us else -1)
 return n
def search(a,turn,castle,ep,depth,alpha,beta):
 global N
 N+=1; us=turn=='w'; stand=score(a,us)
 if depth<=0:return stand
 if stand>=beta:return beta
 alpha=max(alpha,stand)
 ms=moves(a,turn,castle,ep)
 if not ms:return (-30000 if any(attacks(a,i,not us) for i,p in enumerate(a) if p==('K' if us else 'k')) else 0)
 ms.sort(key=lambda m:(-(V.get((a[m[1]] or '').lower(),0)+(800 if a[m[0]].lower()=='p' and m[1]//8 in (0,7) else 0)),m[0],m[1]))
 for i,z,b in ms:
  c=castle.replace('K','') if a[i]=='K' else castle.replace('k','') if a[i]=='k' else castle
  e=str((i+z)//2) if a[i].lower()=='p' and abs(z-i)==16 else '-'
  val=-search(b,'b' if us else 'w',c,e,depth-1,-beta,-alpha)
  if val>alpha:alpha=val
  if alpha>=beta:break
 return alpha
def choose(fen,legal):
 a,t,c,e=parse(fen);best=legal[0];bestv=-99999
 root=moves(a,t,c,e); by={(chr(i%8+97)+str(8-i//8)+chr(z%8+97)+str(8-z//8)):b for i,z,b in root}
 for m in sorted(legal):
  b=by.get(m[:4])
  if not b:continue
  if len(m)==5:b=b[:];b[ord(m[2])-97+8*(7-int(m[3]))]=m[4].upper() if t=='w' else m[4]
  v=-search(b,'b' if t=='w' else 'w',c,'-',2,-30001,30001)
  if v>bestv:best,bestv=m,v
 return best
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':g=post('/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
 print('game',g['game'],g['outcome'],g['reason'],file=sys.stderr)
print('done',g.get('wins'),g.get('draws'),g.get('losses'),file=sys.stderr)
