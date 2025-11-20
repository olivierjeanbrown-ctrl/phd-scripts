# adherence_report_refactor.py
# Refactored version of Olivier Brown's Adherence Report Script 2.0
# Preserves original output and variable names, but is more robust & readable.

import os
import pandas as pd
import datetime
from datetime import timedelta

# -------------------------
# Configuration (edit if needed)
# -------------------------
directory = r'C:\Users\Olivier\OneDrive - University of Ottawa\Desktop\GitHub\phd-scripts\python\adherence_report'
raw_dir = os.path.join(directory, "raw")
output_file = os.path.join(directory, "output", "adherence_report.csv")
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# input filenames (as in original)
mbi_file = os.path.join(raw_dir, "MBIProjectPhase2.csv")
outcome_file = os.path.join(raw_dir, "Outcome_complete.csv")
partner_file = os.path.join(raw_dir, "PartnerReport.csv")

# constants (matching original)
DURATION_CAP = 3600
modules1and2_sum = 5439
modules1to4_sum = 10688
seventypercent_mod1and2 = modules1and2_sum * 0.7
seventypercent_mod1to4 = modules1to4_sum * 0.7
mod1 = 2145
mod2 = 3294
mod3 = 2522
mod4 = 2727
avg_weekly = 2672 * 0.7        # same as original
avg_weekly_con = 2400 * 0.7
control_len = 9600
seventypercent_controllen = control_len * 0.7

# -------------------------
# Helper utilities
# -------------------------
def safe_read_csv(path, encoding="utf-8"):
    """Read CSV robustly as strings (keeps header row intact)."""
    return pd.read_csv(path, dtype=str, encoding=encoding, keep_default_na=False)

def parse_ymd_datestring(s):
    """Try to coerce input date string to datetime.date using formats like YYYY/MM/DD or YYYY-MM-DD.
       Returns datetime.date or None."""
    if s is None:
        return None
    s = str(s).strip()
    if s == "":
        return None
    # replace '-' with '/' to mimic original script's replacement
    s2 = s.replace("-", "/")
    # try parsing "%Y/%m/%d"
    try:
        return datetime.datetime.strptime(s2, "%Y/%m/%d").date()
    except Exception:
        # try a few fallbacks
        for fmt in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d/%H/%M/%S", "%Y/%m/%dT%H:%M:%S%z"):
            try:
                return datetime.datetime.strptime(s2, fmt).date()
            except Exception:
                continue
    return None

def snapshot_to_standard(s):
    """Apply transformations similar to clean_snapshot in original script:
       remove timezone suffixes (+00:00, -04:00, -06:00), replace 'T' with '/', '-' and ':' with '/'.
       Returns transformed string or 'null' if missing/invalid."""
    try:
        if not s or pd.isna(s):
            return "null"
        s = str(s)
        # strip timezone segments as original did
        for tz in ["+00:00", "-04:00", "-06:00"]:
            if s.endswith(tz):
                # original strips the timezone digits then +/- char; emulate by removing tz
                s = s[:-len(tz)]
                # also strip possible trailing + or - left
                s = s.rstrip("+-")
        # replace characters
        s = s.replace("T", "/").replace("-", "/").replace(":", "/")
        if s.strip() == "":
            return "null"
        return s
    except Exception:
        return "null"

def parse_snapshot_datetime(s):
    """Expect strings like 'YYYY/MM/DD/H/M/S' and return a datetime, else return a fallback sentinel."""
    try:
        if s in (None, "", "null"):
            # return sentinel datetime far in past (original used '1111/11/11/11/11/11')
            return datetime.datetime.strptime("1111/11/11/11/11/11", "%Y/%m/%d/%H/%M/%S")
        return datetime.datetime.strptime(s, "%Y/%m/%d/%H/%M/%S")
    except Exception:
        # fallback sentinel
        return datetime.datetime.strptime("1111/11/11/11/11/11", "%Y/%m/%d/%H/%M/%S")

# -------------------------
# Load files
# -------------------------
# The original used csv.reader -> list -> DataFrame where row 0 contains column names.
# Here we read normally with pandas; keep empty strings instead of NaN for fidelity.
mbi = safe_read_csv(mbi_file, encoding='utf-8-sig')       # REDCap export (rows per event)
outcome = safe_read_csv(outcome_file)                    # single-column list of ids
partner = safe_read_csv(partner_file, encoding='utf-8')  # PartnerReport

# ensure columns exist (avoid KeyError later)
mbi.columns = mbi.columns.astype(str)
partner.columns = partner.columns.astype(str)

# Extract sid list from outcome file (first column)
sid = outcome.iloc[:, 0].astype(str).tolist()

# -------------------------
# Provide MBI helper functions that mirror original gatherdata behaviour
# -------------------------
def gathersid(arg):
    """Return MPP2_data list (for ids in outcome list) and the column index of arg in mbi."""
    # find column index where header equals arg (original used MPP2_df.loc[0,i] == arg)
    if arg not in mbi.columns:
        raise KeyError(f"{arg} not found in MBIProjectPhase2 columns")
    arg_ind = mbi.columns.get_loc(arg)
    MPP2_data = []
    # For each row in mbi, if record_id in sid_list then append the value at arg_ind
    for _, row in mbi.iterrows():
        rec = str(row.get('record_id', ''))
        # check membership in sid list (original used substring 'in')
        for s in sid:
            if rec == str(s):
                MPP2_data.append(row.iloc[arg_ind])
                break
    return MPP2_data, arg_ind

def gatherevent(arg):
    """Return column index of redcap_event_name variable (mirrors original function)."""
    if arg not in mbi.columns:
        raise KeyError(f"{arg} not found in MBIProjectPhase2 columns")
    return mbi.columns.get_loc(arg)

def gatherdata(var_name, redcap_event_name):
    """Return list of variable values for each sid, matching record_id & redcap_event_name."""
    # find var column index if exists
    if var_name in mbi.columns:
        var_ind = mbi.columns.get_loc(var_name)
    else:
        var_ind = None

    # if var doesn't exist, return list of None
    if var_ind is None:
        return [None] * len(sid)

    results = []
    # For each id in sid, find row where record_id==sid and redcap_event_name==redcap_event_name
    for s in sid:
        found = None
        for _, row in mbi.iterrows():
            if str(row.get('record_id', '')) == str(s) and str(row.get('redcap_event_name', '')) == redcap_event_name:
                found = row.iloc[var_ind]
                break
        # append found or None
        results.append(found if found != "" else None)
    return results

# -------------------------
# Run prerequisites (mirror original flow)
# -------------------------
# gather sids and record_id index (original usage)
# Note: original gathersid appended values for rows with record_id in sid_list; for compatibility, we call but mainly need the index.
try:
    MPP2_sid, record_id_ind = gathersid('record_id')
except KeyError:
    # fallback: find 'record_id' case-insensitively
    rec_cols = [c for c in mbi.columns if c.lower() == 'record_id']
    if rec_cols:
        mbi = mbi.rename(columns={rec_cols[0]: 'record_id'})
        MPP2_sid, record_id_ind = gathersid('record_id')
    else:
        raise

# gather index for redcap_event_name column
try:
    redcap_event_name_ind = gatherevent('redcap_event_name')
except KeyError:
    # fallback: attempt to find close match
    rec_cols = [c for c in mbi.columns if c.lower() == 'redcap_event_name']
    if rec_cols:
        mbi = mbi.rename(columns={rec_cols[0]: 'redcap_event_name'})
        redcap_event_name_ind = gatherevent('redcap_event_name')
    else:
        raise

# -------------------------
# Variables of interest (mirror original calls)
# -------------------------
randomization = gatherdata('randomization', 'day_1_arm_1')       # randomization at day_1
mri_comp_2 = gatherdata('mri_comp_2', 'day_1_arm_1')            # MRI2 at day_1 (original variable name)
week4_comp = gatherdata('week_4_8_questionnaires_complete', 'week_4_arm_1')
debfried_comp = gatherdata('week_4_debriefing_complete', 'week_4_arm_1')  # preserved original typo name

# -------------------------
# Find indices in partner (adhere_df) matching original loop
# -------------------------
# original script assumes header row at row 0 and uses .loc[0,i] to find column names; here we get indices mapping by name
col_index = {name: idx for idx, name in enumerate(partner.columns)}
# define expected columns and set index variables if present (mirror original variable names)
sid_index = col_index.get('sid', None)
session_stage_index = col_index.get('session_stage', None)
session_num_index = col_index.get('session_number', None)
session_start_index = col_index.get('session_start_date', None)
session_duration_index = col_index.get('session_duration', None)
session_length_index = col_index.get('session_length', None)
snapshot_start_pre_index = col_index.get('snapshot_start_pre', None)
snapshot_finish_pre_index = col_index.get('snapshot_finish_pre', None)
snapshot_start_post_index = col_index.get('snapshot_start_post', None)
snapshot_finish_post_index = col_index.get('snapshot_finish_post', None)
group_index = col_index.get('group', None)
heartrate_pre_index = col_index.get('heartrate_pre', None)
sessiontype_index = col_index.get('session_type', None)
breathrate_pre_index = col_index.get('breathrate_pre', None)
o2level_pre_indexx = col_index.get('o2level_pre', None)
hrv_low_freq_sum_pre_index = col_index.get('hrv_low_freq_sum_pre', None)
hrv_high_freq_sum_pre_index = col_index.get('hrv_high_freq_sum_pre', None)
heartrate_post_index = col_index.get('heartrate_post', None)
breathrate_post_index = col_index.get('breathrate_post', None)
o2level_post_index = col_index.get('o2level_post', None)
hrv_low_freq_sum_post_index = col_index.get('hrv_low_freq_sum_post', None)
hrv_high_freq_sum_post_index = col_index.get('hrv_high_freq_sum_post', None)

# -------------------------
# Normalize session_start_date format and compute earliest session start per participant
# -------------------------
# Replace '-' with '/' and coerce blanks to '9999/01/01' as original did (we keep same sentinel)
partner = partner.fillna("")
# ensure session_start_date column exists
if session_start_index is None:
    raise KeyError("session_start_date column not found in PartnerReport.csv")

# Normalize dates (string) and build earliest date per sid
# We'll store parsed datetime.date objects (or sentinel) in dicts for efficient lookups
earliest_start = {}
# iterate partner rows (original used index base 0 and started at row 1; here header is column names)
for _, row in partner.iterrows():
    sid_val = str(row['sid'])
    start_raw = str(row['session_start_date'])
    start_norm = start_raw.replace("-", "/") if start_raw != "" else ""
    if start_norm == "" or start_norm.strip() == "":
        # original set to sentinel '9999/01/01'
        parsed = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date()
    else:
        try:
            parsed = datetime.datetime.strptime(start_norm, "%Y/%m/%d").date()
        except Exception:
            # fallback - try more flexible parsing
            try:
                parsed = pd.to_datetime(start_norm, errors='coerce').date()
                if pd.isna(parsed):
                    parsed = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date()
            except Exception:
                parsed = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date()
    # update earliest per sid
    if sid_val not in earliest_start or parsed < earliest_start[sid_val]:
        earliest_start[sid_val] = parsed

# For any sid in outcome list not present in partner, set sentinel earliest start
for s in sid:
    if s not in earliest_start:
        earliest_start[s] = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date()

# Build week cutoffs per sid (week1 = +7d, week2 +14d, week3 +21d, week4 +56d as original)
session_start_data = []   # list of datetime.date
week_1_dates = []
week_2_dates = []
week_3_dates = []
week_4_dates = []
for s in sid:
    start = earliest_start.get(s, datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date())
    session_start_data.append(start)
    week_1_dates.append(start + timedelta(days=7))
    week_2_dates.append(start + timedelta(days=14))
    week_3_dates.append(start + timedelta(days=21))
    week_4_dates.append(start + timedelta(days=56))

# -------------------------
# Ensure numeric session_duration and heartrate_pre as original did (fill missing with 0)
# -------------------------
# For compatibility with original, iterate rows and coerce ints; where invalid set to '0'
def safe_int_column(df, col):
    if col is None:
        return
    for idx in df.index:
        try:
            # original attempted int conversion and set to 0 on exception
            val = df.at[idx, df.columns[col]]
            int(str(val))
        except Exception:
            df.at[idx, df.columns[col]] = "0"

safe_int_column(partner, session_duration_index)
safe_int_column(partner, heartrate_pre_index)

# -------------------------
# Compute total session_duration within 4-weeks per sid (cap at 3600s)
# -------------------------
session_duration_data = []
for i_s, s in enumerate(sid):
    total = 0
    for _, row in partner.iterrows():
        if str(row['sid']) == s:
            # parse session_start_date to date (original used "%Y/%m/%d")
            start_raw = str(row['session_start_date']).replace("-", "/")
            try:
                start_date = datetime.datetime.strptime(start_raw, "%Y/%m/%d").date()
            except Exception:
                # skip rows that can't be parsed; original replaced with sentinel earlier so keep that behavior
                try:
                    start_date = pd.to_datetime(start_raw, errors='coerce').date()
                except Exception:
                    start_date = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date()
            # include only if before week_4_dates[i_s]
            if start_date < week_4_dates[i_s]:
                # session_duration column contains strings potentially; coerce to int and cap
                try:
                    session_duration = int(float(row['session_duration']))
                except Exception:
                    session_duration = 0
                if session_duration > DURATION_CAP:
                    session_duration = DURATION_CAP
                total += session_duration
    session_duration_data.append(total)

# -------------------------
# Snapshot cleaning (mirror original clean_snapshot)
# -------------------------
# Apply snapshot_to_standard to each snapshot column
for colname in ['snapshot_start_pre','snapshot_finish_pre','snapshot_start_post','snapshot_finish_post']:
    if colname in partner.columns:
        partner[colname] = partner[colname].apply(snapshot_to_standard)
    else:
        # create column of 'null' if missing
        partner[colname] = ["null"] * len(partner)

# -------------------------
# compute_delta_snap function (mirrors original)
# -------------------------
def compute_delta_snap(partner_df, sid_list, sid_col_name, session_start_col_name,
                       week_4_dates_list, snapshot_start_col, snapshot_finish_col, start_point_list):
    delta_snap_data = []
    for idx_s, s in enumerate(sid_list):
        delta_snap_lst = []
        for _, row in partner_df.iterrows():
            # guard: if snapshot entries equal 'null' set sentinel strings (original did that in-loop)
            start_snap = row[snapshot_start_col]
            finish_snap = row[snapshot_finish_col]
            if start_snap == 'null':
                start_snap = '1111/11/11/11/11/11'
                finish_snap = '1111/11/11/11/11/11'
            if finish_snap == 'null':
                start_snap = '1111/11/11/11/11/11'
                finish_snap = '1111/11/11/11/11/11'
            # session start date parsing
            session_start_raw = str(row[session_start_col_name]).replace("-", "/")
            try:
                a = datetime.datetime.strptime(session_start_raw, "%Y/%m/%d")
            except Exception:
                try:
                    a = pd.to_datetime(session_start_raw, errors='coerce')
                    if pd.isna(a):
                        a = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d")
                except Exception:
                    a = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d")
            # include if sid matches and within window (>= start_point and < week_4)
            if str(row[sid_col_name]) == str(s) and a.date() < week_4_dates_list[idx_s] and a.date() >= start_point_list[idx_s]:
                # parse snapshot datetimes formatted like 'YYYY/MM/DD/H/M/S'
                dt_finish = parse_snapshot_datetime(finish_snap)
                dt_start = parse_snapshot_datetime(start_snap)
                # delta in seconds (original used .seconds attribute)
                try:
                    delta_snap = (dt_finish - dt_start).seconds
                except Exception:
                    delta_snap = 0
                delta_snap_lst.append(int(delta_snap))
        delta_snap_data.append(sum(delta_snap_lst))
    return delta_snap_data

delta_snap_pre_data = compute_delta_snap(partner, sid, 'sid', 'session_start_date', week_4_dates, 'snapshot_start_pre', 'snapshot_finish_pre', session_start_data)
delta_snap_post_data = compute_delta_snap(partner, sid, 'sid', 'session_start_date', week_4_dates, 'snapshot_start_post', 'snapshot_finish_post', session_start_data)

# -------------------------
# session_duration + snapshots included
# -------------------------
session_duration_snapsincluded = []
for i in range(len(session_duration_data)):
    total = int(session_duration_data[i] if session_duration_data[i] is not None else 0) \
            + int(delta_snap_pre_data[i] if i < len(delta_snap_pre_data) else 0) \
            + int(delta_snap_post_data[i] if i < len(delta_snap_post_data) else 0)
    session_duration_snapsincluded.append(total)

# -------------------------
# weekly session durations (mirrors compute_weeklyduration)
# -------------------------
def compute_weeklyduration(week_num_list, start_list):
    session_duration_week = []
    for idx_s, s in enumerate(sid):
        total = 0
        for _, row in partner.iterrows():
            if str(row['sid']) == s:
                # parse session start to date
                start_raw = str(row['session_start_date']).replace("-", "/")
                try:
                    sess_date = datetime.datetime.strptime(start_raw, "%Y/%m/%d").date()
                except Exception:
                    try:
                        sess_date = pd.to_datetime(start_raw, errors='coerce').date()
                    except Exception:
                        sess_date = datetime.datetime.strptime("9999/01/01", "%Y/%m/%d").date()
                # include session if start >= start_list[idx_s] and < week_num_list[idx_s]
                if sess_date < week_num_list[idx_s] and sess_date >= start_list[idx_s]:
                    try:
                        sd = int(float(row['session_duration']))
                    except Exception:
                        sd = 0
                    if sd > DURATION_CAP:
                        sd = DURATION_CAP
                    total += sd
        # after iterating all rows, append weekly session total
        session_duration_week.append(total)
    # compute snapshot deltas for same week window and add them
    delta_pre = compute_delta_snap(partner, sid, 'sid', 'session_start_date', week_num_list, 'snapshot_start_pre', 'snapshot_finish_pre', start_list)
    delta_post = compute_delta_snap(partner, sid, 'sid', 'session_start_date', week_num_list, 'snapshot_start_post', 'snapshot_finish_post', start_list)
    session_duration_snaps = []
    for i in range(len(session_duration_week)):
        sc = int(session_duration_week[i]) + int(delta_pre[i]) + int(delta_post[i])
        session_duration_snaps.append(sc)
    return session_duration_snaps

week_1_sessionduration = compute_weeklyduration(week_1_dates, session_start_data)
week_2_sessionduration = compute_weeklyduration(week_2_dates, week_1_dates)
week_3_sessionduration = compute_weeklyduration(week_3_dates, week_2_dates)
week_4_sessionduration = compute_weeklyduration(week_4_dates, week_3_dates)

# -------------------------
# Determine completed_70 (overall across 4 weeks) - mirrors original logic exactly
# -------------------------
completed_70 = []
completed_70_mbi = 0
completed_70_control = 0
total_mbi = 0
total_control = 0
mri_MBI_count = 0
mri_control_count = 0

for i in range(len(sid)):
    # original uses '0' for MBI and '1' for control — use the same string comparison
    if randomization[i] == '0':
        total_mbi += 1
        if int(session_duration_snapsincluded[i]) > seventypercent_mod1to4:
            completed_70.append('1')
            completed_70_mbi += 1
        else:
            completed_70.append('0')
    if randomization[i] == '1':
        total_control += 1
        if int(session_duration_snapsincluded[i]) > seventypercent_controllen:
            completed_70.append('1')
            completed_70_control += 1
        else:
            completed_70.append('0')

# -------------------------
# weekly adherence binary (completed_weekly function in original)
# -------------------------
def completed_weekly(week):
    out = []
    for i in range(len(sid)):
        if randomization[i] == '0':
            # MBI
            if int(week[i]) > avg_weekly:
                out.append('1')
            else:
                out.append('0')
        elif randomization[i] == '1':
            # Control
            if int(week[i]) > avg_weekly_con:
                out.append('1')
            else:
                out.append('0')
        else:
            out.append('0')
    return out

week_1_adh = completed_weekly(week_1_sessionduration)
week_2_adh = completed_weekly(week_2_sessionduration)
week_3_adh = completed_weekly(week_3_sessionduration)
week_4_adh = completed_weekly(week_4_sessionduration)

# -------------------------
# Count standalone and journey sessions per sid (mirrors original loops)
# -------------------------
number_of_standalones = []
number_of_journeys = []

for s in sid:
    n_st = 0
    n_jy = 0
    for _, row in partner.iterrows():
        if str(row['sid']) == s:
            typ = str(row.get('session_type', ''))
            if 'Standalone' in typ:
                n_st += 1
            if 'Journey' in typ:
                n_jy += 1
    number_of_standalones.append(n_st)
    number_of_journeys.append(n_jy)

# -------------------------
# session_stage_max and adherence_stage (same logic as original)
# -------------------------
session_stage_max = []
adherence_stage = []
for s in sid:
    stages = []
    for _, row in partner.iterrows():
        if str(row['sid']) == s:
            stages.append(row.get('session_stage', ''))
    if not stages:
        adherence_stage.append('0')
        session_stage_max.append('0')
    else:
        max_stage = max(stages)
        session_stage_max.append(max_stage)
        if max_stage > 'S20':
            adherence_stage.append('1')
        else:
            adherence_stage.append('0')

# strip leading 'S' from session_stage_max entries (as original did)
session_stage_max = [s.strip('S') if isinstance(s, str) else s for s in session_stage_max]

# Insert header rows at position 0 for lists that original inserted headers into
# Build the header-containing lists according to the original final zip order
sid_with_header = sid.copy()
sid_with_header.insert(0, 'sid')

randomization.insert(0, "randomization")

# zone label calculation: replicate original (note original expression has odd precedence)
zone_percentage = (completed_70_mbi + completed_70_control / total_mbi + total_control)
if zone_percentage < 50:
    zone_label = ('RED Zone: ' + str(int(zone_percentage)) + '% of all listed participants completed 70% of app activity')
if zone_percentage > 49 and zone_percentage < 71:
    zone_label = ('AMBER Zone: ' + str(int(zone_percentage)) + '% of all listed participants completed 70% of app activity')
if zone_percentage > 70:
    zone_label = ('GREEN Zone: ' + str(int(zone_percentage)) + '% of all listed participants completed 70% of app activity')

zone_label_lst = [zone_label] + [''] * (len(sid) - 1 if len(sid) >= 1 else 0)

group_num_lst = []
group_num_lst.append('GROUPA group count: ' + str(total_mbi))
group_num_lst.append('GROUPB group count: ' + str(total_control))
for _ in range(2, len(sid)):
    group_num_lst.append('')

group_adherence_lst = []
group_adherence_lst.append('GROUPA adherence (threshold of 7492, or 70% of modules 1 through 4 [10688]): ' + str(completed_70_mbi) + '/' + str(total_mbi))
group_adherence_lst.append('GROUPB adherence (threshold of 6720s, or 70% of 16 sham sessions [9600s]): ' + str(completed_70_control) + '/' + str(total_control))
for _ in range(2, len(sid)):
    group_adherence_lst.append('')

# insert headers for many vectors to match original output
debfried_comp.insert(0, "debreifed")
week_1_adh.insert(0, "group_adherence_wk1_70% of activity weekly avg")
week_2_adh.insert(0, "group_adherence_wk2")
week_3_adh.insert(0, "group_adherence_wk3")
week_4_adh.insert(0, "group_adherence_wk4")
week_1_sessionduration.insert(0, "sessionduration_wk1")
week_2_sessionduration.insert(0, "sessionduration_wk2")
week_3_sessionduration.insert(0, "sessionduration_wk3")
week_4_sessionduration.insert(0, "sessionduration_wk4")
session_duration_data.insert(0, "session_duration_sum")
session_duration_snapsincluded.insert(0, "session_duration+snapshots")
delta_snap_post_data.insert(0, "delta_snap_post")
delta_snap_pre_data.insert(0, "delta_snap_pre")
completed_70.insert(0, "completed_70%_of_groupactivity?")
number_of_standalones.insert(0, "sessiontype_standalonesnap_totalcount")
number_of_journeys.insert(0, "sessiontype_journey_totalcount")
mri_comp_2.insert(0, 'MRI2 Completed')
week4_comp.insert(0, "Week4 Qs Completed")
session_stage_max.insert(0, 'session_stage_max')
adherence_stage.insert(0, 'adherence_stage')

# combine lists in same order as original
output = list(zip(
    zone_label_lst,
    group_num_lst,
    group_adherence_lst,
    sid_with_header,
    randomization,
    mri_comp_2,
    week4_comp,
    debfried_comp,
    session_duration_data,
    session_duration_snapsincluded,
    week_1_sessionduration,
    week_2_sessionduration,
    week_3_sessionduration,
    week_4_sessionduration,
    number_of_journeys,
    number_of_standalones,
    session_stage_max,
    adherence_stage
))

# create DataFrame and write CSV without header/index (like original)
out_df = pd.DataFrame(output)
out_df.to_csv(output_file, header=False, index=False)

print("Adherence report written to:", output_file)
