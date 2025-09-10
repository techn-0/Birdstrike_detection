import os
import json
from typing import List, Dict, Optional
from fastapi import HTTPException
from pathlib import Path


class PhotoSlidesService:
    def __init__(self):
        self.base_path = Path("app/static")
        self.original_images_path = self.base_path / "DATASET(AirBirds)_Predict_original"
        self.labels_path = self.base_path / "DATASET(AirBirds)_Predict" / "structured_labels"
        self.results_summary_path = self.base_path / "DATASET(AirBirds)_Predict" / "results_summary"
    
    def get_photo_slides_data(self, cctv_id: str, confidence_threshold: float = 0.3) -> Dict:
        """
        특정 CCTV의 포토 슬라이드 데이터를 반환
        낮은 신뢰도 이미지는 제외
        """
        try:
            # 모든 결과 요약 파일 읽기
            all_results_file = self.results_summary_path / "all_results.json"
            if not all_results_file.exists():
                raise HTTPException(status_code=404, detail="Results summary not found")
            
            with open(all_results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
            
            # 신뢰도 기준으로 필터링된 이미지 목록 생성
            filtered_images = []
            
            for result in all_results:
                # 이미지 이름에서 .png 제거
                image_name = result.get('image_name', '').replace('.png', '')
                detections = result.get('detections', [])
                
                # 최대 신뢰도 계산
                max_confidence = 0
                if detections:
                    max_confidence = max(detection.get('confidence', 0) for detection in detections)
                
                # 신뢰도 기준으로 필터링
                if max_confidence >= confidence_threshold and image_name:
                    # 원본 이미지 파일 경로 확인
                    original_image_path = self.original_images_path / f"{image_name}.png"
                    if original_image_path.exists():
                        # 라벨 파일에서 구조화된 라벨 정보 가져오기
                        label_file_path = self.labels_path / f"{image_name}.json"
                        
                        labels = []
                        if label_file_path.exists():
                            with open(label_file_path, 'r', encoding='utf-8') as lf:
                                label_data = json.load(lf)
                                # 라벨 데이터를 프론트엔드 형식으로 변환
                                for detection in label_data.get('detections', []):
                                    bbox = detection.get('bbox', {})
                                    labels.append({
                                        'x1': bbox.get('x1', 0),
                                        'y1': bbox.get('y1', 0),
                                        'x2': bbox.get('x2', 0),
                                        'y2': bbox.get('y2', 0),
                                        'confidence': detection.get('confidence', 0),
                                        'class_name': detection.get('class_name', 'bird')
                                    })
                        
                        filtered_images.append({
                            'image_name': image_name,
                            'image_url': f"/static/DATASET(AirBirds)_Predict_original/{image_name}.png",
                            'labels': labels,
                            'max_confidence': max_confidence,
                            'detection_count': len(labels)
                        })
            
            # 이미지를 신뢰도 순으로 정렬 (높은 순)
            filtered_images.sort(key=lambda x: x['max_confidence'], reverse=True)
            
            return {
                'cctv_id': cctv_id,
                'total_images': len(filtered_images),
                'confidence_threshold': confidence_threshold,
                'images': filtered_images[:100]  # 최대 100개로 제한
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing photo slides data: {str(e)}")
    
    def get_image_statistics(self) -> Dict:
        """전체 이미지 통계 정보 반환"""
        try:
            all_results_file = self.results_summary_path / "all_results.json"
            if not all_results_file.exists():
                return {"error": "Results summary not found"}
            
            with open(all_results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
            
            total_images = len(all_results)
            high_confidence_count = 0
            medium_confidence_count = 0
            low_confidence_count = 0
            
            for result in all_results:
                detections = result.get('detections', [])
                max_confidence = 0
                if detections:
                    max_confidence = max(detection.get('confidence', 0) for detection in detections)
                
                if max_confidence >= 0.7:
                    high_confidence_count += 1
                elif max_confidence >= 0.3:
                    medium_confidence_count += 1
                else:
                    low_confidence_count += 1
            
            return {
                'total_images': total_images,
                'high_confidence_images': high_confidence_count,
                'medium_confidence_images': medium_confidence_count,
                'low_confidence_images': low_confidence_count,
                'available_original_images': len(list(self.original_images_path.glob("*.png"))),
                'available_label_files': len(list(self.labels_path.glob("*.json")))
            }
            
        except Exception as e:
            return {"error": f"Error getting statistics: {str(e)}"}


# 서비스 인스턴스
photo_slides_service = PhotoSlidesService()
