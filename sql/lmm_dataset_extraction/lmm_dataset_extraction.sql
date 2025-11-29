-- only select variables of interest for interaction LMM model
SELECT 
    m.record_id, 
    m.cdrisc_72, 
    m.cdrisc_4w, 
    m.sex, 
    m.calc_age, 
    m.randomization,
    p.*  -- include all columns from PartnerReport
FROM MBI4mTBIoutput AS m
-- join PartnerReport data based on record_id
LEFT JOIN PartnerReport AS p
    ON p.sid = m.record_id
-- only include those that completed BOTH MRIs
WHERE m.mri_comp = 1 
  AND m.mri_comp_2 = 1
-- only include those that adhered to the protocol (spent 9600 in app activities)
  AND m.session_duration_sum > 9600 
-- only include those with existing values for relevant variables (cdrisc)
  AND m.cdrisc_72 IS NOT NULL 
  AND m.cdrisc_4w IS NOT NULL
-- sort by randomization, specifically grouping MBIs first then Shams
ORDER BY m.randomization ASC;
