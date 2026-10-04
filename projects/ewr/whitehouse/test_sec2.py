import sys,os,time,json; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp'); from mcmcp import server as S
R=lambda *c: S.run_commands(list(c)).replace('\n',' | ')
print([ (p['name'],p['block']) for p in json.loads(S.get_players())])
print(R('summon cow -209.5 72 -115.5 {Tags:["ewhs","ewhs_testsubj","ewhs_t_snipe"],NoAI:1b,PersistenceRequired:1b,CustomName:"TEST intruder (lawn)",CustomNameVisible:1b,attributes:[{id:"minecraft:max_health",base:100}],Health:100f}'))
for t in range(12):
    time.sleep(2.5)
    print(round(t*2.5+2.5,1), R('scoreboard players get @e[tag=ewhs_t_snipe,limit=1] ewhs_st','data get entity @e[tag=ewhs_t_snipe,limit=1] Health',
        'scoreboard players get @e[tag=ewhs_t_arrest,limit=1] ewhs_st','data get entity @e[tag=ewhs_t_arrest,limit=1] Pos',
        'execute store result score #c ewhs_tmp if entity @e[tag=ewhs_return]','scoreboard players get #c ewhs_tmp')[:700])
