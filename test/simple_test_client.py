"""
간단한 조류 탐지 결과 전송 테스트
CSV 형식 (detection_results.csv) 기반으로 수정
"""

import requests
import json
import csv
from datetime import datetime
import random
import os

# 서버 URL 설정
SERVER_URL = "http://localhost:8000"

def send_csv_detection(detection_data):
    """
    CSV 형식의 탐지 결과를 서버로 전송
    
    Args:
        detection_data: CSV 행 데이터 (dict)
    
    Returns:
        bool: 전송 성공 여부
    """
    
    # CSV 데이터를 API 형식으로 변환
    data = {
        "image_index": int(detection_data.get("image_index", 0)),
        "image_path": detection_data.get("image_path", ""),
        "image_name": detection_data.get("image_name", ""),
        "object_id": int(detection_data.get("object_id", 0)),
        "class_name": detection_data.get("class_name", "bird"),
        "class_id": int(detection_data.get("class_id", 0)),
        "x1": float(detection_data.get("x1", 0)),
        "y1": float(detection_data.get("y1", 0)),
        "x2": float(detection_data.get("x2", 0)),
        "y2": float(detection_data.get("y2", 0)),
        "confidence": float(detection_data.get("confidence", 0)),
        "width": float(detection_data.get("width", 0)),
        "height": float(detection_data.get("height", 0)),
        "center_x": float(detection_data.get("center_x", 0)),
        "center_y": float(detection_data.get("center_y", 0)),
        "cctv_id": detection_data.get("cctv_id"),  # 추가될 수 있음
        "captured_at": datetime.now().isoformat()
    }
    
    try:
        # 새로운 CSV 형식 API 호출
        response = requests.post(
            f"{SERVER_URL}/detect/csv",
            json=data,
            timeout=10
        )
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ CSV 탐지 결과 전송 성공: {data['image_name']}")
                return True
            else:
                print(f"❌ 서버 에러: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP 에러 {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 전송 실패: {e}")
        return False

def test_csv_samples():
    """첨부된 CSV 데이터 샘플 테스트"""
    print("🔍 CSV 형식 탐지 데이터 테스트 시작...")
    
    # 첨부된 CSV 데이터에서 가져온 샘플들
    csv_samples = [
        {
            "image_index": 0,
            "image_path": "G:\\AirBirds\\datasets\\DATASET(Airbirds)_CROPPED\\images\\val\\D02_20210628090856_0000714_crop_000.png",
            "image_name": "D02_20210628090856_0000714_crop_000.png",
            "object_id": 0,
            "class_name": "bird",
            "class_id": 0,
            "x1": 508.8328857421875,
            "y1": 534.927490234375,
            "x2": 524.5106201171875,
            "y2": 543.120849609375,
            "confidence": 0.27232813835144043,
            "width": 15.677734375,
            "height": 8.193359375,
            "center_x": 516.6717529296875,
            "center_y": 539.024169921875
        },
        {
            "image_index": 2,
            "image_path": "G:\\AirBirds\\datasets\\DATASET(Airbirds)_CROPPED\\images\\val\\D02_20210721142744_0001120_crop_007.png",
            "image_name": "D02_20210721142744_0001120_crop_007.png",
            "object_id": 0,
            "class_name": "bird",
            "class_id": 0,
            "x1": 108.12217712402344,
            "y1": 170.91787719726562,
            "x2": 112.88771057128906,
            "y2": 175.89199829101562,
            "confidence": 0.29926395416259766,
            "width": 4.765533447265625,
            "height": 4.97412109375,
            "center_x": 110.50494384765625,
            "center_y": 173.40493774414062
        },
        {
            "image_index": 5,
            "image_path": "G:\\AirBirds\\datasets\\DATASET(Airbirds)_CROPPED\\images\\val\\D02_20210721142744_0009499_crop_007.png",
            "image_name": "D02_20210721142744_0009499_crop_007.png",
            "object_id": 0,
            "class_name": "bird",
            "class_id": 0,
            "x1": 435.5831298828125,
            "y1": 167.29034423828125,
            "x2": 489.4793701171875,
            "y2": 208.7540283203125,
            "confidence": 0.2754083573818207,
            "width": 53.896240234375,
            "height": 41.46368408203125,
            "center_x": 462.53125,
            "center_y": 188.02218627929688
        }
    ]
    
    success_count = 0
    
    for i, sample in enumerate(csv_samples, 1):
        print(f"\n[{i}/3] CSV 샘플 {i} 전송 중...")
        print(f"  이미지: {sample['image_name']}")
        print(f"  바운딩박스: [{sample['x1']:.1f}, {sample['y1']:.1f}, {sample['x2']:.1f}, {sample['y2']:.1f}]")
        print(f"  신뢰도: {sample['confidence']:.3f}")
        print(f"  크기: {sample['width']:.1f} x {sample['height']:.1f}")
        
        if send_csv_detection(sample):
            success_count += 1
    
    print(f"\n📊 CSV 테스트 완료: {success_count}/3 성공")

def simulate_real_model_output():
    """실제 AI 모델 출력을 시뮬레이션 - CSV 형식 기반"""
    print("\n🤖 AI 모델 출력 시뮬레이션 (CSV 형식)...")
    
    # 실제 CSV 패턴과 유사한 시뮬레이션 데이터
    for i in range(5):
        # 랜덤한 탐지 결과 생성 (CSV 형식)
        image_index = random.randint(100, 999)
        image_num = random.randint(1000, 9999)
        crop_num = random.randint(0, 10)
        
        # 이미지명 생성 (실제 패턴과 유사)
        image_name = f"D0{random.randint(1,2)}_20210{random.randint(601,801):03d}{random.randint(10,23):02d}{random.randint(10,59):02d}{random.randint(10,59):02d}_{image_num:07d}_crop_{crop_num:03d}.png"
        
        # 바운딩 박스 생성 (실제 범위와 유사)
        x1 = random.uniform(50, 500)
        y1 = random.uniform(50, 400)
        width = random.uniform(5, 50)
        height = random.uniform(5, 40)
        x2 = x1 + width
        y2 = y1 + height
        
        # 중심점 계산
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # 신뢰도 (실제 CSV와 유사한 범위)
        confidence = random.uniform(0.25, 0.95)
        
        simulation_data = {
            "image_index": image_index,
            "image_path": f"G:\\AirBirds\\datasets\\DATASET(Airbirds)_CROPPED\\images\\val\\{image_name}",
            "image_name": image_name,
            "object_id": 0,
            "class_name": "bird",
            "class_id": 0,
            "x1": round(x1, 2),
            "y1": round(y1, 2),
            "x2": round(x2, 2),
            "y2": round(y2, 2),
            "confidence": round(confidence, 6),
            "width": round(width, 2),
            "height": round(height, 2),
            "center_x": round(center_x, 2),
            "center_y": round(center_y, 2)
        }
        
        print(f"\n🔍 시뮬레이션 #{i+1}: 신뢰도 {confidence:.3f}")
        print(f"   이미지: {image_name}")
        send_csv_detection(simulation_data)

def load_csv_file(csv_path: str):
    """CSV 파일을 읽어서 테스트"""
    if not os.path.exists(csv_path):
        print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_path}")
        return
    
    print(f"📄 CSV 파일 로드 중: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            detections = list(reader)
        
        print(f"✅ {len(detections)}개의 탐지 결과를 로드했습니다.")
        
        # 처음 5개만 테스트
        test_count = min(5, len(detections))
        success_count = 0
        
        for i in range(test_count):
            detection = detections[i]
            print(f"\n[{i+1}/{test_count}] CSV 행 {i+1} 처리 중...")
            print(f"  이미지: {detection['image_name']}")
            print(f"  신뢰도: {float(detection['confidence']):.3f}")
            
            if send_csv_detection(detection):
                success_count += 1
        
        print(f"\n📊 CSV 파일 테스트 완료: {success_count}/{test_count} 성공")
        
    except Exception as e:
        print(f"❌ CSV 파일 처리 실패: {e}")

def check_server():
    """서버 연결 확인"""
    try:
        response = requests.get(f"{SERVER_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ 서버 연결 성공")
            return True
        else:
            print(f"⚠️ 서버 응답 이상: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        print("💡 백엔드 서버가 실행되고 있는지 확인해주세요.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚁 조류 탐지 시스템 - CSV 형식 테스트")
    print("=" * 60)
    
    # 서버 연결 확인
    if not check_server():
        exit(1)
    
    # CSV 샘플 테스트 실행
    test_csv_samples()
    
    # 시뮬레이션 테스트
    simulate_real_model_output()
    
    # CSV 파일이 있다면 로드해서 테스트
    csv_path = "detection_results.csv"
    if os.path.exists(csv_path):
        print(f"\n📁 로컬 CSV 파일 발견: {csv_path}")
        load_csv_file(csv_path)
    
    print("\n🎉 모든 테스트 완료!")
    print("\n💡 사용법:")
    print("   1. CSV 샘플 테스트: test_csv_samples()")
    print("   2. CSV 파일 로드: load_csv_file('your_file.csv')")
    print("   3. 개별 전송: send_csv_detection(detection_dict)")
