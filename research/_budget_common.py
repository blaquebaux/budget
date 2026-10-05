#!/usr/bin/python3
# =============================================================================
# _budget_common.py — shared helpers for Blaque Baux BUDGET (systematic short-dated put/call selling).
# Alpaca SIP daily bars (adjustment=all → total return, collateral yield counted); env keys. Read-only.
#
# BUDGET tests systematic OTM option SELLING for income — distinct from bankroll (monthly buy-write, XYLD/DIVO):
# here the engine is pure premium/vega harvest, the put-write. The marketed profile is seductive — a real program
# claims ~16%/yr at a 4.16% max drawdown over 2021-2026, "uncorrelated or negative in bear markets." That is an
# extraordinary risk profile for selling puts (which IS long equity-tail risk), so BUDGET asks where it comes from.
# Proxy: PUTW (CBOE S&P 500 PutWrite ETF — sells ATM SPX puts, holds T-bills) vs SPY, the buy-write complex, and a
# BIL collateral benchmark. The family's prior (brace = VRP harvest lags & crashes; brittle = near-expiry far-OTM
# short-vol is a trap) says selling vol is the insurer's side: steady premium, fat LEFT tail. The honest tells here:
# (1) PUTW's window INCLUDES the March-2020 vol gap that a 2021 start date skips; (2) a 16%/4%-DD profile is a far-OTM,
# mostly-T-bill book whose "return" is the collateral rate and whose tiny drawdown is tiny DELTA, not skill.
# =============================================================================
import os, json, urllib.request, math
import numpy as np

H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"], "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}
START, END = "2016-01-01", "2026-08-01"
_cache = {}

def bars(s):
    if s in _cache: return _cache[s]
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={s}&timeframe=1Day"
         f"&start={START}&end={END}&adjustment=all&feed=sip&limit=10000")
    try:
        d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=40))
        _cache[s] = {b["t"][:10]: b["c"] for b in d.get("bars", {}).get(s, [])}
    except Exception:
        _cache[s] = {}
    return _cache[s]

def panel(syms):
    D = {s: bars(s) for s in syms}; D = {s: v for s, v in D.items() if len(v) > 250}
    if not D: return {}, []
    u = list(D); dates = sorted(set.intersection(*[set(D[s]) for s in u]))
    return {s: np.array([D[s][d] for d in dates], float) for s in u}, dates

def rets(px): return px[1:] / px[:-1] - 1

def stats(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 30 or r.std() == 0: return dict(sh=float('nan'), cagr=float('nan'), dd=float('nan'), vol=float('nan'))
    cum = np.cumprod(1 + r)
    return dict(sh=r.mean()/r.std()*math.sqrt(252), cagr=cum[-1]**(252/len(r))-1,
                dd=(cum/np.maximum.accumulate(cum)-1).min(), vol=r.std()*math.sqrt(252))

def jarque_bera(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]; n = len(r)
    if n < 30 or r.std() == 0: return dict(skew=float('nan'), exkurt=float('nan'))
    z = (r - r.mean())/r.std(); return dict(skew=float(np.mean(z**3)), exkurt=float(np.mean(z**4)-3.0))

def beta_to(r, rb):
    r = np.asarray(r, float); rb = np.asarray(rb, float); m = np.isfinite(r) & np.isfinite(rb)
    if m.sum() < 30 or np.var(rb[m]) == 0: return float('nan')
    return float(np.cov(r[m], rb[m])[0,1]/np.var(rb[m]))

def maxdd(r):
    r = np.asarray(r, float); r = r[np.isfinite(r)]
    if len(r) < 5: return float('nan')
    cum = np.cumprod(1+r); return float((cum/np.maximum.accumulate(cum)-1).min())
