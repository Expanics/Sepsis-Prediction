WITH soi_stay AS (
  SELECT
    stay_id,
    subject_id,
    MAX(suspected_infection) AS suspected_infection_stay
  FROM `physionet-data.mimiciv_3_1_derived.suspicion_of_infection`
  GROUP BY stay_id, subject_id
),

sepsis_time AS (
  SELECT
    s.stay_id,
    f.subject_id,
    MIN(s.hr) AS first_sepsis_hr
  FROM `physionet-data.mimiciv_3_1_derived.sofa` AS s
  LEFT JOIN `physionet-data.mimiciv_3_1_derived.first_day_sofa` AS f
    ON s.stay_id = f.stay_id
  LEFT JOIN soi_stay AS soi
    ON s.stay_id = soi.stay_id
  WHERE soi.suspected_infection_stay = 1
    AND (s.sofa_24hours - f.sofa) >= 2
  GROUP BY s.stay_id, f.subject_id
),

baseline_union AS (
  SELECT
    fd.subject_id,
    fd.stay_id,
    -1 AS hr,
    CAST(NULL AS DATETIME) AS starttime,
    CAST(NULL AS DATETIME) AS endtime,
    NULL AS age,
    NULL AS height,
    NULL AS weight,
    CAST(NULL AS STRING) AS gender,

    -- Vitals (first_day_vitalsign)
    fv.heart_rate_min,
    fv.heart_rate_max,
    fv.sbp_min,
    fv.sbp_max,
    fv.dbp_min,
    fv.dbp_max,
    fv.mbp_min,
    fv.mbp_max,
    fv.resp_rate_min,
    fv.resp_rate_max,
    fv.temperature_min,
    fv.temperature_max,
    fv.spo2_min,
    fv.spo2_max,
    fv.glucose_min,
    fv.glucose_max,

    -- Blood (from first_day_bg)
    lab.wbc_min AS wbc_min,
    lab.wbc_max AS wbc_max,
    lab.platelets_min AS platelet_min,
    lab.platelets_max AS platelet_max,
    lab.hemoglobin_min AS hemoglobin_min,
    lab.hemoglobin_max AS hemoglobin_max,
    NULL AS neutrophils_min,
    NULL AS neutrophils_max,
    lab.bands_min AS bands_min,
    lab.bands_max AS bands_max,
    lab.imm_granulocytes_min AS imm_granulocytes_min,
    lab.imm_granulocytes_max AS imm_granulocytes_max,
    NULL AS lymphocytes_abs_min,
    NULL AS lymphocytes_abs_max,
    lab.fibrinogen_min AS fibrinogen_min,
    lab.fibrinogen_max AS fibrinogen_max,
    lab.inr_min AS inr_min,
    lab.inr_max AS inr_max,
    lab.pt_min AS pt_min,
    lab.pt_max AS pt_max,

    NULL AS antibiotic_count,

    -- Respiratory
    fd.so2_min AS so2_min,
    fd.so2_max AS so2_max,
    fd.po2_min AS po2_min,
    fd.po2_max AS so2_max,
    fd.pco2_min AS pco2_min,
    fd.pco2_max AS pco2_max,
    NULL AS fio2_min,
    NULL AS fio2_max,
    NULL AS pfratio_min,
    NULL AS pfratio_max,
    NULL AS Ventilation_flag,

    -- Acid Base
    fd.ph_min AS ph_min,
    fd.ph_max AS ph_max,
    fd.baseexcess_min AS baseexcess_min,
    fd.baseexcess_max AS baseexcess_max,
    fd.bicarbonate_min AS bicarbonate_min,
    fd.bicarbonate_max AS bicarbonate_max,
    fd.totalco2_min AS totalco2_min,
    fd.totalco2_max AS totalco2_max,
    fd.lactate_min AS lactate_min,
    fd.lactate_max AS lactate_max,

    -- Electrolyte
    fd.sodium_min AS sodium_min,
    fd.sodium_max AS sodium_max,
    fd.potassium_min AS potassium_min,
    fd.potassium_max AS potassium_max,
    fd.chloride_min AS chloride_min,
    fd.chloride_max AS chloride_max,
    fd.calcium_min AS calcium_min,
    fd.calcium_max AS calcium_max,
    fd.glucose_min AS glucose_min,
    fd.glucose_max AS glucose_max,

    -- Lab (from first_day_lab)
    NULL AS albumin_min,
    NULL AS albumin_max,

    NULL AS aniongap_min,
    NULL AS aniongap_max,

    NULL AS bun_min,
    NULL AS bun_max,

    NULL AS creatinine_min,
    NULL AS creatinine_max,

    NULL AS total_protein_min,
    NULL AS total_protein_max,

    NULL AS globulin_min,
    NULL AS globulin_max,

    lab.alt_min AS alt_min,
    lab.alt_max AS alt_max,
    lab.ast_min AS ast_min,
    lab.ast_max AS ast_max,
    lab.alp_min AS alp_min,
    lab.alp_max AS alp_max,
    lab.ggt_min AS ggt_min,
    lab.ggt_max AS ggt_max,
    lab.bilirubin_total_min AS bilirubin_total_min,
    lab.bilirubin_total_max AS bilirubin_total_max,
    lab.bilirubin_direct_min AS bilirubin_direct_min,
    lab.bilirubin_direct_max AS bilirubin_direct_max,
    lab.bilirubin_indirect_min AS bilirubin_indirect_min,
    lab.bilirubin_indirect_max AS bilirubin_indirect_max,

    -- GCS (first_day_gcs)
    gcs.gcs_min AS gcs_min,
    NULL AS gcs_max,
    gcs.gcs_motor AS gcs_motor_min,
    gcs.gcs_motor AS gcs_motor_max,
    gcs.gcs_verbal AS gcs_verbal_min,
    gcs.gcs_verbal AS gcs_verbal_max,
    gcs.gcs_eyes AS gcs_eyes_min,
    gcs.gcs_eyes AS gcs_eyes_max,
    
    -- Addition
    NULL AS crp_min,
    NULL AS crp_max,
    NULL AS urineoutput_min,
    NULL AS urineoutput_max,
    NULL AS troponin_t_min,
    NULL AS troponin_t_max,
    lab.ck_mb_min AS ck_mb_min,
    lab.ck_mb_max AS ck_mb_max,
    NULL AS ntprobnp_min,
    NULL AS ntprobnp_max,

    -- defaults
    0 AS vaso_dopamine_max,
    0 AS vaso_epinephrine_max,
    0 AS vaso_norepinephrine_max,
    0 AS vaso_phenylephrine_max,
    0 AS vaso_vasopressin_max,
    0 AS sepsis,

  FROM `physionet-data.mimiciv_3_1_derived.first_day_bg` fd
  LEFT JOIN `physionet-data.mimiciv_3_1_derived.first_day_lab` lab
    ON fd.stay_id = lab.stay_id
  LEFT JOIN `physionet-data.mimiciv_3_1_derived.first_day_gcs` gcs
    ON fd.stay_id = gcs.stay_id
  LEFT JOIN `physionet-data.mimiciv_3_1_derived.first_day_vitalsign` fv
    ON fd.stay_id = fv.stay_id
  LEFT JOIN `physionet-data.mimiciv_3_1_derived.age` a
    ON a.subject_id = fd.subject_id
)


SELECT
  f.subject_id,
  s.stay_id,
  s.hr,
  s.starttime,
  s.endtime,
  MAX(a.anchor_age) + EXTRACT(YEAR FROM s.starttime) - MAX(a.anchor_year)  AS age,
  MAX(height.height) AS height,
  MAX(weight.weight) AS weight,
  ANY_VALUE(de.gender) AS gender,

  -- MIN / MAX per hour window
  MIN(v.heart_rate) AS heart_rate_min,
  MAX(v.heart_rate) AS heart_rate_max,

	MIN(COALESCE(v.sbp, v.sbp_ni)) AS sbp_min,
	MAX(COALESCE(v.sbp, v.sbp_ni)) AS sbp_max,
 
	MIN(COALESCE(v.dbp, v.dbp_ni)) AS dbp_min,
	MAX(COALESCE(v.dbp, v.dbp_ni)) AS dbp_max,
 
	MIN(COALESCE(v.mbp, v.mbp_ni)) AS mbp_min,
	MAX(COALESCE(v.mbp, v.mbp_ni)) AS mbp_max,

  MIN(v.resp_rate) AS resp_rate_min,
  MAX(v.resp_rate) AS resp_rate_max,

  MIN(v.temperature) AS temperature_min,
  MAX(v.temperature) AS temperature_max,

  MIN(v.spo2) AS spo2_min,
  MAX(v.spo2) AS spo2_max,

  MIN(v.glucose) AS glucose_min,
  MAX(v.glucose) AS glucose_max,

  -- LAB MIN / MAX per hour window

  -- 0. BLOOD
  MIN(cbc.wbc) AS wbc_min,
  MAX(cbc.wbc) AS wbc_max,

  MIN(cbc.platelet) AS platelet_min,
  MAX(cbc.platelet) AS platelet_max,

  MIN(cbc.hemoglobin) AS hemoglobin_min,
  MAX(cbc.hemoglobin) AS hemoglobin_max,

  MIN(bd.neutrophils_abs)        AS neutrophils_abs_min,
  MAX(bd.neutrophils_abs)        AS neutrophils_abs_max,

  MIN(bd.bands)                  AS bands_min,
  MAX(bd.bands)                  AS bands_max,

  MIN(bd.immature_granulocytes) AS immature_granulocytes_min,
  MAX(bd.immature_granulocytes) AS immature_granulocytes_max,

  MIN(bd.lymphocytes_abs)        AS lymphocytes_abs_min,
  MAX(bd.lymphocytes_abs)        AS lymphocytes_abs_max,

  MIN(coag.fibrinogen) AS fibrinogen_min,
  MAX(coag.fibrinogen) AS fibrinogen_max,

  MIN(coag.inr) AS inr_min,
  MAX(coag.inr) AS inr_max,

  MIN(coag.pt) AS pt_min,
  MAX(coag.pt) AS pt_max,

  COUNT(ab.starttime) AS antibiotic_count,

  -- 1. RESPIRATORY
  MIN(bg.so2)  AS so2_min,
  MAX(bg.so2)  AS so2_max,

  MIN(bg.po2)  AS po2_min,
  MAX(bg.po2)  AS po2_max,

  MIN(bg.pco2) AS pco2_min,
  MAX(bg.pco2) AS pco2_max,

  MIN(bg.fio2) AS fio2_min,
  MAX(bg.fio2) AS fio2_max,

  MIN(bg.pao2fio2ratio) AS pfratio_min,
  MAX(bg.pao2fio2ratio) AS pfratio_max,

  CASE 
    WHEN ANY_VALUE(vf.ventilation_status) IS NOT NULL THEN 1
    ELSE 0
END AS ventilation_flag,

  -- 2. ACID–BASE
  MIN(bg.ph) AS ph_min,
  MAX(bg.ph) AS ph_max,

  MIN(bg.baseexcess) AS baseexcess_min,
  MAX(bg.baseexcess) AS baseexcess_max,

  MIN(bg.bicarbonate) AS bicarbonate_min,
  MAX(bg.bicarbonate) AS bicarbonate_max,

  MIN(bg.totalco2) AS totalco2_min,
  MAX(bg.totalco2) AS totalco2_max,

  MIN(bg.lactate) AS lactate_min,
  MAX(bg.lactate) AS lactate_max,

  -- 3. ELECTROLYTE
  MIN(bg.sodium) AS sodium_min,
  MAX(bg.sodium) AS sodium_max,

  MIN(bg.potassium) AS potassium_min,
  MAX(bg.potassium) AS potassium_max,

  MIN(bg.chloride) AS chloride_min,
  MAX(bg.chloride) AS chloride_max,

  MIN(bg.calcium) AS calcium_min,
  MAX(bg.calcium) AS calcium_max,

  MIN(bg.glucose) AS glucose_min,
  MAX(bg.glucose) AS glucose_max,

  -- 4. CHEMISTRY
  MIN(chem.albumin) AS albumin_min,
  MAX(chem.albumin) AS albumin_max,

  MIN(chem.aniongap) AS aniongap_min,
  MAX(chem.aniongap) AS aniongap_max,

  MIN(chem.bun) AS bun_min,
  MAX(chem.bun) AS bun_max,

  MIN(chem.creatinine) AS creatinine_min,
  MAX(chem.creatinine) AS creatinine_max,

  MIN(chem.total_protein) AS total_protein_min,
  MAX(chem.total_protein) AS total_protein_max,

  MIN(chem.globulin) AS globulin_min,
  MAX(chem.globulin) AS globulin_max,

  MIN(l.alt) AS alt_min,
  MAX(l.alt) AS alt_max,
    
  MIN(l.ast) AS ast_min,
  MAX(l.ast) AS ast_max,
  
  MIN(l.alp) AS alp_min,
  MAX(l.alp) AS alp_max,
  
  MIN(l.ggt) AS ggt_min,
  MAX(l.ggt) AS ggt_max,
  
  MIN(l.bilirubin_total) AS bilirubin_total_min,
  MAX(l.bilirubin_total) AS bilirubin_total_max,
  
  MIN(l.bilirubin_direct) AS bilirubin_direct_min,
  MAX(l.bilirubin_direct) AS bilirubin_direct_max,
  
  MIN(l.bilirubin_indirect) AS bilirubin_indirect_min,
  MAX(l.bilirubin_indirect) AS bilirubin_indirect_max,

  -- 5. CONSCIOUS
  MIN(g.gcs) AS gcs_min,
  MAX(g.gcs) AS gcs_max,
  
  MIN(g.gcs_motor) AS gcs_motor_min,
  MAX(g.gcs_motor) AS gcs_motor_max,
  
  MIN(g.gcs_verbal) AS gcs_verbal_min,
  MAX(g.gcs_verbal) AS gcs_verbal_max,
  
  MIN(g.gcs_eyes) AS gcs_eyes_min,
  MAX(g.gcs_eyes) AS gcs_eyes_max,

  -- INFLAMMATION
  MIN(crp.crp) AS crp_min,
  MAX(crp.crp) AS crp_max,

  -- URINE
  MIN(u.urineoutput) AS urineoutput_min,
  MAX(u.urineoutput) AS urineoutput_max,

  -- CARDIAC
  MIN(cm.troponin_t) AS troponin_t_min,
  MAX(cm.troponin_t) AS troponin_t_max,

  MIN(cm.ck_mb) AS ck_mb_min,
  MAX(cm.ck_mb) AS ck_mb_max,

  MIN(cm.ntprobnp) AS ntprobnp_min,
  MAX(cm.ntprobnp) AS ntprobnp_max,

  -- VASOPRESSOR
  MAX(COALESCE(vaso.dopamine, 0))        AS vaso_dopamine_max,
  MAX(COALESCE(vaso.epinephrine, 0))     AS vaso_epinephrine_max,
  MAX(COALESCE(vaso.norepinephrine, 0))  AS vaso_norepinephrine_max,
  MAX(COALESCE(vaso.phenylephrine, 0))   AS vaso_phenylephrine_max,
  MAX(COALESCE(vaso.vasopressin, 0))     AS vaso_vasopressin_max,

  CASE
    WHEN s.hr >= st.first_sepsis_hr THEN 1
    ELSE 0
  END AS sepsis

FROM `physionet-data.mimiciv_3_1_derived.sofa` s

LEFT JOIN `physionet-data.mimiciv_3_1_derived.first_day_sofa` f
  ON s.stay_id = f.stay_id

LEFT JOIN sepsis_time st
  ON s.stay_id = st.stay_id

LEFT JOIN `physionet-data.mimiciv_3_1_derived.age` a 
  ON a.subject_id = f.subject_id

LEFT JOIN `physionet-data.mimiciv_3_1_derived.vitalsign` v
  ON s.stay_id = v.stay_id
 AND v.charttime >= s.starttime
 AND v.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.complete_blood_count` cbc
  ON f.subject_id = cbc.subject_id AND cbc.hadm_id = f.hadm_id
 AND cbc.charttime >= s.starttime
 AND cbc.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.antibiotic` ab
  ON ab.stay_id = s.stay_id AND ab.starttime BETWEEN s.starttime AND s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.bg` bg
  ON bg.hadm_id = f.hadm_id
 AND bg.charttime >= s.starttime
 AND bg.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.blood_differential` bd
  ON bd.hadm_id = f.hadm_id
 AND bd.subject_id = f.subject_id
 AND bd.charttime >= s.starttime
 AND bd.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.chemistry` chem
  ON chem.hadm_id = f.hadm_id
 AND chem.charttime >= s.starttime
 AND chem.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.coagulation` coag
  ON coag.hadm_id = f.hadm_id
 AND coag.charttime >= s.starttime
 AND coag.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.enzyme` l
  ON l.hadm_id = f.hadm_id
 AND l.charttime >= s.starttime
 AND l.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.gcs` g
  ON g.stay_id = f.stay_id
 AND g.charttime >= s.starttime
 AND g.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.height` height
  ON height.stay_id = f.stay_id
 AND height.charttime >= s.starttime
 AND height.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.weight_durations` weight
  ON weight.stay_id = f.stay_id
 AND weight.starttime >= s.starttime
 AND weight.starttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.inflammation` crp
  ON crp.hadm_id = f.hadm_id
 AND crp.charttime >= s.starttime
 AND crp.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.urine_output` u
  ON u.stay_id = f.stay_id
 AND u.charttime >= s.starttime
 AND u.charttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.ventilation` vf
  ON vf.stay_id = f.stay_id
 AND vf.starttime >= s.starttime
 AND vf.starttime <  s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.icustay_detail` de
  ON de.stay_id = f.stay_id

LEFT JOIN `physionet-data.mimiciv_3_1_derived.cardiac_marker` cm
  ON cm.subject_id = f.subject_id AND cm.hadm_id = f.hadm_id
  AND cm.charttime >= s.starttime
  AND cm.charttime < s.endtime

LEFT JOIN `physionet-data.mimiciv_3_1_derived.vasoactive_agent` vaso
  ON vaso.stay_id = f.stay_id
  AND vaso.starttime >= s.starttime
  AND vaso.starttime < s.endtime

GROUP BY
  f.subject_id,
  s.stay_id,
  s.hr,
  s.starttime,
  s.endtime,
  st.first_sepsis_hr

UNION ALL
SELECT * FROM baseline_union

ORDER BY stay_id, hr
