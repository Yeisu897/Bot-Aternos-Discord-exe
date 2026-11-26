# Parte el audio de una escena en frases: candidatos = silencios; se eligen por programación dinámica
# combinando largo del silencio y cercanía al punto esperado (proporcional a las letras de cada frase).
import sys, subprocess, json, numpy as np, soundfile as sf
def split(mp3, texts, outprefix, weights=None):
    n = len(texts)
    wav = mp3[:-4] + ".wav"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", mp3, "-ac", "1", "-ar", "24000", wav], check=True)
    a, sr = sf.read(wav); hop = int(sr * 0.01)
    e = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)])
    thr = max(1e-4, np.percentile(e, 95) * 0.04)
    sil = e < thr
    voiced = np.where(~sil)[0]; v0, v1 = voiced[0], voiced[-1]
    runs = []; i = v0
    while i < v1:
        if sil[i]:
            j = i
            while j < v1 and sil[j]: j += 1
            if j - i >= 12: runs.append(((i + j) / 2, (j - i) / 100))
            i = j
        else: i += 1
    L = weights or [len(t) + 6 for t in texts]; tot = sum(L); span = v1 - v0
    exp = [v0 + span * sum(L[:k + 1]) / tot for k in range(n - 1)]
    C = len(runs); INF = 1e9
    # dp[k][c] = mejor costo usando el candidato c como corte k
    def cost(k, c):
        pos, g = runs[c]
        return abs(pos - exp[k]) / 100 * 1.0 - g * 6.0
    dp = [[INF] * C for _ in range(n - 1)]; bk = [[-1] * C for _ in range(n - 1)]
    for c in range(C): dp[0][c] = cost(0, c)
    for k in range(1, n - 1):
        best, bi = INF, -1
        for c in range(C):
            if c > 0 and dp[k - 1][c - 1] < best: best, bi = dp[k - 1][c - 1], c - 1
            if bi >= 0: dp[k][c] = best + cost(k, c); bk[k][c] = bi
    c = min(range(C), key=lambda c: dp[n - 2][c]); cuts = [c]
    for k in range(n - 2, 0, -1): c = bk[k][c]; cuts.append(c)
    cuts = sorted(int(runs[c][0]) for c in cuts)
    bounds = [0] + [x * hop for x in cuts] + [len(a)]
    info = []
    for k in range(n):
        seg = a[bounds[k]:bounds[k + 1]]
        idx = np.where(np.abs(seg) > thr * 2)[0]
        if len(idx): seg = seg[max(0, idx[0] - int(0.05 * sr)): idx[-1] + int(0.08 * sr)]
        sf.write(f"{outprefix}_{k:02d}.wav", seg, sr); info.append(round(len(seg) / sr, 2))
    return info
if __name__ == "__main__":
    sc = json.load(open(sys.argv[2]))
    o = [x for x in sc if x["ep"] == int(sys.argv[3]) and x["si"] == int(sys.argv[4])][0]
    texts = o["text"].split("\n\n")
    sys.path.insert(0, "/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/work"); import episodios2 as E, hashlib, soundfile as sf2
    from tts import tts_text
    lines = [e for e in E.EPISODIOS if e["n"] == o["ep"]][0]["escenas"][o["si"]]["lineas"]
    ws = []
    for ln in lines:
        h = hashlib.md5(tts_text(ln[0]).encode()).hexdigest()[:12]
        ws.append(sf2.info("/tmp/claude-0/-home-user-Bot-Aternos-Discord-exe/5b37ac7f-bef1-5d76-a31d-0c39ffbb2892/scratchpad/voz2/" + h + ".wav").duration)
    info = split(sys.argv[1], texts, sys.argv[5], ws)
    print([ (d, len(t)) for d, t in zip(info, texts)])
