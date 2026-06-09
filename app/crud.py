from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas


def get_char_by_id(db: Session, char_id: int) -> Optional[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(models.GuangyunChar.id == char_id).first()


def get_chars_by_char(db: Session, char: str) -> List[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(models.GuangyunChar.char == char).all()


def get_chars_by_shengmu(db: Session, shengmu: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(
        models.GuangyunChar.shengmu == shengmu
    ).offset(skip).limit(limit).all()


def get_chars_by_yunmu(db: Session, yunmu: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(
        models.GuangyunChar.yunmu == yunmu
    ).offset(skip).limit(limit).all()


def get_chars_by_shengdiao(db: Session, shengdiao: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(
        models.GuangyunChar.shengdiao == shengdiao
    ).offset(skip).limit(limit).all()


def get_chars_by_fanqie_upper(db: Session, upper_char: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(
        models.GuangyunChar.fanqie_upper == upper_char
    ).offset(skip).limit(limit).all()


def get_chars_by_fanqie_lower(db: Session, lower_char: str, skip: int = 0, limit: int = 100) -> List[models.GuangyunChar]:
    return db.query(models.GuangyunChar).filter(
        models.GuangyunChar.fanqie_lower == lower_char
    ).offset(skip).limit(limit).all()


def get_chars_by_yun_tu_position(
    db: Session,
    deng: Optional[int] = None,
    hu: Optional[str] = None,
    she: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.GuangyunChar]:
    query = db.query(models.GuangyunChar)
    if deng is not None:
        query = query.filter(models.GuangyunChar.deng == deng)
    if hu:
        query = query.filter(models.GuangyunChar.hu == hu)
    if she:
        query = query.filter(models.GuangyunChar.she == she)
    return query.offset(skip).limit(limit).all()


def create_char(db: Session, char: schemas.GuangyunCharCreate) -> models.GuangyunChar:
    db_char = models.GuangyunChar(**char.model_dump())
    db.add(db_char)
    db.commit()
    db.refresh(db_char)
    return db_char


def create_chars_bulk(db: Session, chars: List[schemas.GuangyunCharCreate]) -> List[models.GuangyunChar]:
    db_chars = [models.GuangyunChar(**c.model_dump()) for c in chars]
    db.bulk_save_objects(db_chars)
    db.commit()
    return db_chars


def get_all_shengmu(db: Session) -> List[str]:
    results = db.query(models.GuangyunChar.shengmu).distinct().all()
    return [r[0] for r in results if r[0]]


def get_all_yunmu(db: Session) -> List[str]:
    results = db.query(models.GuangyunChar.yunmu).distinct().all()
    return [r[0] for r in results if r[0]]


def get_all_she(db: Session) -> List[str]:
    results = db.query(models.GuangyunChar.she).distinct().all()
    return [r[0] for r in results if r[0]]


def search_chars(
    db: Session,
    char: Optional[str] = None,
    shengmu: Optional[str] = None,
    yunmu: Optional[str] = None,
    shengdiao: Optional[str] = None,
    she: Optional[str] = None,
    deng: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.GuangyunChar]:
    query = db.query(models.GuangyunChar)
    if char:
        query = query.filter(models.GuangyunChar.char == char)
    if shengmu:
        query = query.filter(models.GuangyunChar.shengmu == shengmu)
    if yunmu:
        query = query.filter(models.GuangyunChar.yunmu == yunmu)
    if shengdiao:
        query = query.filter(models.GuangyunChar.shengdiao == shengdiao)
    if she:
        query = query.filter(models.GuangyunChar.she == she)
    if deng is not None:
        query = query.filter(models.GuangyunChar.deng == deng)
    return query.offset(skip).limit(limit).all()
