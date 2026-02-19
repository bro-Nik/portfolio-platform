import React from 'react';

const StatisticCards = ({ cards }) => {

  return (
    <div className="row mb-4">
      {cards.map((card, index) => (
        <div key={index} className="col-auto">
          <p className="small-text">{card.title}</p>
          <span className={`text-average ${card.class || ''}`}>{card.value}</span>
        </div>
      ))}
    </div>
  );
};

export default StatisticCards;
