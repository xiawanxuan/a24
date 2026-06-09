import urllib.request
import urllib.parse
import json
import sys

def test_endpoint(name, url, method='GET', data=None):
    try:
        if method == 'POST' and data:
            req_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        else:
            req = urllib.request.Request(url)
        
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode('utf-8'))
        print(f"[OK] {name}")
        return result
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return None

def main():
    base = "http://localhost:8000"
    all_passed = True

    print("=" * 50)
    print("Testing Guangyun Phonology API")
    print("=" * 50)
    print()

    # 1. 健康检查
    r = test_endpoint("健康检查", f"{base}/health")
    if r is None: all_passed = False
    print()

    # 2. 根路径
    r = test_endpoint("根路径", f"{base}/")
    if r is None: all_passed = False
    print()

    # 3. 汉字查询
    char = urllib.parse.quote("东")
    r = test_endpoint("汉字查询 (东)", f"{base}/api/v1/chars/{char}")
    if r:
        print(f"  反切: {r[0]['fanqie']}, 声母: {r[0]['shengmu']}, 韵母: {r[0]['yunmu']}, 声调: {r[0]['shengdiao']}")
    else:
        all_passed = False
    print()

    # 4. 多条件搜索
    shengmu = urllib.parse.quote("见")
    r = test_endpoint("多条件搜索 (声母=见)", f"{base}/api/v1/chars/search?shengmu={shengmu}&limit=5")
    if r:
        print(f"  找到 {len(r)} 个汉字")
        for c in r[:3]:
            print(f"    {c['char']}: {c['shengmu']}母 + {c['yunmu']}韵")
    else:
        all_passed = False
    print()

    # 5. 声母列表
    r = test_endpoint("声母列表", f"{base}/api/v1/shengmu/list")
    if r:
        print(f"  共 {len(r)} 个声母: {', '.join(r[:5])}...")
    else:
        all_passed = False
    print()

    # 6. 韵母列表
    r = test_endpoint("韵母列表", f"{base}/api/v1/yunmu/list")
    if r:
        print(f"  共 {len(r)} 个韵母: {', '.join(r[:5])}...")
    else:
        all_passed = False
    print()

    # 7. 韵摄列表
    r = test_endpoint("韵摄列表", f"{base}/api/v1/she/list")
    if r:
        print(f"  共 {len(r)} 个韵摄: {', '.join(r)}")
    else:
        all_passed = False
    print()

    # 8. 反切推导
    r = test_endpoint("反切推导 (德红切)", 
        f"{base}/api/v1/fanqie/derive", 
        method='POST', 
        data={"upper_char": "德", "lower_char": "红"})
    if r:
        print(f"  上字声母选项: {r['upper_shengmu_options']}")
        print(f"  下字韵母选项: {r['lower_yunmu_options']}")
        print(f"  推导结果数: {len(r['derivations'])}")
        if r['derivations']:
            d = r['derivations'][0]
            print(f"  组合读音: {d['combined_pronunciation']}")
    else:
        all_passed = False
    print()

    # 9. 音韵相似度
    r = test_endpoint("音韵相似度 (东 vs 红)",
        f"{base}/api/v1/similarity",
        method='POST',
        data={"char1": "东", "char2": "红"})
    if r:
        print(f"  声母相似度: {r['shengmu_similarity']}")
        print(f"  韵母相似度: {r['yunmu_similarity']}")
        print(f"  声调相似度: {r['shengdiao_similarity']}")
        print(f"  总体相似度: {r['overall_similarity']}")
    else:
        all_passed = False
    print()

    # 10. 查找相似汉字
    char = urllib.parse.quote("东")
    r = test_endpoint("查找相似汉字 (东)",
        f"{base}/api/v1/similarity/find/{char}?threshold=0.3&limit=5")
    if r:
        print(f"  找到 {len(r)} 个相似汉字")
        for item in r[:3]:
            print(f"    {item['char']}: 相似度={item['overall_similarity']}")
    else:
        all_passed = False
    print()

    # 11. Swagger 文档
    r = test_endpoint("Swagger 文档", f"{base}/docs")
    if r is None: all_passed = False
    print()

    # 12. OpenAPI JSON
    r = test_endpoint("OpenAPI JSON", f"{base}/openapi.json")
    if r:
        print(f"  API 路径数: {len(r.get('paths', {}))}")
    else:
        all_passed = False
    print()

    print("=" * 50)
    if all_passed:
        print("All tests PASSED!")
    else:
        print("Some tests FAILED!")
    print("=" * 50)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
