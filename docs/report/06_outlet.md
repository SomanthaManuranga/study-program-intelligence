# Claim D: graduate outlet

<!-- Evidence: docs/evidence_outlet_jobs.md. -->

**Claim:** graduates of a cybersecurity bachelor find relevant jobs, in Germany and in the region.

## Job ads

We counted job offers on the job board of the Federal Employment Agency by keyword and region [@ba2026jobsuche]
(snapshot {{job_snapshot_date}}; [evidence_outlet_jobs.md](../../docs/evidence_outlet_jobs.md)):

| Keyword | Germany | Bavaria's share | Within 100 km of Amberg |
|---|---|---|---|
| Cyber Security | {{ads_cyber_security_de}} | {{ads_cyber_security_by_share}} | {{ads_cyber_security_amberg_100km}} |
| OT Security | {{ads_ot_security_de}} | {{ads_ot_security_by_share}} | {{ads_ot_security_amberg_100km}} |
| Robotik (comparison) | {{ads_robotik_de}} | {{ads_robotik_by_share}} | {{ads_robotik_amberg_100km}} |

- **Security is a large job market, not a niche.** "Security Engineer" matches {{ads_security_engineer}} ads and
  "Cyber Security" {{ads_cyber_security_de}}, about as many as "Künstliche Intelligenz" ({{ads_ki}}); the German term
  "IT-Sicherheit" matches {{ads_it_sicherheit}}, partly because security is named as a requirement in other IT jobs.
- **Bavaria is over-represented in security**, and most in industrial security: its share is
  {{ads_cyber_security_by_share}} for "Cyber Security" and {{ads_ot_security_by_share}} for "OT Security", against
  {{baseline_share}} for general IT keywords.
- **The jobs are in the wider region.** Within 50 km of Amberg there are only {{ads_cyber_50km}} "Cyber Security" ads,
  but {{ads_cyber_security_amberg_100km}} within 100 km, where Nuremberg and Regensburg fall inside. That is normal for
  a university in a small town.

{{fig:f03_job_ads}}

A second snapshot two days later changed little (median change {{snapshot_change}}), so the counts are stable to
measure; further snapshots follow until the analysis freeze on 4 December.

## Employment and shortage

IT employment in Bavaria grew {{it_jobs_by_growth}} between 2019 and 2023, and IT employment of graduates
{{it_jobs_by_academic_growth}}; the academic share reached {{academic_share_2023}} [@lfstat2024employment]. The
Federal Employment Agency lists computer-science occupations at bachelor (specialist) level as a shortage occupation
in 2025 (score {{shortage_score}}); at master (expert) level software development is no longer a shortage occupation
[@ba2025engpass]. The outlet argument is therefore strongest for a bachelor; for a master it has to rest on the
security specialisation and on job ads rather than on the shortage list.

For robotics the job-ad signal is strong and the most local of all keywords ({{ads_robotik_de}} ads in Germany,
{{ads_robotik_amberg_50km}} within 50 km of Amberg), but the shortage analysis does not name mechatronics or
automation occupations among its published top lists, so their shortage status is unknown.

## Assessment

Claim D holds for a cyber bachelor: security is a large and Bavarian-heavy job market, and computer science is a
shortage occupation at bachelor level. **Strength: medium.** Keyword counts are indicators, not vacancies by
occupation; an ad can match several keywords; the job board does not contain every ad in Germany; and no county-level
occupation data were available.
