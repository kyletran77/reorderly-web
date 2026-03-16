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
  list: {
    padding: 0,
    margin: 0,
  },
  item: {
    padding: '16px 20px',
    borderBottom: '1px solid #f9fafb',
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: '12px',
  },
  itemLeft: {
    flex: 1,
    minWidth: 0,
  },
  itemTitle: {
    fontSize: '14px',
    fontWeight: 600,
    color: '#111827',
    marginBottom: '3px',
    whiteSpace: 'nowrap',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  itemMeta: {
    fontSize: '12px',
    color: '#9ca3af',
  },
  statusBadge: (status) => ({
    display: 'inline-block',
    padding: '3px 8px',
    borderRadius: '100px',
    fontSize: '11px',
    fontWeight: 600,
    flexShrink: 0,
    background:
      status === 'confirmed' ? '#d1fae5' :
      status === 'sent' ? '#dbeafe' :
      status === 'draft' ? '#f3f4f6' : '#fef3c7',
    color:
      status === 'confirmed' ? '#065f46' :
      status === 'sent' ? '#1d4ed8' :
      status === 'draft' ? '#6b7280' : '#92400e',
  }),
}

function formatDate(dateStr) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export default function POLog({ orders = [] }) {
  if (orders.length === 0) {
    return (
      <div style={styles.emptyState}>
        <div style={styles.emptyIcon}>📋</div>
        <div style={styles.emptyTitle}>No purchase orders yet</div>
        <div style={styles.emptyText}>
          Once Reorderly detects low stock, it will<br />automatically send POs to your suppliers.
        </div>
      </div>
    )
  }

  return (
    <ul style={styles.list}>
      {orders.map((order, i) => (
        <li key={order.id || i} style={styles.item}>
          <div style={styles.itemLeft}>
            <div style={styles.itemTitle}>
              PO to {order.supplier || 'Unknown Supplier'}
            </div>
            <div style={styles.itemMeta}>
              {order.items || '—'} items &middot; Sent {formatDate(order.sent_at)}
            </div>
          </div>
          {order.status && (
            <span style={styles.statusBadge(order.status)}>
              {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
            </span>
          )}
        </li>
      ))}
    </ul>
  )
}
