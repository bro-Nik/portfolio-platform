import React from 'react';

const LoadingSpinner = () => (
  <div className="d-flex justify-content-center align-items-center w-100 h-100">
    <div className="spinner-border text-primary" role="status">
      <span className="visually-hidden">Загрузка...</span>
    </div>
  </div>
);

export default LoadingSpinner;
