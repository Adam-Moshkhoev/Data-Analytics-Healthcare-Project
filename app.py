# Healthcare Insurance Cost Analysis - Streamlit dashboard
#
# How to run:   streamlit run app.py
#
# This dashboard uses the CLEANED data made by the Jupyter notebook
# (data/clean/insurance_clean.csv). Run the notebook first if that file is missing.

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Healthcare Insurance Costs", page_icon="🏥", layout="wide")

AGE_BANDS = ["18-24", "25-34", "35-44", "45-54", "55-64"]


# ---------- 1. Load the cleaned data ----------
@st.cache_data  # load the file once, not on every click
def load_data():
    return pd.read_csv("data/clean/insurance_clean.csv")


try:
    df = load_data()
except FileNotFoundError:
    st.error("Cleaned data not found. Please run the notebook first to create "
             "data/clean/insurance_clean.csv")
    st.stop()


# ---------- 2. Sidebar filters ----------
st.sidebar.header("Filters")
chosen_ages = st.sidebar.multiselect("Age band", AGE_BANDS, default=AGE_BANDS)
chosen_smoker = st.sidebar.multiselect("Smoker", ["no", "yes"], default=["no", "yes"])
regions = sorted(df["region"].unique())
chosen_regions = st.sidebar.multiselect("Region", regions, default=regions)

# Keep only the rows that match ALL the chosen filters
filtered = df[
    df["age_band"].isin(chosen_ages)
    & df["smoker"].isin(chosen_smoker)
    & df["region"].isin(chosen_regions)
]


# ---------- 3. Title and headline numbers ----------
st.title("🏥 Healthcare Insurance Cost Analysis")
st.write("How do medical insurance **charges** change with age, BMI, smoking and region? "
         "*These results show links (associations), not causes.*")

if filtered.empty:
    st.warning("No people match these filters. Please choose at least one option in each filter.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("People", len(filtered))
col2.metric("Median charge", f"{filtered['charges'].median():,.0f}")
col3.metric("Mean charge", f"{filtered['charges'].mean():,.0f}")
col4.metric("Smokers", f"{(filtered['smoker'] == 'yes').mean() * 100:.1f}%")

if len(filtered) < 30:
    st.info("Fewer than 30 people selected - results for small groups are not reliable.")


# ---------- 4. Charts, one tab per business question ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Distribution", "Q1 Smoking", "Q2 Age & BMI", "Q3 Regions", "Summary for managers"])

with tab1:
    st.subheader("How are charges spread out?")
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.histplot(filtered["charges"], bins=40, ax=ax)
    ax.axvline(filtered["charges"].median(), color="green", label="Median")
    ax.axvline(filtered["charges"].mean(), color="red", linestyle="--", label="Mean")
    ax.set_title("Distribution of charges")
    ax.set_xlabel("Charges")
    ax.set_ylabel("Number of people")
    ax.legend()
    st.pyplot(fig)
    st.write("Most people have low charges, but a few have very high charges. "
             "This pulls the **mean** above the **median**, so the median is the better 'typical' value.")

with tab2:
    st.subheader("Q1. Do smokers have higher charges?")
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.boxplot(data=filtered, x="smoker", y="charges", order=["no", "yes"], ax=ax)
    ax.set_title("Charges by smoking status")
    ax.set_xlabel("Smoker")
    ax.set_ylabel("Charges")
    st.pyplot(fig)
    # Count, mean and median for each group
    smoker_table = filtered.groupby("smoker")["charges"].agg(["count", "mean", "median"]).round(0)
    st.dataframe(smoker_table)

with tab3:
    st.subheader("Q2. How are age and BMI linked to charges?")
    left, right = st.columns(2)
    for column, place in [("age", left), ("bmi", right)]:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.scatterplot(data=filtered, x=column, y="charges", hue="smoker", alpha=0.6, ax=ax)
        ax.set_title(f"{column.upper()} vs charges")
        ax.set_xlabel(column.upper())
        ax.set_ylabel("Charges")
        place.pyplot(fig)
    st.write("Charges go **up with age** for everyone. For **smokers**, charges jump when BMI "
             "is above about 30. For non-smokers, BMI makes little difference.")

with tab4:
    st.subheader("Q3. How do regions compare?")
    region_table = filtered.groupby("region")["charges"].agg(["count", "mean", "median"]).round(0)
    fig, ax = plt.subplots(figsize=(8, 4))
    region_table[["mean", "median"]].plot(kind="bar", ax=ax)
    ax.set_title("Mean and median charges by region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Charges")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)
    st.dataframe(region_table)
    st.write("Regions with more smokers (like the southeast) have higher average charges. "
             "So region on its own does not explain the cost differences.")

with tab5:
    st.subheader("Summary for managers")
    st.caption("Based on all 1,337 people (not the filters). Drafted with help from an AI "
               "assistant; every number was checked in the notebook.")
    st.markdown("""
- **Smoking has the strongest link with charges.** Smokers' median charge is **34,456**,
  compared with **7,346** for non-smokers - about **4.7 times higher**.
- **Charges rise with age.** The median goes from **2,458** (age 18-24) to **13,227** (age 55-64).
- **BMI matters mainly for smokers.** Smokers with a BMI of 30 or more have a median of **40,904**.
- **Regional differences are small.** The southeast has the highest average (**14,735**), but it
  also has the most smokers (**25%**). Among non-smokers, the southeast is actually the lowest.
- **Caution:** these are associations, not causes. The data has no medical details or dates,
  and must **not** be used to make decisions about individual people.
""")
