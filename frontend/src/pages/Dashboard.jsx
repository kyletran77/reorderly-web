import React, { useState, useEffect } from 'react'
import InventoryTable from '../components/InventoryTable.jsx'
import POLog from '../components/POLog.jsx'

const styles = {
  app: {
    minHeight: '100vh',
    background: '#f9fafb',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
  },
  header: {
    background: '#fff',
    borderBottom: '1px solid #e5e7eb',
    padding: '0 32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    height: '60px',
    position: 'sticky',
    top: 0,
    zIndex: 10,
  },
  logo: {
    display: 'flex',
    flexDirection: 'column',
    lineHeight: 1,
  },
  logoName: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#111827',
    letterSpacing: '-0.3px',
  },
  logoTag: {
    fontSize: '10px',
    fontWeight: 600,
    color: '#2563eb',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  badge: {
    background: '#dbeafe',
    color: '#1d4ed8',
    fontSize: '12px',
    fontWeight: 600,
    padding: '4px 10px',
    borderRadius: '100px',
  },
  btn: {
    padding: '8px 16px',
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: 600,
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'inline-block',
  },
  main: {
    padding: '32px',
    maxWidth: '1200px',
    margin: '0 auto',
  },
  pageTitle: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#111827',
    letterSpacing: '-0.5px',
    marginBottom: '4px',
  },
  pageSubtitle: {
    fontSize: '15px',
    color: '#6b7280',
    marginBottom: '32px',
  },
  connectBanner: {
    background: '#fff',
    border: '1.5px dashed #d1d5db',
    borderRadius: '12px',
    padding: '40px 32px',
    textAlign: 'center',
    marginBottom: '32px',
  },
  connectTitle: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#111827',
    marginBottom: '8px',
  },
  connectText: {
    fontSize: '15px',
    color: '#6b7280',
    marginBottom: '20px',
    lineHeight: 1.6,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '24px',
  },
  card: {
    background: '#fff',
    border: '1.5px solid #e5e7eb',
    borderRadius: '12px',
    overflow: 'hidden',
  },
  cardHeader: {
    padding: '20px 24px 16px',
    borderBottom: '1px solid #f3f4f6',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  cardTitle: {
    fontSize: '15px',
    fontWeight: 700,
    color: '#111827',
  },
  cardCount: {
    fontSize: '13px',
    color: '#9ca3af',
    fontWeight: 500,
  },
  statsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(4, 1fr)',
    gap: '16px',
    marginBottom: '24px',
  },
  statCard: {
    background: '#fff',
    border: '1.5px solid #e5e7eb',
    borderRadius: '10px',
    padding: '20px 20px',
  },
  statLabel: {
    fontSize: '12px',
    fontWeight: 600,
    color: '#9ca3af',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    marginBottom: '8px',
  },
  statValue: {
    fontSize: '28px',
    fontWeight: 700,
    color: '#111827',
    letterSpacing: '-1px',
    lineHeight: 1,
  },
  statSub: {
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '4px',
  },
}

export default function Dashboard() {
  const [connected, setConnected] = useState(false)

  return (
    <div style={styles.app}>
      <header style={styles.header}>
        <div style={styles.logo}>
          <span style={styles.logoName}>Reorderly</span>
          <span style={styles.logoTag}>AI Supplier Agent</span>
        </div>
        <div style={styles.headerRight}>
          <span style={styles.badge}>Early Access</span>
          <a href="/" style={{ ...styles.btn, background: 'transparent', color: '#6b7280', border: '1.5px solid #e5e7eb', fontSize: '13px' }}>
            Back to site
          </a>
        </div>
      </header>

      <main style={styles.main}>
        <h1 style={styles.pageTitle}>Dashboard</h1>
        <p style={styles.pageSubtitle}>Manage your inventory reordering and supplier purchase orders.</p>

        {!connected && (
          <div style={styles.connectBanner}>
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>🔗</div>
            <div style={styles.connectTitle}>Connect your Shopify store to get started</div>
            <p style={styles.connectText}>
              Link your store to start monitoring inventory and automating purchase orders.<br />
              Setup takes less than 2 minutes.
            </p>
            <a href="/app/onboarding/" style={styles.btn}>Connect Shopify Store</a>
          </div>
        )}

        <div style={styles.statsRow}>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Total SKUs</div>
            <div style={styles.statValue}>—</div>
            <div style={styles.statSub}>Connect store to sync</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Low Stock</div>
            <div style={styles.statValue}>—</div>
            <div style={styles.statSub}>Items below threshold</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>POs Sent</div>
            <div style={styles.statValue}>0</div>
            <div style={styles.statSub}>This month</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statLabel}>Suppliers</div>
            <div style={styles.statValue}>0</div>
            <div style={styles.statSub}>Configured</div>
          </div>
        </div>

        <div style={styles.grid}>
          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.cardTitle}>Inventory Status</span>
              <span style={styles.cardCount}>0 items</span>
            </div>
            <InventoryTable items={[]} />
          </div>

          <div style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.cardTitle}>Recent Purchase Orders</span>
              <span style={styles.cardCount}>0 orders</span>
            </div>
            <POLog orders={[]} />
          </div>
        </div>
      </main>
    </div>
  )
}
