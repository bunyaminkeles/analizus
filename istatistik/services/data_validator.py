import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

ID_KEYWORDS = [
    'id', 'no', 'num', 'kod', 'sira', 'katilimci', 'ogrenci', 'participant', 'respondent',
    'user', 'uye', 'kisi', 'person', 'student', 'record', 'case'
]
LIKERT_RANGES = [
    (1, 5),
    (1, 7),
    (0, 10),
    (1, 9),
    (1, 6),
]


def _normalize_column_name(name: str) -> str:
    name = str(name).strip().lower()
    name = name.replace('ı', 'i').replace('ö', 'o').replace('ü', 'u').replace('ş', 's')
    name = name.replace('ğ', 'g').replace('ç', 'c')
    return name


def _is_likely_id_column(series: pd.Series) -> bool:
    if series.dropna().empty:
        return False
    if not series.is_unique:
        return False

    if is_numeric_dtype(series):
        values = series.dropna().astype(float)
        return values.is_monotonic_increasing or values.is_monotonic_decreasing

    if series.dtype == object:
        cleaned = series.dropna().astype(str).str.strip()
        return cleaned.str.isnumeric().all()

    return False


def detect_id_columns(df: pd.DataFrame) -> list[str]:
    candidates = []
    for col in df.columns:
        normalized = _normalize_column_name(col)
        if any(keyword in normalized for keyword in ID_KEYWORDS):
            series = df[col]
            if series.dropna().nunique() >= max(3, len(series) // 5) and _is_likely_id_column(series):
                candidates.append(col)
    return candidates


def detect_non_numeric_columns(df: pd.DataFrame, tool: str) -> list[str]:
    if tool in ('cronbach', 'normallik'):
        return [col for col in df.columns if not is_numeric_dtype(df[col])]
    return []


def detect_missing_values(df: pd.DataFrame) -> list[dict]:
    warnings = []
    missing = df.isna().sum()
    total_missing = int(missing.sum())
    if total_missing == 0:
        return warnings

    cols = [col for col, cnt in missing.items() if cnt > 0]
    cols_summary = ', '.join(f'{col} ({int(missing[col])})' for col in cols[:3])
    more_text = f' +{len(cols) - 3} sütun' if len(cols) > 3 else ''
    warnings.append({
        'level': 'warning',
        'title': 'Boş değerler tespit edildi',
        'message': f'{len(cols)} sütunda toplam {total_missing} boş değer var: {cols_summary}{more_text}. Boş hücreler analizde otomatik olarak atılacaktır.',
    })
    return warnings


def detect_likert_issues(df: pd.DataFrame) -> list[dict]:
    warnings = []
    numeric = df.select_dtypes(include=[np.number])
    if numeric.empty:
        return warnings

    for col in numeric.columns:
        series = numeric[col].dropna()
        if series.empty:
            continue
        if not np.all(np.equal(np.mod(series, 1), 0)):
            continue

        values = series.astype(int).values
        if len(values) < 5:
            continue

        if np.mean((values >= 1) & (values <= 7)) < 0.8:
            continue

        out_of_range = values[(values < 1) | (values > 7)]
        if len(out_of_range) > 0:
            unique_out = sorted(np.unique(out_of_range))
            warnings.append({
                'level': 'danger',
                'title': 'Likert aralığı dışı değerler',
                'message': f'"{col}" sütununda tipik Likert aralığı 1–7 dışında {len(out_of_range)} değer bulundu: {unique_out[:5]}{"..." if len(unique_out) > 5 else ""}. Bu değerler analiz sonuçlarını etkileyebilir.',
            })
    return warnings


def validate_dataframe(df: pd.DataFrame, tool: str) -> list[dict]:
    warnings = []

    warnings.extend(detect_missing_values(df))

    id_columns = detect_id_columns(df)
    if id_columns:
        warnings.append({
            'level': 'warning',
            'title': 'Olası ID alanı bulundu',
            'message': f'Analizde kullanılmaması önerilen aşağıdaki alanlar bulundu: {", ".join(id_columns)}. Bu tür kimlik sütunları genellikle analiz sonuçlarını bozar.',
        })

    non_numeric = detect_non_numeric_columns(df, tool)
    if non_numeric:
        warnings.append({
            'level': 'warning',
            'title': 'Sayısal olmayan sütunlar',
            'message': f'Analize sayısal olarak dahil edilmeyecek sütunlar: {", ".join(non_numeric)}.',
        })

    if tool == 'cronbach':
        warnings.extend(detect_likert_issues(df))

    return warnings
