import pandas as pd

def solution_analysis(df, df_shelf):
    # 計算總商品個數
    total_product_amount = len(df)
    
    # 計算總空間利用率
    placed_shelves = df['貨架ID'].unique()
    total_shelf_space = 0.0
    used_space = 0.0
    
    shelf_utilization = []  # 用於存放每個貨架的空間利用率

    for _, shelf in df_shelf.iterrows():
        shelf_id = shelf['貨架ID']
        shelf_space = shelf['寬'] * shelf['高']
        
        if shelf_id in placed_shelves:
            total_shelf_space += shelf_space
            
            # 計算該貨架的已用空間
            shelf_items = df[df['貨架ID'] == shelf_id]
            shelf_used_space = (shelf_items['層高'] * shelf_items['寬度']).sum()
            used_space += shelf_used_space
            
            # 計算該貨架的空間利用率
            if shelf_space > 0:
                shelf_utilization_rate = (shelf_used_space / shelf_space) * 100
            else:
                shelf_utilization_rate = 0
            
            shelf_utilization.append({
                '貨架ID': shelf_id,
                '貨架利用率(%)': shelf_utilization_rate,
                '已用空間': shelf_used_space,
                '總空間': shelf_space
            })
    
    # 計算總空間利用率
    if total_shelf_space > 0:
        space_utilization = (used_space / total_shelf_space) * 100
    else:
        space_utilization = 0

    # 計算品牌聚合度（此處保留空，需根據需求具體實現）
    brand_cluster_score = 0

    # 轉換個別貨架利用率為 DataFrame
    shelf_utilization_df = pd.DataFrame(shelf_utilization).sort_values('貨架ID').reset_index(drop=True)

    return total_product_amount, space_utilization, brand_cluster_score, shelf_utilization_df
