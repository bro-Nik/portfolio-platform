import React from 'react';
import ReactDOM from 'react-dom/client';
// import './index.css';
import App from './App';
import ToastContainer from '/app/src/components/ui/Toast/ToastContainer';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
    <ToastContainer />
  </React.StrictMode>
);
