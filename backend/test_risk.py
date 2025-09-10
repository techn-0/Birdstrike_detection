#!/usr/bin/env python3
"""새로운 위험도 계산 테스트"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.detection_service import DetectionService

def test_new_risk_calculation():
    """새로운 위험도 계산 기준 테스트"""
    print("새로운 위험도 계산 기준 테스트:")
    print(f"미탐지 (count=0): {DetectionService.calculate_risk_by_count_and_confidence(0)}")
    print(f"1개 + 낮은 신뢰도 (count=1, conf=0.2): {DetectionService.calculate_risk_by_count_and_confidence(1, 0.2)}")
    print(f"1개 + 높은 신뢰도 (count=1, conf=0.5): {DetectionService.calculate_risk_by_count_and_confidence(1, 0.5)}")
    print(f"2개 이상 (count=2, conf=0.1): {DetectionService.calculate_risk_by_count_and_confidence(2, 0.1)}")
    print(f"3개 이상 (count=3, conf=0.9): {DetectionService.calculate_risk_by_count_and_confidence(3, 0.9)}")

if __name__ == "__main__":
    test_new_risk_calculation()
