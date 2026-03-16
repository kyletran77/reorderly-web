import React from 'react'

const styles = {
  emptyState: {
    padding: '48px 24px',
    textAlign: 'center',
  },
  emptyIcon: {
    fontSize: '36px',
    marginBottom: '12px',
  },
  emptyTitle: {
    fontSize: '15px',
    fontWeight: 600,
    color: '#374151',
    marginBottom: '6px',
  },
  emptyText: {
    fontSize: '14px',
    color: '#9ca3af',
    lineHeight: 1.6,
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '14px',
  },
  th: {
    padding: '10px 16px',
    textAlign: 'left',
    fontSize: '11px',
    fontWeight: 700,
    color: '#9ca3af',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    background: '#f9fafb',
    borderBottom: '1px solid #f3f4f6',
  },
  td: {
    padding: '12px 16px',
    borderBottom: '1px solid #f9fafb',
    color: '#374151',
    verticalAlign: 'middle',
  },
  skuText: {
    fontSize: '11px',
    color: '#9ca3af',
    fontFamily: 'monospace',
  },
  badge: (status) => ({
    display: 'inline-block',
    padding: '3px 8px',
    borderRadius: '100px',
    fontSize: '11px',
    fontWeight: 600,
    background: status === 'low' ? '#fef3c7' : status === 'critical' ? '#fee2e2' : '#d1fae5',
    color: status === 'low' ? '#92400e' : status === 'critical' ? '#991b1b' : '#065f46',
  }),
}

export default function InventoryTable({ items = [] }) {
  if (items.length === 0) {
    return (
      <div style={styles.emptyState}>
        <div style={styles.emptyIcon}>📦</div>
        <div style={styles.emptyTitle}>No inventory data yet</div>
        <div style={styles.emptyText}>
          Connect your Shopify store to<br />start monitoring inventory levels.
        </div>
      </div>
    )
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>Product</th>
            <th style={styles.th}>Stock</th>
            <th style={styles.th}>Threshold</th>
            <th style={styles.th}>Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={item.id || i}>
              <td style={styles.td}>
                <div style={{ fontWeight: 500 }}>{item.name}</div>
                {item.sku && <div style={styles.skuText}>{item.sku}</div>}
              </td>
              <td style={styles.td}>{item.stock ?? '—'}</td>
              <td style={styles.td}>{item.threshold ?? '—'}</td>
              <td style={styles.td}>
                {item.status && (
                  <span style={styles.badge(item.status)}>
                    {item.status === 'low' ? 'Low stock' : item.status === 'critical' ? 'Critical' : 'OK'}
                  </span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
