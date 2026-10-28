# QUANTUM READINESS SURVEY

COMP 524 - Cryptography & Security Project: a TLS quantum-readiness scan of 250 websites across 7 sectors, scored for HN-DL (harvest now, decrypt later) risk.

---

## RESEARCH PAPERS

| # | PAPER | AUTHORS | PUBLISHED |
|---|---|---|---|
| 1 | [On the Practical Feasibility of Harvest-Now, Decrypt-Later Attacks](https://arxiv.org/abs/2603.01091) | Javier Blanco-Romero, Florina Almenares Mendoza, Carlos García Rubio, Celeste Campo, Daniel Díaz Sánchez | arXiv:2603.01091, 2026 |
| 2 | [Harvest-Now, Decrypt-Later: A Temporal Cybersecurity Risk in the Quantum Transition](https://doi.org/10.3390/telecom6040100) | Francis Kagai, Philip Branch, Jason But, Rebecca Allen | *Telecom* 6(4), 100, 2025 |
| 3 | [A Layered Risk Scoring Model for TLS Connections Against Quantum Threats](https://eprint.iacr.org/2026/1174) | Yu-Lim Hyoung, Su-Min Jeong, Da-Eun Lim, Do-Yun Park, Su-Been Cho, Jae-Hwan Kim, Hyun-Ji Kim, Hwa-Jeong Seo | Cryptology ePrint Archive 2026/1174 |

Paper 3 is the source of the risk score below.

---

## FILES

| FILE / FOLDER | WHAT IT IS |
|---|---|
| `sites-for-probing.csv` | The real list: 250 hand-picked websites across 7 sectors |
| `tranco-top1m-GQ32K.csv` | The full Tranco list we downloaded |
| `tranco-top250-raw.csv` | First 250 rows of Tranco, kept to show why the raw list was not used |
| `probe-sites.py` | Probes every site with OpenSSL and saves one `.txt` per site |
| `probe-results/` | Raw OpenSSL output, one `.txt` per site (latest probe; older runs are in git history) |
| `probe-results-key-readings.py` | Reads each `.txt`, assigns a tier and risk score, prints CSV rows |
| `scores/tiers-YYYY-MM-DD.csv` | Scored results for each probe, named by date |
| `scores/summary-YYYY-MM-DD.txt` | Saved sector summary for each probe |
| `probe-result-count-tiers.py` | Summary per sector: count, % safe, average risk, readiness |

---

## DATA SOURCE

| ITEM | VALUE |
|---|---|
| Tranco list ID | GQ32K ([link](https://tranco-list.eu/list/GQ32K)) |
| Downloaded | October 24, 2026 |
| Covers | Sep 25 to Oct 24, 2026 |
| Sources combined | CrUX, Farsight, Majestic, Cloudflare Radar, Cisco Umbrella |
| File | `tranco-top1m-GQ32K.csv` |

---

## SITE SELECTION

- **NOT** the raw Tranco top 250. Many top-ranked domains are infrastructure (CDNs, DNS, ad hosts like `gstatic.com` or `akamai.net`), not websites people visit. See `tranco-top250-raw.csv`.
- **INSTEAD:** 250 well-known websites hand-picked across 7 sectors, 35 to 36 per sector (250 ÷ 7 does not divide evenly).
- **CHECKED:** every domain is on Tranco list GQ32K, with its rank in the `tranco_rank` column.
- **SORTED:** by Tranco rank within each sector.
- **SCOPE:** mostly US-based websites, probed from the US. Results reflect what a US user sees. A global sample is future work.

| SECTOR | SITES |
|---|---|
| Banking | 36 |
| Education | 36 |
| Government | 36 |
| Healthcare | 35 |
| News | 35 |
| Retail | 36 |
| Technology | 36 |

---

## FIXED SITE LIST

- `sites-for-probing.csv` is frozen as of October 24, 2026.
- The same 250 sites are used for every probe through December 2026.
- Sites that fail are kept in the list and reported as "No connection", not replaced.

---

## TOOLS

| TOOL | VERSION | LINK |
|---|---|---|
| OpenSSL | 4.0.3 | [Source code](https://github.com/openssl/openssl) · [s_client manual](https://docs.openssl.org/master/man1/openssl-s_client/) |
| Python | 3.15.1 | |
| OS | macOS | |
| Network | Direct connection, no VPN or proxy | |

ML-KEM support was confirmed with `openssl list -kem-algorithms`.

---

## THE PROBE COMMAND

```
echo | openssl s_client -connect SITE:443 -servername SITE -groups X25519MLKEM768:X25519:secp256r1:MLKEM768 2>/dev/null > probe-results/SITE.txt
```

### `openssl s_client`

- **OPENSSL SAYS:** "SSL/TLS client program."
- **WHAT IT DOES:** does one TLS handshake with a website, like a browser would.
- **WHY:** a browser hides the handshake details, and s_client prints them.

### `-connect SITE:443`

- **OPENSSL SAYS:** "This specifies the host and optional port to connect to."
- **WHAT IT DOES:** picks the website and the port.
- **WHY:** 443 is the standard HTTPS port.

### `-servername SITE`

- **OPENSSL SAYS:** "Set the TLS SNI (Server Name Indication) extension in the ClientHello message to the given value."
- **WHAT IT DOES:** tells the server which website we want.
- **WHY:** one server can host many sites, and without SNI it might send the wrong certificate.

### `-groups X25519MLKEM768:X25519:secp256r1:MLKEM768`

- **OPENSSL SAYS:** no description of its own; it points to [SSL_CONF_cmd](https://docs.openssl.org/master/man3/SSL_CONF_cmd/).
- **WHAT IT DOES:** lists the key exchange options we offer, separated by `:`, best first. The site picks the first one it supports.
- **WHY:** it copies a modern browser, so we measure what real users get.
- **NOTE:** ML-KEM-512 was not offered, so L2c (weak PQC) is 0 for every site.

| OPTION | TYPE | TIER IF PICKED |
|---|---|---|
| `X25519MLKEM768` | Hybrid (classical + post-quantum) | Tier 2, safe |
| `X25519` | Classical | Tier 1b, not safe |
| `secp256r1` | Classical (shows as `prime256v1`) | Tier 1b, not safe |
| `MLKEM768` | Post-quantum only | Tier 3, PQC-ready |

### SHELL PARTS (NOT OPENSSL)

| PART | WHAT IT DOES |
|---|---|
| `echo \|` | Sends empty input, so the connection closes right away |
| `2>/dev/null` | Throws away error messages |
| `> probe-results/SITE.txt` | Saves the output, one file per site |

---

## TIERS

| TIER | MEANING | HOW IT IS DETECTED |
|---|---|---|
| Tier 1a (worst) | RSA key exchange, no forward secrecy | TLS 1.2, cipher with no "DHE", no key exchange line |
| Tier 1b (not safe) | Classical key exchange (X25519, prime256v1) | `Peer Temp Key` line |
| Tier 2 (safe) | Hybrid post-quantum | `MLKEM` in the key exchange line |
| Unclear | OpenSSL could not name the group | `NID: 0`, left out of scoring |
| No connection | No HTTPS handshake | No key exchange line, left out of scoring |

---

## RISK SCORE

Based on *A Layered Risk Scoring Model for TLS Connections Against Quantum Threats* (Hyoung et al.), using the paper's own test settings.

| LAYER | CHECKS | POINTS |
|---|---|---|
| L1 | TLS version | TLS 1.2 + RSA = 6, TLS 1.2 + ECDHE = 4.5, TLS 1.3 + hybrid = 3, TLS 1.3 classical = 0 |
| L2a | Key exchange | RSA = 20, ECDHE = 12, hybrid = 0 |
| L2b | Cipher | AES-128 = 2, AES-256 = 0 |
| L2c | Weak post-quantum | ML-KEM-512 = 6, otherwise 0 |
| L3 | Certificate | Expired = 5, under 30 days = 5 × (30 − days) ÷ 30, otherwise 0 |

```
score = (L1 + L2a + L2b + L2c + L3) × 1.5 ÷ 118 × 100
readiness = 100 − average score per sector
```

---

## RUN ORDER

| STEP | COMMAND | OUTPUT |
|---|---|---|
| 1. Probe | `python3 probe-sites.py` | `probe-results/` (one .txt per site) |
| 2. Score | `python3 probe-results-key-readings.py > scores/tiers-YYYY-MM-DD.csv` | Dated CSV in `scores/` |
| 3. Summary | `python3 probe-result-count-tiers.py \| tee scores/summary-YYYY-MM-DD.txt` | Results per sector (set the CSV date inside the script) |

---

## PROBE LOG

| PROBE | DATE | SCORES FILE | SITES SCORED | NOTES |
|---|---|---|---|---|
| 1 | October 24, 2026 | `scores/tiers-2026-10-24.csv` | 242 of 250 | 1 no connection, 7 unclear. Raw `.txt` files were accidentally deleted. |
| 1 (re-probe) | October 25, 2026 | `scores/tiers-2026-10-25.csv` | 245 of 250 | Re-probe to rebuild the raw files. |
| 2 | October 28, 2026 | `scores/tiers-2026-10-28.csv` | 244 of 250 | state.gov, ssa.gov, humana.com hung (no connection). vs Oct 25: nps.gov, mychart.com, spotify.com, homedepot.com moved to hybrid; etrade.com moved off RSA; fidelity.com dropped to classical. Current `probe-results/` is from this run. |

- **CONSISTENCY:** results shift slightly between runs (irs.gov switched TLS versions; spotify.com and fidelity.com flipped between hybrid and classical). Big sites run many servers that are not all upgraded at once, which is why each site is probed more than once.
- **HANGS:** ssa.gov and humana.com were "Unclear" on Oct 24 and hung on Oct 28. Some servers may stall on the larger post-quantum ClientHello (the ML-KEM key share makes the first message bigger).
