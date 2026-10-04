import sys,os,time,json; os.environ['MCMCP_KEEP_FORCELOAD']='1'; sys.path.insert(0, r'C:\Users\benny\minecraft-mcp'); from mcmcp import server as S
R=lambda *c: print(S.run_commands(list(c)))
print([ (p['name'],p['block']) for p in json.loads(S.get_players())])
R('kill @e[tag=ewhs_testsubj]',
  'summon armor_stand -264.5 72 -160.5 {Tags:["ewhs","ewhs_testsubj","ewhs_t_arrest"],Invulnerable:1b,CustomName:"TEST intruder (indoors)",CustomNameVisible:1b}',
  'summon husk -209.5 72 -115.5 {Tags:["ewhs","ewhs_testsubj","ewhs_t_snipe"],NoAI:1b,PersistenceRequired:1b,CustomName:"TEST intruder (lawn)",CustomNameVisible:1b,attributes:[{id:"minecraft:max_health",base:100}],Health:100f}',
  'function ewr_whitehouse:security_on')
for t in range(16):
    time.sleep(2)
    print(t*2+2, S.run_commands(['scoreboard players get @e[tag=ewhs_t_arrest,limit=1] ewhs_st','data get entity @e[tag=ewhs_t_arrest,limit=1] Pos',
        'scoreboard players get @e[tag=ewhs_t_snipe,limit=1] ewhs_st','data get entity @e[tag=ewhs_t_snipe,limit=1] Health',
        'execute store result score #c ewhs_tmp if entity @e[tag=ewhs_chaser]','scoreboard players get #c ewhs_tmp']).replace('\n',' | ')[:900])
