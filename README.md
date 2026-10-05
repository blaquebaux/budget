# Blaque Baux Budget

**Systematic short-dated put/call selling — the "16%/yr at 4% drawdown" claim, taken apart. It's the insurer's seat, dressed up.**

Budget tests systematic OTM option *selling* for income — distinct from `bankroll`'s monthly buy-write. The marketed
profile is seductive: a real program claims **~16%/yr at a 4.16% max drawdown, "uncorrelated or negative in bear
markets," 2021–2026.** That's an extraordinary risk profile for selling puts, which *is* long equity-tail risk — so
Budget asks where it actually comes from. Proxy: **PUTW** (CBOE S&P 500 PutWrite ETF), whose data runs 2016–2025 and
therefore *includes* the March-2020 vol gap the claim's start date skips.

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/budget_1_putwrite.py   # needs Alpaca data keys in the environment
```

## The finding (the miracle is a mirage — four tells)

[`research/budget_1_putwrite.py`](research/budget_1_putwrite.py) — SIP daily total return (collateral counted), causal.

**1 — It's the insurer's seat.** PUTW: Sharpe **+0.57** vs SPY +0.82, **skew −1.82**, excess kurtosis **+31**, β 0.64 —
an equity-risk + VRP harvest that *lags* the index with a fat left tail (confirms `brace`).

**2 — The 4% drawdown is a window trick.** PUTW's real max drawdown is **−28%** from 2016 (March-2020 alone was −28%).
Even from the claim's 2021 start it's **−16.5%** (2022). A −4% figure only exists if you start *after* the crash *and*
shrink the position.

**3 — Not uncorrelated in a bear.** Correlation to SPY is **+0.87** in the bear regime (SPY < 200-dma) — put-selling
loses *with* the market, by design, not "uncorrelated/negative."

**4 — The 16%/4%-DD is collateral, not edge.** Solve for the position size that yields a 4% drawdown: it's **~14%
premium exposure**, returning **+2.7%/yr — of which +1.9% is just the T-bill collateral** in a high-rate regime. To
reach 16%/yr you'd need ~2.9× exposure → a **−69%** drawdown. **You can have the 4% DD or the 16%, not both honestly.**

## Verdict

**NULL / LANDMINE — `brace` and `brittle` reconfirmed.** Systematic put-selling is the insurer's side: a real
volatility-risk-premium harvest that lags the index risk-adjusted and carries a fat left tail. The marketed
"16%/yr at 4% DD, uncorrelated in bear" is built from a post-2020 start, a tiny-delta book whose return is mostly the
collateral rate, and quietly ignoring that short vol loses in real bears. Size it *tiny*, as insurance-selling, gated
on vol — the mirror of `bushel`, not alpha. (Short-dated/weekly selling, the claim's actual engine, only sharpens the
gamma/pin tail `brittle` already rejected.) The honest home for option income that *clears* the hurdle remains
`bankroll`'s selective/active book — not naked premium.

## Status

**Research.** Honest null — a seductive brochure taken apart line by line with the fund's own numbers. Fat-tail
scorecard (Sharpe, skew, excess-kurtosis, β, drawdown), window-sensitivity, regime-conditional correlation, a
collateral-vs-premium decomposition, Alpaca SIP daily total return. No live capital.
