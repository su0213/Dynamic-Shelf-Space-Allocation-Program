#import extisted module
import pandas as pd
import time

#import funciton used in this program
from utils.sells_value_placement import sells_value_placement
from utils.product_clustering import clustering_result
from utils.placement_algo import phase3_program
from solution_analysis import solution_analysis

def main():
    # Phase 1: Frist assign products with sells value to place on the shelf with highest weight
    start_time = time.time()
    input_file = 'product-shelf data\sample_data_0806.xlsx'
    df_products = pd.read_excel(input_file, sheet_name='商品', dtype={'條碼': str})
    print(df_products)
    df_products["條碼"] = df_products["條碼"].astype(str) # 確認條碼為str型態
    df_shelves = pd.read_excel(input_file, sheet_name='貨架') 
    remaining_products_df, remaining_shelves_df = sells_value_placement(df_products, df_shelves)
    print(remaining_products_df)
    print(remaining_shelves_df)
    # End of phase 1: Return placed result, remaining products, and remaining shelves area
    
    # Phase 2: Use remaining products and remaining shelves area to assign products to place on the shelf, and then append to the previous placed result
    assigned_result = clustering_result(remaining_products_df, remaining_shelves_df)
    print(assigned_result.to_string())
    # End of phase 2: Require where products to be placed. Return assigned result to phase 3
    
    # Phase 3: Use algorithm to determine how exactly the products' location 
    final_result = phase3_program(assigned_result, df_products, df_shelves)
    final_result.to_excel('output.xlsx')
    print(final_result.to_string())
    # End of phase 3: Return final result
    
    # Solution Analysis
    total_product_amount, space_utilization, brand_cluster_score,  shelf_utilization_df = solution_analysis(final_result, df_shelves)
    print(shelf_utilization_df)
    print(f"貨架空間利用率: ", space_utilization,"%", ", 總擺放個數: ", total_product_amount,"個商品。")
    end_time = time.time()
    print(f"程序花費時間: {end_time - start_time} 秒")
    
    #測試行銷值商品是否在結果中的程式
    # sells = df_products[df_products['行銷中'] == 'Y'].reset_index()
    # print(sells)
    # test = {}
    # for idx, p in sells.iterrows():
    #     if p['條碼'] in final_result['商品ID'].values:
    #         print(final_result[final_result['商品ID'] == p['條碼']])
    #         test[idx] = True
    #     else:
    #         test[idx] = False
    # print(test)
    
    return

if __name__ == "__main__":
    main()

