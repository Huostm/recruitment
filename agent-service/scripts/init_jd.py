import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from services.milvus_service import MilvusService

# 读取 JD 文件
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
jd_path = os.path.join(base_dir, 'data', 'jd', 'comprehensive_jd.txt')

with open(jd_path, 'r', encoding='utf-8') as f:
    jd_text = f.read()

jd_list = [jd_text]

print("=" * 60)
print("初始化 JD 数据到 Milvus")
print("=" * 60)

# 初始化 MilvusService
milvus_service = MilvusService()

# 清空已有数据
print("\n清空旧数据...")
milvus_service.clear_collection()

# 批量插入 JD
print(f"\n插入 {len(jd_list)} 个 JD...")
print(f"JD 文本长度: {len(jd_list[0])} 字符")
success = milvus_service.insert_jd_batch(jd_list)

if success:
    # 等待数据落盘
    import time
    time.sleep(2)
    count = milvus_service.get_count()
    print(f"\n[SUCCESS] 初始化成功！当前 JD chunks 数量: {count}")

    # 测试检索
    print("\n测试检索...")
    results = milvus_service.search("Python LangChain Agent", top_k=3)
    print(f"检索到 {len(results)} 个结果")
    if results:
        print(f"Top 1: score={results[0]['score']:.3f}, text={results[0]['text'][:50]}...")
else:
    print("\n[ERROR] 初始化失败")
