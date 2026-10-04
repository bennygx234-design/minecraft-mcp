import json,statistics
H={tuple(map(int,k.split(','))):v for k,v in json.load(open(r'C:\Users\benny\.claude\jobs\ef42125c\tmp\ewr\whitehouse\heights.json')).items()}
W,D=150,120
res=[]
for x in range(-312,-88-W+1,2):
  for z in range(-232,-94-D+1,2):
    pts=[H[(px,pz)] for px in range(x,x+W,2) for pz in range(z,z+D,2) if (px,pz) in H]
    nw=sum(p[1] for p in pts); hs=[p[0] for p in pts]
    m=statistics.median(hs)
    cf=sum(abs(h-m) for h in hs)
    res.append((cf,x,z,m,min(hs),max(hs),nw))
res.sort()
for r in res[:8]: print(r)
