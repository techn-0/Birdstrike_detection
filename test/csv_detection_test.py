import requests
import csv
import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil

class CSVDetectionTester:
    """CSV 기반 탐지 결과 테스트 클래스"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # 이미지 디렉토리 경로
        self.image_dir = Path("detection_image")
        if not self.image_dir.exists():
            print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {self.image_dir}")
            sys.exit(1)
        
        # CCTV 메타데이터 캐시
        self.cctv_metadata = {}
    
    def extract_cctv_id_from_image_name(self, image_name: str) -> str:
        """이미지 이름에서 CCTV ID 추출"""
        if "0008246" in image_name:
            return "cctv_1"
        elif "0009630" in image_name:
            return "cctv_2"
        else:
            return "AIRPORT_CAM_D02_DEFAULT"
    
    def get_cctv_metadata(self, cctv_id: str) -> Optional[Dict]:
        """CCTV 메타데이터 조회 (해상도 정보 포함)"""
        if cctv_id in self.cctv_metadata:
            return self.cctv_metadata[cctv_id]
        
        try:
            response = self.session.get(f"{self.server_url}/cctv/meta/{cctv_id}")
            if response.status_code == 200:
                metadata = response.json()
                self.cctv_metadata[cctv_id] = metadata
                return metadata
            else:
                print(f"⚠️ CCTV 메타데이터 조회 실패: {cctv_id}")
                return None
        except Exception as e:
            print(f"❌ CCTV 메타데이터 조회 오류: {e}")
            return None
    
    def get_image_resolution(self, cctv_id: str) -> Tuple[float, float]:
        """CCTV 해상도 정보 가져오기"""
        metadata = self.cctv_metadata.get(cctv_id)
        
        if metadata and metadata.get('resolution'):
            width, height = metadata['resolution']
            print(f"   📐 {cctv_id} 해상도: {width}x{height} (메타데이터)")
            return float(width), float(height)
        else:
            # 기본값 (표준 FHD)
            print(f"   📐 {cctv_id} 해상도: 1920x1080 (기본값)")
            return 1920.0, 1080.0
    
    def calculate_risk_by_count_and_confidence(self, bird_count: int, max_confidence: float = 0.0) -> str:
        """
        DetectionService와 동일한 위험도 계산 로직
        - Green: 객체 탐지 안됨 (bird_count = 0)
        - Yellow: 1개 객체 + confidence < 30%
        - Orange: 1개 객체 + confidence ≥ 30%
        - Red: 2개 이상의 조류 탐지
        """
        if bird_count == 0:
            return "green"  # 미탐지
        elif bird_count == 1:
            if max_confidence < 0.30:  # 30% 미만
                return "yellow"  # 모니터링 대상
            else:
                return "orange"  # 주의 필요
        else:  # bird_count >= 2
            return "red"  # 즉시 경보 필요
        
    def load_csv_detections(self, csv_file: str = "detection_results.csv") -> List[Dict]:
        """CSV 파일에서 탐지 결과 로딩"""
        detections = []
        
        if not os.path.exists(csv_file):
            print(f"❌ CSV 파일을 찾을 수 없습니다: {csv_file}")
            return []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 숫자 필드 변환
                    detection = {
                        'image_index': int(row['image_index']),
                        'image_name': row['image_name'],
                        'object_id': int(row['object_id']),
                        'class_name': row['class_name'],
                        'confidence': float(row['confidence']),
                        'x1': float(row['x1']),
                        'y1': float(row['y1']),
                        'x2': float(row['x2']),
                        'y2': float(row['y2']),
                        'width': float(row['width']),
                        'height': float(row['height']),
                        'center_x': float(row['center_x']),
                        'center_y': float(row['center_y'])
                    }
                    detections.append(detection)
            
            print(f"✅ CSV에서 {len(detections)}개의 탐지 결과를 로딩했습니다.")
            return detections
            
        except Exception as e:
            print(f"❌ CSV 파일 로딩 실패: {e}")
            return []
    
    def upload_image(self, image_path: Path) -> Optional[str]:
        """이미지 파일 업로드"""
        if not image_path.exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
        
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/png')}
                headers = {k: v for k, v in self.session.headers.items() if k.lower() != 'content-type'}
                response = requests.post(
                    f"{self.server_url}/upload/image",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    print(f"✅ 이미지 업로드 성공: {image_path.name} -> {result['url']}")
                    return result['url']
            
            print(f"❌ 이미지 업로드 실패: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"❌ 이미지 업로드 오류: {e}")
            return None

    def create_detection_with_objects_array(self, image_detections: List[Dict], cctv_id: str, frame_url: str) -> Dict:
        """
        올바른 API 스키마에 맞는 탐지 결과 생성
        - 기본 Detection 모델 준수
        - objects 배열은 별도 필드로 추가
        """
        # CCTV 해상도 정보 가져오기
        image_width, image_height = self.get_image_resolution(cctv_id)
        
        # 개별 객체 정보 수집
        objects = []
        confidences = []
        class_counts = {}
        
        for detection in image_detections:
            # 개별 객체 정보 (상대좌표로 정규화)
            obj_info = {
                "object_id": detection['object_id'],
                "class_name": detection['class_name'],
                "confidence": detection['confidence'],
                "bbox": [
                    detection['x1'] / image_width,    # x 정규화
                    detection['y1'] / image_height,   # y 정규화  
                    detection['width'] / image_width, # width 정규화
                    detection['height'] / image_height # height 정규화
                ],
                "pos": [
                    detection['center_x'] / image_width,   # u (수평 상대좌표)
                    detection['center_y'] / image_height   # v (수직 상대좌표)
                ]
            }
            objects.append(obj_info)
            
            # 신뢰도 수집
            confidences.append(detection['confidence'])
            
            # 클래스별 카운트
            class_name = detection['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # 위험도 계산 (DetectionService와 동일한 로직)
        total_objects = len(image_detections)
        max_confidence = max(confidences) if confidences else 0.0
        risk = self.calculate_risk_by_count_and_confidence(total_objects, max_confidence)
        
        # 대표 bbox와 위치 계산 (첫 번째 객체 기준, 정규화된 좌표)
        if objects:
            representative_bbox = objects[0]["bbox"]  # 이미 정규화됨
            representative_pos = objects[0]["pos"]    # 이미 정규화됨
        else:
            representative_bbox = [0.0, 0.0, 0.0, 0.0]
            representative_pos = [0.0, 0.0]
        
        # API 스키마에 맞는 기본 Detection 모델
        detection_result = {
            "cctv_id": cctv_id,
            "bbox": representative_bbox,  # Detection 모델 필수 필드
            "pos": representative_pos,    # Detection 모델 필수 필드  
            "risk": risk,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": frame_url,
            "bird_count": total_objects,
            "objects": objects,  # 개별 객체 배열
        }
        
        print(f"   📊 탐지 결과: {total_objects}개 객체, 최대 신뢰도 {max_confidence:.3f}, 위험도 {risk}")
        if class_counts:
            class_info = ", ".join([f"{cls}: {count}개" for cls, count in class_counts.items()])
            print(f"   🐦 객체 분포: {class_info}")
        
        return detection_result

    def send_detection_result(self, detection_data: Dict) -> bool:
        """개별 탐지 결과 전송"""
        try:
            # API 요청 전 데이터 검증
            required_fields = ["cctv_id", "bbox", "pos", "risk", "captured_at", "bird_count", "objects"]
            for field in required_fields:
                if field not in detection_data:
                    print(f"❌ 필수 필드 누락: {field}")
                    return False
            
            # bbox와 pos가 올바른 형식인지 확인
            if not isinstance(detection_data["bbox"], list) or len(detection_data["bbox"]) != 4:
                print(f"❌ bbox 형식 오류: {detection_data['bbox']}")
                return False
                
            if not isinstance(detection_data["pos"], list) or len(detection_data["pos"]) != 2:
                print(f"❌ pos 형식 오류: {detection_data['pos']}")
                return False
            
            response = self.session.post(
                f"{self.server_url}/detect/result",
                json=detection_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    return True
            
            print(f"❌ 탐지 결과 전송 실패: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ 탐지 결과 전송 오류: {e}")
            return False
    
    def test_server_connection(self) -> bool:
        """서버 연결 테스트"""
        try:
            response = self.session.get(f"{self.server_url}/docs")
            if response.status_code == 200:
                print("✅ 서버 연결 성공")
                return True
            else:
                print(f"❌ 서버 연결 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 오류: {e}")
            return False
    
    def get_detection_history(self, cctv_id: str) -> List[Dict]:
        """탐지 내역 조회"""
        try:
            response = self.session.get(f"{self.server_url}/detect/history/{cctv_id}")
            
            if response.status_code == 200:
                detections = response.json()
                print(f"✅ {cctv_id} 탐지 내역 조회 성공: {len(detections)}개")
                return detections
            else:
                print(f"❌ 탐지 내역 조회 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 탐지 내역 조회 오류: {e}")
            return []

    def load_cctv_metadata_for_test(self):
        """테스트용 CCTV 메타데이터 미리 로딩"""
        try:
            cctv_ids = ["cctv_1", "cctv_2"]
            for cctv_id in cctv_ids:
                response = self.session.get(f"{self.server_url}/cctv/meta/{cctv_id}")
                if response.status_code == 200:
                    metadata = response.json()
                    self.cctv_metadata[cctv_id] = metadata
                    print(f"✅ {cctv_id} 메타데이터 로딩 성공")
                    if metadata.get('resolution'):
                        width, height = metadata['resolution']
                        print(f"   📐 해상도: {width}x{height}")
                else:
                    print(f"⚠️ {cctv_id} 메타데이터 로딩 실패, 기본값 사용")
        except Exception as e:
            print(f"⚠️ CCTV 메타데이터 로딩 오류: {e}, 기본값 사용")
    
    def process_all_csv_detections(self, csv_file: str = "detection_results.csv") -> Dict[str, int]:
        """모든 CSV 탐지 결과 처리 - 개별 객체 정보 포함"""
        print("\n🚀 수정된 CSV 기반 탐지 결과 DB 저장 시작")
        print("=" * 60)
        
        # CCTV 메타데이터 미리 로딩
        self.load_cctv_metadata_for_test()
        
        # CSV 데이터 로딩
        detections = self.load_csv_detections(csv_file)
        if not detections:
            return {"total": 0, "success": 0, "failed": 0}
        
        # 이미지별 그룹화
        detections_by_image = {}
        for detection in detections:
            image_name = detection['image_name']
            if image_name not in detections_by_image:
                detections_by_image[image_name] = []
            detections_by_image[image_name].append(detection)
        
        results = {"total": len(detections_by_image), "success": 0, "failed": 0}
        cctv_stats = {}
        
        for i, (image_name, image_detections) in enumerate(detections_by_image.items(), 1):
            cctv_id = self.extract_cctv_id_from_image_name(image_name)
            
            print(f"\n📸 [{i}/{len(detections_by_image)}] 처리 중: {image_name}")
            print(f"   CCTV ID: {cctv_id}")
            print(f"   탐지된 객체 수: {len(image_detections)}")
            
            # 통계 업데이트
            if cctv_id not in cctv_stats:
                cctv_stats[cctv_id] = 0
            
            # 이미지 업로드
            image_path = self.image_dir / image_name
            frame_url = self.upload_image(image_path)
            
            if not frame_url:
                print(f"   ❌ 이미지 업로드 실패, 탐지 결과 건너뜀")
                results["failed"] += 1
                continue
            
            # 올바른 API 스키마에 맞는 탐지 결과 생성
            detection_data = self.create_detection_with_objects_array(
                image_detections, cctv_id, frame_url
            )
            
            # 탐지 결과 전송
            if self.send_detection_result(detection_data):
                print(f"   ✅ 탐지 결과 저장 성공")
                results["success"] += 1
                cctv_stats[cctv_id] += 1
            else:
                print(f"   ❌ 탐지 결과 저장 실패")
                results["failed"] += 1
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 처리 결과 요약")
        print("=" * 60)
        print(f"전체 이미지: {results['total']}개")
        print(f"성공: {results['success']}개")
        print(f"실패: {results['failed']}개")
        
        print("\n📹 CCTV별 탐지 결과:")
        for cctv_id, success in cctv_stats.items():
            print(f"  {cctv_id}: {'success' if success is 1 else 'failed'}")
        
        return results
    
    def verify_frontend_data(self) -> bool:
        """프론트엔드 데이터 확인"""
        print("\n🔍 프론트엔드 데이터 확인")
        print("=" * 40)
        
        # 각 CCTV의 탐지 내역 확인
        cctv_ids = ["cctv_1", "cctv_2"]
        
        for cctv_id in cctv_ids:
            detections = self.get_detection_history(cctv_id)
            
            if detections:
                print(f"\n✅ {cctv_id}: {len(detections)}개 탐지 결과")
                
                # 최근 탐지 결과 미리보기
                if len(detections) > 0:
                    latest = detections[0]
                    print(f"   최근 탐지: {latest.get('captured_at', 'N/A')}")
                    print(f"   위험도: {latest.get('risk', 'N/A')}")
                    print(f"   객체 수: {latest.get('bird_count', 'N/A')}")
                    if 'objects' in latest:
                        print(f"   개별 객체: {len(latest['objects'])}개")
            else:
                print(f"❌ {cctv_id}: 탐지 결과 없음")
        
        return True
    
    def run_complete_test(self) -> bool:
        """전체 테스트 실행"""
        print("🎯 수정된 CSV 기반 탐지 결과 DB 저장 및 프론트엔드 테스트")
        print("=" * 80)
        
        # 1. 서버 연결 확인
        if not self.test_server_connection():
            return False
        
        # 2. 모든 CSV 탐지 결과 처리
        results = self.process_all_csv_detections()
        
        if results["success"] == 0:
            print("❌ 모든 탐지 결과 저장에 실패했습니다.")
            return False
        
        # 3. 프론트엔드 데이터 확인
        self.verify_frontend_data()
        
        # 4. 프론트엔드 접속 안내
        print("\n" + "=" * 80)
        print("🎉 테스트 완료!")
        print("=" * 80)
        print("📱 프론트엔드에서 결과 확인:")
        print("   1. 브라우저에서 http://localhost:3000 접속")
        print("   2. CCTV 목록에서 다음 카메라들 확인:")
        print("      - cctv_1, cctv_2")
        print("   3. 각 카메라 클릭하여 탐지 결과 및 이미지 확인")
        print("   4. objects 배열에서 개별 객체 위치 정보 확인")
        print("\n💡 참고:")
        print("   - 위험도는 DetectionService와 동일한 로직 사용")
        print("   - 해상도는 CCTV 메타데이터에서 가져옴")
        print("   - 좌표는 상대좌표로 정규화됨")
        print("   - objects 배열에 개별 객체 정보 포함")
        
        return True


def main():
    """메인 실행 함수"""
    tester = CSVDetectionTester("http://localhost:8000")
    
    # 현재 디렉토리 확인
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"CSV 파일 경로: {os.path.abspath('detection_results.csv')}")
    print(f"이미지 디렉토리: {os.path.abspath('detection_image')}")
    
    # 파일 존재 확인
    if not os.path.exists("detection_results.csv"):
        print("❌ detection_results.csv 파일이 없습니다.")
        print("   test 디렉토리에서 실행해주세요.")
        return
    
    if not os.path.exists("detection_image"):
        print("❌ detection_image 디렉토리가 없습니다.")
        return
    
    # 전체 테스트 실행
    success = tester.run_complete_test()
    
    if success:
        print("\n✅ 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 테스트 중 일부 문제가 발생했습니다.")


if __name__ == "__main__":
    main()