# Potential International Fixtures

This file records source-backed candidate amortization examples found during
the May 2026 international fixture search. None of these have been committed
as fixtures yet. Each candidate still needs source re-retrieval, local
Decimal simulation, and exact reconciliation against every published value
selected from the source.

Standing rules from `CLAUDE.md` apply:

- Start from the retrieved source; do not invent parameters and search for a
  matching citation later.
- A fixture must reproduce every published value it claims to validate.
- Sources with missing parameters, approximate values, whole-currency-only
  rounding where cents are required, or internally inconsistent rows belong
  here or in `future-work.md`, not in `tests/schedules/`.

## Japan

### JHF / Flat35 equal-payment table

- Source: Japan Housing Finance Agency / Flat35, "元利均等返済・元金均等返済"
- URL: <https://www.flat35.com/loan/lineup/kinto/index.html>
- Type: official JHF/Flat35 page; copyright/license not stated.
- Location: section `元利均等返済と元金均等返済の比較（参考）`.
- Published parameters: `借入額 2,000万円`, fixed annual rate `年1.5%`,
  term `30年`.
- Published level-payment rows, in yen:

| Payment | Payment | Principal | Interest | Balance |
|---:|---:|---:|---:|---:|
| 12 | 69,024 | 44,634 | 24,390 | 19,468,058 |
| 60 | 69,024 | 47,392 | 21,632 | 17,258,727 |
| 120 | 69,024 | 51,081 | 17,943 | 14,304,092 |
| 180 | 69,024 | 55,056 | 13,968 | 11,119,489 |
| 240 | 69,024 | 59,342 | 9,682 | 7,687,015 |
| 300 | 69,024 | 63,960 | 5,064 | 3,987,379 |

- Published totals: total payment `24,848,426`, principal
  `20,000,000`, interest `4,848,426`.
- Likely model: fixed-rate monthly level-payment annuity, nominal annual
  rate divided by 12, yen-rounded row values.
- Caveats: the page labels the values as approximate/reference (`概算` /
  `参考`). The current library quantizes to cents (`0.01`), while this
  source publishes integer-yen rows. The same page also publishes a
  constant-principal (`元金均等返済`) table, which is outside the current
  `mortgagemath` surface.

### LoanKeisan full 360-row calculator schedule

- Source: ローン計算ドットコム, "3,000万円借入のローン計算、金利1.000％、借入期間30年"
- URL: <https://www.loankeisan.com/bin/calc?a=3000&b=0&i=1&p=30&t=r>
- Type: private calculator; copyright 2006-2025, no reuse license found.
- Published parameters: `借入金額 3,000万円`, `金利 1.000%`,
  `借入期間 30年 (360回払)`.
- Published summary values: total payment `34,736,908円`, total interest
  `4,736,908円`, monthly payment `96,491円`, annual payment `1,157,892円`.
- Published schedule columns: `回数`, `返済月額`, `元金分`, `利息分`,
  `返済後残高`.
- Example anchors:

| Payment | Payment | Principal | Interest | Balance |
|---:|---:|---:|---:|---:|
| 1 | 96,491 | 71,491 | 25,000 | 29,928,509 |
| 120 | 96,491 | 78,941 | 17,550 | 20,981,354 |
| 240 | 96,491 | 87,240 | 9,251 | 11,014,627 |
| 360 | 96,639 | 96,559 | 80 | 0 |

- Likely model: fixed monthly level-payment annuity, yen-rounded interest
  and balance each row, final payment adjusted to clear balance.
- Caveats: strong arithmetic source but weaker institutional authority
  because it is a generic private calculator, not a lender, regulator, or
  textbook. Integer-yen quantization is now supported with
  `currency_unit = "1"`, but a quick local check still differs by one yen
  from the published payment/final adjustment, so this likely needs an
  explicit floor/`ROUND_DOWN` convention before becoming fixture-ready.

## South Korea

### Tistory worked Korean mortgage table

- Source: "2025년 주택담보대출 3억! 월 상환금은 얼마일까? 금리별 실전 비교표"
- URL:
  <https://jjonew.tistory.com/entry/2025%EB%85%84-%EC%A3%BC%ED%83%9D%EB%8B%B4%EB%B3%B4%EB%8C%80%EC%B6%9C-3%EC%96%B5-%EC%9B%94-%EC%83%81%ED%99%98%EA%B8%88%EC%9D%80-%EC%96%BC%EB%A7%88%EC%9D%BC%EA%B9%8C-%EA%B8%88%EB%A6%AC%EB%B3%84-%EC%8B%A4%EC%A0%84-%EB%B9%84%EA%B5%90%ED%91%9C-%F0%9F%93%8A>
- Type: Korean blog; license not stated.
- Location: `주택담보대출 기본 가정`, `금리·기간별 월 납부액 비교표`, and
  `30년 대출 시, 매달 납부 내역 (4.0% 금리 기준)`.
- Published parameters: principal `300,000,000원`, repayment method
  `원리금균등상환`, rates `4.00%` and `4.50%`, terms 10/20/30 years.
- Payment anchors:

| Rate | Term | Monthly payment | Total paid | Total interest |
|---:|---:|---:|---:|---:|
| 4.00% | 10 yr | 3,037,354 | 364,482,480 | 64,482,480 |
| 4.00% | 20 yr | 1,817,941 | 436,305,840 | 136,305,840 |
| 4.00% | 30 yr | 1,432,246 | 515,608,560 | 215,608,560 |
| 4.50% | 10 yr | 3,109,152 | 373,098,240 | 73,098,240 |
| 4.50% | 20 yr | 1,897,948 | 455,507,520 | 155,507,520 |
| 4.50% | 30 yr | 1,520,056 | 547,220,160 | 247,220,160 |

- Published row cells for the `4.00%`, 30-year case:

| Payment | Payment | Interest | Principal | Balance |
|---:|---:|---:|---:|---:|
| 1 | 1,432,246 | 1,000,000 | 432,246 | 299,567,754 |
| 2 | 1,432,246 | 998,559 | 433,687 | 299,134,067 |
| 3 | 1,432,246 | 997,114 | 435,132 | 298,698,935 |

- Likely model: monthly level-payment annuity, nominal annual rate divided
  by 12, integer-won payment and interest rounding.
- Caveats: self-published source and only the first three rows are
  published. Current `mortgagemath` is cents-oriented, not integer-won
  oriented.

### Rankmin payment-anchor table

- Source: "1억~10억 대출 월상환액은 얼마일까?"
- URL:
  <https://rankmin.com/1%EC%96%B5-%EB%8C%80%EC%B6%9C-%EC%9B%94%EC%83%81%ED%99%98%EC%95%A1/>
- Type: Korean blog; license not stated.
- Location: section `1~10억 대출 월상환액 (30년, 3.5%, 원리금균등 상환)`.
- Published parameters: principal `1억` through `10억` KRW, annual rate
  `3.5%`, term `30년 / 360개월`, repayment method `원리금균등`.
- Published payment anchors:

| Principal | Monthly payment |
|---:|---:|
| 100,000,000 | 449,044 |
| 200,000,000 | 898,088 |
| 300,000,000 | 1,347,132 |
| 400,000,000 | 1,796,176 |
| 500,000,000 | 2,245,220 |
| 600,000,000 | 2,694,264 |
| 700,000,000 | 3,143,308 |
| 800,000,000 | 3,592,352 |
| 900,000,000 | 4,041,396 |
| 1,000,000,000 | 4,490,440 |

- Caveats: payment-only anchors, self-published source, integer-won
  rounding.

### Official Korean near misses

- Source: 주택도시기금 맞춤정보 IV 상환액 정보
- URL: <https://nhuf.molit.go.kr/FP/FP11/FP1104.jsp>
- Caveat: official source with monthly payment examples, but the exact
  annual rate tied to the table was not published on the retrieved page.

- Source: Korea Housing Finance Corporation 보금자리론 설명서, 붙임1
- URL:
  <https://www.hf.go.kr/cms/etcResourceDown.do?key=%24cms%24AwRg+sBsEExjlgBYRIHQAcAmAzIA&site=%24cms%24NYeyA>
- Caveat: official PDF with `100,000,000원 / 3% / 10년`, but values are
  annual and rounded in `만원`, not won-precision row values.

## Italy

### MutuiOnline row excerpt

- Source: MutuiOnline.it, "Ammortamento alla francese..."
- URL:
  <https://www.mutuionline.it/guide-mutui/domande-frequenti/ammortamento-alla-francese-cos-e-e-in-cosa-si-differenzia-da-quello-all-italiana.asp>
- Type: public web article; no reuse license found.
- Location: row excerpt around the worked example table.
- Published parameters: capital financed `€200,000.00`, fixed rate
  `3.40%`, term `20 anni`, constant payment `€1,149.67`. Monthly
  cadence is implied by the payment amount and 20-year term, but should
  be rechecked in source text.
- Published rows:

| Row | Payment | Interest | Principal | Balance |
|---:|---:|---:|---:|---:|
| 0 | 1,149.67 | 0.00 | 0.00 | 200,000.00 |
| 1 | 1,149.67 | 566.67 | 583.00 | 199,417.00 |
| 2 | 1,149.67 | 565.01 | 584.65 | 198,832.34 |
| 3 | 1,149.67 | 563.36 | 586.31 | 198,246.03 |
| 4 | 1,149.67 | 561.70 | 587.97 | 197,658.06 |
| 5 | 1,149.67 | 560.03 | 589.64 | 197,068.42 |

- Likely model: fixed monthly level-payment annuity, nominal annual rate
  divided by 12, possibly carry-precision balance tracking.
- Caveats: only an excerpt, not a full schedule. Local simulation must
  verify whether every row matches; the row-level cents suggest a convention
  that may differ from simple round-each subtraction.

### Italian bank transparency PDFs

These are useful payment-only anchors because they disclose Italian
`Francese` amortization and day-count conventions. Each needs local
simulation before fixture work.

- Banca Etica, "FIMU_1S0244 - Mutuo fondiario CONSAP Soci - Fondo di
  garanzia prima casa"
  - URL:
    <https://assets.bancaetica.it/FogliInformativi/FIMU_1S0244%20-%20Mutuo%20fondiario%20CONSAP%20Soci%20-%20Fondo%20di%20garanzia%20prima%20casa.pdf>
  - Location: page 8 of 13, piano/rate table.
  - Details: `FRANCESE A RATE COST. POSTIC.`, `GIORNI COMMERCIALI / 360`.
  - Fixed anchor: `€200,000`, `3.50%`, `20 anni`, monthly payment
    `€1,159.92`; `3.60%`, `30 anni`, monthly payment `€909.29`.

- Solution Bank, "Informazioni Generali sul Credito Immobiliare - Mutuo
  Fondiario MCD Prima Casa"
  - URL:
    <https://solution.bank/wp-content/uploads/2024/06/Informazioni-Credito-Immobiliare-Consumatori-Mutuo-Fondario-Prima-Casa-MCD.pdf>
  - Document code: `ZF/000004812`, updated `04/04/2026`, page 4 of 7.
  - Details: `Tipo piano Francese`, monthly/trimestral/semestral/annual
    frequencies, `Giorni commerciali / 360`.
  - Fixed anchors for `€200,000`: `7%`, 10 years `€2,322.17`; 15 years
    `€1,797.66`; 20 years `€1,550.60`; 25 years `€1,413.56`; 30 years
    `€1,330.60`.

- Banca CRS, "Foglio Informativo Mutuo Ipotecario Ordinario Imprese"
  - URL:
    <https://bancacrs.it/trasparenza/TRASPARENZA%20BANCA/MUTUI%20E%20FINANZIAMENTI/MUTUI%20IPOTECARI/ORDINARI/MUTUO_IPOTECARIO_ORDINARIO_IMPRESE.pdf?x=08-01-2026_11_09>
  - Document code: `ZF/000005400`, updated `01/01/2026`, page 6 of 10.
  - Details: `Tipo ammortamento Francese`, monthly, `Giorni commerciali /
    360`.
  - Fixed anchors for `€200,000`: `5%`, 5 years `€3,774.25`; 10 years
    `€2,121.31`; 15 years `€1,581.59`; 20 years `€1,319.91`; 25 years
    `€1,169.18`.

- BCC Brescia, "Foglio Informativo Mutuo Fondiario Agrario Tasso
  Variabile Euribor"
  - URL: <https://www.bccbrescia.it/umbraco/surface/transparency/ShowFile/67119>
  - Document code: `ZF/000011881`, updated `01/04/2026`, page 7 of 10.
  - Details: `Francese`, monthly, `Giorni commerciali / 360`.
  - Variable payment anchors for `€200,000`, `5.65%`: 5 years
    `€3,834.09`; 10 years `€2,185.42`; 15 years `€1,650.13`.

## Denmark

The Denmark search did not produce a current fixture-ready source.
The strongest results were low-precision educational examples and
constant-principal/serial-loan examples outside the current package surface.

### Financer annuity explainer

- Source: Financer.dk, "Hvad er et annuitetslån?"
- URL: <https://financer.dk/laan/hvad-er-annuitetslaan/>
- Type: commercial explainer.
- Caveat: publishes Danish annuity concepts and examples, but values are
  not a source-backed cent/øre-precision mortgage schedule suitable for a
  fixture.

### Dinero amortization-plan explainer

- Source: Dinero.dk, "Amortisationsplan"
- URL: <https://dinero.dk/ordbog/amortisationsplan/>
- Type: accounting/education article.
- Caveat: useful conceptually, but not a mortgage/realkredit fixture with
  full parameters and øre-precision amortization rows.

### Constant-principal feature triggers

- Search terms found Danish `serielån` / constant-principal material, but
  no fixture-ready source was verified.
- Current `mortgagemath` does not model constant-principal/serial loans.
  A Danish or Nordic row-level `serielån` table could become a feature
  trigger only if the source publishes complete parameters and exact rows.

## Netherlands

### De Hypotheker annuity example

- Source: De Hypotheker, "Hoe werkt een annuïteitenhypotheek?"
- URL:
  <https://www.hypotheker.nl/begrippenlijst/hypotheek-afsluiten/annuiteitenhypotheek/>
- Type: commercial mortgage-advice article, license not stated.
- Location: `Rekenvoorbeeld annuïteitenhypotheek`.
- Published parameters: principal `€216,000`, rate `4%`, term `30 jaar`,
  monthly payment `€1,031.21`.
- Published rows:

| Month | Balance at start | Principal | Interest | Gross payment |
|---:|---:|---:|---:|---:|
| 1 | 216,000.00 | 311.22 | 720.00 | 1,031.21 |
| 2 | 215,688.78 | 312.25 | 718.96 | 1,031.21 |
| 3 | 215,376.53 | 313.30 | 717.92 | 1,031.21 |
| 4 | 215,063.23 | 314.34 | 716.88 | 1,031.21 |
| 5 | 214,748.89 | 315.39 | 715.83 | 1,031.21 |
| 355 | 6,115.75 | 1,010.83 | 20.39 | 1,031.21 |
| 356 | 5,104.92 | 1,014.20 | 17.02 | 1,031.21 |
| 357 | 4,090.72 | 1,017.58 | 13.64 | 1,031.21 |
| 358 | 3,073.14 | 1,020.97 | 10.24 | 1,031.21 |
| 359 | 2,052.17 | 1,024.38 | 6.84 | 1,031.21 |
| 360 | 1,027.79 | 1,027.79 | 3.43 | 1,031.21 |

- Likely model: monthly level-payment annuity, nominal annual rate divided
  by 12.
- Caveats: row 1 and row 360 have one-cent arithmetic tension:
  principal plus interest equals `€1,031.22`, while the table payment is
  `€1,031.21`. This may need to stay in `future-work.md` unless the exact
  convention can be reproduced.

### Hulp bij Excel schedule excerpt

- Source: Hulp bij Excel, "Hypotheek berekenen in Excel: maandlasten en
  rente (2026)"
- URL: <https://hulpbijexcel.nl/hypotheek-berekenen-excel/>
- Type: instructional Excel article; license not stated.
- Location: `Hypotheek berekenen stap voor stap` and
  `Voorbeeld aflossingsschema`.
- Published parameters: principal `€350,000`, rate `4.5%`, term `30 jaar`,
  payment count `360`, payment `€1,773.40`.
- Published rows use Excel cashflow signs:

| Term | Interest | Principal | Total | Balance |
|---:|---:|---:|---:|---:|
| 1 | -1,312.50 | -460.90 | -1,773.40 | 349,539.10 |
| 2 | -1,310.77 | -462.63 | -1,773.40 | 349,076.47 |
| 3 | -1,309.04 | -464.36 | -1,773.40 | 348,612.11 |
| 360 | -6.61 | -1,766.79 | -1,773.40 | 0.00 |

- Likely model: Excel PMT/IPMT/PPMT carry-precision style, monthly
  nominal rate divided by 12.
- Caveats: not a lender/regulator; signs would need normalization in a
  fixture. Needs exact verification against the package's
  `BalanceTracking.CARRY_PRECISION` mode.

### Netherlands payment-only anchors

- Lening.com, "Aflossingsvrije lening binnen de familie"
  - URL: <https://www.lening.com/kennisbank/aflossingsvrije-lening-familie/>
  - Published parameters: fiscal annuity for own home/family mortgage,
    `€100,000`, `4%`, `30 jaar`, monthly payment `€477.42`, total
    interest `€71,871.20`, total paid `€171,871.20`.

- Goedmetjegeld, "Een hypotheek bij de bank en een lening bij je ouders;
  kan dat?"
  - URL:
    <https://goedmetjegeld.nl/een-hypotheek-bij-de-bank-en-een-lening-bij-je-ouders-kan-dat/>
  - Published parameters: family loan `€100,000`, `4%`, annuity form,
    maximum 30 years, monthly payment `€477.42`.

### Linear-mortgage feature trigger

- Source: De Hypotheker, "Hoe werkt een lineaire hypotheek?"
- URL:
  <https://www.hypotheker.nl/begrippenlijst/hypotheek-afsluiten/lineaire-hypotheek/>
- Published parameters: principal `€216,000`, rate `4%`, term
  `30 jaar = 360 maanden`, constant principal `€600`.
- Published rows include months 1-5 and 355-360 with interest and gross
  payment.
- Caveat: useful as a constant-principal feature trigger, but outside the
  current `mortgagemath` surface.

## France

### Magnolia mortgage and insurance schedule excerpt

- Source: Magnolia.fr, "Échéancier assurance de prêt : tout comprendre"
- URL: <https://www.magnolia.fr/assurance-pret-immobilier/contrat/echeancier>
- Type: commercial mortgage-insurance article; license not stated.
- Location: `Hypothèses` and `Tableau d'Amortissement (extrait sur les
  12 premiers mois)`.
- Published parameters: principal `€200,000`, fixed annual interest `2%`,
  term `20 ans (240 mois)`, constant monthly loan payment `€1,011.23`,
  insurance `0.30% du capital restant dû`.
- Published row examples:
  - Month 1: payment `1,011.23`, interest `333.33`, principal `677.90`,
    insurance `50.00`, total monthly `1,061.23`, balance `199,322.10`.
  - Month 12: interest `320.80`, principal `690.43`, insurance `48.13`,
    total monthly `1,059.36`, balance `191,790.25`.
- Caveats: quick local annuity check for `€200,000 / 2% / 240 months`
  gives a standard monthly P&I near `€1,011.77`, not `€1,011.23`, so this
  is not fixture-ready without reconciling the source's convention. The
  insurance column is computed on declining balance, while the current
  `fee_per_period` feature models a flat per-period fee; this source would
  need either a variable-fee schedule mode or a different interpretation of
  the published insurance values.

### French near misses

- Empruntis, "Tableau d'amortissement : définition, calcul et exemple"
  - URL:
    <https://www.empruntis.com/financement/simulation-pret-immobilier/simulation-tableau-amortissement/tableau-amortissement-exemple/>
  - Caveat: publishes `€200,000 / 20 ans / 3.35% / 0.36% insurance`, but
    values are whole-euro and the total monthly payment is approximate.

- Solutis, "Tableau d'amortissement de crédit : exemple, simulateur et
  guide Excel"
  - URL: <https://www.solutis.fr/tableau-amortissement.html>
  - Caveat: values are integer-euro, explicitly non-contractual, and the
    principal/rate are not clearly published in the example block.

- Service-Public / ANIL simulator, "Faire une simulation de l'échéancier
  et du TAEG d'un crédit immobilier"
  - URL: <https://www.service-public.gouv.fr/particuliers/vosdroits/R2924>
  - Persistent ID: `R2924`
  - Caveat: official calculator reference, but the static page publishes no
    fixed worked parameters or row values.

## Cross-Cutting Notes

- Japan and Korea produced promising integer-currency schedules, but the
  package currently assumes a cents-style `0.01` display quantum. Do not
  add a currency-scale/quantum option unless a verified source is selected
  and the feature is needed to reproduce it exactly.
- Netherlands and France produced useful row excerpts with one-cent or
  larger tensions that must be resolved before fixture work.
- Italy's bank transparency PDFs may be the best short path to new
  single-anchor European fixtures because they publish complete parameters
  and exact euro-cent payments under stated `Francese` conventions.
- Denmark remains the weakest search result set from this pass; no
  verified Danish source found both complete mortgage parameters and
  øre-precision amortization rows for the current annuity surface.
