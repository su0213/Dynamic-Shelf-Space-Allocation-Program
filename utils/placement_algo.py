import pandas as pd
import numpy as np
def sort_by_sales(product_info_df):
    return product_info_df.sort_values(by='月銷量', ascending=False)

def group_by_height(products_df, bucket_interval):
    products_df_copy = products_df.copy()
    products_df_copy['高度桶'] = (products_df_copy['單品高'] // bucket_interval) * bucket_interval
    grouped_buckets = products_df_copy.groupby('高度桶')
    return grouped_buckets

def calculate_brand_bonus(bucket):
    # 計算同品牌商品的銷量加成
    brand_counts = bucket['品牌'].value_counts()
    brand_bonus = {}
    for brand, count in brand_counts.items():
        if count >= 4:
            bonus = 1.3
        elif count >= 2:
            bonus = 1.1
        else:
            bonus = 1.0
        brand_bonus[brand] = bonus
    # 應用銷量加成
    bucket['加成後銷量'] = bucket.apply(lambda row: row['月銷量'] * brand_bonus[row['品牌']], axis=1)
    return bucket

def knapsack_dp(items, capacity):
    items = items.copy()
    items['單品面寬'] = items['單品面寬'].astype(float)
    items['加成後銷量'] = items['加成後銷量'].astype(float)

    n = len(items)
    w = list(items['單品面寬'])
    v = list(items['加成後銷量'])
    dp = np.zeros((n+1, int(capacity)+1), dtype=float)
    keep = np.zeros((n+1, int(capacity)+1), dtype=int)

    for i in range(1, n+1):
        for cw in range(int(capacity)+1):
            if w[i-1] <= cw:
                if dp[i-1][cw] < dp[i-1][cw - int(w[i-1])] + v[i-1]:
                    dp[i][cw] = dp[i-1][cw - int(w[i-1])] + v[i-1]
                    keep[i][cw] = 1
                else:
                    dp[i][cw] = dp[i-1][cw]
            else:
                dp[i][cw] = dp[i-1][cw]

    # 反向追蹤選擇的商品
    res_items = []
    cw = int(capacity)
    for i in range(n, 0, -1):
        if keep[i][cw] == 1:
            res_items.append(i-1)
            cw -= int(w[i-1])

    selected_items = items.iloc[res_items]
    return selected_items

def placement_algorithm(products_barcodes, current_product_info, current_shelf_info):
    rows = []  # 用於收集所有行
    total_products = current_product_info.copy()
    X_initial = 60  # 初始取前 X 個熱銷商品
    bucket_interval = 10  # 高度分組間隔
    W_threshold = 10.0  # 寬度浪費容忍度 (改為浮點數)

    for _, shelf in current_shelf_info.iterrows():
        shelf_id = str(shelf['貨架ID'])
        shelf_width = float(shelf['寬'])
        shelf_height = float(shelf['高'])
        can_overheight = shelf['超高']  # 假設在 shelf_info 中有這個欄位
        layer_index = 1  # 層序起始為 1
        X = X_initial
        used_height = 0.0  # 累計已使用的高度

        max_iterations = 300  # 設定最大迭代次數，避免無窮迴圈
        iteration_count = 0

        while not total_products.empty and iteration_count < max_iterations:
            iteration_count += 1
            X = min(X, len(total_products))
            sorted_products = sort_by_sales(total_products).head(X)
            grouped_buckets = group_by_height(sorted_products, bucket_interval)
            layer_products = pd.DataFrame()  # 用於存放本層所有選擇的商品
            layer_height = 0.0  # 本層的高度
            remaining_width = shelf_width  # 剩餘寬度
            bucket_found = False

            # 遍歷所有高度桶，嘗試在同一層添加更多商品
            for height_bucket, bucket in grouped_buckets:
                # 計算品牌加成
                bucket = calculate_brand_bonus(bucket)

                # 在剩餘寬度下，使用動態規劃選擇商品組合
                capacity = remaining_width
                selected_items = knapsack_dp(bucket, capacity)

                # 檢查是否有選擇到商品
                if selected_items.empty:
                    continue

                # 計算選擇的商品總寬度
                selected_total_width = selected_items['單品面寬'].sum()
                W = remaining_width - selected_total_width

                if W >= -W_threshold:
                    # 接受該組合，更新本層商品和剩餘寬度
                    layer_products = pd.concat([layer_products, selected_items])
                    remaining_width -= selected_total_width
                    # 更新本層高度，取最大值
                    layer_height = max(layer_height, height_bucket + bucket_interval)
                    # 更新商品列表，移除已選商品
                    total_products = total_products.drop(selected_items.index)
                    bucket_found = True
                    # 如果剩餘寬度已經接近0，跳出高度桶迴圈
                    if remaining_width <= 0:
                        break
                else:
                    continue  # 繼續嘗試下一個高度桶

            if bucket_found:
                # 在放置本層商品前，檢查總高度限制
                if can_overheight == 'Y' and layer_index == 1:
                    # 如果允許超高，且是最上層，則不檢查高度限制
                    pass
                else:
                    if used_height + layer_height > shelf_height:
                        print(f"貨架 {shelf_id} 的總高度超過限制，停止擺放更多層。")
                        break

                # 放置本層商品
                layer_products = layer_products.sort_values(by='單品面寬', ascending=False)
                for order, (_, product) in enumerate(layer_products.iterrows(), start=1):
                    rows.append({
                        '貨架ID': shelf_id,
                        '層序': layer_index,
                        '層高': layer_height,
                        '順序': order,
                        '商品ID': product['條碼'],
                        '寬度': product['單品面寬']
                    })
                # 更新已使用的總高度
                used_height += layer_height
                layer_index += 1
                # 重置迭代計數器和 X
                iteration_count = 0
                X = X_initial
            else:
                # 增加 X，嘗試更多商品
                X += 10
                if X > len(current_product_info):
                    print(f"無法為貨架 {shelf_id} 的層 {layer_index} 找到合適的商品組合。")
                    break  # 跳出 while 迴圈
        else:
            if iteration_count >= max_iterations:
                print(f"達到最大迭代次數，停止處理貨架 {shelf_id}。")
    # 在處理完所有貨架後，創建最終的 DataFrame
    final_df = pd.DataFrame(rows)
    return final_df

def phase3_program(assigned_result, df_products, df_shelves):
    # 確保所有條碼和貨架ID都是字串類型
    df_products['條碼'] = df_products['條碼'].astype(str).str.strip()
    df_shelves['貨架ID'] = df_shelves['貨架ID'].astype(str).str.strip()
    assigned_result['貨架ID'] = assigned_result['貨架ID'].astype(str).str.strip()

    # 將 assigned_result 的商品名稱與條碼分離，並清理條碼的格式
    assigned_result['商品條碼'] = assigned_result['商品'].str.split(' - ').str[0].str.strip()

    # 將每個貨架及其商品對應拆開傳入演算法做最佳化
    total_data = assigned_result['貨架ID'].unique()
    final_result = []
    
    for shelf_id in total_data:
        # 取得該貨架上的商品條碼
        products_barcodes = assigned_result[assigned_result['貨架ID'] == shelf_id]['商品條碼'].tolist()
        
        # 打印檢查分離出的條碼
        print(f"貨架 {shelf_id} 的商品條碼: {products_barcodes}")
        
        # 根據條碼查找對應商品資料
        current_product_info = df_products[df_products['條碼'].isin(products_barcodes)]
        
        # 根據貨架ID查找對應的貨架資料
        current_shelf_info = df_shelves[df_shelves['貨架ID'] == shelf_id]
        
        # 打印檢查商品與貨架資訊
        print(f"貨架ID: {shelf_id}")
        print("商品詳細資訊：")
        print(current_product_info)
        print("貨架詳細資訊：")
        print(current_shelf_info)
        
        # 調用最佳化函數
        current_result = placement_algorithm(products_barcodes, current_product_info, current_shelf_info)
        final_result.append(current_result)
    df = pd.DataFrame(columns=['貨架ID', '層序', '層高', '順序', '商品ID', '寬度'])
    for result in final_result:
        df = pd.concat([df, result], ignore_index = True)

    return df
