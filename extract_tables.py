import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

import pandas as pd
import pdfplumber

ROOT_DIR = Path(__file__).resolve().parent

POSSIBLE_PDF_PATHS = [
    ROOT_DIR / "ewha.pdf",
    ROOT_DIR.parent / "ewha.pdf",
]
PDF_PATH = POSSIBLE_PDF_PATHS[0]

OUTPUT_DIR = ROOT_DIR
DEGREES_FILE = OUTPUT_DIR / "degrees.csv"
CONTRACT_FILE = OUTPUT_DIR / "contract_dept.csv"


def normalize_cell(value: Optional[str]) -> str:
    if value is None:
        return ""
    return str(value).replace("\n", " ").replace("\r", " ").replace("\xa0", " ").strip()


def normalize_header(value: str) -> str:
    cleaned = normalize_cell(value)
    for ch in [" ", "·", ".", "ㆍ"]:
        cleaned = cleaned.replace(ch, "")
    for ch in "()[]{}:;,-_/\\.":
        cleaned = cleaned.replace(ch, "")
    return cleaned


TABLE_SPECS = [
    {
        "name": "degrees",
        "targets": {"설치대학", "학과_전공", "학위_종류"},
        "outputs": ["설치대학", "학과_전공", "학위_종류"],
        "path": DEGREES_FILE,
        "page_range": (50, 52),  # 별표 2: 학사학위의 종류 (페이지 51)
        "exclude_columns": {"설치형태"},  # 설치형태 컬럼이 없어야 함
    },
    {
        "name": "contract",
        "targets": {"설치대학", "설치형태", "학과_전공", "학위_종류", "입학정원_명", "설치_운영기간"},
        "outputs": ["설치대학", "설치형태", "학과_전공", "학위_종류", "입학정원_명", "설치_운영기간"],
        "path": CONTRACT_FILE,
        "page_range": (52, 54),  # 별표 3: 계약학과 설치·운영 (페이지 53)
        "require_columns": {"설치형태"},  # 설치형태 컬럼이 있어야 함
    },
]

COLUMN_ALIASES: Dict[str, Iterable[str]] = {
    "설치대학": ["설치대학", "대학", "대 학"],
    "설치형태": ["설치형태"],
    "학과_전공": ["학과_전공", "학과또는전공", "학과 또는 전공"],
    "학위_종류": ["학위_종류", "학위의종류"],
    "입학정원_명": ["입학정원(명)", "입학정원"],
    "설치_운영기간": ["설치·운영기간", "설치운영기간"],
}

HEADER_LOOKUP: Dict[str, str] = {}
for canonical, variants in COLUMN_ALIASES.items():
    for variant in variants:
        HEADER_LOOKUP[normalize_header(variant)] = canonical


def table_to_dataframe(table: Sequence[Sequence[str]]) -> Optional[pd.DataFrame]:
    rows = [[normalize_cell(cell) for cell in row] for row in table if any(str(cell).strip() for cell in row)]
    if not rows:
        return None
    header = [normalize_header(cell) for cell in rows[0]]
    data_rows = rows[1:]
    if not data_rows:
        return None

    max_len = max(len(header), *(len(r) for r in data_rows))
    header = (header + [""] * max_len)[:max_len]
    normalized_data = [
        (row + [""] * max_len)[:max_len]
        for row in data_rows
    ]
    return pd.DataFrame(normalized_data, columns=header)


def map_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed_cols = {}
    for col in df.columns:
        key = normalize_header(col)
        renamed = HEADER_LOOKUP.get(key)
        if renamed:
            renamed_cols[col] = renamed
    if not renamed_cols:
        return pd.DataFrame()
    return df[list(renamed_cols.keys())].rename(columns=renamed_cols)


def extract_tables(
    target_columns: set,
    page_range: Optional[tuple] = None,
    exclude_columns: Optional[set] = None,
    require_columns: Optional[set] = None,
) -> pd.DataFrame:
    """
    특정 조건에 맞는 테이블 추출
    
    Args:
        target_columns: 필수로 포함되어야 하는 컬럼들
        page_range: (시작페이지, 끝페이지) 튜플. None이면 모든 페이지 검색
        exclude_columns: 포함되어 있으면 안 되는 컬럼들
        require_columns: 반드시 포함되어야 하는 컬럼들
    """
    frames: List[pd.DataFrame] = []
    with pdfplumber.open(PDF_PATH) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            # 페이지 범위 필터링
            if page_range:
                start_page, end_page = page_range
                if not (start_page <= page_number <= end_page):
                    continue
            
            tables = page.extract_tables()
            for table in tables:
                df = table_to_dataframe(table)
                if df is None:
                    continue
                mapped = map_columns(df)
                if mapped.empty:
                    continue
                
                mapped_columns = set(mapped.columns)
                
                # 필수 컬럼 확인
                if not target_columns.issubset(mapped_columns):
                    continue
                
                # 제외할 컬럼 확인
                if exclude_columns and exclude_columns.intersection(mapped_columns):
                    continue
                
                # 필수 포함 컬럼 확인
                if require_columns and not require_columns.issubset(mapped_columns):
                    continue
                
                # 대상 컬럼만 선택
                ordered = [col for col in mapped.columns if col in target_columns]
                frames.append(mapped[ordered])
    
    if not frames:
        raise ValueError(
            f"필요한 컬럼 {target_columns} 을 포함한 표를 찾을 수 없습니다. "
            f"(페이지 범위: {page_range}, 제외 컬럼: {exclude_columns}, 필수 컬럼: {require_columns})"
        )
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.loc[:, ~combined.columns.duplicated()]
    return combined


def main() -> None:
    global PDF_PATH
    for path in POSSIBLE_PDF_PATHS:
        if path.exists():
            PDF_PATH = path
            break
    else:
        raise FileNotFoundError("ewha.pdf 파일을 찾을 수 없습니다.")

    print("📄 PDF 표 추출을 시작합니다...")
    summary: Dict[str, int] = {}
    for spec in TABLE_SPECS:
        df = extract_tables(
            target_columns=spec["targets"],
            page_range=spec.get("page_range"),
            exclude_columns=spec.get("exclude_columns"),
            require_columns=spec.get("require_columns"),
        )
        
        # 출력 컬럼에 없는 컬럼은 빈 값으로 추가
        for column in spec["outputs"]:
            if column not in df.columns:
                df[column] = ""
        
        # 출력 컬럼 순서대로 정렬
        df = df[spec["outputs"]]
        df.to_csv(spec["path"], index=False, encoding="utf-8-sig")
        summary[f"{spec['name']}_rows"] = len(df)
        print(f"  - {spec['name']} 표 {len(df)}건 저장 ({spec['path'].name})")

    print("✅ CSV 저장 완료:", json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

