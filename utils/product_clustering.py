import pandas as pd
from collections import defaultdict

def clustering_result(df_products, df_shelves):
    # 計算每個商品的面積（單品面寬 * 單品高）
    df_products['商品面積'] = df_products['單品面寬'] * df_products['單品高']
    
    # 將 df_shelves 中的 NaN 替換為 '無分類'
    df_shelves['商品分類'] = df_shelves['商品分類'].fillna('無分類')
    
    # 準備分配結果
    shelves_result = defaultdict(list)
    
    # 計算所有貨架的總數
    total_shelves_count = len(df_shelves)
    
    # 計算所有商品的總面積
    total_products_area = df_products['商品面積'].sum()
    
    # 計算每個貨架平均可分配的商品面積
    average_area_per_shelf = total_products_area / total_shelves_count
    
    # 初始化每個貨架的剩餘空間
    shelf_space = {shelf['貨架ID']: average_area_per_shelf for _, shelf in df_shelves.iterrows()}
    
    # 將商品中 NaN 的分類標示為 '無分類'
    df_products['分類'] = df_products['分類'].fillna('無分類')
    
    # 優先處理行銷中的商品
    marketing_products = df_products[df_products['行銷中'] == 'Y']
    other_products = df_products[df_products['行銷中'] != 'Y']
    
    # 定義分配商品的函數
    def allocate_products(products):
        unallocated_products = []
        
        for _, product in products.iterrows():
            category = product['分類']
            allocated = False
            
            # 優先分配到相同分類且剩餘空間足夠的貨架
            possible_shelves = df_shelves[df_shelves['商品分類'] == category]
            for _, shelf in possible_shelves.iterrows():
                shelf_id = shelf['貨架ID']
                if shelf_space[shelf_id] >= product['商品面積']:
                    shelves_result[shelf_id].append(f"{product['條碼']} - {product['名稱']}")
                    shelf_space[shelf_id] -= product['商品面積']
                    allocated = True
                    break
            
            # 如果分類無法分配，嘗試分配到 "無分類" 貨架
            if not allocated:
                no_category_shelves = df_shelves[df_shelves['商品分類'] == '無分類']
                for _, shelf in no_category_shelves.iterrows():
                    shelf_id = shelf['貨架ID']
                    if shelf_space[shelf_id] >= product['商品面積']:
                        shelves_result[shelf_id].append(f"{product['條碼']} - {product['名稱']}")
                        shelf_space[shelf_id] -= product['商品面積']
                        allocated = True
                        break

            # 如果仍無法分配，將商品記錄為未分配
            if not allocated:
                unallocated_products.append(f"{product['條碼']} - {product['名稱']}")
                print(f"商品 {product['條碼']}（分類: {category}）無法分配到任何貨架。")
        
        return unallocated_products

    # 先分配行銷中的商品
    unallocated_marketing = allocate_products(marketing_products)
    
    # 然後分配其他商品
    unallocated_others = allocate_products(other_products)
    
    # 構建結果資料
    data = []
    for shelf_id, products in shelves_result.items():   
        for product in products:
            data.append([shelf_id, product])
    
    # 創建一個 DataFrame 來顯示分配結果
    df_allocation = pd.DataFrame(data, columns=['貨架ID', '商品'])
    df_allocation.sort_values('貨架ID', inplace=True)
    df_allocation = df_allocation.reset_index(drop=True)
    
    print(f"未分配商品總數: {len(unallocated_marketing) + len(unallocated_others)}")
    return df_allocation

# 測試時，將商品與貨架資料載入，呼叫 clustering_result(df_products, df_shelves)
