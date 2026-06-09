from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app import schemas, crud
from app.services.phonology_service import PhonologyService
from app.services.similarity_service import SimilarityService
from app.services.rhyme_chart_service import RhymeChartService

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


@router.post("/rhyme-chart", response_model=schemas.RhymeChartResponse, summary="构建等韵图（JSON格式）")
def build_rhyme_chart(
    request: schemas.RhymeChartRequest,
    db: Session = Depends(get_db)
):
    """
    给定汉字序列，自动在等韵图中标出每个字的位置，返回 JSON 格式的韵图数据。
    
    - **char_list**: 汉字列表
    - **she_filter**: 可选，只显示某一摄
    - **hu_filter**: 可选，只显示开口或合口
    - **shengdiao_filter**: 可选，只显示某一声调
    - **group_by**: 分组方式：she（按韵摄）或 shengdiao（按声调）
    """
    service = RhymeChartService(db)
    result = service.build_rhyme_chart(
        char_list=request.char_list,
        she_filter=request.she_filter,
        hu_filter=request.hu_filter,
        shengdiao_filter=request.shengdiao_filter,
        group_by=request.group_by
    )
    if not result["charts"]:
        raise HTTPException(status_code=404, detail="未找到可用于构建韵图的汉字数据")
    return result


@router.post("/rhyme-chart/svg", summary="生成等韵图 SVG 图像")
def generate_rhyme_chart_svg(
    request: schemas.RhymeChartRequest,
    db: Session = Depends(get_db)
):
    """
    给定汉字序列，生成 SVG 格式的等韵图图像。
    
    - **char_list**: 汉字列表
    - **she_filter**: 可选，只显示某一摄
    - **hu_filter**: 可选，只显示开口或合口
    - **shengdiao_filter**: 可选，只显示某一声调
    - **group_by**: 分组方式：she（按韵摄）或 shengdiao（按声调）
    """
    service = RhymeChartService(db)
    svg = service.generate_svg(
        char_list=request.char_list,
        she_filter=request.she_filter,
        hu_filter=request.hu_filter,
        shengdiao_filter=request.shengdiao_filter,
    )
    if not svg:
        raise HTTPException(status_code=404, detail="无法生成韵图 SVG")
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/rhyme-chart/she/list", response_model=List[str], summary="获取所有可用韵摄列表")
def get_available_she_list(db: Session = Depends(get_db)):
    """
    获取数据库中所有可用的韵摄列表。
    """
    service = RhymeChartService(db)
    return service.get_available_she_list()


@router.get("/rhyme-chart/she/{she}/svg", summary="获取指定韵摄的等韵图 SVG")
def get_she_rhyme_chart_svg(
    she: str,
    width: int = Query(1000, ge=500, le=3000, description="SVG 宽度"),
    db: Session = Depends(get_db)
):
    """
    获取指定韵摄下所有汉字的等韵图 SVG 图像。
    
    - **she**: 韵摄名称（如通、江、止、遇等）
    - **width**: 图像宽度
    """
    service = RhymeChartService(db)
    svg = service.generate_single_she_svg(she, width=width)
    if not svg:
        raise HTTPException(status_code=404, detail=f"未找到韵摄 '{she}' 的数据")
    return Response(content=svg, media_type="image/svg+xml")


@router.get("/rhyme-chart/she/{she}", summary="获取指定韵摄的完整等韵图（JSON）")
def get_she_rhyme_chart(
    she: str,
    db: Session = Depends(get_db)
):
    """
    获取指定韵摄下所有汉字的等韵图。
    
    - **she**: 韵摄名称（如通、江、止、遇等）
    """
    service = RhymeChartService(db)
    all_chars = crud.search_chars(db, she=she, limit=500)
    if not all_chars:
        raise HTTPException(status_code=404, detail=f"未找到韵摄 '{she}' 的数据")
    char_list = [c.char for c in all_chars]
    result = service.build_rhyme_chart(char_list, she_filter=she)
    if not result["charts"]:
        raise HTTPException(status_code=404, detail=f"未找到韵摄 '{she}' 的数据")
    return result
