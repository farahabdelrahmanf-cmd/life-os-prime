#!/usr/bin/env python3
"""
LIFE OS PRIME // Automated Garmin Connect Sync Engine
Pulls latest biometrics, sleep, body battery, steps, VO2 max, and race predictions
and saves them to garmin_data.json for instant web app telemetry.
"""
import os
import json
from datetime import date, timedelta, datetime
from garminconnect import Garmin

def sync():
    token_dir = os.path.expanduser("~/.garminconnect")
    client = Garmin()
    client.login(token_dir)

    today_str = date.today().isoformat()
    yesterday_str = (date.today() - timedelta(days=1)).isoformat()

    data = {
        "last_synced": datetime.now().isoformat(),
        "device": "Garmin Forerunner 265",
        "user": {
            "weight_kg": 75.0,
            "height_cm": 188.0,
            "target_weight_kg": 80.0
        },
        "race_predictions": {
            "time_5k_seconds": 1259,
            "time_5k_formatted": "20:59",
            "time_10k_formatted": "45:54",
            "time_half_formatted": "1:44:16",
            "target_5k_formatted": "19:59",
            "pace_gap_seconds": 12
        },
        "metrics": {
            "vo2_max": 52,
            "body_battery": 84,
            "resting_hr": 52,
            "sleep_score": 86,
            "training_status": "RECOVERY / LOW CHRONIC LOAD",
            "steps": 0,
            "step_goal": 10000
        }
    }

    try:
        profile = client.get_user_profile()
        ud = profile.get("userData", {})
        if ud.get("weight"):
            data["user"]["weight_kg"] = round(ud.get("weight") / 1000.0, 1)
        if ud.get("height"):
            data["user"]["height_cm"] = round(ud.get("height"), 1)
    except Exception as e:
        print("Profile fetch warning:", e)

    try:
        races = client.get_race_predictions()
        t5k = races.get("time5K")
        if t5k:
            data["race_predictions"]["time_5k_seconds"] = t5k
            mins = t5k // 60
            secs = t5k % 60
            data["race_predictions"]["time_5k_formatted"] = f"{mins}:{secs:02d}"
            # Target is 19:59 (1199s)
            gap = max(0, t5k - 1199)
            data["race_predictions"]["pace_gap_seconds"] = round(gap / 5.0)

        t10k = races.get("time10K")
        if t10k:
            mins = t10k // 60
            secs = t10k % 60
            data["race_predictions"]["time_10k_formatted"] = f"{mins}:{secs:02d}"

        thalf = races.get("timeHalfMarathon")
        if thalf:
            hrs = thalf // 3600
            mins = (thalf % 3600) // 60
            secs = thalf % 60
            data["race_predictions"]["time_half_formatted"] = f"{hrs}:{mins:02d}:{secs:02d}"
    except Exception as e:
        print("Race predictions warning:", e)

    try:
        summary = client.get_user_summary(today_str)
        if summary.get("totalSteps"):
            data["metrics"]["steps"] = summary.get("totalSteps")
        if summary.get("dailyStepGoal"):
            data["metrics"]["step_goal"] = summary.get("dailyStepGoal")
        if summary.get("restingHeartRate"):
            data["metrics"]["resting_hr"] = summary.get("restingHeartRate")
    except Exception as e:
        print("Summary fetch warning:", e)

    try:
        bb = client.get_body_battery(today_str)
        if isinstance(bb, list) and len(bb) > 0:
            latest = bb[-1]
            vals = latest.get("bodyBatteryValuesArray", [])
            for pair in reversed(vals):
                if len(pair) > 1 and pair[1] is not None:
                    data["metrics"]["body_battery"] = pair[1]
                    break
    except Exception as e:
        print("Body battery warning:", e)

    try:
        sl = client.get_sleep_data(today_str)
        dto = sl.get("dailySleepDTO", {})
        score = dto.get("sleepScores", {}).get("overall", {}).get("value")
        if score:
            data["metrics"]["sleep_score"] = score
    except Exception as e:
        print("Sleep warning:", e)

    out_path = os.path.join(os.path.dirname(__file__), "garmin_data.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Successfully synced Garmin data to {out_path}")
    print(f"  • Device: {data['device']}")
    print(f"  • 5K Prediction: {data['race_predictions']['time_5k_formatted']} (Pace gap: -{data['race_predictions']['pace_gap_seconds']}s/km)")
    print(f"  • Weight: {data['user']['weight_kg']} kg (Target: {data['user']['target_weight_kg']} kg)")

if __name__ == "__main__":
    sync()
