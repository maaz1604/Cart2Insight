import pandas as pd


# def load_datasets(data_dir: str):
#     """Load all Cart2Insights raw CSV datasets."""

#     datasets = {
#         "customers": pd.read_csv(data_dir + "customers_dataset.csv"),
#         "orders": pd.read_csv(data_dir + "orders_dataset.csv"),
#         "order_items": pd.read_csv(data_dir + "order_items_dataset.csv"),
#         "order_payments": pd.read_csv(data_dir + "order_payments_dataset.csv"),
#         "order_reviews": pd.read_csv(data_dir + "order_reviews_dataset.csv"),
#         "products": pd.read_csv(data_dir + "products_dataset.csv"),
#         "sellers": pd.read_csv(data_dir + "sellers_dataset.csv"),
#         "geolocation": pd.read_csv(data_dir + "geolocation_dataset.csv"),
#         "product_category_translation": pd.read_csv(
#             data_dir + "product_category_name_translation.csv"
#         ),
#     }

#     return datasets

def load_datasets(data_dir: str):
    """Load all Cart2Insights CSV datasets."""

    datasets = {
        "customers": pd.read_csv(data_dir + "customers.csv"),
        "orders": pd.read_csv(data_dir + "orders.csv"),
        "order_items": pd.read_csv(data_dir + "order_items.csv"),
        "order_payments": pd.read_csv(data_dir + "order_payments.csv"),
        "order_reviews": pd.read_csv(data_dir + "order_reviews.csv"),
        "products": pd.read_csv(data_dir + "products.csv"),
        "sellers": pd.read_csv(data_dir + "sellers.csv"),
        "geolocation": pd.read_csv(data_dir + "geolocation.csv"),
        "product_category_translation": pd.read_csv(
            data_dir + "product_category_name_translation.csv"
        ),
    }

    return datasets