"""
CSV 기반 탐지 결과 DB 저장 및 프론트엔드 출력 테스트

🎯 목적:
- detection_results.csv 파일의 모든 탐지 결과를 DB에 저장
- 실제 이미지 파일과 함께 탐지 결과 업로드
- 프론트엔드에서 탐지 결과 조회 가능하도록 테스트

📋 CCTV ID 매핑:
- D02_20210628* → cctv_1 (공항 D02 카메라 A지점)
- D02_20210721* → cctv_2 (공항 D02 카메라 B지점)

🔧 실행 방법:
1. 백엔드 서버 실행: uvicorn app.main:app --reload --port 8000
2. 프론트엔드 실행: npm start
3. python csv_detection_test.py 실행
4. 프론트엔드에서 탐지 결과 확인
"""

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
    
    def extract_cctv_id_from_image_name(self, image_name: str) -> str:
        """
        이미지 이름에서 CCTV ID 추출
        
        Args:
            image_name: 이미지 파일명
        
        Returns:
            str: CCTV ID (예: cctv_1)
        """
        if "0008246" in image_name:
            return "cctv_1"
        elif "0009630" in image_name:
            return "cctv_2"
        else:
            # 기본값
            return "AIRPORT_CAM_D02_DEFAULT"
    
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
            # 이미지 업로드를 위한 별도의 세션 생성 (multipart/form-data용)
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/png')}
                # Content-Type 헤더를 제거하여 requests가 자동으로 multipart/form-data로 설정하도록 함
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
    
    def send_detection_result(self, detection_data: Dict) -> bool:
        """개별 탐지 결과 전송"""
        try:
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
    
    def create_combined_detection(self, image_detections: List[Dict], cctv_id: str, frame_url: str) -> Dict:
        """같은 이미지의 여러 객체를 하나의 탐지 결과로 통합"""
        
        # 이미지 크기 (D02 카메라 표준 해상도)
        image_width = 1920.0
        image_height = 1080.0
        
        # 모든 객체의 바운딩 박스와 위치 정보 수집
        all_bboxes = []
        all_positions = []
        confidences = []
        class_counts = {}
        
        for detection in image_detections:
            # 바운딩 박스 [x, y, width, height]
            bbox = [
                detection['x1'],
                detection['y1'], 
                detection['width'],
                detection['height']
            ]
            all_bboxes.append(bbox)
            
            # 상대좌표 위치
            pos = [
                detection['center_x'] / image_width,   # u (수평 상대좌표)
                detection['center_y'] / image_height   # v (수직 상대좌표)
            ]
            all_positions.append(pos)
            
            # 신뢰도 수집
            confidences.append(detection['confidence'])
            
            # 클래스별 카운트
            class_name = detection['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1
        
        # 평균 신뢰도 계산
        avg_confidence = sum(confidences) / len(confidences)
        
        # 위험도 계산 (객체 수와 평균 신뢰도 고려)
        total_objects = len(image_detections)
        if total_objects >= 5 or avg_confidence >= 0.7:
            risk = "red"    # 위험
        elif total_objects >= 1 or avg_confidence >= 0.5:
            risk = "orange" # 주의
        else:
            risk = "yellow" # 모니터링
        
        # 대표 bbox와 위치 계산 (첫 번째 객체 또는 중심점)
        if len(all_bboxes) == 1:
            # 단일 객체인 경우
            representative_bbox = all_bboxes[0]
            representative_pos = all_positions[0]
        else:
            # 다중 객체인 경우: 모든 객체를 포함하는 통합 bbox 계산
            min_x = min(bbox[0] for bbox in all_bboxes)
            min_y = min(bbox[1] for bbox in all_bboxes)
            max_x = max(bbox[0] + bbox[2] for bbox in all_bboxes)
            max_y = max(bbox[1] + bbox[3] for bbox in all_bboxes)
            
            representative_bbox = [min_x, min_y, max_x - min_x, max_y - min_y]
            
            # 중심점 계산
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            representative_pos = [center_x / image_width, center_y / image_height]
        
        # 통합 탐지 결과 생성
        combined_result = {
            "cctv_id": cctv_id,
            "bbox": representative_bbox,  # 단일 bbox [x, y, width, height]
            "pos": representative_pos,    # 단일 위치 [u, v]
            "risk": risk,
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "frame_url": frame_url,
            "bird_count": total_objects,
            "avg_confidence": round(avg_confidence, 3),
            "class_counts": class_counts  # 예: {"bird": 3, "crow": 2}
        }
        
        print(f"   📊 통합 결과: {total_objects}개 객체, 평균 신뢰도 {avg_confidence:.3f}, 위험도 {risk}")
        if class_counts:
            class_info = ", ".join([f"{cls}: {count}개" for cls, count in class_counts.items()])
            print(f"   🐦 객체 분포: {class_info}")
        
        return combined_result

    def process_all_csv_detections(self, csv_file: str = "detection_results.csv") -> Dict[str, int]:
        """모든 CSV 탐지 결과 처리 - 이미지별로 통합"""
        print("\n🚀 CSV 기반 탐지 결과 DB 저장 시작")
        print("=" * 60)
        
        # CSV 데이터 로딩
        detections = self.load_csv_detections(csv_file)
        if not detections:
            return {"total": 0, "success": 0, "failed": 0}
        
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
            
            # 이미지 업로드 (한 번만)
            image_path = self.image_dir / image_name
            frame_url = self.upload_image(image_path)
            
            if not frame_url:
                print(f"   ❌ 이미지 업로드 실패, 탐지 결과 건너뜀")
                results["failed"] += 1
                continue
            
            detection_data = self.create_combined_detection(image_detections, cctv_id, frame_url)
            
            # 탐지 결과 전송 (이미지당 한 번만)
            if self.send_detection_result(detection_data):
                print(f"   ✅ 통합 탐지 결과 저장 성공")
                results["success"] += 1
                cctv_stats[cctv_id] += 1
            else:
                print(f"   ❌ 탐지 결과 저장 실패")
                results["failed"] += 1
        
        # 결과 요약 (기존과 동일)
        print("\n" + "=" * 60)
        print("📊 처리 결과 요약")
        print("=" * 60)
        print(f"전체 이미지: {results['total']}개")
        print(f"성공: {results['success']}개")
        print(f"실패: {results['failed']}개")
        
        print("\n📹 CCTV별 탐지 결과:")
        for cctv_id, count in cctv_stats.items():
            print(f"  {cctv_id}: {count}개")
        
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
                    print(f"   이미지: {latest.get('frame_url', 'N/A')}")
            else:
                print(f"❌ {cctv_id}: 탐지 결과 없음")
        
        return True
    
    def run_complete_test(self) -> bool:
        """전체 테스트 실행"""
        print("🎯 CSV 기반 탐지 결과 DB 저장 및 프론트엔드 테스트")
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
        print("   3. 각 카메라 클릭하여 탐지 결과 및 이미지 확인")
        print("\n💡 참고:")
        print("   - 위험도는 신뢰도에 따라 자동 설정됩니다")
        print("   - 모든 이미지는 /frames/ 경로에 저장됩니다")
        print("   - 탐지 결과는 MongoDB에 저장됩니다")
        
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