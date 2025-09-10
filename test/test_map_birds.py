#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지도에 새 표시 기능 테스트 - 실제 AirBirds JSON 데이터 사용
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime, timezone


def load_real_airbirds_data():
    """실제 AirBirds JSON 파일 로드"""
    json_file = Path("../backend/app/static/DATASET(AirBirds)_Predict/structured_labels/D02_20210721142744_0007999.json")
    
    if not json_file.exists():
        print(f"❌ JSON 파일을 찾을 수 없습니다: {json_file}")
        return None
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ JSON 파일 로딩 실패: {e}")
        return None


def upload_image(image_name):
    """실제 이미지 파일을 서버에 업로드"""
    image_path = Path(f"../backend/app/static/DATASET(AirBirds)_Predict_original/{image_name}")
    
    if not image_path.exists():
        print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
        return None
    
    try:
        api_url = "http://localhost:8000/upload/image"
        
        with open(image_path, 'rb') as f:
            files = {'file': (image_name, f, 'image/png')}
            response = requests.post(api_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                print(f"   📤 이미지 업로드 성공: {result['url']}")
                return result['url']
            else:
                print(f"   ❌ 이미지 업로드 실패: {result}")
                return None
        else:
            print(f"   ❌ 이미지 업로드 실패: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ 이미지 업로드 오류: {e}")
        return None


def convert_airbirds_to_api_format(airbirds_data):
    """AirBirds JSON 형식을 API 형식으로 변환"""
    if not airbirds_data or "detections" not in airbirds_data:
        return []
    
    converted_detections = []
    image_shape = airbirds_data.get("image_shape", [1080, 1920])  # [height, width]
    image_name = airbirds_data.get("image_name", "")
    
    # CCTV ID 추출
    cctv_id = image_name.split("_")[0] if image_name else "D02"
    
    # 실제 이미지 업로드
    print(f"📷 실제 이미지 업로드 중: {image_name}")
    frame_url = upload_image(image_name)
    
    if not frame_url:
        print("❌ 이미지 업로드 실패, 기본 URL 사용")
        frame_url = f"/static/DATASET(AirBirds)_Predict_original/{image_name}"
    
    for i, detection in enumerate(airbirds_data["detections"], 1):
        bbox_data = detection["bbox"]
        
        # 픽셀 좌표 추출
        x1, y1 = bbox_data["x1"], bbox_data["y1"]
        x2, y2 = bbox_data["x2"], bbox_data["y2"]
        
        # bbox [x, y, width, height] 형식으로 변환
        bbox = [x1, y1, x2 - x1, y2 - y1]
        
        # 중심점 계산 (픽셀 좌표)
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # 상대좌표로 변환 (0-1 범위)
        pos = [center_x / image_shape[1], center_y / image_shape[0]]  # [u, v]
        
        # 신뢰도 기반 위험도 계산
        confidence = detection.get("confidence", 0.0)
        if confidence >= 0.7:
            risk = "red"
        elif confidence >= 0.4:
            risk = "orange"
        else:
            risk = "yellow"
        
        converted_detection = {
            "cctv_id": cctv_id,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "pos": pos,
            "bbox": bbox,
            "risk": risk,
            "frame_url": frame_url,  # 업로드된 실제 이미지 URL
            "confidence": confidence,
            "bird_count": 1
        }
        
        converted_detections.append(converted_detection)
        print(f"   🐦 새 {i}: 신뢰도 {confidence:.3f}, 위험도 {risk}")
    
    return converted_detections


def test_detection_api():
    """실제 AirBirds 탐지 결과를 API로 전송하여 지도에 새가 표시되는지 테스트"""
    
    print("=== 실제 AirBirds 데이터로 지도 표시 테스트 ===")
    
    # 실제 AirBirds JSON 데이터 로드
    airbirds_data = load_real_airbirds_data()
    if not airbirds_data:
        print("❌ AirBirds 데이터를 로드할 수 없어 모의 데이터를 사용합니다.")
        # 모의 탐지 결과 (Detection 모델 형식)
        detection_data = {
            "cctv_id": "D02",
            "captured_at": "2025-09-10T22:30:00Z",
            "pos": [0.3, 0.4],  # 상대좌표 [u, v]
            "bbox": [500, 300, 100, 100],  # [x, y, width, height]
            "risk": "red",  # 위험도 필수 필드
            "frame_url": "/static/test_frame.jpg"
        }
        converted_detections = [detection_data]
    else:
        print(f"✅ AirBirds 데이터 로드 성공: {airbirds_data['image_name']}")
        print(f"   탐지된 새: {len(airbirds_data['detections'])}마리")
        
        # AirBirds 형식을 API 형식으로 변환
        converted_detections = convert_airbirds_to_api_format(airbirds_data)
        print(f"   변환된 탐지 결과: {len(converted_detections)}개")
    
    # 백엔드 API URL  
    api_url = "http://localhost:8000/detect/result"
    print()
    print(f"API URL: {api_url}")
    
    success_count = 0
    total_count = len(converted_detections)
    
    try:
        for i, detection_data in enumerate(converted_detections, 1):
            print(f"\n[{i}/{total_count}] 탐지 결과 전송:")
            print(f"   CCTV ID: {detection_data['cctv_id']}")
            print(f"   위치: {detection_data['pos']}")
            print(f"   위험도: {detection_data['risk']}")
            print(f"   신뢰도: {detection_data.get('confidence', 'N/A')}")
            
            # 1. 탐지 결과 전송
            response = requests.post(api_url, json=detection_data)
            print(f"   상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ 전송 성공: {response.json()}")
                success_count += 1
            else:
                print(f"   ❌ 전송 실패: {response.text}")
        
        print(f"\n📊 전송 결과: {success_count}/{total_count} 성공")
        
        if success_count > 0:
            # 2. 저장된 탐지 결과 확인
            cctv_id = converted_detections[0]['cctv_id']
            history_url = f"http://localhost:8000/detect/history/{cctv_id}"
            history_response = requests.get(history_url)
            
            print(f"\n2. 저장된 탐지 결과 확인:")
            print(f"   URL: {history_url}")
            print(f"   상태 코드: {history_response.status_code}")
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                print(f"   저장된 탐지 수: {len(history_data)}")
                
                if history_data:
                    latest = history_data[0]
                    print(f"   최신 탐지:")
                    print(f"     CCTV ID: {latest.get('cctv_id')}")
                    print(f"     위치: {latest.get('pos')}")
                    print(f"     위험도: {latest.get('risk')}")
                    print(f"     시간: {latest.get('captured_at')}")
                    print()
                    
                    print("✅ 탐지 결과가 성공적으로 저장되었습니다!")
                    print("💡 이제 프론트엔드에서 지도를 새로고침하면 새가 표시될 것입니다.")
                else:
                    print("❌ 탐지 결과가 저장되지 않았습니다.")
            else:
                print(f"   오류: {history_response.text}")
        else:
            print("❌ 모든 탐지 결과 전송에 실패했습니다.")
            
    except requests.exceptions.ConnectionError:
        print("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


def test_airbirds_api():
    """AirBirds 전용 API 엔드포인트 테스트 (필요시 주석 해제)"""
    pass  # 현재는 사용하지 않음


def test_multiple_detections():
    """여러 탐지 결과를 전송하여 지도에 여러 새가 표시되는지 테스트 (필요시 주석 해제)"""
    pass  # 현재는 사용하지 않음


if __name__ == "__main__":
    print("🚁 BirdWatch - 지도에 새 표시 기능 테스트")
    print("=" * 60)
    
    # 실제 AirBirds 데이터로 테스트
    test_detection_api()
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("📱 프론트엔드 확인: http://localhost:3000")
    print("🗺️  지도에서 새 마커들을 확인해보세요.")
