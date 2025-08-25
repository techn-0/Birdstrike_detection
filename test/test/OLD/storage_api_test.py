"""
조류 탐지 결과 저장 API 테스트 클라이언트

🎯 목적:
- 조류 탐지 모델의 결과를 백엔드 서버로 전송하는 API 테스트
- 실시간 탐지 결과와 배치 처리 결과 저장 기능 검증
- 탐지 모델 팀이 API 사용법을 이해하고 통합할 수 있도록 지원

📋 주요 기능:
1. 개별 탐지 결과 저장 (/detect/result)
2. 배치 탐지 결과 저장 (/detect/batch) 
3. 탐지 내역 조회 (/detect/history/{cctv_id})
4. CSV 파일 기반 테스트 데이터 처리

🔧 사용 방법:
1. 백엔드 서버 실행 (http://localhost:8000)
2. detection_results.csv 파일 준비
3. python storage_api_test.py 실행

💡 탐지 모델 팀 참고사항:
- 탐지 결과는 JSON 형태로 HTTP POST 요청
- 바운딩 박스는 [x, y, width, height] 형식
- 신뢰도(confidence)에 따라 위험도 자동 분류
- 실시간 처리용 개별 API와 배치 처리용 API 제공
"""

import requests
import csv
import json
from datetime import datetime, timezone
import os
import time
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class DetectionStorageTester:
    """
    조류 탐지 결과 저장 API 테스트 클래스
    
    🎯 탐지 모델 팀을 위한 API 통합 가이드:
    
    1. 실시간 탐지 결과 전송:
       - 단일 탐지 결과를 즉시 서버로 전송
       - API: POST /detect/result
       - 용도: 실시간 모니터링, 즉시 알림
    
    2. 배치 탐지 결과 전송:
       - 여러 탐지 결과를 한 번에 전송
       - API: POST /detect/batch
       - 용도: 영상 분석 완료 후 일괄 처리
    
    3. 탐지 내역 조회:
       - 특정 카메라의 탐지 기록 조회
       - API: GET /detect/history/{cctv_id}
       - 용도: 분석 결과 확인, 통계 생성
    
    📝 데이터 형식:
    - 바운딩 박스: [x, y, width, height] (픽셀 단위)
    - 중심점: [center_x, center_y] (픽셀 단위)
    - 신뢰도: 0.0 ~ 1.0 범위의 float
    - 시간: ISO 8601 형식 (예: 2025-08-15T12:34:56.789Z)
    """
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
        # 기본 헤더 설정
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def load_csv_data(self, csv_file_path: str = "detection_results.csv") -> List[Dict]:
        """
        CSV 파일에서 탐지 결과 데이터 로딩
        
        Args:
            csv_file_path: CSV 파일 경로
        
        Returns:
            List[Dict]: 탐지 결과 리스트
        """
        if not os.path.exists(csv_file_path):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file_path}")
            return []
        
        detections = []
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                for row in csv_reader:
                    detection = {
                        "image_index": int(row['image_index']),
                        "image_path": row['image_path'],
                        "image_name": row['image_name'],
                        "object_id": int(row['object_id']),
                        "class_name": row['class_name'],
                        "class_id": int(row['class_id']),
                        "x1": float(row['x1']),
                        "y1": float(row['y1']),
                        "x2": float(row['x2']),
                        "y2": float(row['y2']),
                        "confidence": float(row['confidence']),
                        "width": float(row['width']),
                        "height": float(row['height']),
                        "center_x": float(row['center_x']),
                        "center_y": float(row['center_y'])
                    }
                    detections.append(detection)
            
            print(f"📂 CSV 파일 로딩 완료: {len(detections)}개 탐지 결과")
            return detections
            
        except Exception as e:
            print(f"❌ CSV 파일 로딩 중 오류: {e}")
            return []
    
    def convert_csv_to_detection_format(self, csv_detection: Dict, cctv_id: str) -> Dict:
        """
        CSV 형식을 Detection API 형식으로 변환
        
        🔧 탐지 모델 팀 참고:
        이 함수는 탐지 모델의 출력을 API 형식으로 변환하는 예시입니다.
        실제 탐지 모델에서는 다음과 같이 데이터를 준비하세요:
        
        📊 입력 데이터 (탐지 모델 출력):
        - 바운딩 박스 좌표 (x1, y1, x2, y2)
        - 신뢰도 점수 (confidence)
        - 클래스 정보 (class_name, class_id)
        
        📤 출력 데이터 (API 전송 형식):
        - bbox: [x, y, width, height] 형식
        - pos: [center_x, center_y] 형식
        - risk: 신뢰도 기반 위험도 등급
        
        Args:
            csv_detection: CSV 탐지 데이터
            cctv_id: 카메라 ID (예: "airport_cam_01")
        
        Returns:
            Dict: Detection API 형식 데이터
        """
        # 바운딩 박스를 [x, y, w, h] 형식으로 변환
        # 🔧 탐지 모델팀: x1,y1은 좌상단, x2,y2는 우하단 좌표
        bbox = [
            csv_detection['x1'],
            csv_detection['y1'],
            csv_detection['width'],
            csv_detection['height']
        ]
        
        # 중심점을 pos로 사용
        # 🔧 탐지 모델팀: 객체의 중심 좌표 (추적에 사용)
        pos = [csv_detection['center_x'], csv_detection['center_y']]
        
        # 신뢰도 기반 위험도 설정
        # 🚨 탐지 모델팀: 신뢰도에 따른 자동 위험도 분류
        # - red: 높은 신뢰도 (즉시 경보)
        # - orange: 중간 신뢰도 (주의 필요)
        # - yellow: 낮은 신뢰도 (모니터링)
        # - green: 매우 낮은 신뢰도 (참고용)
        confidence = csv_detection['confidence']
        if confidence >= 0.8:
            risk = "red"      # 🔴 즉시 경보 (신뢰도 80% 이상)
        elif confidence >= 0.6:
            risk = "orange"   # 🟠 주의 필요 (신뢰도 60-80%)
        elif confidence >= 0.4:
            risk = "yellow"   # 🟡 모니터링 (신뢰도 40-60%)
        else:
            risk = "green"    # 🟢 참고용 (신뢰도 40% 미만)
        
        # API 전송용 데이터 구성
        detection_data = {
            "cctv_id": cctv_id,                                    # 카메라 식별자
            "bbox": bbox,                                          # 바운딩 박스 [x,y,w,h]
            "pos": pos,                                            # 중심점 [x,y]
            "risk": risk,                                          # 위험도 등급
            "captured_at": datetime.now(timezone.utc).isoformat(), # 탐지 시간 (UTC)
            "frame_url": f"frames/{csv_detection['image_name']}",  # 프레임 이미지 URL
            "bird_count": 1                                        # 탐지된 조류 수
        }
        
        return detection_data
    
    def test_batch_storage_api(self, csv_file_path: str = "detection_results.csv", 
                              cctv_id: str = "camera_01") -> bool:
        """
        CSV 배치 저장 API 테스트 (/detect/batch)
        
        🎯 탐지 모델팀 사용법:
        이 API는 한 번에 여러 탐지 결과를 전송할 때 사용합니다.
        
        📝 사용 시나리오:
        1. 영상 파일 전체 분석 완료 후 결과 전송
        2. 오프라인 배치 처리 결과 업로드
        3. 대량의 과거 데이터 처리
        
        🔧 API 호출 방법:
        ```python
        # 예시: 탐지 모델에서 배치 결과 전송
        import requests
        
        # 탐지 결과 리스트 준비
        detection_results = [
            {
                "image_index": 1,
                "image_name": "frame_001.jpg",
                "x1": 100, "y1": 150, "x2": 200, "y2": 250,
                "confidence": 0.85,
                "class_name": "bird",
                "width": 100, "height": 100,
                "center_x": 150, "center_y": 200
            },
            # ... 더 많은 탐지 결과
        ]
        
        # 배치 데이터 구성
        batch_data = {
            "detections": detection_results,
            "cctv_id": "airport_cam_01",
            "captured_at": "2025-08-15T12:34:56.789Z"
        }
        
        # API 호출
        response = requests.post(
            "http://localhost:8000/detect/batch",
            json=batch_data
        )
        ```
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
        
        Returns:
            bool: 테스트 성공 여부
        """
        print(f"\n🔄 CSV 배치 저장 API 테스트 시작")
        print(f"   파일: {csv_file_path}")
        print(f"   카메라 ID: {cctv_id}")
        
        detections = self.load_csv_data(csv_file_path)
        if not detections:
            return False
        
        # DetectionBatch 형식으로 데이터 구성
        batch_data = {
            "detections": detections,
            "cctv_id": cctv_id,
            "captured_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            print(f"📡 배치 저장 요청 전송 중... ({len(detections)}개)")
            
            response = self.session.post(
                f"{self.server_url}/detect/batch",
                json=batch_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 배치 저장 성공!")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 배치 저장 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 배치 저장 API 테스트 중 오류: {e}")
            return False
    
    def test_individual_storage_api(self, csv_detection: Dict, cctv_id: str) -> bool:
        """
        개별 탐지 결과 저장 API 테스트 (/detect/result)
        
        🎯 탐지 모델팀 사용법:
        이 API는 실시간으로 개별 탐지 결과를 전송할 때 사용합니다.
        
        📝 사용 시나리오:
        1. 실시간 CCTV 모니터링
        2. 즉시 경보가 필요한 상황
        3. 스트리밍 처리 중 탐지 결과
        
        🔧 API 호출 방법:
        ```python
        # 예시: 탐지 모델에서 실시간 결과 전송
        import requests
        from datetime import datetime, timezone
        
        # 단일 탐지 결과 데이터 준비
        detection_data = {
            "cctv_id": "airport_cam_01",           # 카메라 ID
            "bbox": [100, 150, 100, 100],          # [x, y, width, height]
            "pos": [150, 200],                     # [center_x, center_y]
            "risk": "red",                         # 위험도: red/orange/yellow/green
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": "frames/frame_001.jpg",   # 프레임 이미지 경로
            "bird_count": 1                        # 탐지된 조류 수
        }
        
        # API 호출
        response = requests.post(
            "http://localhost:8000/detect/result",
            json=detection_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("탐지 결과 저장 성공!")
            result = response.json()
            print(f"저장된 ID: {result.get('id')}")
        ```
        
        ⚠️ 중요사항:
        - 실시간 처리시 네트워크 지연 고려
        - 높은 신뢰도(0.8+)일 때만 red 등급 사용 권장
        - 프레임 이미지는 별도 저장소에 업로드 후 URL 제공
        
        Args:
            csv_detection: CSV 탐지 데이터
            cctv_id: 카메라 ID
        
        Returns:
            bool: 테스트 성공 여부
        """
        detection_data = self.convert_csv_to_detection_format(csv_detection, cctv_id)
        
        try:
            print(f"🔍 개별 저장 API 테스트:")
            print(f"   이미지: {csv_detection['image_name']}")
            print(f"   신뢰도: {csv_detection['confidence']:.3f}")
            print(f"   위험도: {detection_data['risk']}")
            
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 개별 저장 성공!")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 개별 저장 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 개별 저장 API 테스트 중 오류: {e}")
            return False
    
    def test_sequential_storage_api(self, csv_file_path: str = "detection_results.csv",
                                  cctv_id: str = "camera_01", delay: float = 0.5,
                                  max_count: Optional[int] = None) -> Tuple[int, int]:
        """
        CSV 파일의 탐지 결과를 개별 저장 API로 순차 전송
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
            delay: 전송 간격 (초)
            max_count: 최대 전송 개수 (None이면 전체)
        
        Returns:
            Tuple[int, int]: (성공 개수, 전체 개수)
        """
        print(f"\n🔄 순차 저장 API 테스트 시작")
        print(f"   파일: {csv_file_path}")
        print(f"   카메라 ID: {cctv_id}")
        print(f"   전송 간격: {delay}초")
        
        detections = self.load_csv_data(csv_file_path)
        if not detections:
            return 0, 0
        
        # 전송할 개수 제한
        if max_count:
            detections = detections[:max_count]
            print(f"   전송 제한: {len(detections)}개")
        
        success_count = 0
        total_count = len(detections)
        
        try:
            for i, detection in enumerate(detections, 1):
                print(f"\n[{i}/{total_count}] 개별 저장 테스트")
                
                if self.test_individual_storage_api(detection, cctv_id):
                    success_count += 1
                
                if delay > 0 and i < total_count:
                    print(f"⏳ {delay}초 대기...")
                    time.sleep(delay)
            
            print(f"\n📊 순차 저장 완료: {success_count}/{total_count} 성공")
            success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
            print(f"   성공률: {success_rate:.1f}%")
            
            return success_count, total_count
            
        except Exception as e:
            print(f"❌ 순차 저장 테스트 중 오류: {e}")
            return success_count, total_count
    
    def test_detection_history_api(self, cctv_id: str) -> bool:
        """
        탐지 내역 조회 API 테스트 (/detect/history/{cctv_id})
        
        🎯 탐지 모델팀 사용법:
        이 API는 특정 카메라의 탐지 기록을 조회할 때 사용합니다.
        
        📝 사용 시나리오:
        1. 탐지 모델 성능 분석
        2. 과거 탐지 결과 통계 생성
        3. 특정 시간대 탐지 패턴 분석
        4. 모델 정확도 검증
        
        🔧 API 호출 방법:
        ```python
        # 예시: 특정 카메라의 탐지 내역 조회
        import requests
        
        cctv_id = "airport_cam_01"
        response = requests.get(
            f"http://localhost:8000/detect/history/{cctv_id}",
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            history = response.json()
            print(f"총 {len(history)}개의 탐지 기록")
            
            for detection in history:
                print(f"시간: {detection['captured_at']}")
                print(f"위험도: {detection['risk']}")
                print(f"위치: {detection['bbox']}")
                print("---")
        ```
        
        📊 응답 데이터 구조:
        ```json
        [
            {
                "id": "unique_detection_id",
                "cctv_id": "airport_cam_01",
                "bbox": [100, 150, 100, 100],
                "pos": [150, 200],
                "risk": "red",
                "captured_at": "2025-08-15T12:34:56.789Z",
                "frame_url": "frames/frame_001.jpg",
                "bird_count": 1,
                "created_at": "2025-08-15T12:34:57.123Z"
            }
        ]
        ```
        
        Args:
            cctv_id: 카메라 ID
        
        Returns:
            bool: 테스트 성공 여부
        """
        print(f"\n🔍 탐지 내역 조회 API 테스트")
        print(f"   카메라 ID: {cctv_id}")
        
        try:
            response = self.session.get(
                f"{self.server_url}/detect/history/{cctv_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                history = response.json()
                print(f"✅ 내역 조회 성공!")
                print(f"   저장된 탐지 결과: {len(history)}개")
                
                if history:
                    print(f"   최신 탐지: {history[0].get('captured_at', 'N/A')}")
                    print(f"   첫 번째 결과 예시:")
                    for key, value in list(history[0].items())[:5]:  # 처음 5개 필드만 표시
                        print(f"     {key}: {value}")
                    if len(history[0]) > 5:
                        print(f"     ... 및 {len(history[0]) - 5}개 필드 더")
                
                return True
            else:
                print(f"❌ 내역 조회 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 내역 조회 API 테스트 중 오류: {e}")
            return False
    
    def test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            print(f"🔗 서버 연결 테스트: {self.server_url}")
            response = self.session.get(f"{self.server_url}/ping", timeout=5)
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 서버 연결 성공!")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 서버 응답 오류: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            print("   서버가 실행 중인지 확인해주세요.")
            return False
    
    def upload_image(self, image_path: str) -> Optional[str]:
        """
        이미지 파일을 서버에 업로드
        
        Args:
            image_path: 업로드할 이미지 파일 경로
        
        Returns:
            Optional[str]: 업로드된 이미지의 URL (실패시 None)
        """
        try:
            if not os.path.exists(image_path):
                print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
                return None
            
            print(f"📤 이미지 업로드 중: {os.path.basename(image_path)}")
            
            with open(image_path, 'rb') as file:
                files = {'file': (os.path.basename(image_path), file, 'image/png')}
                response = requests.post(
                    f"{self.server_url}/upload/image",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    print(f"✅ 이미지 업로드 성공!")
                    print(f"   파일명: {result.get('filename')}")
                    print(f"   URL: {result.get('url')}")
                    print(f"   크기: {result.get('size')} bytes")
                    return result.get('url')
                else:
                    print(f"❌ 이미지 업로드 실패: {result}")
                    return None
            else:
                print(f"❌ 이미지 업로드 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 이미지 업로드 중 오류: {e}")
            return None
    
    def test_image_upload_detection(self, csv_detection: Dict, cctv_id: str, 
                                   image_dir: str = "detection_image") -> bool:
        """
        이미지를 업로드하고 탐지 결과 저장하는 통합 테스트
        
        Args:
            csv_detection: CSV 탐지 데이터
            cctv_id: 카메라 ID
            image_dir: 이미지 파일들이 있는 디렉토리
        
        Returns:
            bool: 테스트 성공 여부
        """
        try:
            # 이미지 파일 경로 생성
            image_path = os.path.join(image_dir, csv_detection['image_name'])
            
            print(f"\n🖼️  이미지 업로드 및 탐지 결과 저장 테스트")
            print(f"   이미지: {csv_detection['image_name']}")
            print(f"   신뢰도: {csv_detection['confidence']:.3f}")
            
            # 1. 이미지 업로드
            uploaded_url = self.upload_image(image_path)
            if not uploaded_url:
                print("❌ 이미지 업로드 실패로 테스트 중단")
                return False
            
            # 2. 탐지 결과 데이터 준비 (업로드된 이미지 URL 사용)
            detection_data = self.convert_csv_to_detection_format(csv_detection, cctv_id)
            detection_data['frame_url'] = uploaded_url  # 업로드된 URL로 교체
            
            # 3. 탐지 결과 저장
            print(f"💾 탐지 결과 저장 중...")
            
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 이미지 포함 탐지 결과 저장 성공!")
                print(f"   위험도: {detection_data['risk']}")
                print(f"   이미지 URL: {uploaded_url}")
                print(f"   응답: {result}")
                return True
            else:
                print(f"❌ 탐지 결과 저장 실패: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 이미지 업로드 및 탐지 결과 저장 중 오류: {e}")
            return False
    
    def test_batch_with_image_upload(self, csv_file_path: str = "detection_results.csv",
                                    cctv_id: str = "camera_01", 
                                    image_dir: str = "detection_image",
                                    max_count: int = 3) -> bool:
        """
        여러 이미지를 업로드하고 배치로 탐지 결과 저장하는 테스트
        
        Args:
            csv_file_path: CSV 파일 경로
            cctv_id: 카메라 ID
            image_dir: 이미지 디렉토리
            max_count: 최대 처리할 이미지 수
        
        Returns:
            bool: 테스트 성공 여부
        """
        print(f"\n📦 이미지 업로드 배치 테스트 시작")
        print(f"   CSV 파일: {csv_file_path}")
        print(f"   이미지 디렉토리: {image_dir}")
        print(f"   카메라 ID: {cctv_id}")
        print(f"   최대 처리 수: {max_count}")
        
        detections = self.load_csv_data(csv_file_path)
        if not detections:
            return False
        
        # 처리할 개수 제한
        detections = detections[:max_count]
        
        success_count = 0
        
        try:
            for i, detection in enumerate(detections, 1):
                print(f"\n[{i}/{len(detections)}] 이미지 업로드 및 저장")
                
                if self.test_image_upload_detection(detection, f"{cctv_id}_batch_{i}", image_dir):
                    success_count += 1
                
                # 서버 부하 방지를 위한 대기
                if i < len(detections):
                    print("⏳ 1초 대기...")
                    time.sleep(1)
            
            print(f"\n📊 배치 이미지 업로드 완료: {success_count}/{len(detections)} 성공")
            success_rate = (success_count / len(detections)) * 100 if len(detections) > 0 else 0
            print(f"   성공률: {success_rate:.1f}%")
            
            return success_count == len(detections)
            
        except Exception as e:
            print(f"❌ 배치 이미지 업로드 테스트 중 오류: {e}")
            return False
    
    def create_sample_detection(self, image_name: str = "sample_bird.jpg", 
                              confidence: float = 0.75) -> Dict:
        """
        샘플 탐지 결과 생성
        
        Args:
            image_name: 이미지 파일명
            confidence: 신뢰도
        
        Returns:
            Dict: 샘플 탐지 데이터
        """
        return {
            "image_index": 999,
            "image_path": f"sample/{image_name}",
            "image_name": image_name,
            "object_id": 0,
            "class_name": "bird",
            "class_id": 0,
            "x1": 100.0,
            "y1": 150.0,
            "x2": 200.0,
            "y2": 250.0,
            "confidence": confidence,
            "width": 100.0,
            "height": 100.0,
            "center_x": 150.0,
            "center_y": 200.0
        }
    
    def run_comprehensive_test(self, csv_file_path: str = "detection_results.csv") -> Dict[str, bool]:
        """
        전체 저장 API 종합 테스트 실행
        
        Args:
            csv_file_path: CSV 파일 경로
        
        Returns:
            Dict[str, bool]: 각 테스트 결과
        """
        results = {}
        
        print("=" * 60)
        print("🧪 조류 탐지 결과 저장 API 종합 테스트")
        print("=" * 60)
        
        # 1. 서버 연결 테스트
        print("\n1️⃣ 서버 연결 테스트")
        print("-" * 40)
        results['connection'] = self.test_server_connection()
        
        if not results['connection']:
            print("\n❌ 서버 연결 실패로 테스트를 중단합니다.")
            return results
        
        # 2. 개별 샘플 저장 테스트
        print("\n2️⃣ 개별 샘플 저장 테스트")
        print("-" * 40)
        sample_detection = self.create_sample_detection("test_sample.jpg", 0.85)
        results['individual_sample'] = self.test_individual_storage_api(sample_detection, "test_camera")
        
        # 3. CSV 배치 저장 테스트
        print("\n3️⃣ CSV 배치 저장 테스트")
        print("-" * 40)
        results['batch_storage'] = self.test_batch_storage_api(csv_file_path, "camera_batch")
        
        # 4. CSV 순차 저장 테스트 (처음 3개만)
        print("\n4️⃣ CSV 순차 저장 테스트 (제한적)")
        print("-" * 40)
        success, total = self.test_sequential_storage_api(csv_file_path, "camera_sequential", 
                                                         delay=1.0, max_count=3)
        results['sequential_storage'] = (success == total and total > 0)
        
        # 5. 탐지 내역 조회 테스트
        print("\n5️⃣ 탐지 내역 조회 테스트")
        print("-" * 40)
        results['history_query'] = self.test_detection_history_api("camera_batch")
        
        # 6. 이미지 업로드 및 탐지 결과 저장 테스트 (NEW!)
        print("\n6️⃣ 이미지 업로드 및 탐지 결과 저장 테스트")
        print("-" * 40)
        if os.path.exists("detection_image"):
            detections = self.load_csv_data(csv_file_path)
            if detections:
                results['image_upload'] = self.test_image_upload_detection(
                    detections[0], "camera_with_image", "detection_image"
                )
            else:
                results['image_upload'] = False
                print("❌ CSV 데이터 로딩 실패")
        else:
            results['image_upload'] = False
            print("❌ detection_image 디렉토리를 찾을 수 없습니다")
        
        # 7. 배치 이미지 업로드 테스트 (NEW!)
        print("\n7️⃣ 배치 이미지 업로드 테스트")
        print("-" * 40)
        if os.path.exists("detection_image"):
            results['batch_image_upload'] = self.test_batch_with_image_upload(
                csv_file_path, "camera_batch_images", "detection_image", max_count=2
            )
        else:
            results['batch_image_upload'] = False
            print("❌ detection_image 디렉토리를 찾을 수 없습니다")
        
        # 8. 이미지가 포함된 탐지 내역 조회 테스트
        print("\n8️⃣ 이미지 포함 탐지 내역 조회 테스트")
        print("-" * 40)
        results['history_with_images'] = self.test_detection_history_api("camera_with_image")
        
        # 9. 다른 카메라 내역 조회 테스트
        print("\n9️⃣ 기존 카메라 내역 조회 테스트")
        print("-" * 40)
        results['history_query_2'] = self.test_detection_history_api("camera_sequential")
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        passed = 0
        total_tests = len(results)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            print(f"   {test_name}: {status}")
            if passed_test:
                passed += 1
        
        print(f"\n총 {passed}/{total_tests}개 테스트 통과 ({(passed/total_tests)*100:.1f}%)")
        
        if passed == total_tests:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 로그를 확인해주세요.")
        
        return results

def main():
    """
    메인 테스트 실행 함수
    
    🎯 탐지 모델팀을 위한 실행 가이드:
    
    1. 테스트 준비:
       ```bash
       # 백엔드 서버 실행
       cd backend
       python -m uvicorn app.main:app --reload --port 8000
       
       # 테스트 파일 실행
       cd test
       python storage_api_test.py
       ```
    
    2. 실제 탐지 모델 통합시:
       ```python
       # 탐지 모델 코드에서 API 호출 예시
       from storage_api_test import DetectionStorageTester
       
       # API 클라이언트 초기화
       api_client = DetectionStorageTester("http://localhost:8000")
       
       # 탐지 결과를 API 형식으로 변환 후 전송
       detection_result = {
           "cctv_id": "your_camera_id",
           "bbox": [x, y, width, height],
           "pos": [center_x, center_y],
           "risk": "red",  # 신뢰도에 따라 설정
           "captured_at": current_time,
           "frame_url": frame_image_url,
           "bird_count": detected_bird_count
       }
       
       # 실시간 전송
       api_client.test_individual_storage_api(detection_result, "camera_id")
       ```
    
    📞 연락처:
    - API 관련 문의: 백엔드 팀
    - 데이터 형식 문의: 이 테스트 코드 참조
    - 통합 지원: 프로젝트 관리자
    """
    
    # 테스터 초기화
    tester = DetectionStorageTester("http://localhost:8000")
    
    # 종합 테스트 실행
    results = tester.run_comprehensive_test("detection_results.csv")
    
    # 추가 개별 테스트 예제
    if results.get('connection', False):
        print("\n" + "=" * 60)
        print("🔧 추가 개별 테스트 예제")
        print("=" * 60)
        
        # 고신뢰도 샘플 테스트
        print("\n🔥 고신뢰도 탐지 결과 테스트")
        high_conf_sample = tester.create_sample_detection("high_confidence_bird.jpg", 0.95)
        tester.test_individual_storage_api(high_conf_sample, "camera_high_conf")
        
        # 저신뢰도 샘플 테스트
        print("\n🟡 저신뢰도 탐지 결과 테스트")
        low_conf_sample = tester.create_sample_detection("low_confidence_bird.jpg", 0.35)
        tester.test_individual_storage_api(low_conf_sample, "camera_low_conf")
        
        # 프론트엔드 확인 가이드 추가
        print("\n" + "=" * 60)
        print("🌐 프론트엔드에서 이미지 확인 방법")
        print("=" * 60)
        print("""
📋 프론트엔드에서 탐지 결과 이미지 확인:

1. 프론트엔드 서버 실행:
   cd frontend
   npm start

2. 브라우저에서 http://localhost:3000 접속

3. 지도에서 다음 카메라들을 클릭하여 탐지 내역 확인:
   - camera_with_image (이미지 업로드 테스트)
   - camera_batch_images_1, camera_batch_images_2 (배치 이미지 테스트)
   - camera_batch (기존 배치 테스트)

4. 탐지 결과 모달에서 이미지가 정상 표시되는지 확인

🔍 디버깅 방법:
- 브라우저 개발자 도구 (F12) → Network 탭에서 이미지 로딩 확인
- Console 탭에서 에러 메시지 확인
- 이미지 URL 직접 접속: http://localhost:8000/frames/파일명.png

⚠️  주의사항:
- 백엔드 서버가 계속 실행 중이어야 합니다
- 이미지 파일이 backend/app/static/frames 디렉토리에 있어야 합니다
- CORS 설정이 올바르게 되어 있어야 합니다
        """)
        
        # 이미지 URL 테스트
        print("🔗 업로드된 이미지 URL 접근 테스트:")
        try:
            response = requests.get(f"{tester.server_url}/frames/")
            print(f"   정적 파일 서빙 상태: HTTP {response.status_code}")
        except:
            print("   정적 파일 서빙 확인 실패")
            
        # 샘플 이미지 URL 확인
        for camera_id in ["camera_with_image", "camera_batch_images_1"]:
            print(f"\n📷 {camera_id} 탐지 내역에서 이미지 URL 확인:")
            try:
                response = requests.get(f"{tester.server_url}/detect/history/{camera_id}")
                if response.status_code == 200:
                    history = response.json()
                    if history and len(history) > 0:
                        frame_url = history[0].get('frame_url')
                        if frame_url:
                            full_url = f"{tester.server_url}{frame_url}"
                            img_response = requests.head(full_url)
                            status = "✅ 접근 가능" if img_response.status_code == 200 else "❌ 접근 불가"
                            print(f"   이미지 URL: {full_url} - {status}")
                        else:
                            print("   ❌ frame_url이 없습니다")
                    else:
                        print("   ❌ 탐지 내역이 없습니다")
                else:
                    print(f"   ❌ 내역 조회 실패: {response.status_code}")
            except Exception as e:
                print(f"   ❌ 확인 중 오류: {e}")

if __name__ == "__main__":
    """
    🚀 테스트 실행부
    
    💡 탐지 모델팀 참고:
    이 스크립트를 실행하면 다음과 같은 순서로 테스트가 진행됩니다:
    
    1. ✅ 서버 연결 확인
    2. 🔍 개별 탐지 결과 저장 테스트
    3. 📦 배치 탐지 결과 저장 테스트  
    4. 🔄 순차 전송 테스트
    5. 📊 탐지 내역 조회 테스트
    
    각 테스트는 실제 API 호출 방법을 보여주므로,
    탐지 모델 통합시 이 코드를 참고하여 구현하세요.
    
    🔧 실행 전 확인사항:
    - 백엔드 서버가 http://localhost:8000에서 실행 중인지 확인
    - detection_results.csv 파일이 test 폴더에 있는지 확인
    - 네트워크 연결 상태 확인
    """
    main()
