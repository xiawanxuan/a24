from sqlalchemy.orm import Session
from typing import Optional, Tuple, Dict, Any
from app import crud, models, schemas
from data.sample_data import get_shengmu_order, get_yunmu_order


SHENGMU_CATEGORIES = {
    "帮": "唇音", "滂": "唇音", "并": "唇音", "明": "唇音",
    "非": "唇音", "敷": "唇音", "奉": "唇音", "微": "唇音",
    "端": "舌音", "透": "舌音", "定": "舌音", "泥": "舌音",
    "知": "舌音", "彻": "舌音", "澄": "舌音", "娘": "舌音",
    "精": "齿音", "清": "齿音", "从": "齿音", "心": "齿音", "邪": "齿音",
    "庄": "齿音", "初": "齿音", "崇": "齿音", "生": "齿音",
    "章": "齿音", "昌": "齿音", "船": "齿音", "书": "齿音", "禅": "齿音",
    "见": "牙音", "溪": "牙音", "群": "牙音", "疑": "牙音",
    "影": "喉音", "晓": "喉音", "匣": "喉音", "喻": "喉音",
    "来": "半舌", "日": "半齿",
}

SHENGMU_QINGZHUO = {
    "帮": "全清", "滂": "次清", "并": "全浊", "明": "次浊",
    "非": "全清", "敷": "次清", "奉": "全浊", "微": "次浊",
    "端": "全清", "透": "次清", "定": "全浊", "泥": "次浊",
    "知": "全清", "彻": "次清", "澄": "全浊", "娘": "次浊",
    "精": "全清", "清": "次清", "从": "全浊", "心": "全清", "邪": "全浊",
    "庄": "全清", "初": "次清", "崇": "全浊", "生": "全清",
    "章": "全清", "昌": "次清", "船": "全浊", "书": "全清", "禅": "全浊",
    "见": "全清", "溪": "次清", "群": "全浊", "疑": "次浊",
    "影": "全清", "晓": "全清", "匣": "全浊", "喻": "次浊",
    "来": "次浊", "日": "次浊",
}

SHE_DISTANCE = {
    "通": 1, "江": 2, "止": 3, "遇": 4, "蟹": 5, "臻": 6,
    "山": 7, "效": 8, "果": 9, "假": 10, "宕": 11, "曾": 12,
    "梗": 13, "流": 14, "深": 15, "咸": 16,
}

SHENGDIAO_ORDER = {"平": 1, "上": 2, "去": 3, "入": 4}


class SimilarityService:
    def __init__(self, db: Session):
        self.db = db
        self.shengmu_order = get_shengmu_order()
        self.yunmu_order = get_yunmu_order()

    def calculate_shengmu_similarity(self, sm1: str, sm2: str) -> Tuple[float, Dict[str, Any]]:
        if not sm1 or not sm2:
            return 0.0, {"reason": "缺少声母数据"}

        if sm1 == sm2:
            return 1.0, {"reason": "声母完全相同"}

        cat1 = SHENGMU_CATEGORIES.get(sm1, "未知")
        cat2 = SHENGMU_CATEGORIES.get(sm2, "未知")
        qz1 = SHENGMU_QINGZHUO.get(sm1, "未知")
        qz2 = SHENGMU_QINGZHUO.get(sm2, "未知")

        details = {
            "shengmu1": sm1,
            "shengmu2": sm2,
            "category1": cat1,
            "category2": cat2,
            "qingzhuo1": qz1,
            "qingzhuo2": qz2,
        }

        score = 0.0
        reasons = []

        if cat1 == cat2 and cat1 != "未知":
            score += 0.4
            reasons.append(f"同属{cat1}")
        elif cat1 != "未知" and cat2 != "未知":
            reasons.append(f"不同发音部位（{cat1} vs {cat2}）")

        if qz1 == qz2 and qz1 != "未知":
            score += 0.3
            reasons.append(f"同属{qz1}")
        elif qz1 != "未知" and qz2 != "未知":
            reasons.append(f"清浊不同（{qz1} vs {qz2}）")

        order1 = self.shengmu_order.get(sm1)
        order2 = self.shengmu_order.get(sm2)
        if order1 and order2:
            distance = abs(order1 - order2)
            proximity = max(0, 1 - distance / 38)
            score += 0.3 * proximity
            reasons.append(f"声母顺序距离: {distance}")

        details["reasons"] = reasons
        details["score_breakdown"] = {
            "same_category": 0.4 if cat1 == cat2 else 0,
            "same_qingzhuo": 0.3 if qz1 == qz2 else 0,
            "order_proximity": round(0.3 * (max(0, 1 - abs(order1 - order2) / 38)) if order1 and order2 else 0, 3)
        }

        return min(1.0, score), details

    def calculate_yunmu_similarity(self, c1: models.GuangyunChar, c2: models.GuangyunChar) -> Tuple[float, Dict[str, Any]]:
        details = {}
        score = 0.0
        reasons = []

        if c1.yunmu and c2.yunmu:
            if c1.yunmu == c2.yunmu:
                score += 0.3
                reasons.append("韵母完全相同")
            else:
                order1 = self.yunmu_order.get(c1.yunmu)
                order2 = self.yunmu_order.get(c2.yunmu)
                if order1 and order2:
                    distance = abs(order1 - order2)
                    proximity = max(0, 1 - distance / 61)
                    score += 0.15 * proximity
                    reasons.append(f"韵母顺序距离: {distance}")

        if c1.she and c2.she:
            if c1.she == c2.she:
                score += 0.3
                reasons.append(f"同属{c1.she}摄")
            else:
                d1 = SHE_DISTANCE.get(c1.she, 0)
                d2 = SHE_DISTANCE.get(c2.she, 0)
                if d1 and d2:
                    distance = abs(d1 - d2)
                    proximity = max(0, 1 - distance / 16)
                    score += 0.15 * proximity
                    reasons.append(f"韵摄距离: {distance}")

        if c1.deng and c2.deng:
            if c1.deng == c2.deng:
                score += 0.2
                reasons.append(f"同属{c1.deng}等")
            else:
                distance = abs(c1.deng - c2.deng)
                proximity = max(0, 1 - distance / 4)
                score += 0.1 * proximity
                reasons.append(f"等的距离: {distance}")

        if c1.hu and c2.hu:
            if c1.hu == c2.hu:
                score += 0.2
                reasons.append(f"同属{c1.hu}口呼")
            else:
                reasons.append(f"呼法不同（{c1.hu} vs {c2.hu}）")

        details["yunmu1"] = c1.yunmu
        details["yunmu2"] = c2.yunmu
        details["she1"] = c1.she
        details["she2"] = c2.she
        details["deng1"] = c1.deng
        details["deng2"] = c2.deng
        details["hu1"] = c1.hu
        details["hu2"] = c2.hu
        details["reasons"] = reasons

        return min(1.0, score), details

    def calculate_shengdiao_similarity(self, sd1: str, sd2: str) -> Tuple[float, Dict[str, Any]]:
        if not sd1 or not sd2:
            return 0.0, {"reason": "缺少声调数据"}

        if sd1 == sd2:
            return 1.0, {"reason": "声调完全相同"}

        o1 = SHENGDIAO_ORDER.get(sd1)
        o2 = SHENGDIAO_ORDER.get(sd2)

        if o1 and o2:
            distance = abs(o1 - o2)
            score = max(0, 1 - distance / 3)
            details = {
                "shengdiao1": sd1,
                "shengdiao2": sd2,
                "distance": distance,
                "reason": f"声调距离: {distance}"
            }
            return score, details

        return 0.0, {"reason": "声调数据无法比较"}

    def calculate_overall_similarity(
        self,
        shengmu_sim: float,
        yunmu_sim: float,
        shengdiao_sim: float
    ) -> float:
        return shengmu_sim * 0.35 + yunmu_sim * 0.45 + shengdiao_sim * 0.2

    def get_phonetic_similarity(self, char1: str, char2: str) -> Optional[dict]:
        chars1 = crud.get_chars_by_char(self.db, char1)
        chars2 = crud.get_chars_by_char(self.db, char2)

        if not chars1 or not chars2:
            return None

        best_result = None
        best_score = -1

        for c1 in chars1:
            for c2 in chars2:
                sm_sim, sm_details = self.calculate_shengmu_similarity(c1.shengmu, c2.shengmu)
                ym_sim, ym_details = self.calculate_yunmu_similarity(c1, c2)
                sd_sim, sd_details = self.calculate_shengdiao_similarity(c1.shengdiao, c2.shengdiao)
                overall = self.calculate_overall_similarity(sm_sim, ym_sim, sd_sim)

                if overall > best_score:
                    best_score = overall
                    best_result = {
                        "char1": char1,
                        "char2": char2,
                        "char1_info": schemas.GuangyunCharRead.model_validate(c1),
                        "char2_info": schemas.GuangyunCharRead.model_validate(c2),
                        "shengmu_similarity": round(sm_sim, 4),
                        "yunmu_similarity": round(ym_sim, 4),
                        "shengdiao_similarity": round(sd_sim, 4),
                        "overall_similarity": round(overall, 4),
                        "details": {
                            "shengmu_details": dict(sm_details),
                            "yunmu_details": dict(ym_details),
                            "shengdiao_details": dict(sd_details),
                            "weights": {
                                "shengmu_weight": 0.35,
                                "yunmu_weight": 0.45,
                                "shengdiao_weight": 0.2
                            }
                        }
                    }

        return best_result

    def find_similar_chars(
        self,
        target_char: str,
        threshold: float = 0.5,
        limit: int = 20
    ) -> Optional[list]:
        target_chars = crud.get_chars_by_char(self.db, target_char)
        if not target_chars:
            return None

        all_chars = crud.search_chars(self.db, limit=1000)

        results = []
        for target in target_chars:
            for other in all_chars:
                if other.char == target_char:
                    continue

                sm_sim, _ = self.calculate_shengmu_similarity(target.shengmu, other.shengmu)
                ym_sim, _ = self.calculate_yunmu_similarity(target, other)
                sd_sim, _ = self.calculate_shengdiao_similarity(target.shengdiao, other.shengdiao)
                overall = self.calculate_overall_similarity(sm_sim, ym_sim, sd_sim)

                if overall >= threshold:
                    results.append({
                        "char": other.char,
                        "overall_similarity": round(overall, 4),
                        "shengmu_similarity": round(sm_sim, 4),
                        "yunmu_similarity": round(ym_sim, 4),
                        "shengdiao_similarity": round(sd_sim, 4),
                        "shengmu": other.shengmu,
                        "yunmu": other.yunmu,
                        "shengdiao": other.shengdiao,
                        "she": other.she,
                        "deng": other.deng,
                        "hu": other.hu,
                    })

        results.sort(key=lambda x: x["overall_similarity"], reverse=True)
        return results[:limit]
