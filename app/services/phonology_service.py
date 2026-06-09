from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from app import crud, schemas, models
from data.sample_data import get_shengmu_order, get_yunmu_order


class PhonologyService:
    def __init__(self, db: Session):
        self.db = db
        self.shengmu_order = get_shengmu_order()
        self.yunmu_order = get_yunmu_order()

    def get_char_info(self, char: str) -> List[models.GuangyunChar]:
        return crud.get_chars_by_char(self.db, char)

    def search_chars(
        self,
        char: Optional[str] = None,
        shengmu: Optional[str] = None,
        yunmu: Optional[str] = None,
        shengdiao: Optional[str] = None,
        she: Optional[str] = None,
        deng: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[models.GuangyunChar]:
        return crud.search_chars(
            self.db,
            char=char,
            shengmu=shengmu,
            yunmu=yunmu,
            shengdiao=shengdiao,
            she=she,
            deng=deng,
            skip=skip,
            limit=limit
        )

    def derive_fanqie(self, upper_char: str, lower_char: str) -> Optional[dict]:
        upper_chars = crud.get_chars_by_char(self.db, upper_char)
        lower_chars = crud.get_chars_by_char(self.db, lower_char)

        if not upper_chars or not lower_chars:
            return None

        upper_shengmu_list = list(set(c.shengmu for c in upper_chars if c.shengmu))
        lower_yunmu_list = list(set(c.yunmu for c in lower_chars if c.yunmu))
        lower_shengdiao_list = list(set(c.shengdiao for c in lower_chars if c.shengdiao))

        lower_pronunciations = list(set(
            (c.yunmu, c.shengdiao)
            for c in lower_chars
            if c.yunmu and c.shengdiao
        ))

        if not upper_shengmu_list or not lower_pronunciations:
            return None

        results = []
        for usm in upper_shengmu_list:
            for lym, lsd in lower_pronunciations:
                possible_chars = crud.search_chars(
                    self.db,
                    shengmu=usm,
                    yunmu=lym,
                    shengdiao=lsd,
                    limit=50
                )
                combined = f"{usm}母 + {lym}韵 + {lsd}声"
                results.append({
                    "upper_shengmu": usm,
                    "lower_yunmu": lym,
                    "lower_shengdiao": lsd,
                    "combined_pronunciation": combined,
                    "possible_chars": [
                        schemas.GuangyunCharRead.model_validate(c)
                        for c in possible_chars
                    ]
                })

        return {
            "upper_char": upper_char,
            "lower_char": lower_char,
            "derivations": results,
            "upper_shengmu_options": upper_shengmu_list,
            "lower_yunmu_options": lower_yunmu_list,
            "lower_shengdiao_options": lower_shengdiao_list
        }

    def get_shengmu_list(self) -> List[str]:
        all_shengmu = crud.get_all_shengmu(self.db)
        return sorted(
            all_shengmu,
            key=lambda x: self.shengmu_order.get(x, 99)
        )

    def get_yunmu_list(self) -> List[str]:
        all_yunmu = crud.get_all_yunmu(self.db)
        return sorted(
            all_yunmu,
            key=lambda x: self.yunmu_order.get(x, 99)
        )

    def get_she_list(self) -> List[str]:
        return crud.get_all_she(self.db)

    def get_chars_by_shengmu(self, shengmu: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
        return crud.get_chars_by_shengmu(self.db, shengmu, skip, limit)

    def get_chars_by_yunmu(self, yunmu: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
        return crud.get_chars_by_yunmu(self.db, yunmu, skip, limit)

    def get_chars_by_fanqie_upper(self, upper_char: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
        return crud.get_chars_by_fanqie_upper(self.db, upper_char, skip, limit)

    def get_chars_by_fanqie_lower(self, lower_char: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
        return crud.get_chars_by_fanqie_lower(self.db, lower_char, skip, limit)
