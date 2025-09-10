import React, { useState } from 'react';
import { AirBirdsDetection, ProcessedDetection } from '../types';
import { convertAirBirdsToRelative } from '../utils/geometry';

interface Props {
  onDetectionsChange: (detections: ProcessedDetection[]) => void;
}

const TestAirBirdsPanel: React.FC<Props> = ({ onDetectionsChange }) => {
  const [isLoading, setIsLoading] = useState(false);

  // 테스트용 JSON 데이터 (기존 CCTV ID 사용)
  const testAirBirdsData: AirBirdsDetection = {
    "image_path": "G:\\AirBirds\\datasets\\DATASET(AirBirds)\\images\\val\\AIRPORT_CAM_D02_A_20210721142744_0007999.png",
    "image_name": "AIRPORT_CAM_D02_A_20210721142744_0007999.png",
    "image_shape": [1080, 1920],
    "detections": [
      {
        "class_id": 0,
        "class_name": "bird",
        "confidence": 0.39513248205184937,
        "bbox": {
          "x1": 698.89306640625,
          "y1": 664.9843139648438,
          "x2": 702.904052734375,
          "y2": 669.0383911132812
        }
      },
      {
        "class_id": 0,
        "class_name": "bird",
        "confidence": 0.24672605097293854,
        "bbox": {
          "x1": 24.141807556152344,
          "y1": 271.5225524902344,
          "x2": 28.511383056640625,
          "y2": 275.5994567871094
        }
      },
      {
        "class_id": 0,
        "class_name": "bird",
        "confidence": 0.22049757838249207,
        "bbox": {
          "x1": 619.464599609375,
          "y1": 527.0271606445312,
          "x2": 623.735107421875,
          "y2": 531.0919799804688
        }
      }
    ]
  };

  const handleLoadTestData = async () => {
    setIsLoading(true);
    try {
      // 프론트엔드에서 변환
      const processedDetections = convertAirBirdsToRelative(testAirBirdsData);
      onDetectionsChange(processedDetections);
      
      // 백엔드에도 전송 (선택사항)
      const response = await fetch(`${process.env.REACT_APP_API_HTTP}/detect/airbirds`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testAirBirdsData),
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Backend response:', result);
      }
    } catch (error) {
      console.error('Error loading test data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearDetections = () => {
    onDetectionsChange([]);
  };

  return (
    <div style={{ 
      position: 'fixed',  // absolute → fixed로 변경
      top: 20, 
      right: 20, 
      zIndex: 9999,  // z-index 높임
      background: 'white', 
      padding: '15px',
      borderRadius: '8px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
      border: '2px solid #007bff',  // 테두리 추가
      minWidth: '200px'
    }}>
      <h4 style={{ margin: '0 0 10px 0', color: '#007bff' }}>🐦 AirBirds 테스트</h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <button 
          onClick={handleLoadTestData} 
          disabled={isLoading}
          style={{
            padding: '10px 15px',
            backgroundColor: isLoading ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        >
          {isLoading ? '로딩 중...' : '🚁 테스트 데이터 로드'}
        </button>
        <button 
          onClick={handleClearDetections}
          style={{
            padding: '10px 15px',
            backgroundColor: '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
        >
          🗑️ 탐지 결과 지우기
        </button>
      </div>
      <div style={{ fontSize: '12px', color: '#666', marginTop: '10px', textAlign: 'center' }}>
        💡 AIRPORT_CAM_D02_A에서 3마리 새 탐지
      </div>
    </div>
  );
};

export default TestAirBirdsPanel;
