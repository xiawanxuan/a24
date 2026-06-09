import urllib.request
import json

base = "http://localhost:8000"

print("=== 测试反切推导 ===")
data = json.dumps({"upper_char": "德", "lower_char": "红"}).encode('utf-8')
req = urllib.request.Request(
    f"{base}/api/v1/fanqie/derive",
    data=data,
    headers={'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode('utf-8'))
    print("成功!")
    print(f"上字声母选项: {result['upper_shengmu_options']}")
    print(f"下字韵母选项: {result['lower_yunmu_options']}")
    print(f"推导结果数: {len(result['derivations'])}")
    if result['derivations']:
        d = result['derivations'][0]
        print(f"组合读音: {d['combined_pronunciation']}")
        print(f"匹配汉字数: {len(d['possible_chars'])}")
except Exception as e:
    print(f"失败: {e}")

print()

print("=== 测试音韵相似度 ===")
data = json.dumps({"char1": "东", "char2": "红"}).encode('utf-8')
req = urllib.request.Request(
    f"{base}/api/v1/similarity",
    data=data,
    headers={'Content-Type': 'application/json'}
)
try:
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode('utf-8'))
    print("成功!")
    print(f"声母相似度: {result['shengmu_similarity']}")
    print(f"韵母相似度: {result['yunmu_similarity']}")
    print(f"声调相似度: {result['shengdiao_similarity']}")
    print(f"总体相似度: {result['overall_similarity']}")
except Exception as e:
    print(f"失败: {e}")

print()

print("=== 测试查找相似汉字 ===")
try:
    resp = urllib.request.urlopen(f"{base}/api/v1/similarity/find/%E4%B8%9C?threshold=0.3&limit=5")
    result = json.loads(resp.read().decode('utf-8'))
    print("成功!")
    print(f"找到 {len(result)} 个相似汉字")
    for item in result[:3]:
        print(f"  {item['char']}: 相似度={item['overall_similarity']}, 声母={item['shengmu']}, 韵母={item['yunmu']}")
except Exception as e:
    print(f"失败: {e}")
