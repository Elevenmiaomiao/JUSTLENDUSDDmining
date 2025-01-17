import requests
import csv
import time
from datetime import datetime, timezone, timedelta

# 常量
API_URL = "https://api.trongrid.io/v1/accounts/THxNCPGp8N8SJBScRU8rKPf7PvuwkGihmW/transactions/trc20"
API_KEY = "自己去申请trongridkey"   # trongird.io
LIMIT = 50
TRC20_ID = "TPYmHEhy5n8TCEfYGqW2rPxsghSfzghPDn"

# 初始化
start = 0
数据获取总量 = 0
总转出金额 = 0
总转入金额 = 0
输出文件 = "trongrid_data.csv"

# CSV 表头
表头 = ["UTC+8 时间", "发送方", "接收方", "交易哈希", "交易方向", "交易金额"]

with open(输出文件, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(表头)

    while True:
        # 调用 Trongrid API 请求
        params = {
            "limit": LIMIT,
            "only_to": False,
            "only_from": False,
            "min_timestamp": 0,
            "max_timestamp": int(time.time() * 1000),
            "contract_address": TRC20_ID
        }
        headers = {"Authorization": API_KEY}
        response = requests.get(API_URL, params=params, headers=headers)

        if response.status_code != 200:
            print(f"错误：收到状态码 {response.status_code}")
            break

        result = response.json()
        data = result.get("data", [])

        if not data:
            print("没有更多数据可以获取。")
            break

        for item in data:
            # 处理数据
            timestamp = item["block_timestamp"] // 1000
            utc_plus_8 = datetime.fromtimestamp(timestamp, timezone.utc) + timedelta(hours=8)
            from_address = item["from"]
            to_address = item["to"]
            tx_hash = item["transaction_id"]
            direction = "转出" if from_address == "THxNCPGp8N8SJBScRU8rKPf7PvuwkGihmW" else "转入"
            amount = int(item["value"] or 0) / (10 ** 18)

            if direction == "转出":
                总转出金额 += amount
            else:
                总转入金额 += amount

            # 写入 CSV
            writer.writerow([
                utc_plus_8.strftime("%Y-%m-%d %H:%M:%S"),
                from_address,
                to_address,
                tx_hash,
                direction,
                amount
            ])

        # 打印日志
        数据获取总量 += len(data)
        if 数据获取总量 % 200 == 0:
            print(f"已获取 {数据获取总量} 条记录。")
            print(f"总转出金额：{总转出金额:.6f}")
            print(f"总转入金额：{总转入金额:.6f}")

        # 更新分页参数
        start += LIMIT
        time.sleep(0.5)  # 防止请求频率过高

print(f"数据获取完成。总获取记录数：{数据获取总量}")
print(f"最终总转出金额：{总转出金额:.6f}")
print(f"最终总转入金额：{总转入金额:.6f}")
