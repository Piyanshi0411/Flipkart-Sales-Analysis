from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "flipkart_products.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def save_chart(filename: str) -> None:
    """Save the current Matplotlib chart using a consistent layout."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / filename, dpi=180)
    plt.close()


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)

    numeric_columns = [
        "actual_price",
        "discounted_price",
        "discount_percentage",
        "rating",
        "rating_count",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["price_difference"] = df["actual_price"] - df["discounted_price"]
    df["value_score"] = (
        df["rating"] * 20
        + df["discount_percentage"] * 0.6
        + (df["rating_count"] / df["rating_count"].max()) * 20
    )

    return df


def create_summary_tables(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    category_summary = (
        df.groupby("category")
        .agg(
            product_count=("product_name", "count"),
            average_actual_price=("actual_price", "mean"),
            average_discounted_price=("discounted_price", "mean"),
            average_discount_percentage=("discount_percentage", "mean"),
            average_rating=("rating", "mean"),
        )
        .round(2)
        .sort_values("average_actual_price", ascending=False)
    )

    top_discounted = df.sort_values("discount_percentage", ascending=False).head(10)
    best_value = df.sort_values("value_score", ascending=False).head(10)

    category_summary.to_csv(OUTPUT_DIR / "category_summary.csv")
    top_discounted.to_csv(OUTPUT_DIR / "top_discounted_products.csv", index=False)
    best_value.to_csv(OUTPUT_DIR / "best_value_products.csv", index=False)


def create_visualizations(df: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid", palette="Set2")

    plt.figure(figsize=(10, 6))
    category_price = (
        df.groupby("category")["actual_price"].mean().sort_values(ascending=False)
    )
    sns.barplot(x=category_price.values, y=category_price.index)
    plt.title("Average Actual Price by Category")
    plt.xlabel("Average Actual Price")
    plt.ylabel("Category")
    save_chart("average_price_by_category.png")

    plt.figure(figsize=(10, 6))
    category_discount = (
        df.groupby("category")["discount_percentage"].mean().sort_values(ascending=False)
    )
    sns.barplot(x=category_discount.values, y=category_discount.index)
    plt.title("Average Discount Percentage by Category")
    plt.xlabel("Average Discount Percentage")
    plt.ylabel("Category")
    save_chart("average_discount_by_category.png")

    plt.figure(figsize=(10, 6))
    sns.histplot(df["discounted_price"], bins=20, kde=True)
    plt.title("Distribution of Discounted Product Prices")
    plt.xlabel("Discounted Price")
    plt.ylabel("Number of Products")
    save_chart("discounted_price_distribution.png")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x="discounted_price",
        y="rating",
        hue="category",
        size="discount_percentage",
        sizes=(40, 220),
        alpha=0.75,
    )
    plt.title("Discounted Price vs Rating")
    plt.xlabel("Discounted Price")
    plt.ylabel("Rating")
    plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    save_chart("price_vs_rating.png")

    plt.figure(figsize=(10, 6))
    top_discounted = df.sort_values("discount_percentage", ascending=False).head(10)
    sns.barplot(
        data=top_discounted,
        x="discount_percentage",
        y="product_name",
        hue="category",
        dodge=False,
    )
    plt.title("Top 10 Most Discounted Products")
    plt.xlabel("Discount Percentage")
    plt.ylabel("Product")
    plt.legend(title="Category", bbox_to_anchor=(1.02, 1), loc="upper left")
    save_chart("top_discounted_products.png")

    plt.figure(figsize=(11, 6))
    sns.boxplot(data=df, x="category", y="discounted_price")
    plt.title("Discounted Price Variation Across Categories")
    plt.xlabel("Category")
    plt.ylabel("Discounted Price")
    plt.xticks(rotation=35, ha="right")
    save_chart("category_price_boxplot.png")


def print_insights(df: pd.DataFrame) -> None:
    highest_price_category = (
        df.groupby("category")["actual_price"].mean().sort_values(ascending=False).index[0]
    )
    highest_discount_category = (
        df.groupby("category")["discount_percentage"]
        .mean()
        .sort_values(ascending=False)
        .index[0]
    )
    best_value_product = df.sort_values("value_score", ascending=False).iloc[0]

    print("Flipkart Product Price Analysis")
    print("=" * 34)
    print(f"Total products analyzed: {len(df)}")
    print(f"Categories analyzed: {df['category'].nunique()}")
    print(f"Highest average price category: {highest_price_category}")
    print(f"Highest average discount category: {highest_discount_category}")
    print(
        "Best value product: "
        f"{best_value_product['product_name']} "
        f"({best_value_product['brand']})"
    )
    print()
    print(f"Charts and summary files saved in: {OUTPUT_DIR}")


def main() -> None:
    df = load_data()
    create_summary_tables(df)
    create_visualizations(df)
    print_insights(df)


if __name__ == "__main__":
    main()
