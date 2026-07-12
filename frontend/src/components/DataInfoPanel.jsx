import { useState, useEffect } from 'react';
import { fetchDatasetSummary } from '../api';
import './DataInfoPanel.css';

export default function DataInfoPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [summaryData, setSummaryData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    fetchDatasetSummary()
      .then((data) => {
        if (isMounted) {
          setSummaryData(data);
          setIsLoading(false);
        }
      })
      .catch(() => {
        if (isMounted) {
          setIsLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const renderOrdersBreakdown = (byStatus) => {
    if (!byStatus) return null;
    return Object.entries(byStatus)
      .map(([status, count]) => `${count} ${status}`)
      .join(', ');
  };

  return (
    <div className="data-info-panel">
      <button
        type="button"
        className="data-info-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <span className="data-info-title">
          <span className="data-info-icon">📊</span>
          What's in this data?
        </span>
        <span className={`data-info-arrow ${isOpen ? 'open' : ''}`}>▼</span>
      </button>

      {isOpen && (
        <div className="data-info-content">
          <p className="data-info-description">
            This demo uses a small online store's data: customers, their orders, products across categories like Electronics/Clothing/Groceries, payments, and order statuses (completed/pending/cancelled).
          </p>

          <div className="data-domains-grid">
            {/* Customers Card */}
            <div className="domain-card">
              <span className="domain-icon">👥</span>
              <div className="domain-details">
                <strong>Customers</strong>
                {isLoading ? (
                  <div className="skeleton-container">
                    <div className="skeleton-line short" />
                    <div className="skeleton-line" />
                  </div>
                ) : summaryData?.customers ? (
                  <>
                    <span className="domain-count">{summaryData.customers.count} customers</span>
                    {summaryData.customers.sample?.slice(0, 3).map((cust, idx) => (
                      <span key={idx} className="domain-subtext">
                        • {cust.name} ({cust.signup_date})
                      </span>
                    ))}
                  </>
                ) : (
                  <span>Profiles, registration info</span>
                )}
              </div>
            </div>

            {/* Products Card */}
            <div className="domain-card">
              <span className="domain-icon">🛍️</span>
              <div className="domain-details">
                <strong>Products & Categories</strong>
                {isLoading ? (
                  <div className="skeleton-container">
                    <div className="skeleton-line short" />
                    <div className="skeleton-line" />
                  </div>
                ) : summaryData?.products ? (
                  <>
                    <span className="domain-count">
                      {summaryData.products.count} products ({summaryData.products.categories?.join(', ')})
                    </span>
                    {summaryData.products.sample?.slice(0, 3).map((prod, idx) => (
                      <span key={idx} className="domain-subtext">
                        • {prod.name} (${prod.price})
                      </span>
                    ))}
                  </>
                ) : (
                  <span>Electronics, Clothing, Groceries</span>
                )}
              </div>
            </div>

            {/* Orders Card */}
            <div className="domain-card">
              <span className="domain-icon">📦</span>
              <div className="domain-details">
                <strong>Orders & Statuses</strong>
                {isLoading ? (
                  <div className="skeleton-container">
                    <div className="skeleton-line short" />
                    <div className="skeleton-line" />
                  </div>
                ) : summaryData?.orders ? (
                  <>
                    <span className="domain-count">{summaryData.orders.count} total orders</span>
                    <span className="domain-subtext">
                      {renderOrdersBreakdown(summaryData.orders.by_status)}
                    </span>
                  </>
                ) : (
                  <span>Completed, Pending, Cancelled</span>
                )}
              </div>
            </div>

            {/* Payments Card */}
            <div className="domain-card">
              <span className="domain-icon">💳</span>
              <div className="domain-details">
                <strong>Payments</strong>
                {isLoading ? (
                  <div className="skeleton-container">
                    <div className="skeleton-line short" />
                    <div className="skeleton-line" />
                  </div>
                ) : summaryData?.payments ? (
                  <>
                    <span className="domain-count">{summaryData.payments.count} payment transactions</span>
                    <span className="domain-subtext">
                      Methods: {summaryData.payments.methods?.join(', ')}
                    </span>
                  </>
                ) : (
                  <span>Payment methods & totals</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
