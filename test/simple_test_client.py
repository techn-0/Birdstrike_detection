"""
조류 탐지 시스템 - 간소화된 API 테스트 클라이언트
현재 프로젝트의 /detect 엔드포인트에 맞게 수정
"""

import requests
import json
import csv
from datetime import datetime
import random
import os

# 서버 URL 설정
SERVER_URL = "http://localhost:8000"

def send_detection_batch(detections_list, cctv_id="unknown"):
    """
    여러 탐지 결과를 배치로 전송 (DetectionCSV 형식)
    
    Args:
        detections_list: 탐지 결과 리스트
        cctv_id: CCTV ID
    
    Returns:
        bool: 전송 성공 여부
    """
    
    # DetectionBatch 형식으로 변환
    batch_data = {
        "detections": [],
        "cctv_id": cctv_id,
        "captured_at": datetime.now().isoformat()
    }
    
    for i, detection_data in enumerate(detections_list):
        x1 = float(detection_data.get("x1", 0))
        y1 = float(detection_data.get("y1", 0))
        x2 = float(detection_data.get("x2", 0))
        y2 = float(detection_data.get("y2", 0))
        
        # width, height, center 계산
        width = x2 - x1
        height = y2 - y1
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # DetectionCSV 형식 (API 스키마에 따른 필수 필드들)
        detection_csv = {
            "image_index": i,
            "image_path": f"/path/to/{detection_data.get('image_name', f'batch_image_{i}.jpg')}",
            "image_name": detection_data.get("image_name", f"batch_image_{i}.jpg"),
            "object_id": int(detection_data.get("object_id", 0)),
            "class_name": detection_data.get("class_name", "bird"),
            "class_id": 0,
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "confidence": float(detection_data.get("confidence", 0)),
            "width": width,
            "height": height,
            "center_x": center_x,
            "center_y": center_y,
            "cctv_id": detection_data.get("cctv_id", cctv_id),
            "captured_at": datetime.now().isoformat()
        }
        
        batch_data["detections"].append(detection_csv)
    
    try:
        # 배치 API 호출
        response = requests.post(
            f"{SERVER_URL}/detect/batch",
            json=batch_data,
            timeout=15
        )
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ 배치 탐지 결과 전송 성공: {len(detections_list)}개 항목")
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

def test_batch_detection():
    """배치 탐지 결과 테스트"""
    print("\n📦 배치 탐지 결과 테스트...")
    
    # 한 번에 여러 개의 탐지 결과 생성
    batch_detections = []
    
    for i in range(3):
        # 같은 CCTV에서 여러 조류 탐지
        x1 = random.uniform(100, 400)
        y1 = random.uniform(100, 300)
        width = random.uniform(10, 50)
        height = random.uniform(10, 40)
        
        detection = {
            "x1": round(x1, 2),
            "y1": round(y1, 2),
            "x2": round(x1 + width, 2),
            "y2": round(y1 + height, 2),
            "confidence": round(random.uniform(0.4, 0.9), 3),
            "image_name": f"batch_test_frame_{i+1}.jpg",
            "object_id": i,
            "class_name": "bird"
        }
        
        batch_detections.append(detection)
        print(f"  탐지 {i+1}: 신뢰도 {detection['confidence']}")
    
    # 배치로 전송
    success = send_detection_batch(batch_detections, "camera_01")
    
    if success:
        print("📊 배치 테스트 성공!")
    else:
        print("❌ 배치 테스트 실패")

def send_detection_result(detection_data):
    """
    탐지 결과를 서버로 전송 (Detection 모델 형식)
    
    Args:
        detection_data: 탐지 데이터
    
    Returns:
        bool: 전송 성공 여부
    """
    
    # Detection 모델에 맞는 데이터 형식으로 변환
    x1 = float(detection_data.get("x1", 0))
    y1 = float(detection_data.get("y1", 0))
    x2 = float(detection_data.get("x2", 0))
    y2 = float(detection_data.get("y2", 0))
    confidence = float(detection_data.get("confidence", 0))
    
    # bbox 배열 형식 [x1, y1, x2, y2]
    bbox = [x1, y1, x2, y2]
    
    # pos 배열 형식 [center_x, center_y] (정규화된 좌표)
    center_x = (x1 + x2) / 2
    center_y = (y1 + y2) / 2
    pos = [center_x, center_y]
    
    # risk 계산 (confidence 기반)
    if confidence >= 0.8:
        risk = "red"
    elif confidence >= 0.6:
        risk = "orange"
    elif confidence >= 0.4:
        risk = "yellow"
    else:
        risk = "green"
    
    # frame_url 생성
    image_name = detection_data.get("image_name", "unknown.jpg")
    frame_url = f"/frames/{image_name}" if image_name != "unknown.jpg" else None
    
    # CCTV ID 추론 또는 사용
    cctv_id = detection_data.get("cctv_id")
    if not cctv_id and image_name:
        if image_name.startswith("D01_"):
            cctv_id = "camera_01"
        elif image_name.startswith("D02_"):
            cctv_id = "camera_02"
        else:
            cctv_id = "unknown"
    
    if not cctv_id:
        cctv_id = "unknown"
    
    data = {
        "cctv_id": cctv_id,
        "bbox": bbox,
        "pos": pos,
        "risk": risk,
        "captured_at": datetime.now().isoformat(),
        "frame_url": frame_url,
        "bird_count": 1
    }
    
    try:
        # Detection API 호출
        response = requests.post(
            f"{SERVER_URL}/detect",
            json=data,
            timeout=10
        )
        
        # 응답 확인
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ 탐지 결과 전송 성공: {image_name} (위험도: {risk})")
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

def test_detection_samples():
    """첨부된 CSV 데이터 샘플 테스트"""
    print("🔍 탐지 데이터 샘플 테스트 시작...")
    
    # 첨부된 CSV 데이터에서 가져온 샘플들
    detection_samples = [
        {
            "image_name": "D02_20210628090856_0000714_crop_000.png",
            "object_id": 0,
            "class_name": "bird",
            "x1": 508.8328857421875,
            "y1": 534.927490234375,
            "x2": 524.5106201171875,
            "y2": 543.120849609375,
            "confidence": 0.27232813835144043,
            "cctv_id": "camera_02"  # D02로 시작하므로 camera_02로 추론
        },
        {
            "image_name": "D02_20210721142744_0001120_crop_007.png",
            "object_id": 0,
            "class_name": "bird",
            "x1": 108.12217712402344,
            "y1": 170.91787719726562,
            "x2": 112.88771057128906,
            "y2": 175.89199829101562,
            "confidence": 0.29926395416259766,
            "cctv_id": "camera_02"
        },
        {
            "image_name": "D02_20210721142744_0009499_crop_007.png",
            "object_id": 0,
            "class_name": "bird",
            "x1": 435.5831298828125,
            "y1": 167.29034423828125,
            "x2": 489.4793701171875,
            "y2": 208.7540283203125,
            "confidence": 0.2754083573818207,
            "cctv_id": "camera_02"
        }
    ]
    
    success_count = 0
    
    for i, sample in enumerate(detection_samples, 1):
        print(f"\n[{i}/3] 샘플 {i} 전송 중...")
        print(f"  이미지: {sample['image_name']}")
        print(f"  바운딩박스: [{sample['x1']:.1f}, {sample['y1']:.1f}, {sample['x2']:.1f}, {sample['y2']:.1f}]")
        print(f"  신뢰도: {sample['confidence']:.3f}")
        print(f"  CCTV: {sample['cctv_id']}")
        
        if send_detection_result(sample):
            success_count += 1
    
    print(f"\n📊 샘플 테스트 완료: {success_count}/3 성공")

def simulate_real_model_output():
    """실제 AI 모델 출력을 시뮬레이션"""
    print("\n🤖 AI 모델 출력 시뮬레이션...")
    
    # 실제 패턴과 유사한 시뮬레이션 데이터
    for i in range(5):
        # 랜덤한 탐지 결과 생성
        image_num = random.randint(1000, 9999)
        crop_num = random.randint(0, 10)
        
        # 이미지명 생성 (실제 패턴과 유사)
        camera_id = random.choice(["D01", "D02"])
        image_name = f"{camera_id}_20210{random.randint(601,801):03d}{random.randint(10,23):02d}{random.randint(10,59):02d}{random.randint(10,59):02d}_{image_num:07d}_crop_{crop_num:03d}.png"
        
        # 바운딩 박스 생성 (실제 범위와 유사)
        x1 = random.uniform(50, 500)
        y1 = random.uniform(50, 400)
        width = random.uniform(5, 50)
        height = random.uniform(5, 40)
        x2 = x1 + width
        y2 = y1 + height
        
        # 신뢰도 (실제 범위와 유사)
        confidence = random.uniform(0.25, 0.95)
        
        # CCTV ID 추론
        cctv_id = "camera_01" if camera_id == "D01" else "camera_02"
        
        simulation_data = {
            "image_name": image_name,
            "object_id": 0,
            "class_name": "bird",
            "x1": round(x1, 2),
            "y1": round(y1, 2),
            "x2": round(x2, 2),
            "y2": round(y2, 2),
            "confidence": round(confidence, 6),
            "cctv_id": cctv_id
        }
        
        print(f"\n🔍 시뮬레이션 #{i+1}: 신뢰도 {confidence:.3f}")
        print(f"   이미지: {image_name}")
        print(f"   CCTV: {cctv_id}")
        send_detection_result(simulation_data)

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
            
            # CSV 데이터를 API 형식으로 변환
            converted_detection = {
                "x1": float(detection['x1']),
                "y1": float(detection['y1']),
                "x2": float(detection['x2']),
                "y2": float(detection['y2']),
                "confidence": float(detection['confidence']),
                "image_name": detection['image_name'],
                "object_id": int(detection.get('object_id', 0)),
                "class_name": detection.get('class_name', 'bird')
            }
            
            # CCTV ID 추론 (이미지명에서)
            if detection['image_name'].startswith("D01_"):
                converted_detection['cctv_id'] = "camera_01"
            elif detection['image_name'].startswith("D02_"):
                converted_detection['cctv_id'] = "camera_02"
            else:
                converted_detection['cctv_id'] = "unknown"
            
            print(f"\n[{i+1}/{test_count}] CSV 행 {i+1} 처리 중...")
            print(f"  이미지: {detection['image_name']}")
            print(f"  신뢰도: {float(detection['confidence']):.3f}")
            print(f"  CCTV: {converted_detection['cctv_id']}")
            
            if send_detection_result(converted_detection):
                success_count += 1
        
        print(f"\n📊 CSV 파일 테스트 완료: {success_count}/{test_count} 성공")
        
    except Exception as e:
        print(f"❌ CSV 파일 처리 실패: {e}")

def convert_yolo_format(yolo_detection, image_width=640, image_height=480):
    """
    YOLO 형식의 탐지 결과를 API 형식으로 변환
    
    Args:
        yolo_detection: YOLO 형식 [class_id, center_x, center_y, width, height, confidence]
        image_width: 이미지 너비
        image_height: 이미지 높이
    
    Returns:
        dict: API 형식의 탐지 결과
    """
    class_id, center_x, center_y, width, height, confidence = yolo_detection
    
    # YOLO 정규화 좌표를 픽셀 좌표로 변환
    x1 = (center_x - width/2) * image_width
    y1 = (center_y - height/2) * image_height
    x2 = (center_x + width/2) * image_width
    y2 = (center_y + height/2) * image_height
    
    return {
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2,
        "confidence": confidence,
        "class_name": "bird" if class_id == 0 else f"class_{class_id}"
    }

def convert_coco_format(coco_detection):
    """
    COCO 형식의 탐지 결과를 API 형식으로 변환
    
    Args:
        coco_detection: COCO 형식 [x, y, width, height, confidence, class_id]
    
    Returns:
        dict: API 형식의 탐지 결과
    """
    x, y, width, height, confidence, class_id = coco_detection
    
    return {
        "x1": x,
        "y1": y,
        "x2": x + width,
        "y2": y + height,
        "confidence": confidence,
        "class_name": "bird" if class_id == 0 else f"class_{class_id}"
    }

def test_various_formats():
    """다양한 형식의 탐지 결과 테스트"""
    print("\n🔄 다양한 형식 변환 테스트...")
    
    # YOLO 형식 테스트
    print("\n📍 YOLO 형식 테스트")
    yolo_detections = [
        [0, 0.5, 0.5, 0.1, 0.1, 0.85],  # [class, center_x, center_y, width, height, conf]
        [0, 0.3, 0.4, 0.05, 0.08, 0.72]
    ]
    
    for i, yolo_det in enumerate(yolo_detections):
        converted = convert_yolo_format(yolo_det)
        converted["image_name"] = f"yolo_test_{i+1}.jpg"
        converted["cctv_id"] = "camera_01"
        
        print(f"  YOLO {i+1}: {yolo_det} -> 신뢰도 {converted['confidence']}")
        send_detection_result(converted)
    
    # COCO 형식 테스트
    print("\n📍 COCO 형식 테스트")
    coco_detections = [
        [100, 150, 50, 30, 0.78, 0],  # [x, y, w, h, conf, class]
        [200, 250, 40, 35, 0.65, 0]
    ]
    
    for i, coco_det in enumerate(coco_detections):
        converted = convert_coco_format(coco_det)
        converted["image_name"] = f"coco_test_{i+1}.jpg"
        converted["cctv_id"] = "camera_02"
        
        print(f"  COCO {i+1}: {coco_det} -> 신뢰도 {converted['confidence']}")
        send_detection_result(converted)

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
    print("🚁 조류 탐지 시스템 - 간소화된 API 테스트")
    print("=" * 60)
    
    # 서버 연결 확인
    if not check_server():
        exit(1)
    
    # 샘플 테스트 실행
    test_detection_samples()
    
    # 배치 테스트
    test_batch_detection()
    
    # 다양한 형식 테스트
    test_various_formats()
    
    # 시뮬레이션 테스트
    simulate_real_model_output()
    
    # CSV 파일이 있다면 로드해서 테스트
    csv_path = "detection_results.csv"
    if os.path.exists(csv_path):
        print(f"\n📁 로컬 CSV 파일 발견: {csv_path}")
        load_csv_file(csv_path)
    
    print("\n🎉 모든 테스트 완료!")
    print("\n💡 사용법:")
    print("   1. 샘플 테스트: test_detection_samples()")
    print("   2. 배치 테스트: test_batch_detection()")
    print("   3. 형식 변환 테스트: test_various_formats()")
    print("   4. CSV 파일 로드: load_csv_file('your_file.csv')")
    print("   5. 개별 전송: send_detection_result(detection_dict)")
    print("   6. 배치 전송: send_detection_batch(detections_list, cctv_id)")
    print("   7. 시뮬레이션: simulate_real_model_output()")
    print("   8. YOLO 변환: convert_yolo_format(yolo_detection)")
    print("   9. COCO 변환: convert_coco_format(coco_detection)")
    
    print("\n📋 API 형식:")
    print("   단일 탐지: POST /detect")
    print("   {")
    print("     'x1': float, 'y1': float, 'x2': float, 'y2': float,")
    print("     'confidence': float,")
    print("     'cctv_id': str (선택),")
    print("     'image_name': str (선택),")
    print("     'class_name': str (기본값: 'bird')")
    print("   }")
    print("")
    print("   배치 탐지: POST /detect/batch")
    print("   {")
    print("     'detections': [탐지결과배열],")
    print("     'cctv_id': str,")
    print("     'captured_at': str (선택)")
    print("   }")
    print("")
    print("💡 지원하는 입력 형식:")
    print("   - 직접 API 형식 (x1, y1, x2, y2)")
    print("   - CSV 형식 (detection_results.csv)")
    print("   - YOLO 형식 (정규화된 center_x, center_y, width, height)")
    print("   - COCO 형식 (x, y, width, height)")
