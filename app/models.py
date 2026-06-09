from sqlalchemy import Column, Integer, String, Float, Index

from app.database import Base


class GuangyunChar(Base):
    __tablename__ = "guangyun_chars"

    id = Column(Integer, primary_key=True, index=True)
    char = Column(String(1), nullable=False, index=True)
    fanqie = Column(String(2), index=True)
    fanqie_upper = Column(String(1), index=True)
    fanqie_lower = Column(String(1), index=True)
    shengmu = Column(String(4), index=True)
    yunmu = Column(String(8), index=True)
    shengdiao = Column(String(4), index=True)
    deng = Column(Integer, index=True)
    hu = Column(String(4), index=True)
    she = Column(String(4), index=True)
    yunshu = Column(String(8), index=True)
    diao_leibie = Column(String(4), index=True)
    yun_tu_number = Column(Integer, index=True)
    shengmu_order = Column(Integer)
    yunmu_order = Column(Integer)
    note = Column(String(255), nullable=True)

    __table_args__ = (
        Index('idx_char_shengmu', 'char', 'shengmu'),
        Index('idx_fanqie_upper_lower', 'fanqie_upper', 'fanqie_lower'),
    )
