// import React from 'react';
// import { formatCurrency } from '/app/src/utils/format';
// import StatisticCards from '/app/src/features/statistics/StatisticCards';
//
// const AssetDetail = ({ data }) => {
//
//   return (
//     <div className="row">
//       <div className="col-md-6">
//         <div className="card">
//           <div className="card-header">
//             <h6 className="mb-0">Детали распределения</h6>
//           </div>
//           <div className="card-body">
//             {data.distribution.portfolios.map((portfolio, index) => (
//               <div key={portfolio.portfolioId} className="row mb-2">
//                 <div className="col-8">
//                   <div className="fw-bold">{portfolio.portfolioName}</div>
//                   <small className="text-muted">{portfolio.quantity} шт.</small>
//                 </div>
//                 <div className="col-4 text-end">
//                   <div className="fw-bold">{formatCurrency(portfolio.amount)}</div>
//                   <small className="text-muted">{portfolio.percentageOfTotal.toFixed(1)}%</small>
//                 </div>
//               </div>
//             ))}
//             <div className="row mt-3 pt-2 border-top">
//               <div className="col-8">
//                 <strong>Всего:</strong>
//               </div>
//               <div className="col-4 text-end">
//                 <strong>{formatCurrency(data.distribution.totalAmountAllPortfolios)}</strong>
//               </div>
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// };
//
// export default AssetDetail;
