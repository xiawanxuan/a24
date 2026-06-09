from pydantic import BaseModel, Field
from typing import List, Optional


class GuangyunCharBase(BaseModel):
    char: str
    fanqie: Optional[str] = None
    fanqie_upper: Optional[str] = None
    fanqie_lower: Optional[str] = None
    shengmu: Optional[str] = None
    yunmu: Optional[str] = None
    shengdiao: Optional[str] = None
    deng: Optional[int] = None
    hu: Optional[str] = None
    she: Optional[str] = None
    yunshu: Optional[str] = None
    diao_leibie: Optional[str] = None
    yun_tu_number: Optional[int] = None
    note: Optional[str] = None


class GuangyunCharCreate(GuangyunCharBase):
    shengmu_order: Optional[int] = None
    yunmu_order: Optional[int] = None


class GuangyunCharRead(GuangyunCharBase):
    id: int
    shengmu_order: Optional[int] = None
    yunmu_order: Optional[int] = None

    class Config:
        from_attributes = True


class FanqieDerivationRequest(BaseModel):
    upper_char: str = Field(..., description="反切上字")
    lower_char: str = Field(..., description="反切下字")


class FanqieDerivationResult(BaseModel):
    upper_shengmu: str
    lower_yunmu: str
    lower_shengdiao: str
    combined_pronunciation: str
    possible_chars: List[GuangyunCharRead]


class PhoneticSimilarityRequest(BaseModel):
    char1: str = Field(..., description="第一个汉字")
    char2: str = Field(..., description="第二个汉字")


class PhoneticSimilarityResult(BaseModel):
    char1_info: GuangyunCharRead
    char2_info: GuangyunCharRead
    shengmu_similarity: float
    yunmu_similarity: float
    shengdiao_similarity: float
    overall_similarity: float
    details: dict


class RhymeChartCell(BaseModel):
    char: str
    fanqie: Optional[str] = None
    yunmu: Optional[str] = None


class RhymeChartGrid(BaseModel):
    pass


class RhymeChart(BaseModel):
    shengmu_list: List[str]
    deng_list: List[int]
    hu_list: List[str]
    shengdiao_list: List[str]
    categories: Dict[str, List[str]]
    grid: Dict[str, Dict[str, Dict[str, Dict[str, List[RhymeChartCell]]]]]


class RhymeChartRequest(BaseModel):
    char_list: List[str] = Field(..., description="汉字序列")
    she_filter: Optional[str] = Field(None, description="韵摄筛选")
    hu_filter: Optional[str] = Field(None, description="开合筛选")
    shengdiao_filter: Optional[str] = Field(None, description="声调筛选")
    group_by: Optional[str] = Field("she", description="分组方式：she(韵摄) 或 shengdiao(声调)")


class RhymeChartResponse(BaseModel):
    total_chars: int
    unique_chars: int
    group_by: str
    charts: Dict[str, RhymeChart]
