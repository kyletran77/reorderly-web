import React, { useState } from 'react'

const styles = {
  page: {
    minHeight: '100vh',
    background: '#f9fafb',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    background: '#fff',
    borderBottom: '1px solid #e5e7eb',
    padding: '0 32px',
    display: 'flex',
    alignItems: 'center',
    height: '60px',
  },
  logoName: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#111827',
    letterSpacing: '-0.3px',
  },
  body: {
    flex: 1,
    display: 'flex',
    alignItems: 'flex-start',
    justifyContent: 'center',
    padding: '60px 24px',
  },
  card: {
    background: '#fff',
    border: '1.5px solid #e5e7eb',
    borderRadius: '16px',
    padding: '48px 40px',
    width: '100%',
    maxWidth: '520px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.06)',
  },
  progress: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '40px',
  },
  progressStep: {
    flex: 1,
    height: '3px',
    background: '#e5e7eb',
    borderRadius: '2px',
    overflow: 'hidden',
  },
  progressStepFill: {
    height: '100%',
    background: '#2563eb',
    borderRadius: '2px',
    transition: 'width 0.3s',
  },
  progressLabel: {
    fontSize: '13px',
    color: '#6b7280',
    fontWeight: 500,
    marginBottom: '32px',
    textAlign: 'center',
  },
  stepTitle: {
    fontSize: '22px',
    fontWeight: 700,
    color: '#111827',
    letterSpacing: '-0.4px',
    marginBottom: '8px',
  },
  stepDesc: {
    fontSize: '15px',
    color: '#6b7280',
    lineHeight: 1.6,
    marginBottom: '32px',
  },
  fieldGroup: {
    marginBottom: '20px',
  },
  label: {
    display: 'block',
    fontSize: '14px',
    fontWeight: 600,
    color: '#374151',
    marginBottom: '6px',
  },
  input: {
    width: '100%',
    padding: '11px 14px',
    border: '1.5px solid #e5e7eb',
    borderRadius: '8px',
    fontSize: '15px',
    fontFamily: 'inherit',
    color: '#111827',
    outline: 'none',
    transition: 'border-color 0.15s, box-shadow 0.15s',
    background: '#fff',
  },
  inputHint: {
    fontSize: '12px',
    color: '#9ca3af',
    marginTop: '5px',
    lineHeight: 1.5,
  },
  btnPrimary: {
    width: '100%',
    padding: '13px 20px',
    background: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: '10px',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
    marginTop: '8px',
    transition: 'background 0.15s',
  },
  btnSecondary: {
    width: '100%',
    padding: '13px 20px',
    background: 'transparent',
    color: '#6b7280',
    border: '1.5px solid #e5e7eb',
    borderRadius: '10px',
    fontSize: '15px',
    fontWeight: 600,
    cursor: 'pointer',
    fontFamily: 'inherit',
    marginTop: '10px',
    transition: 'background 0.15s',
  },
  successIcon: {
    fontSize: '56px',
    textAlign: 'center',
    marginBottom: '20px',
  },
  successTitle: {
    fontSize: '24px',
    fontWeight: 700,
    color: '#111827',
    textAlign: 'center',
    marginBottom: '12px',
    letterSpacing: '-0.4px',
  },
  successDesc: {
    fontSize: '15px',
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 1.65,
    marginBottom: '32px',
  },
  checkList: {
    listStyle: 'none',
    padding: 0,
    marginBottom: '32px',
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
  },
  checkItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    fontSize: '15px',
    color: '#374151',
    fontWeight: 500,
  },
  checkMark: {
    width: '22px',
    height: '22px',
    background: '#d1fae5',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    color: '#059669',
    fontWeight: 700,
    flexShrink: 0,
  },
}

function StepShopify({ onNext }) {
  const [storeUrl, setStoreUrl] = useState('')
  const [token, setToken] = useState('')

  return (
    <>
      <h2 style={styles.stepTitle}>Connect your Shopify store</h2>
      <p style={styles.stepDesc}>
        We need read-only access to your inventory to monitor stock levels. Setup takes 2 minutes.
      </p>
      <div style={styles.fieldGroup}>
        <label style={styles.label} htmlFor="store-url">Shopify store URL</label>
        <input
          id="store-url"
          type="text"
          style={styles.input}
          placeholder="yourstore.myshopify.com"
          value={storeUrl}
          onChange={e => setStoreUrl(e.target.value)}
        />
        <div style={styles.inputHint}>Your .myshopify.com domain, not your custom domain.</div>
      </div>
      <div style={styles.fieldGroup}>
        <label style={styles.label} htmlFor="access-token">Admin API access token</label>
        <input
          id="access-token"
          type="password"
          style={styles.input}
          placeholder="shpat_..."
          value={token}
          onChange={e => setToken(e.target.value)}
        />
        <div style={styles.inputHint}>
          Generate a read-only token in Shopify Admin &rarr; Settings &rarr; Apps and sales channels &rarr; Develop apps.
          We only need read_inventory and read_products scopes.
        </div>
      </div>
      <button
        style={styles.btnPrimary}
        onClick={() => storeUrl && token && onNext({ storeUrl, token })}
      >
        Connect Store &rarr;
      </button>
    </>
  )
}

function StepSupplier({ onNext, onBack }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [moq, setMoq] = useState('')

  return (
    <>
      <h2 style={styles.stepTitle}>Add your first supplier</h2>
      <p style={styles.stepDesc}>
        Tell us about one of your suppliers. You can add more from the dashboard later.
      </p>
      <div style={styles.fieldGroup}>
        <label style={styles.label} htmlFor="supplier-name">Supplier name</label>
        <input
          id="supplier-name"
          type="text"
          style={styles.input}
          placeholder="Acme Wholesale Co."
          value={name}
          onChange={e => setName(e.target.value)}
        />
      </div>
      <div style={styles.fieldGroup}>
        <label style={styles.label} htmlFor="supplier-email">Supplier PO email</label>
        <input
          id="supplier-email"
          type="email"
          style={styles.input}
          placeholder="orders@acmewholesale.com"
          value={email}
          onChange={e => setEmail(e.target.value)}
        />
        <div style={styles.inputHint}>The email address where purchase orders should be sent.</div>
      </div>
      <div style={styles.fieldGroup}>
        <label style={styles.label} htmlFor="supplier-moq">Minimum order quantity (MOQ)</label>
        <input
          id="supplier-moq"
          type="number"
          style={styles.input}
          placeholder="50"
          value={moq}
          onChange={e => setMoq(e.target.value)}
          min="1"
        />
        <div style={styles.inputHint}>The minimum number of units per order this supplier requires.</div>
      </div>
      <button
        style={styles.btnPrimary}
        onClick={() => name && email && onNext({ name, email, moq })}
      >
        Add Supplier &rarr;
      </button>
      <button style={styles.btnSecondary} onClick={onBack}>
        Back
      </button>
    </>
  )
}

function StepDone() {
  return (
    <>
      <div style={styles.successIcon}>🎉</div>
      <div style={styles.successTitle}>You're all set!</div>
      <p style={styles.successDesc}>
        Reorderly is now monitoring your inventory. When stock hits a reorder threshold, we'll automatically send a purchase order to your supplier.
      </p>
      <ul style={styles.checkList}>
        <li style={styles.checkItem}>
          <span style={styles.checkMark}>✓</span>
          Shopify store connected
        </li>
        <li style={styles.checkItem}>
          <span style={styles.checkMark}>✓</span>
          First supplier added
        </li>
        <li style={styles.checkItem}>
          <span style={styles.checkMark}>✓</span>
          Inventory monitoring active
        </li>
      </ul>
      <a href="/app/" style={{ ...styles.btnPrimary, textAlign: 'center', display: 'block', textDecoration: 'none' }}>
        Go to Dashboard
      </a>
    </>
  )
}

export default function Onboarding() {
  const [step, setStep] = useState(1)
  const [data, setData] = useState({})

  const totalSteps = 3
  const progress = (step / totalSteps) * 100

  const stepLabels = ['Connect store', 'Add supplier', 'All set']

  return (
    <div style={styles.page}>
      <header style={styles.header}>
        <span style={styles.logoName}>Reorderly</span>
      </header>
      <div style={styles.body}>
        <div style={styles.card}>
          {step < 3 && (
            <>
              <div style={styles.progress}>
                {[1, 2, 3].map(s => (
                  <div key={s} style={styles.progressStep}>
                    <div
                      style={{
                        ...styles.progressStepFill,
                        width: step >= s ? '100%' : '0%',
                      }}
                    />
                  </div>
                ))}
              </div>
              <div style={styles.progressLabel}>
                Step {step} of {totalSteps} &mdash; {stepLabels[step - 1]}
              </div>
            </>
          )}

          {step === 1 && (
            <StepShopify
              onNext={(shopifyData) => {
                setData(d => ({ ...d, shopify: shopifyData }))
                setStep(2)
              }}
            />
          )}

          {step === 2 && (
            <StepSupplier
              onNext={(supplierData) => {
                setData(d => ({ ...d, supplier: supplierData }))
                setStep(3)
              }}
              onBack={() => setStep(1)}
            />
          )}

          {step === 3 && <StepDone />}
        </div>
      </div>
    </div>
  )
}
