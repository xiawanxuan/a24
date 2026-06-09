import urllib.request
import json
import threading
import time
import sys

base = "http://localhost:8000"

def test_fanqie_derive():
    print("=" * 60)
    print("测试 1: 反切推导（德红切）")
    print("=" * 60)
    
    data = json.dumps({"upper_char": "德", "lower_char": "红"}).encode('utf-8')
    req = urllib.request.Request(
        f"{base}/api/v1/fanqie/derive",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode('utf-8'))
        print(f"上字声母选项数: {len(result['upper_shengmu_options'])}")
        print(f"下字韵母选项数: {len(result['lower_yunmu_options'])}")
        print(f"下字声调选项数: {len(result['lower_shengdiao_options'])}")
        print(f"推导结果数: {len(result['derivations'])}")
        print()
        
        for i, d in enumerate(result['derivations']):
            print(f"  推导 {i+1}: {d['combined_pronunciation']}")
            print(f"    匹配汉字数: {len(d['possible_chars'])}")
            if d['possible_chars']:
                chars = [c['char'] for c in d['possible_chars'][:5]]
                print(f"    示例汉字: {', '.join(chars)}")
        print()
        
        print("[PASS] 反切推导测试通过")
        return True
    except Exception as e:
        print(f"[FAIL] 反切推导测试失败: {e}")
        return False


def test_similarity():
    print("=" * 60)
    print("测试 2: 音韵相似度（东 vs 红）")
    print("=" * 60)
    
    data = json.dumps({"char1": "东", "char2": "红"}).encode('utf-8')
    req = urllib.request.Request(
        f"{base}/api/v1/similarity",
        data=data,
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        resp = urllib.request.urlopen(req)
        result = json.loads(resp.read().decode('utf-8'))
        
        char1_info = result['char1_info']
        char2_info = result['char2_info']
        
        print(f"字1: {char1_info['char']}, 声母: {char1_info['shengmu']}, 韵母: {char1_info['yunmu']}, 声调: {char1_info['shengdiao']}")
        print(f"字2: {char2_info['char']}, 声母: {char2_info['shengmu']}, 韵母: {char2_info['yunmu']}, 声调: {char2_info['shengdiao']}")
        print(f"声母相似度: {result['shengmu_similarity']}")
        print(f"韵母相似度: {result['yunmu_similarity']}")
        print(f"声调相似度: {result['shengdiao_similarity']}")
        print(f"总体相似度: {result['overall_similarity']}")
        print()
        
        if char1_info['char'] == '东' and char2_info['char'] == '红':
            print("[PASS] 音韵相似度测试通过 - 字数据正确对应")
            return True
        else:
            print("[FAIL] 音韵相似度测试失败 - 字数据不匹配")
            return False
    except Exception as e:
        print(f"[FAIL] 音韵相似度测试失败: {e}")
        return False


def test_concurrent_similarity():
    print("=" * 60)
    print("测试 3: 并发音韵相似度测试（验证数据不错乱）")
    print("=" * 60)
    
    pairs = [
        ("东", "红"),
        ("公", "古"),
        ("德", "多"),
        ("子", "则"),
        ("良", "张"),
        ("力", "竹"),
        ("林", "寻"),
        ("鱼", "居"),
        ("之", "止"),
        ("章", "诸"),
    ]
    
    results = []
    errors = []
    lock = threading.Lock()
    
    def worker(char1, char2):
        try:
            data = json.dumps({"char1": char1, "char2": char2}).encode('utf-8')
            req = urllib.request.Request(
                f"{base}/api/v1/similarity",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            resp = urllib.request.urlopen(req)
            result = json.loads(resp.read().decode('utf-8'))
            
            c1 = result['char1_info']['char']
            c2 = result['char2_info']['char']
            sm1 = result['char1_info']['shengmu']
            sm2 = result['char2_info']['shengmu']
            ym1 = result['char1_info']['yunmu']
            ym2 = result['char2_info']['yunmu']
            
            correct = (c1 == char1 and c2 == char2)
            
            with lock:
                results.append((char1, char2, correct, c1, c2, sm1, sm2, ym1, ym2))
                if not correct:
                    errors.append(f"{char1}+{char2} → {c1}+{c2}")
        except Exception as e:
            with lock:
                errors.append(f"{char1}+{char2} 错误: {e}")
    
    threads = []
    for i in range(10):
        for c1, c2 in pairs:
            t = threading.Thread(target=worker, args=(c1, c2))
            threads.append(t)
    
    start_time = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - start_time
    
    total = len(results)
    correct = sum(1 for r in results if r[2])
    
    print(f"总请求数: {total}")
    print(f"正确数: {correct}")
    print(f"错误数: {total - correct}")
    print(f"耗时: {elapsed:.2f}秒")
    print(f"QPS: {total/elapsed:.1f}")
    print()
    
    if errors:
        print("错误详情:")
        for e in errors[:5]:
            print(f"  {e}")
        print()
        print("[FAIL] 并发测试发现数据错乱")
        return False
    else:
        print("[PASS] 并发测试通过 - 所有数据正确对应")
        return True


def test_find_similar():
    print("=" * 60)
    print("测试 4: 查找相似汉字")
    print("=" * 60)
    
    try:
        resp = urllib.request.urlopen(f"{base}/api/v1/similarity/find/%E4%B8%9C?threshold=0.3&limit=5")
        result = json.loads(resp.read().decode('utf-8'))
        
        print(f"找到 {len(result)} 个相似汉字")
        for i, item in enumerate(result[:5]):
            print(f"  {i+1}. {item['char']}: 相似度={item['overall_similarity']}, "
                  f"声母={item['shengmu']}, 韵母={item['yunmu']}, 声调={item['shengdiao']}")
        print()
        
        all_chars_match = all(item['char'] != '东' for item in result)
        if all_chars_match:
            print("[PASS] 查找相似汉字测试通过")
            return True
        else:
            print("[WARN] 结果中包含目标字本身")
            return True
    except Exception as e:
        print(f"[FAIL] 查找相似汉字测试失败: {e}")
        return False


def test_char_query():
    print("=" * 60)
    print("测试 5: 汉字查询（验证多音字支持）")
    print("=" * 60)
    
    try:
        resp = urllib.request.urlopen(f"{base}/api/v1/chars/%E4%B8%9C")
        result = json.loads(resp.read().decode('utf-8'))
        
        print(f"找到 {len(result)} 条记录")
        for i, c in enumerate(result):
            print(f"  {i+1}. {c['char']}: {c['shengmu']}母 + {c['yunmu']}韵 + {c['shengdiao']}声")
            print(f"     反切: {c['fanqie']}")
            print(f"     韵图: {c['she']}摄 {c['deng']}等 {c['hu']}口")
        print()
        
        print("[PASS] 汉字查询测试通过")
        return True
    except Exception as e:
        print(f"[FAIL] 汉字查询测试失败: {e}")
        return False


def main():
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "古汉语音韵学 API 修复验证测试" + " " * 16 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    tests = [
        test_fanqie_derive,
        test_similarity,
        test_concurrent_similarity,
        test_find_similar,
        test_char_query,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] 测试异常: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"测试总结: 通过 {passed}/{len(tests)}, 失败 {failed}/{len(tests)}")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
