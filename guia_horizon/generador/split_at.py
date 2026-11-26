import sys, numpy as np, soundfile as sf
def split_at(wav, cuts, outprefix):
    a, sr = sf.read(wav); b = [0] + [int(c * sr) for c in cuts] + [len(a)]
    thr = np.percentile(np.abs(a), 95) * 0.03; out = []
    for k in range(len(b) - 1):
        seg = a[b[k]:b[k + 1]]; idx = np.where(np.abs(seg) > thr)[0]
        if len(idx): seg = seg[max(0, idx[0] - int(0.05 * sr)): idx[-1] + int(0.08 * sr)]
        sf.write(f"{outprefix}_{k:02d}.wav", seg, sr); out.append(round(len(seg) / sr, 2))
    return out
if __name__ == "__main__":
    print(split_at(sys.argv[1], [float(x) for x in sys.argv[2].split(",")], sys.argv[3]))
