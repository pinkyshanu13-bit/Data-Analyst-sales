from pathlib import Path
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)
BASE = Path(__file__).resolve().parent

@app.route("/")
def dashboard():
    df = pd.read_csv(BASE / "data" / "sales_data.csv", parse_dates=["Order Date"])
    df["Revenue"] = df["Units Sold"] * df["Unit Price"]
    df["Profit"] = df["Units Sold"] * (df["Unit Price"] - df["Unit Cost"])
    monthly = df.groupby(df["Order Date"].dt.strftime("%b %Y"))["Revenue"].sum()
    categories = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
    regions = df.groupby("Region")["Profit"].sum().sort_values(ascending=False)
    return render_template(
        "index.html",
        revenue=f"{df['Revenue'].sum():,.2f}",
        profit=f"{df['Profit'].sum():,.2f}",
        units=f"{int(df['Units Sold'].sum()):,}",
        top_category=categories.index[0],
        top_region=regions.index[0],
        months=list(monthly.index), monthly_values=monthly.round(2).tolist(),
        category_labels=list(categories.index), category_values=categories.round(2).tolist(),
        region_labels=list(regions.index), region_values=regions.round(2).tolist(),
        records=df.sort_values("Order Date", ascending=False).head(8).assign(
            **{"Order Date": lambda x: x["Order Date"].dt.strftime("%d %b %Y")}
        )[["Order Date","Region","Product","Units Sold","Revenue","Profit"]].to_dict("records")
    )

if __name__ == "__main__":
    app.run(debug=True)
