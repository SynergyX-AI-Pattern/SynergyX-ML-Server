from typing import List, Optional, Tuple
from fastdtw import fastdtw
from app.exceptions.base import APIException
from app.api_payload.code.status_code import ErrorStatus


def validate_unit(unit: str, value: int):
    """
    사용자 설정 단위(unit)와 값(value)이 유효한지 검증합니다.

    Raises:
        APIException: 유효하지 않은 단위 또는 값일 경우
    """
    if value < 1:
        raise APIException(ErrorStatus.INVALID_UNIT_VALUE)
    if unit not in {"HOUR", "DAY"}:
        raise APIException(ErrorStatus.INVALID_UNIT)


def zscore_normalize(sequence: List[float]) -> Optional[List[float]]:
    """
    z-score 정규화를 수행합니다.

    Returns:
        - 정규화된 시계열 데이터
        if 분산이 거의 0이면 (모든 값이 거의 동일하면) None 반환
    """

    # 빈 리스트가 입력될 경우 방지
    if not sequence:
        return None

    mean = sum(sequence) / len(sequence)  # 평균 계산
    var = sum((x - mean) ** 2 for x in sequence) / len(sequence)  # 분산 계산

    # 분산 0일 경우
    if var < 1e-8:
        return None
    std = var ** 0.5  # 표준 편차 계산
    return [(x - mean) / std for x in sequence]


def find_match_indices(
    pattern: List[float],
    closes: List[float],
    tolerance: float
) -> Tuple[List[int], List[float]]:
    """
    DTW를 통해 패턴과 유사한 구간 탐색합니다.

    Parameters:
        pattern: 사용자 패턴
        closes: 비교 대상 종가 데이터
        tolerance: 허용 가능한 DTW 거리 상한값

    Returns:
        시작 인덱스 리스트, 해당 거리 리스트

    Raises:
        APIException:
            - 시계열이 패턴보다 짧은 경우
            - 패턴의 분산이 0에 가까워 정규화가 불가능할 경우
    """
    pattern_length = len(pattern)

    # 비교 대상 데이터가 패턴보다 짧은 경우
    if len(closes) < pattern_length:
        raise APIException(ErrorStatus.NOT_ENOUGH_DATA)

    # 패턴을 z-score 정규화 (평균 0, 표준편차 1)
    norm_pat = zscore_normalize(pattern)

    # 패턴 값이 모두 동일한 경우
    if norm_pat is None:
        raise APIException(ErrorStatus.PATTERN_TOO_FLAT)

    idxes, distances = [], []
    last_end = -1

    # 슬라이딩 윈도우 방식으로 유사 구간 탐색
    for i in range(len(closes) - pattern_length  + 1):
        if i <= last_end:
            # 이전 매칭 구간과 겹치지 않도록 넘김
            continue

        win = closes[i:i+pattern_length ]
        norm_win = zscore_normalize(win)

        # 분산 0일 경우
        if norm_win is None:
            continue

        # DTW 로직 구현
        dist_value, _ = fastdtw(norm_pat, norm_win, dist=lambda a, b: abs(a - b))
        if dist_value <= tolerance:
            idxes.append(i)
            distances.append(dist_value)
            last_end = i + pattern_length  - 1 # 매칭 구간 이후 다시 탐색
    return idxes, distances