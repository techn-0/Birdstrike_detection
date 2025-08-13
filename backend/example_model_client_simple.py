# 간소화된 탐지 클라이언트 예제
import requests
from datetime import datetime

class BirdDetectionClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
    
    def send_detection(self, 
                      x1: float, y1: float, x2: float, y2: float,
                      confidence: float,
                      cctv_id: str = None,
                      image_name: str = None):
        """
        탐지 결과를 서버로 전송 (간소화된 형식)
        
        Args:
            x1, y1, x2, y2: 바운딩 박스 좌표
            confidence: 신뢰도 (0.0 ~ 1.0)
            cctv_id: 카메라 ID (옵션)
            image_name: 이미지 파일명 (옵션)
        """
        detection_data = {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "confidence": confidence,
            "cctv_id": cctv_id,
            "captured_at": datetime.now().isoformat(),
            "image_name": image_name
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/detect",
                json=detection_data,
                timeout=10
            )
            return response.json()
        except Exception as e:
            print(f"전송 실패: {e}")
            return {"ok": False, "error": str(e)}

# 사용 예제
if __name__ == "__main__":
    client = BirdDetectionClient()
    
    # 테스트 탐지 결과 전송
    result = client.send_detection(
        x1=100, y1=100, x2=200, y2=200,
        confidence=0.85,
        cctv_id="camera_01",
        image_name="test_image.jpg"
    )
    
    print(f"전송 결과: {result}")
