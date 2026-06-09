import urllib.request
import urllib.parse
import json


def test_char_query():
    print("=== 测试：汉字查询 (东) ===")
    char = urllib.parse.quote("东")
    url = f"http://localhost:8000/api/v1/chars/{char}"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print()


def test_shengmu_list():
    print("=== 测试：声母列表 ===")
    url = "http://localhost:8000/api/v1/shengmu/list"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(data)
    print()


def test_yunmu_list():
    print("=== 测试：韵母列表 ===")
    url = "http://localhost:8000/api/v1/yunmu/list"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(data)
    print()


def test_she_list():
    print("=== 测试：韵摄列表 ===")
    url = "http://localhost:8000/api/v1/she/list"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(data)
    print()


def test_fanqie_derive():
    print("=== 测试：反切推导 (德红切) ===")
    url = "http://localhost:8000/api/v1/fanqie/derive"
    req_data = json.dumps({"upper_char": "德", "lower_char": "红"}).encode()
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode())
    print("上字声母选项:", data["upper_shengmu_options"])
    print("下字韵母选项:", data["lower_yunmu_options"])
    print("下字声调选项:", data["lower_shengdiao_options"])
    print("推导结果数:", len(data["derivations"]))
    if data["derivations"]:
        d = data["derivations"][0]
        print("组合读音:", d["combined_pronunciation"])
        print("匹配字数:", len(d["possible_chars"]))
    print()


def test_similarity():
    print("=== 测试：音韵相似度 (东 vs 红) ===")
    url = "http://localhost:8000/api/v1/similarity"
    req_data = json.dumps({"char1": "东", "char2": "红"}).encode()
    req = urllib.request.Request(url, data=req_data, headers={"Content-Type": "application/json"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read().decode())
    print("声母相似度:", data["shengmu_similarity"])
    print("韵母相似度:", data["yunmu_similarity"])
    print("声调相似度:", data["shengdiao_similarity"])
    print("总体相似度:", data["overall_similarity"])
    print()


def test_find_similar():
    print("=== 测试：查找相似汉字 (东) ===")
    char = urllib.parse.quote("东")
    url = f"http://localhost:8000/api/v1/similarity/find/{char}?threshold=0.3&limit=10"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(f"找到 {len(data)} 个相似汉字：")
    for item in data[:5]:
        print(f"  {item['char']}: 相似度={item['overall_similarity']}, "
              f"声母={item['shengmu']}, 韵母={item['yunmu']}, 声调={item['shengdiao']}")
    print()


def test_search():
    print("=== 测试：多条件搜索 (声母=见) ===")
    shengmu = urllib.parse.quote("见")
    url = f"http://localhost:8000/api/v1/chars/search?shengmu={shengmu}&limit=10"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(f"找到 {len(data)} 个汉字：")
    for item in data[:5]:
        print(f"  {item['char']}: {item['shengmu']}母 + {item['yunmu']}韵 + {item['shengdiao']}声")
    print()


def test_health():
    print("=== 测试：健康检查 ===")
    url = "http://localhost:8000/health"
    resp = urllib.request.urlopen(url)
    data = json.loads(resp.read().decode())
    print(data)
    print()


if __name__ == "__main__":
    try:
        test_health()
        test_char_query()
        test_shengmu_list()
        test_yunmu_list()
        test_she_list()
        test_search()
        test_fanqie_derive()
        test_similarity()
        test_find_similar()
        print("✓ 所有测试通过！")
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
