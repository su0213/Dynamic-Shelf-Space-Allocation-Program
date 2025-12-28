def sells_value_placement(df_products, df_shelves):
    max_sales = df_products['月銷量'].max()
    df_products.loc[df_products['行銷中'] == 'Y', '月銷量'] = max_sales + 10000
    return df_products, df_shelves
