#!/usr/bin/env python3
"""
배치 테스트만 따로 실행
"""

import requests
import json
from datetime import datetime
import random

SERVER_URL = "http://localhost:8000"

def test_batch_only():
    """배치 탐지 결과 테스트만"""
    print("📦 배치 탐지 결과 테스트...")
    
    # 한 번에 여러 개의 탐지 결과 생성
    batch_detections = []
    
    for i in range(3):
        # 같은 CCTV에서 여러 조류 탐지
        x1 = random.uniform(100, 400)
        y1 = random.uniform(100, 300)
        width = random.uniform(10, 50)
        height = random.uniform(10, 40)
        x2 = x1 + width
        y2 = y1 + height
        
        # width, height, center 계산
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # DetectionCSV 형식 (API 스키마에 따른 필수 필드들)
        detection_csv = {
            "image_index": i,
            "image_path": f"/path/to/batch_test_frame_{i+1}.jpg",
            "image_name": f"batch_test_frame_{i+1}.jpg",
            "object_id": i,
            "class_name": "bird",
            "class_id": 0,
            "x1": round(x1, 2),
            "y1": round(y1, 2),
            "x2": round(x2, 2),
            "y2": round(y2, 2),
            "confidence": round(random.uniform(0.4, 0.9), 3),
            "width": round(width, 2),
            "height": round(height, 2),
            "center_x": round(center_x, 2),
            "center_y": round(center_y, 2),
            "cctv_id": "camera_01",
            "captured_at": datetime.now().isoformat()
        }
        
        batch_detections.append(detection_csv)
        print(f"  탐지 {i+1}: 신뢰도 {detection_csv['confidence']}")
    
    # DetectionBatch 형식으로 변환
    batch_data = {
        "detections": batch_detections,
        "cctv_id": "camera_01",
        "captured_at": datetime.now().isoformat()
    }
    
    print(f"\n📤 전송할 배치 데이터:")
    print(json.dumps(batch_data, indent=2, ensure_ascii=False))
    
    try:
        # 배치 API 호출
        response = requests.post(
            f"{SERVER_URL}/detect/batch",
            json=batch_data,
            timeout=15
        )
        
        print(f"📡 응답 상태: {response.status_code}")
        print(f"📝 응답 내용: {response.text}")
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ 배치 탐지 결과 전송 성공: {len(batch_detections)}개 항목")
                return True
            else:
                print(f"❌ 서버 에러: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP 에러 {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 배치 전송 실패: {e}")
        return False

if __name__ == "__main__":
    test_batch_only()
