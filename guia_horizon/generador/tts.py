import re, sys, os, json, hashlib
sys.path.insert(0,'/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/work')
from episodios2 import EPISODIOS
REP=[(r'/guia','barra guía'),(r'desafio\b','desafío'),(r'Dr\. Stone','doctor Stoun'),(r'/hm ', 'barra hache eme '),(r'/createc','barra créate ce'),(r'/joinc','barra yóin ce'),(r'/exitc','barra éxit ce'),
 (r'/mgc','barra eme ge ce'),(r'/mgp','barra eme ge pe'),(r'/subc','barra sub ce'),(r'/asubc','barra a sub ce'),(r'/asub','barra a sub'),
 (r'/trade','barra tréid'),(r'/(\w+)',r'barra \1'),(r'barra c\b','barra ce'),(r'barra alcancia','barra alcancía'),(r'\bg6\b','ge seis'),(r'\bY 280','i griega 280'),(r'F3','efe tres'),
 (r'\bcamera\b','cámera'),(r'\bhitbox(es)?\b',r'jitbox\1'),(r'\bchunks?\b','chanks'),(r'\bdebug\b','dibág'),(r'\bDebug\b','Dibág'),(r'Inventory','Ínventori'),
 (r'\bLove\b','Lov'),(r'\bAngry\b','Ángri'),(r'Triple T','Triple Te'),(r'HorizonWare','Jorizon uér'),(r'Horizon','Joráizon'),(r'Raypaint','Réi peint'),
 (r'\bwarden\b','uórden'),(r'\bwither\b','uíder'),(r'\bbreeze\b','bris'),(r'\bhusk\b','jasc'),(r'\bghasts?\b','gasts'),(r'\bevoker\b','évoquer'),
 (r'\bphantoms\b','fántoms'),(r'\bcreeper\b','críper'),(r'\bshulker\b','shúlker'),(r'Overworld','Óver uorld'),(r'\bNether\b','Néder'),
 (r'\bblaze\b','bleis'),(r'Hardcore','Jardcor'),(r'\bJava\b','Yava'),(r'Tung Tung Sahur','Tun tun sajur'),(r'\bBro\b','Brou'),(r'Matrix','Méitrix'),
 (r'Extra Live','Extra laif'),(r'\bitem\b','ítem'),(r'\bpiglins\b','píglins'),(r'endermites','endermáits'),(r'\bEnd\b','End'),(r'\bmix\b','mics'),(r'kevlar','kévlar'),(r'HUD','jud')]
def tts_text(s):
    for a,b in REP: s=re.sub(a,b,s)
    return s
if __name__=='__main__':
    from kokoro_onnx import Kokoro
    import soundfile as sf
    k=Kokoro('/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/tts/kokoro.onnx','/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/tts/voices.bin')
    os.makedirs('/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/voz2',exist_ok=True)
    eps=[int(x) for x in sys.argv[1:]]
    for ep in EPISODIOS:
        if ep['n'] not in eps: continue
        for sc in ep['escenas']:
            for ln in sc['lineas']:
                say=ln[0]
                t=tts_text(say); h=hashlib.md5(t.encode()).hexdigest()[:12]
                p=f'/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/voz2/{h}.wav'
                if os.path.exists(p): continue
                a,sr=k.create(t,voice='ef_dora',speed=1.08,lang='es'); sf.write(p,a,sr)
        print('ep',ep['n'],'ok',flush=True)
