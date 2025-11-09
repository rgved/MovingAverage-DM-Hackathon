# src/trim_data.py
import pandas as pd
import os

# ---------- Paths ----------
input_dir = "data/processed"
output_dir = "data/trimmed"
os.makedirs(output_dir, exist_ok=True)

# ---------- Date Range (Hackathon Period) ----------
start_date = pd.Timestamp("2025-08-01")
end_date = pd.Timestamp("2025-11-07")
print(f"📅 Trimming all datasets to {start_date.date()} → {end_date.date()} (Hackathon 3-month period)\n")

summary = []

# ---------- Trim Loop ----------
for file in os.listdir(input_dir):
    if file.endswith(".csv"):
        file_path = os.path.join(input_dir, file)
        df = pd.read_csv(file_path)
        # Convert and remove timezone info safely
        df["Date"] = pd.to_datetime(df["Date"], utc=True, errors="coerce").dt.tz_convert(None)

        # Strictly include data between start_date and end_date (inclusive)
        df_trimmed = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

        # Save to trimmed folder
        out_path = os.path.join(output_dir, file)
        df_trimmed.to_csv(out_path, index=False)

        row_count = len(df_trimmed)
        status = "✅" if row_count > 0 else "⚠️ Empty"
        print(f"{status} {file:<20} | {row_count:>4} rows retained | Saved to data/trimmed/")
        summary.append((file, row_count))

# ---------- Summary ----------
print("\n📊 Summary Report")
for f, count in summary:
    if count < 30:
        print(f"⚠️ {f:<20} — Only {count} rows (less than 30 trading days)")
    else:
        print(f"✅ {f:<20} — OK ({count} rows)")

print("\n🎯 All trimmed files saved in data/trimmed/")
