from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas
from app.services.phonology_service import PhonologyService
from app.services.similarity_service import SimilarityService

router = APIRouter(prefix="/api/v1", tags=["guangyun"])


@router.get("/chars/search", response_model=List[schemas.GuangyunCharRead], summary="多条件搜索汉字音韵信息")
def search_chars(
    char: Optional[str] = Query(None, description="汉字"),
    shengmu: Optional[str] = Query(None, description="声母"),
    yunmu: Optional[str] = Query(None, description="韵母"),
    shengdiao: Optional[str] = Query(None, description="声调"),
    she: Optional[str] = Query(None, description="韵摄"),
    deng: Optional[int] = Query(None, description="等（一二三四等）"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=500, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    多条件组合搜索《广韵》汉字的音韵信息。
    """
    service = PhonologyService(db)
    results = service.search_chars(
        char=char,
        shengmu=shengmu,
        yunmu=yunmu,
        shengdiao=shengdiao,
        she=she,
        deng=deng,
        skip=skip,
        limit=limit
    )
    return results


@router.get("/chars/{char}", response_model=List[schemas.GuangyunCharRead], summary="按汉字查询《广韵》音韵信息")
def get_char(char: str, db: Session = Depends(get_db)):
    """
    按汉字查询《广韵》中的音韵信息，包括反切、声母、韵母、声调、韵图位置等。

    - **char**: 要查询的汉字
    """
    service = PhonologyService(db)
    results = service.get_char_info(char)
    if not results:
        raise HTTPException(status_code=404, detail=f"未找到汉字 '{char}' 的音韵信息")
    return results


@router.post("/fanqie/derive", summary="反切推导：根据反切上字和下字推导可能的读音组合")
def derive_fanqie(
    request: schemas.FanqieDerivationRequest,
    db: Session = Depends(get_db)
):
    """
    根据反切上字和反切下字推导可能的读音组合。

    反切原理：上字取声，下字取韵和调。

    - **upper_char**: 反切上字
    - **lower_char**: 反切下字
    """
    service = PhonologyService(db)
    result = service.derive_fanqie(request.upper_char, request.lower_char)
    if not result:
        raise HTTPException(status_code=404, detail="无法根据给定的反切上下字推导读音")
    return result


@router.get("/fanqie/upper/{upper_char}", response_model=List[schemas.GuangyunCharRead], summary="查询以某字为反切上字的所有字")
def get_by_fanqie_upper(
    upper_char: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = PhonologyService(db)
    results = service.get_chars_by_fanqie_upper(upper_char, skip, limit)
    return results


@router.get("/fanqie/lower/{lower_char}", response_model=List[schemas.GuangyunCharRead], summary="查询以某字为反切下字的所有字")
def get_by_fanqie_lower(
    lower_char: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = PhonologyService(db)
    results = service.get_chars_by_fanqie_lower(lower_char, skip, limit)
    return results


@router.get("/shengmu/list", response_model=List[str], summary="获取所有声母列表")
def get_shengmu_list(db: Session = Depends(get_db)):
    service = PhonologyService(db)
    return service.get_shengmu_list()


@router.get("/yunmu/list", response_model=List[str], summary="获取所有韵母列表")
def get_yunmu_list(db: Session = Depends(get_db)):
    service = PhonologyService(db)
    return service.get_yunmu_list()


@router.get("/she/list", response_model=List[str], summary="获取所有韵摄列表")
def get_she_list(db: Session = Depends(get_db)):
    service = PhonologyService(db)
    return service.get_she_list()


@router.get("/shengmu/{shengmu}", response_model=List[schemas.GuangyunCharRead], summary="按声母查询汉字")
def get_chars_by_shengmu(
    shengmu: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = PhonologyService(db)
    results = service.get_chars_by_shengmu(shengmu, skip, limit)
    if not results:
        raise HTTPException(status_code=404, detail=f"未找到声母为 '{shengmu}' 的汉字")
    return results


@router.get("/yunmu/{yunmu}", response_model=List[schemas.GuangyunCharRead], summary="按韵母查询汉字")
def get_chars_by_yunmu(
    yunmu: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    service = PhonologyService(db)
    results = service.get_chars_by_yunmu(yunmu, skip, limit)
    if not results:
        raise HTTPException(status_code=404, detail=f"未找到韵母为 '{yunmu}' 的汉字")
    return results


@router.post("/similarity", summary="计算两个汉字的音韵相似度")
def get_phonetic_similarity(
    request: schemas.PhoneticSimilarityRequest,
    db: Session = Depends(get_db)
):
    """
    计算两个汉字的音韵相似度，基于韵图位置（声母、韵母、声调、等、呼、摄等维度）。

    - **char1**: 第一个汉字
    - **char2**: 第二个汉字
    """
    service = SimilarityService(db)
    result = service.get_phonetic_similarity(request.char1, request.char2)
    if not result:
        raise HTTPException(status_code=404, detail="无法获取汉字的音韵信息进行相似度计算")
    return result


@router.get("/similarity/find/{char}", summary="查找与给定汉字音韵相似的其他汉字")
def find_similar_chars(
    char: str,
    threshold: float = Query(0.5, ge=0, le=1, description="相似度阈值"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: Session = Depends(get_db)
):
    """
    查找与给定汉字音韵相似的其他汉字，按相似度从高到低排序。

    - **char**: 目标汉字
    - **threshold**: 最小相似度阈值（0-1）
    - **limit**: 返回结果数量限制
    """
    service = SimilarityService(db)
    results = service.find_similar_chars(char, threshold, limit)
    if results is None:
        raise HTTPException(status_code=404, detail=f"未找到汉字 '{char}' 的音韵信息")
    return results
