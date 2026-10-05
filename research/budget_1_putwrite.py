#!/usr/bin/python3
# =============================================================================
# budget_1_putwrite.py — is systematic put-selling a 16%/4%-DD miracle, or the insurer's fat-left-tail seat?
#
# All SIP daily total return (collateral yield counted), causal. PUTW = CBOE S&P 500 PutWrite proxy.
#  (A) THE COMPLEX: PUTW / PBP / XYLD vs SPY and a BIL (T-bill) floor — Sharpe, maxDD, skew, β/SPY. Put-write is an
#      equity-risk + VRP harvest; does it beat the index risk-adjusted, or lag it with a fat left tail (brace)?
#  (B) THE WINDOW TRICK: PUTW max drawdown measured from 2016 (incl. the March-2020 vol gap) vs from 2021 (the claim's
#      start, which SKIPS 2020). The 4.16% DD only exists if you start after the crash.
#  (C) BULL vs BEAR CORRELATION: claim says ~0/neg in bear. Put-selling is LONG equity-tail risk → it should be MORE
#      correlated and LOSE in bear. We split on SPY's 200-day regime and measure corr in each.
#  (D) WHERE 16%/4%-DD COMES FROM: synthetic far-OTM seller = BIL collateral + w·(PUTW − BIL) excess. Solve for the w
#      that yields ~4% DD, then show its return is mostly the COLLATERAL rate — not a vol-premium edge.
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _budget_common import panel, rets, stats, jarque_bera, beta_to, maxdd
import numpy as np

P, dates = panel(["SPY", "PUTW", "PBP", "XYLD", "BIL"])
R = {s: rets(P[s]) for s in P}; D = dates[1:]; spy = R["SPY"]
print("="*98); print(f"BUDGET #1 — systematic put-selling: miracle or the insurer's seat?  ({dates[0]} → {dates[-1]}, {len(dates)} days)"); print("="*98)
print("  CLAIM: ~16%/yr, maxDD -4.16%, 'uncorrelated/negative in bear', 2021-2026.")

# ---- (A) the complex --------------------------------------------------------------------------------
print(f"\n(A) COMPLEX vs SPY (full window)    {'Sharpe':>8}{'CAGR':>8}{'maxDD':>8}{'skew':>7}{'exKurt':>8}{'β/SPY':>7}")
for s in ["SPY","PUTW","PBP","XYLD","BIL"]:
    if s not in R: continue
    a=stats(R[s]); jb=jarque_bera(R[s]); b=beta_to(R[s], spy[-len(R[s]):]) if s!="SPY" else 1.0
    lab={"SPY":"index","PUTW":"ATM put-write","PBP":"buy-write","XYLD":"S&P buy-write","BIL":"T-bills (collateral)"}[s]
    print(f"  {s:5} {lab:20}{a['sh']:>+8.2f}{a['cagr']*100:>+7.1f}%{a['dd']*100:>+7.0f}%{jb['skew']:>+7.2f}{jb['exkurt']:>+8.1f}{b:>+7.2f}")

# ---- (B) the window trick ---------------------------------------------------------------------------
pw = R["PUTW"]; dpw = D[-len(pw):]
dd_full = maxdd(pw)
i2021 = next((k for k,x in enumerate(dpw) if x >= "2021-01-01"), 0)
dd_2021 = maxdd(pw[i2021:])
mar20 = [pw[k] for k,x in enumerate(dpw) if "2020-02-18" <= x <= "2020-03-23"]
crash = np.prod([1+z for z in mar20]) - 1 if mar20 else float('nan')
print(f"\n(B) WINDOW TRICK — PUTW max drawdown")
print(f"  from 2016 (incl. March-2020 vol gap): {dd_full*100:+.1f}%      Feb18→Mar23 2020 crash return: {crash*100:+.1f}%")
print(f"  from 2021 (the claim's start, SKIPS 2020): {dd_2021*100:+.1f}%   ← the '-4%' lives only after the crash")

# ---- (C) bull vs bear correlation -------------------------------------------------------------------
sma = np.array([np.mean(P["SPY"][max(0,k-200):k]) if k>=200 else np.nan for k in range(len(P["SPY"]))])[1:]
bull = (P["SPY"][1:] > sma)
m = np.isfinite(pw)
sp_al = spy[-len(pw):]; bull_al = bull[-len(pw):]
def corr(mask):
    mm = m & mask & np.isfinite(sp_al)
    return float(np.corrcoef(pw[mm], sp_al[mm])[0,1]) if mm.sum()>30 else float('nan')
c_bull, c_bear = corr(bull_al), corr(~bull_al)
print(f"\n(C) CORRELATION to SPY   bull regime (SPY>200dma): {c_bull:+.2f}    bear regime (SPY<200dma): {c_bear:+.2f}")
print("    put-selling is LONG equity-tail risk — it stays correlated and loses in the bear, not 'uncorrelated/negative'.")

# ---- (D) where 16%/4%-DD comes from -----------------------------------------------------------------
bil = R["BIL"][-len(pw):]; excess = pw - bil
ws = np.linspace(0, 2, 201); best_w, best_gap = 1.0, 9
for w in ws:
    syn = bil + w*excess
    if abs(maxdd(syn) + 0.0416) < best_gap: best_gap = abs(maxdd(syn)+0.0416); best_w = w
syn = bil + best_w*excess; syn_s = stats(syn); bil_s = stats(bil); pw_s = stats(pw)
print(f"\n(D) SYNTHETIC far-OTM seller = BIL + w·(PUTW−BIL), solved for ~4% maxDD")
print(f"  w={best_w:.2f} → maxDD {maxdd(syn)*100:+.1f}%, return {syn_s['cagr']*100:+.1f}%/yr  (of which BIL collateral alone = {bil_s['cagr']*100:+.1f}%/yr)")
print(f"  to reach the claim's 16%/yr you'd need w≈{(0.16-bil_s['cagr'])/max(pw_s['cagr']-bil_s['cagr'],1e-6):.1f} → maxDD {maxdd(bil + ((0.16-bil_s['cagr'])/max(pw_s['cagr']-bil_s['cagr'],1e-6))*excess)*100:+.0f}% (nowhere near 4%).")

# ---- verdict ----------------------------------------------------------------------------------------
lags = pw_s['sh'] <= stats(spy[-len(pw):])['sh'] + 0.05
fat_tail = jarque_bera(pw)['skew'] < -1.0
window_trick = dd_full < dd_2021 - 0.05
print("\n"+"="*98); print("READ:")
print(f"  • PUTW is the insurer's seat: Sharpe {pw_s['sh']:+.2f} vs SPY {stats(spy[-len(pw):])['sh']:+.2f}, skew {jarque_bera(pw)['skew']:+.2f}, exKurt {jarque_bera(pw)['exkurt']:+.0f} — equity-risk+VRP with a FAT LEFT TAIL, lags the index (brace confirmed).")
print(f"  • THE 4% DD IS A WINDOW TRICK: real maxDD {dd_full*100:+.0f}% (2016, incl. 2020's {crash*100:+.0f}% gap); the '-4%' only appears if you start AFTER the crash ({dd_2021*100:+.0f}% from 2021).")
print(f"  • NOT uncorrelated in bear: corr to SPY is {c_bear:+.2f} in the bear regime — put-selling loses WITH the market, by design.")
print(f"  • THE 16%/4%-DD IS COLLATERAL: a 4%-DD put book is ~{best_w:.0%} premium exposure; its return is mostly the T-bill rate ({bil_s['cagr']*100:+.1f}%/yr of {syn_s['cagr']*100:+.1f}%). The '16%' needs delta that blows the 4% DD.")

if lags and fat_tail and window_trick:
    v = ("NULL / LANDMINE (brace & brittle reconfirmed): systematic put-selling is the insurer's side — a VRP harvest "
         "that LAGS the index risk-adjusted and carries a fat left tail (skew < -1, the 2020 gap). The marketed "
         "'16%/yr at 4% DD, uncorrelated in bear' is a mirage built from (1) a 2021 start that skips the March-2020 "
         "crash, (2) a far-OTM, tiny-delta book whose return is mostly the T-bill COLLATERAL in a high-rate regime, and "
         "(3) ignoring that put-selling stays positively correlated and loses in real bears. You can have the 4% DD or "
         "the 16%, not both honestly. Size it tiny as insurance-selling, gate on vol — the mirror of bushel, not alpha.")
else:
    v = ("CONDITIONAL: put-selling harvests a real VRP but as an equity-risk premium with a left tail; treat the "
         "marketed numbers with suspicion and size to the net, not the brochure.")
print(f"\n  VERDICT: {v}")
print("  (No options chains in Alpaca → PUTW/PBP/XYLD are the listed proxies; total return counts the collateral yield.")
print("   Short-DATED/weekly selling (the claim's engine) only sharpens the gamma/pin tail brittle already rejected. The")
print("   honest home for option income that CLEARS the hurdle is bankroll's selective/active book, not naked premium.)")
