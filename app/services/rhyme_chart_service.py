from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Tuple, Any
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

CATEGORY_ORDER = {
    "唇音": 1,
    "舌音": 2,
    "齿音": 3,
    "牙音": 4,
    "喉音": 5,
    "半舌": 6,
    "半齿": 7,
}

DENG_LIST = [1, 2, 3, 4]
SHENGDIAO_LIST = ["平", "上", "去", "入"]
HU_LIST = ["开", "合"]

SHE_ORDER = {
    "通": 1, "江": 2, "止": 3, "遇": 4,
    "蟹": 5, "臻": 6, "山": 7, "效": 8,
    "果": 9, "假": 10, "宕": 11, "曾": 12,
    "梗": 13, "流": 14, "深": 15, "咸": 16,
}


class RhymeChartService:
    def __init__(self, db: Session):
        self.db = db
        self.shengmu_order = get_shengmu_order()
        self.yunmu_order = get_yunmu_order()

    def get_chars_by_list(self, char_list: List[str]) -> List[models.GuangyunChar]:
        chars = []
        for ch in char_list:
            results = crud.get_chars_by_char(self.db, ch)
            if results:
                chars.extend(results)
        return chars

    def build_rhyme_chart(
        self,
        char_list: List[str],
        she_filter: Optional[str] = None,
        hu_filter: Optional[str] = None,
        shengdiao_filter: Optional[str] = None,
        group_by: str = "she"
    ) -> Dict[str, Any]:
        chars = self.get_chars_by_list(char_list)

        if she_filter:
            chars = [c for c in chars if c.she == she_filter]
        if hu_filter:
            chars = [c for c in chars if c.hu == hu_filter]
        if shengdiao_filter:
            chars = [c for c in chars if c.shengdiao == shengdiao_filter]

        charts = {}

        if group_by == "she":
            she_list = sorted(set(c.she for c in chars if c.she),
                              key=lambda x: SHE_ORDER.get(x, 99))
            for she in she_list:
                she_chars = [c for c in chars if c.she == she]
                charts[she] = self._build_single_chart(she_chars)
        elif group_by == "shengdiao":
            for shengdiao in SHENGDIAO_LIST:
                sd_chars = [c for c in chars if c.shengdiao == shengdiao]
                if sd_chars:
                    charts[shengdiao] = self._build_single_chart(sd_chars)

        return {
            "total_chars": len(chars),
            "unique_chars": len(set(c.char for c in chars)),
            "group_by": group_by,
            "charts": charts,
        }

    def _build_single_chart(self, chars: List[models.GuangyunChar]) -> Dict[str, Any]:
        shengmu_set = set(c.shengmu for c in chars if c.shengmu)
        shengmu_list = sorted(shengmu_set, key=lambda x: self.shengmu_order.get(x, 99))

        deng_list = sorted(set(c.deng for c in chars if c.deng))

        hu_set = set(c.hu for c in chars if c.hu)

        shengdiao_set = set(c.shengdiao for c in chars if c.shengdiao)

        grid = {}
        for sm in shengmu_list:
            grid[sm] = {}
            for deng in deng_list:
                grid[sm][deng] = {}
                for hu in hu_set:
                    grid[sm][deng][hu] = {}
                    for sd in SHENGDIAO_LIST:
                        grid[sm][deng][hu][sd] = []

        for c in chars:
            if c.shengmu and c.deng and c.hu and c.shengdiao:
                if c.shengmu in grid and c.deng in grid[c.shengmu]:
                    if c.hu in grid[c.shengmu][c.deng]:
                        grid[c.shengmu][c.deng][c.hu][c.shengdiao].append({
                            "char": c.char,
                            "fanqie": c.fanqie,
                            "yunmu": c.yunmu,
                        })

        categories = {}
        for sm in shengmu_list:
            cat = SHENGMU_CATEGORIES.get(sm, "其他")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(sm)

        sorted_categories = sorted(categories.keys(), key=lambda x: CATEGORY_ORDER.get(x, 99))

        return {
            "shengmu_list": shengmu_list,
            "deng_list": deng_list,
            "hu_list": list(hu_set),
            "shengdiao_list": [sd for sd in SHENGDIAO_LIST if sd in shengdiao_set],
            "categories": {cat: categories[cat] for cat in sorted_categories},
            "grid": grid,
        }

    def generate_svg(
        self,
        char_list: List[str],
        she_filter: Optional[str] = None,
        hu_filter: Optional[str] = None,
        shengdiao_filter: Optional[str] = None,
        width: int = 1200,
        height: int = 800,
    ) -> str:
        chart_data = self.build_rhyme_chart(
            char_list,
            she_filter=she_filter,
            hu_filter=hu_filter,
            shengdiao_filter=shengdiao_filter,
            group_by="she"
        )

        all_svg_parts = []
        y_offset = 0
        chart_gap = 40

        for she_name, chart in chart_data["charts"].items():
            svg_height, svg_content = self._render_single_svg(
                she_name, chart, width, y_offset
            )
            all_svg_parts.append(svg_content)
            y_offset = svg_height + chart_gap

        total_height = y_offset

        svg_parts = []
        svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">')
        svg_parts.append('<style>')
        svg_parts.append('.chart-title { font-size: 24px; font-weight: bold; fill: #333; font-family: "SimSun", serif; }')
        svg_parts.append('.axis-label { font-size: 14px; fill: #555; font-family: "SimSun", serif; }')
        svg_parts.append('.cat-label { font-size: 12px; fill: #666; font-family: "SimSun", serif; writing-mode: tb; }')
        svg_parts.append('.cell-text { font-size: 16px; fill: #222; font-family: "SimSun", serif; }')
        svg_parts.append('.cell-empty { fill: #f5f5f5; }')
        svg_parts.append('.cell-filled { fill: #e8f5e9; stroke: #4caf50; stroke-width: 1; }')
        svg_parts.append('.grid-line { stroke: #ddd; stroke-width: 1; }')
        svg_parts.append('.deng-label { font-size: 14px; fill: #333; font-family: "SimSun", serif; font-weight: bold; }')
        svg_parts.append('.hu-label { font-size: 12px; fill: #555; font-family: "SimSun", serif; }')
        svg_parts.append('.sd-label { font-size: 11px; fill: #666; font-family: "SimSun", serif; }')
        svg_parts.append('</style>')

        svg_parts.extend(all_svg_parts)
        svg_parts.append('</svg>')

        return "\n".join(svg_parts)

    def _render_single_svg(self, title: str, chart: Dict, width: int, y_start: int) -> Tuple[int, str]:
        shengmu_list = chart["shengmu_list"]
        deng_list = chart["deng_list"]
        hu_list = chart["hu_list"] or ["开"]
        shengdiao_list = chart["shengdiao_list"] or ["平"]
        categories = chart["categories"]
        grid = chart["grid"]

        left_margin = 100
        top_margin = 60
        cell_width = 80
        cell_height = 40
        deng_label_height = 30
        hu_label_height = 25

        num_cols = len(deng_list) * len(hu_list) * len(shengdiao_list)
        num_rows = len(shengmu_list)
        total_width = left_margin + num_cols * cell_width + 20
        total_height = y_start + top_margin + num_rows * cell_height + 20

        lines = []

        lines.append(f'<text x="{width/2}" y="{y_start + 30}" text-anchor="middle" class="chart-title">{title}摄等韵图</text>')

        col_x = left_margin
        deng_col_groups = []
        for deng in deng_list:
            deng_start_x = col_x
            for hu in hu_list:
                for sd in shengdiao_list:
                    deng_col_groups.append((deng, hu, sd, col_x))
                    col_x += cell_width

        for i, (deng, hu, sd, x) in enumerate(deng_col_groups):
            if i % (len(hu_list) * len(shengdiao_list)) == 0:
                deng_width = cell_width * len(hu_list) * len(shengdiao_list)
                lines.append(f'<rect x="{x}" y="{y_start + top_margin - deng_label_height - hu_label_height}" width="{deng_width}" height="{deng_label_height}" fill="#e3f2fd" stroke="#90caf9"/>')
                lines.append(f'<text x="{x + deng_width/2}" y="{y_start + top_margin - deng_label_height - hu_label_height + 22}" text-anchor="middle" class="deng-label">{deng}等</text>')

            if i % len(shengdiao_list) == 0:
                hu_width = cell_width * len(shengdiao_list)
                lines.append(f'<rect x="{x}" y="{y_start + top_margin - hu_label_height}" width="{hu_width}" height="{hu_label_height}" fill="#f3e5f5" stroke="#ce93d8"/>')
                lines.append(f'<text x="{x + hu_width/2}" y="{y_start + top_margin - hu_label_height + 18}" text-anchor="middle" class="hu-label">{hu}口</text>')

            lines.append(f'<rect x="{x}" y="{y_start + top_margin}" width="{cell_width}" height="20" fill="#fff3e0" stroke="#ffcc80"/>')
            lines.append(f'<text x="{x + cell_width/2}" y="{y_start + top_margin + 15}" text-anchor="middle" class="sd-label">{sd}声</text>')

        for i, sm in enumerate(shengmu_list):
            y = y_start + top_margin + 20 + i * cell_height
            lines.append(f'<text x="{left_margin - 10}" y="{y + cell_height/2 + 5}" text-anchor="end" class="axis-label">{sm}</text>')

            for deng, hu, sd, x in deng_col_groups:
                cell_data = grid.get(sm, {}).get(deng, {}).get(hu, {}).get(sd, [])
                if cell_data:
                    lines.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" class="cell-filled"/>')
                    char_text = "".join([c["char"] for c in cell_data[:3]])
                    lines.append(f'<text x="{x + cell_width/2}" y="{y + cell_height/2 + 6}" text-anchor="middle" class="cell-text">{char_text}</text>')
                else:
                    lines.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" class="cell-empty" stroke="#ddd"/>')

        current_cat = None
        cat_start_y = 0
        cat_idx = 0
        for i, sm in enumerate(shengmu_list):
            cat = SHENGMU_CATEGORIES.get(sm, "其他")
            if cat != current_cat:
                if current_cat is not None:
                    cat_height = (i - cat_idx) * cell_height
                    lines.append(f'<rect x="{left_margin - 50}" y="{y_start + top_margin + 20 + cat_idx * cell_height}" width="25" height="{cat_height}" fill="#e0e0e0" stroke="#bdbdbd"/>')
                    lines.append(f'<text x="{left_margin - 38}" y="{y_start + top_margin + 20 + cat_idx * cell_height + cat_height/2 + 4}" text-anchor="middle" class="cat-label">{current_cat}</text>')
                current_cat = cat
                cat_idx = i

        if current_cat is not None:
            cat_height = (len(shengmu_list) - cat_idx) * cell_height
            lines.append(f'<rect x="{left_margin - 50}" y="{y_start + top_margin + 20 + cat_idx * cell_height}" width="25" height="{cat_height}" fill="#e0e0e0" stroke="#bdbdbd"/>')
            lines.append(f'<text x="{left_margin - 38}" y="{y_start + top_margin + 20 + cat_idx * cell_height + cat_height/2 + 4}" text-anchor="middle" class="cat-label">{current_cat}</text>')

        return total_height, "\n".join(lines)

    def generate_single_she_svg(
        self,
        she: str,
        char_list: Optional[List[str]] = None,
        width: int = 1000,
    ) -> Optional[str]:
        if char_list:
            chars = self.get_chars_by_list(char_list)
            chars = [c for c in chars if c.she == she]
        else:
            chars = crud.search_chars(self.db, she=she, limit=500)

        if not chars:
            return None

        chart = self._build_single_chart(chars)

        shengmu_list = chart["shengmu_list"]
        deng_list = chart["deng_list"]
        hu_list = chart["hu_list"] or ["开"]
        shengdiao_list = chart["shengdiao_list"] or ["平"]

        left_margin = 100
        top_margin = 70
        cell_width = 90
        cell_height = 45
        deng_label_height = 35
        hu_label_height = 25
        sd_height = 25

        num_cols = len(deng_list) * len(hu_list) * len(shengdiao_list)
        num_rows = len(shengmu_list)
        svg_width = max(width, left_margin + num_cols * cell_width + 20)
        svg_height = top_margin + num_rows * cell_height + 30

        parts = []
        parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">')
        parts.append('<style>')
        parts.append('.chart-title { font-size: 28px; font-weight: bold; fill: #2c3e50; font-family: "SimSun", "STSong", serif; }')
        parts.append('.shengmu-label { font-size: 16px; fill: #34495e; font-family: "SimSun", "STSong", serif; font-weight: bold; }')
        parts.append('.deng-label { font-size: 18px; fill: #1565c0; font-family: "SimSun", "STSong", serif; font-weight: bold; }')
        parts.append('.hu-label { font-size: 14px; fill: #7b1fa2; font-family: "SimSun", "STSong", serif; }')
        parts.append('.sd-label { font-size: 12px; fill: #e65100; font-family: "SimSun", "STSong", serif; }')
        parts.append('.cat-label { font-size: 13px; fill: #455a64; font-family: "SimSun", "STSong", serif; }')
        parts.append('.cell-text { font-size: 18px; fill: #1b5e20; font-family: "SimSun", "STSong", serif; }')
        parts.append('.cell-text-small { font-size: 14px; fill: #388e3c; font-family: "SimSun", "STSong", serif; }')
        parts.append('.cell-empty { fill: #fafafa; stroke: #e0e0e0; stroke-width: 1; }')
        parts.append('.cell-filled { fill: #e8f5e9; stroke: #66bb6a; stroke-width: 1.5; }')
        parts.append('.deng-header { fill: #e3f2fd; stroke: #90caf9; stroke-width: 1; }')
        parts.append('.hu-header { fill: #f3e5f5; stroke: #ce93d8; stroke-width: 1; }')
        parts.append('.sd-header { fill: #fff3e0; stroke: #ffcc80; stroke-width: 1; }')
        parts.append('.cat-bar { fill: #eceff1; stroke: #cfd8dc; stroke-width: 1; }')
        parts.append('</style>')

        parts.append(f'<text x="{svg_width/2}" y="35" text-anchor="middle" class="chart-title">{she}摄等韵图</text>')

        col_x = left_margin
        col_info = []
        for deng in deng_list:
            for hu in hu_list:
                for sd in shengdiao_list:
                    col_info.append((deng, hu, sd, col_x))
                    col_x += cell_width

        grid = chart["grid"]

        for i, (deng, hu, sd, x) in enumerate(col_info):
            if i % (len(hu_list) * len(shengdiao_list)) == 0:
                deng_w = cell_width * len(hu_list) * len(shengdiao_list)
                parts.append(f'<rect x="{x}" y="{top_margin - deng_label_height - hu_label_height - sd_height}" width="{deng_w}" height="{deng_label_height}" class="deng-header"/>')
                parts.append(f'<text x="{x + deng_w/2}" y="{top_margin - deng_label_height - hu_label_height - sd_height + 25}" text-anchor="middle" class="deng-label">{deng}等</text>')

            if i % len(shengdiao_list) == 0:
                hu_w = cell_width * len(shengdiao_list)
                parts.append(f'<rect x="{x}" y="{top_margin - hu_label_height - sd_height}" width="{hu_w}" height="{hu_label_height}" class="hu-header"/>')
                parts.append(f'<text x="{x + hu_w/2}" y="{top_margin - hu_label_height - sd_height + 18}" text-anchor="middle" class="hu-label">{hu}口</text>')

            parts.append(f'<rect x="{x}" y="{top_margin - sd_height}" width="{cell_width}" height="{sd_height}" class="sd-header"/>')
            parts.append(f'<text x="{x + cell_width/2}" y="{top_margin - sd_height + 17}" text-anchor="middle" class="sd-label">{sd}声</text>')

        for i, sm in enumerate(shengmu_list):
            y = top_margin + i * cell_height

            parts.append(f'<text x="{left_margin - 12}" y="{y + cell_height/2 + 6}" text-anchor="end" class="shengmu-label">{sm}</text>')

            for deng, hu, sd, x in col_info:
                cell_data = grid.get(sm, {}).get(deng, {}).get(hu, {}).get(sd, [])
                if cell_data:
                    parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" class="cell-filled"/>')
                    chars_in_cell = [c["char"] for c in cell_data]
                    if len(chars_in_cell) <= 3:
                        text = "".join(chars_in_cell)
                        parts.append(f'<text x="{x + cell_width/2}" y="{y + cell_height/2 + 7}" text-anchor="middle" class="cell-text">{text}</text>')
                    else:
                        text = "".join(chars_in_cell[:3]) + "…"
                        parts.append(f'<text x="{x + cell_width/2}" y="{y + cell_height/2 + 5}" text-anchor="middle" class="cell-text-small">{text}</text>')
                else:
                    parts.append(f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" class="cell-empty"/>')

        current_cat = None
        cat_start_idx = 0
        for i, sm in enumerate(shengmu_list):
            cat = SHENGMU_CATEGORIES.get(sm, "其他")
            if cat != current_cat:
                if current_cat is not None:
                    cat_h = (i - cat_start_idx) * cell_height
                    parts.append(f'<rect x="{left_margin - 45}" y="{top_margin + cat_start_idx * cell_height}" width="22" height="{cat_h}" class="cat-bar"/>')
                    parts.append(f'<text x="{left_margin - 34}" y="{top_margin + cat_start_idx * cell_height + cat_h/2 + 4}" text-anchor="middle" class="cat-label">{current_cat}</text>')
                current_cat = cat
                cat_start_idx = i

        if current_cat is not None:
            cat_h = (len(shengmu_list) - cat_start_idx) * cell_height
            parts.append(f'<rect x="{left_margin - 45}" y="{top_margin + cat_start_idx * cell_height}" width="22" height="{cat_h}" class="cat-bar"/>')
            parts.append(f'<text x="{left_margin - 34}" y="{top_margin + cat_start_idx * cell_height + cat_h/2 + 4}" text-anchor="middle" class="cat-label">{current_cat}</text>')

        parts.append('</svg>')

        return "\n".join(parts)

    def get_available_she_list(self) -> List[str]:
        all_she = crud.get_all_she(self.db)
        return sorted(all_she, key=lambda x: SHE_ORDER.get(x, 99))
