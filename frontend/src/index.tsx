import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// 타입스크립트 Non-null 단언 (!) 추가
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(<App />);
