# Claim A: demand

<!-- Evidence: docs/evidence_competition_demand.md, docs/evidence_forecast.md, docs/evidence_demand_trends.md,
docs/theme_precision.md, docs/evidence_ranking.md (pipeline). -->

**Claim:** enough prospective students want to study cybersecurity, and the Bavarian pool of computer-science
first-years a cyber programme recruits from is not shrinking. Official statistics have no cybersecurity subject; cyber programmes are counted under computer science.
Demand is therefore read through three proxies: first-year students in the computer-science subjects, search
interest, and the supply of programmes.

## Computer science is the only large EMI field still growing

Between 2019 and 2025 the number of first-year students in Germany fell across all subjects, but Informatik rose
from {{informatik_firstyears_de_2019}} to {{informatik_firstyears_de_2025}} [@destatis2026students]; in Bavaria it
grew by {{informatik_firstyears_by_growth}} a year (2019-2024). Nationally the number has been flat since 2023. Of the
larger electrical and media subjects that make up the rest of EMI, most are shrinking: Elektrotechnik {{elektro_trend}},
Mechatronik {{mechatronik_trend}} and Medientechnik {{funnel_medientechnik}} a year in Germany. Only small
subjects such as microelectronics also grow ([evidence_competition_demand.md](../../docs/evidence_competition_demand.md)).
Computer science also gains share: its part of all first-year students in Germany rose from {{informatik_share_2015}}
in 2015 to {{informatik_share_2024}} in 2024 ([evidence_forecast.md](../../docs/evidence_forecast.md)).

## The growth is mostly foreign students

Split by nationality, most of this growth comes from foreign students
([evidence_demand_split.md](../../docs/evidence_demand_split.md)). In Bavaria, German first-years in Informatik grew by
{{informatik_by_german_growth}} a year (2019-2024) and foreign first-years by {{informatik_by_foreign_growth}};
foreign students account for {{informatik_by_foreign_part}} of the growth. In Germany, German first-years changed by
{{informatik_de_german_growth}} a year and foreign first-years by {{informatik_de_foreign_growth}}; foreign-nationality
students were {{informatik_de_foreign_share_2024}} of all Informatik first-years in 2024 ({{informatik_de_foreign_share_2025}}
in 2025, inflated by the Bavarian G9 gap year). For the Bavarian cyber proxy, German
first-years grew by {{cyber_proxy_by_german_growth}} a year (Germany {{cyber_proxy_de_german_growth}}), and foreign
students made up {{cyber_proxy_by_foreign_share_2024}} of the proxy in 2024 (Bavarian universities of applied
sciences, Informatik: {{haw_informatik_foreign_share}}).

("Foreign" is nationality; first-years include international master students, whose share cannot be measured at
subject level.) For a German-language bachelor that recruits mainly German school leavers, the absolute growth is
therefore much weaker than the headline figure. The relative position holds in Bavaria, where Informatik is the only
large EMI subject that grew among German first-years; in Germany it is about level with Wirtschaftsinformatik, and both
fall slightly. The forecast below continues the total trend,
which is mostly international; for the German target group the conservative path is the more relevant one. The
demand proxy itself is unchanged; the split enters the ranking as a sensitivity (Section 8).

## Forecast of the recruiting pool

We forecast the Bavarian "cyber proxy", the first-year students in Informatik, Technische Informatik and
Computer- und Kommunikationstechniken: the pool from which a cyber bachelor recruits. 2025 is the year of Bavaria's
return to the nine-year Gymnasium (G9): all Bavarian first-year students fell from {{by_all_2024}} to
{{by_all_2025}}, so the models were trained up to 2024.

In rolling-origin backtests the drift model (linear trend of the past changes) was the best model in all four series;
for the Bavarian cyber proxy its MASE is {{forecast_mase_drift_by_cyber}} against {{mase_naive_by_cyber}} for the naive
forecast. But the backtest period was a growth phase, and drift under-forecast the Bavarian surge in
{{drift_underforecast}} of the errors; recent data (Germany flat since 2023, the G9 dip) argue against extrapolating
it. We therefore show two paths and a midpoint:

| Bavaria, cyber proxy | 2024 (actual) | 2030 | 2035 |
|---|---|---|---|
| Conservative: constant subject share x KMK first-year projection [@kmk2025forecast] | {{cyber_proxy_by_2024}} | {{cyber_proxy_by_2030_conservative}} | {{cyber_proxy_by_2035_conservative}} |
| Central: midpoint between the KMK path and the drift trend (a planning value we chose) | {{cyber_proxy_by_2024}} | {{cyber_proxy_by_2030_central}} | {{cyber_proxy_by_2035_central}} |

{{fig:f01_demand_forecast}}

Even the conservative path keeps the pool above its 2024 level after the G9 dip; the KMK index for Bavaria is
{{kmk_by_2030}} in 2030 (2024 = 1). The central value is a choice, not a model output
([evidence_forecast.md](../../docs/evidence_forecast.md)).

## Search interest: cybersecurity is the largest specialist term, but on a plateau

Among the degree terms we tracked, "Cyber Security Studium" has been the largest specialist search term since 2022:
{{search_cyber_vs_ki}} and {{search_cyber_vs_robotik}} [@google2026trends]. Its rise, however, was between 2018 and
2022; since then it is high but flat ({{cyber_search_2022}} in 2022, {{cyber_search_2026}} in 2026 on the same
scale). Its share of all "Informatik Studium" searches is {{cyber_share_of_informatik_search}} in 2026, but that share
rises mainly because general searches fall. Interest in AI degrees peaked in 2024 ({{ki_search_2024}}) and fell to
{{ki_search_2026}} in 2026; robotics is flat. Search interest is a leading indicator, not a student count
([evidence_demand_trends.md](../../docs/evidence_demand_trends.md)).

{{fig:f02_search_interest}}

## Supply: a gap close to OTH

After a hand check of all title matches there are {{cyber_ba_germany}} dedicated cybersecurity bachelors and
{{cyber_ma_germany}} masters in Germany, {{cyber_ba_150km}} and {{cyber_ma_150km}} of them within 150 km of OTH, none
at OTH [@ba2026studiensuche]. {{cyber_ba_haw_share}} of the bachelors are at universities of applied sciences, so the
type fits OTH. The nearest is FAU's part-time online bachelor ({{cyber_ba_nearest_km}}); the nearest full-time
dedicated bachelors are at TH Ingolstadt (82 km) and TH Deggendorf (105 km). Competition is wider than the dedicated
count suggests: {{cyber_focus_germany}} general programmes in Germany offer cybersecurity as a focus area,
{{cyber_focus_150km}} of them within 150 km, two of them at OTH itself (Industrie-4.0-Informatik and
Medieninformatik). This overlap is tested in Section 7.

## Master pipeline

For a master the relevant demand is the number of bachelor graduates in related fields. Informatik graduates (all
degrees) rose from {{grads_de_2019}} (2019) to {{grads_de_2025}} (2025) in Germany and from {{informatik_grads_by_2019}} to
{{informatik_grads_by_2025}} in Bavaria [@destatis2026exams], so kill rule 4 (falling pipeline) does not apply.

## Assessment

Claim A holds for cybersecurity: the field it belongs to is the only large EMI field still growing (mostly through
foreign students; among German first-years it grows only in Bavaria), the Bavarian recruiting pool
is projected to stay above its 2024 level, and supply near OTH is thin. **Strength: strong for the field trend,
medium for cybersecurity itself**, because cyber demand is only visible through proxies and search interest has
plateaued since 2022. For robotics the same proxies point the other way: its feeder subjects (Mechatronik,
Technische Informatik) are flat or falling and its search interest is flat.
