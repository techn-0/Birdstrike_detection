# 팀원의 모델에서 사용할 예제 코드
import requests
import base64
from datetime import datetime
from typing import List

class BirdDetectionClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
    
    def send_detection(self, 
                      cctv_id: str,
                      bbox: List[float],  # [x1, y1, x2, y2] - CSV 형식
                      confidence: float,
                      image_path: str = None,
                      image_data: bytes = None):
        """
        탐지 결과를 서버로 전송
        
        Args:
            cctv_id: 카메라 ID
            bbox: 바운딩 박스 [x1, y1, x2, y2] - CSV 형식
            confidence: 신뢰도 (0.0 ~ 1.0)
            image_path: 이미지 파일 경로 (옵션)
            image_data: 이미지 바이트 데이터 (옵션)
        """
        
        # 이미지를 base64로 인코딩
        encoded_image = None
        if image_path:
            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode('utf-8')
        elif image_data:
            encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        # 탐지 결과 데이터
        detection_data = {
            "cctv_id": cctv_id,
            "bbox": bbox,
            "confidence": confidence,
            "captured_at": datetime.now().isoformat(),
            "image_data": encoded_image,
            "bird_count": 1
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/detect/result",
                json=detection_data,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ 탐지 결과 전송 성공: {cctv_id}")
                return True
            else:
                print(f"❌ 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 네트워크 오류: {e}")
            return False

# 사용 예시
if __name__ == "__main__":
    client = BirdDetectionClient()
    
    # CSV 파일의 첫 번째 탐지 결과 예시 (정확한 형식)
    success = client.send_detection(
        cctv_id="camera_01",
        bbox=[508.83, 534.93, 524.51, 543.12],  # [x1, y1, x2, y2] - CSV 형식
        confidence=0.27,  # CSV의 confidence 값
        image_path="D02_20210628090856_0000714_crop_000.png"  # CSV의 image_name
    )
    
    if success:
        print("모든 처리 완료!")
