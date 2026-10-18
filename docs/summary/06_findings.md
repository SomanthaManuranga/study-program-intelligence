# 6. The four findings

<!-- Plain English. Numbers only as {{key}} placeholders. One subsection per question. -->

## 6.1 Do students want it?

**What we asked.** Is the number of people who want to study this field growing or shrinking?

**What we did.** Official statistics do not count cybersecurity students separately; they count them under computer
science. So we used a **proxy**: we measured the wider field, as you might judge the demand for electric bikes from all
bicycle sales. Our proxy is the number of first-year students in computer science and two closely related subjects in
Bavaria. To look ahead, we used two ways. The careful way follows the official forecast of first-year students. The
trend way continues the growth of the past years. As a planning value we took the middle between the two.

**What we found.**

- Computer science is the only large subject of the faculty that grew: in Bavaria by
  {{informatik_firstyears_by_growth}} a year (2019-2024), with a dip in 2024. In Germany it has been level since 2023.
- Most of that growth is students from abroad. In Bavaria, foreign students made up {{informatik_by_foreign_part}} of
  the growth. German first-year students grew by only {{informatik_by_german_growth}} a year in Bavaria, and in Germany
  they changed by {{informatik_de_german_growth}}. Among German students, computer science is still the strongest
  large subject of the faculty.
- Our proxy was {{cyber_proxy_by_2024}} first-year students in Bavaria in 2024. The careful forecast gives
  {{cyber_proxy_by_2030_conservative}} for 2030, the middle value {{cyber_proxy_by_2030_central}}.
- Online, people search for "Cyber Security Studium" more often than for the AI and robotics degree terms
  ({{search_cyber_vs_ki}}, {{search_cyber_vs_robotik}}). But its search interest has hardly grown since 2022.

{{fig:f01_demand_forecast}}

**How sure are we?** Fairly sure for the field as a whole, less sure for cybersecurity itself, because we can only
measure it through the wider field. A German-taught bachelor draws mainly German students, and their numbers grow much
more slowly.

## 6.2 Would students come to OTH?

**What we asked.** How many students would start the programme at OTH each year?

**What we did.** People tend to shop at the nearest supermarket, and fewer travel far. Students behave in a similar way.
We measured how strongly distance puts students off, using real data on which region the students of each state-run
Bavarian university of applied sciences come from. With this **capture model** we can say how many students OTH would attract compared with
a competitor. But no university we checked publishes how many students start its cybersecurity programme. So we needed
**anchors**: known figures of similar programmes that turn the comparison into a number.

**A worked example.** OTH's **catchment** (the Bavarian counties closer to OTH than to the nearest universities with a
cybersecurity programme) has {{own_pool_exact}} school leavers a year who may go to university. About a third of
them finish school in Regensburg or its county, where other universities are close by. The model says OTH would attract {{rel_capture_thi}}
the students of TH Ingolstadt. TH Ingolstadt plans its programme for {{thi_cyber_capacity}} students a year. Depending
on the model settings, this gives {{low_variant_range}} students; we use {{cyber_bsc_gross_low}} as our low estimate. Compared with TH Deggendorf, OTH would attract {{rel_capture_deg}} its students. With
the {{deg_cyber_anecdote}} first-year students from a student review, this gives our high estimate of
{{cyber_bsc_gross_high}}. For the middle estimate we chose a value between the two, {{cyber_bsc_gross_central}}. This is our choice, not a model
result. That is less than one
in a hundred of OTH's own school leavers.

**What we found.**

- {{cyber_bsc_gross_low}} / {{cyber_bsc_gross_central}} / {{cyber_bsc_gross_high}} first-year students a year (low /
  middle / high) once the programme is fully running; we assume it reaches this level in its third year.
- In the first year: {{year1_low}} / {{year1_central}} / {{year1_high}}.
- We assume a programme needs at least {{min_cohort}} first-year students a year; we found no official rule.

{{fig:f04_capture}}

**How sure are we?** The comparison between the universities is stable. The weak part is the anchors: a planned
capacity and one student review. One real first-year number from TH Ingolstadt or TH Deggendorf would make the range
about half as wide.

- Students from outside Bavaria are not in the model, but they matter little. They are {{oth_outside_bavaria}} of
  OTH's German students, about as many as at the other two universities.
- No university of applied sciences publishes its numbers. Two research universities do: {{rub_cyber_ba_firstyears}}
  and {{uds_cyber_ba_firstyears}} first-year students a year. So the {{deg_cyber_anecdote}} from the student review is believable
  as a high figure. This is a check, not a new anchor.
- TH Deggendorf also runs a regional centre for IT security, so it is a strong competitor in this field.

## 6.3 Can OTH teach it?

**What we asked.** How much of a cybersecurity programme does the faculty already teach, and what is missing?

**What we did.** We compared the **module handbooks** (the official course descriptions) of seven similar programmes
with those of the faculty. A computer program read every pair of module descriptions and marked those that teach the
same thing. It is like comparing two cookbooks by their dishes, not by their exact words. We checked twenty of its
decisions by hand: it was right in {{pairs_e5}}. All four of its mistakes counted too much as already taught, so our coverage
figures are probably on the high side.

**What we found.**

- The faculty already teaches up to {{emi_cover_gen_ba}} of the basics (mathematics, programming, networks). It
  teaches only about {{emi_cover_sec_ba}} of the security content ({{cover_sec_ba_range}}, by programme compared).
- Missing are mainly the practical topics: hacking tests, digital forensics, handling security incidents, secure
  software, security management and law.
- An estimated {{new_professorships}}, a lab engineer, outside teachers for law and security management, and a
  separate security lab would close the gap. A draft course
  plan has {{draft_security_ects}} security credits (**ECTS**) out of 210 ECTS.

OTH's agreement with the state ministry names IT security as one of its research fields.

**How sure are we?** Fairly sure about the module comparison; we checked a sample of its decisions by hand. The staff figure is an estimate, and we
have not estimated the cost of the lab.

## 6.4 Are there jobs?

**What we asked.** Would graduates find relevant jobs, in Germany and in the region?

**What we did.** We counted job adverts on the job board of the Federal Employment Agency, like counting "staff wanted"
signs in shop windows. We also looked at official employment statistics and the national report on jobs with too few
applicants.

**What we found.**

- {{ads_cyber_security_de}} adverts in Germany mentioned "Cyber Security" on one day; {{ads_cyber_security_by_share}} of
  them were in Bavaria, more than the {{baseline_share}} for general IT adverts.
- {{ads_cyber_security_amberg_100km}} adverts were within 100 km of Amberg, an area that includes Nuremberg and
  Regensburg, but only {{ads_cyber_50km}} within 50 km.
- IT jobs held by university graduates in Bavaria: {{it_jobs_by_academic_growth}} from 2019 to 2023. Computer
  scientists with a bachelor's degree are officially in short supply.

**How sure are we?** Medium. A job advert is not a job for a graduate, adverts can mention several keywords, and the
shortage figure is for computer science in general, not for security alone.
