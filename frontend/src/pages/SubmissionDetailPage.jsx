import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getSubmission } from '../utils/api'
import StatusBadge from '../components/StatusBadge'
import styles from './SubmissionDetailPage.module.css'

const fmt   = (n) => new Intl.NumberFormat('en', { maximumFractionDigits: 4 }).format(n)
const fmtDt = (d) => new Date(d).toLocaleString('en', { dateStyle: 'long', timeStyle: 'short' })

export default function SubmissionDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData]   = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getSubmission(id)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className={styles.state}>Loading report...</div>
  if (error)   return <div className={styles.stateErr}>{error}</div>
  if (!data)   return null

  const saved = data.baseline.baseline_co2_tonnes - data.reported_co2_tonnes
  const approved = data.final_status === 'APPROVED'

  return (
    <div className={styles.page}>
      {/* Back */}
      <button className={styles.back} onClick={() => navigate('/submissions')}>← All submissions</button>

      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.company}>{data.company_name}</h1>
          <div className={styles.meta}>
            <span className="mono">{data.company_id}</span>
            <span className={styles.sep}>·</span>
            <span>{data.period}</span>
            <span className={styles.sep}>·</span>
            <span>{fmtDt(data.created_at)}</span>
          </div>
        </div>
        <StatusBadge status={data.final_status} />
      </div>

      <div className={styles.grid}>
        {/* Step 1: Submitted data */}
        <div className={styles.card}>
          <div className={styles.step}>Step 1</div>
          <div className={styles.cardTitle}>Submitted data</div>
          <div className={styles.rows}>
            <Row label="Material"  value={<span className={styles.mat}>{data.material}</span>} />
            <Row label="Quantity"  value={`${fmt(data.quantity_tonnes)} tonnes`} mono />
            <Row label="Reported CO₂" value={`${fmt(data.reported_co2_tonnes)} tonnes`} mono />
          </div>
        </div>

        {/* Step 2: Baseline */}
        <div className={styles.card}>
          <div className={styles.step}>Step 2</div>
          <div className={styles.cardTitle}>Baseline lookup (IPCC)</div>
          <div className={styles.rows}>
            <Row label="Emission factor" value={`${data.baseline.emission_factor} t CO₂/t`} mono />
            <Row label="Calculation"     value={`${fmt(data.quantity_tonnes)} × ${data.baseline.emission_factor}`} mono />
            <Row label="Baseline CO₂"   value={`${fmt(data.baseline.baseline_co2_tonnes)} tonnes`} mono highlight />
            <Row label="Source"         value={data.baseline.source} small />
          </div>
        </div>

        {/* Step 3: AI verification */}
        <div className={styles.card}>
          <div className={styles.step}>Step 3</div>
          <div className={styles.cardTitle}>AI anomaly detection</div>
          <div className={styles.rows}>
            <Row label="Model"         value="Isolation Forest" />
            <Row label="Anomaly score" value={fmt(data.ai_verification.anomaly_score)} mono />
            <Row label="Confidence"    value={`${(data.ai_verification.confidence * 100).toFixed(1)}%`} mono />
            <Row label="Verdict"       value={<StatusBadge status={data.ai_verification.verdict} />} />
          </div>
        </div>

        {/* Step 4: Credit calculation */}
        <div className={`${styles.card} ${approved ? styles.cardApproved : styles.cardRejected}`}>
          <div className={styles.step}>Step 4</div>
          <div className={styles.cardTitle}>Credit calculation</div>
          <div className={styles.rows}>
            <Row label="Baseline CO₂"  value={`${fmt(data.baseline.baseline_co2_tonnes)} t`} mono />
            <Row label="Reported CO₂"  value={`${fmt(data.reported_co2_tonnes)} t`} mono />
            <Row label="CO₂ saved"     value={saved > 0 ? `${fmt(saved)} t` : `Exceeded by ${fmt(Math.abs(saved))} t`} mono highlight={saved > 0} />
            <Row label="Credits (CCT)" value={approved ? `${fmt(data.credits.credits_earned)} CCT` : '0 CCT'} mono highlight={approved} />
          </div>
          <div className={styles.reason}>{data.credits.reason}</div>
        </div>
      </div>

      {/* Blockchain section */}
      <div className={styles.blockchainCard}>
        <div className={styles.blockchainLeft}>
          <div className={styles.bTitle}>Blockchain record</div>
          <div className={styles.bSub}>
            {approved
              ? `${fmt(data.credits.credits_earned)} CCT tokens queued for minting on Polygon`
              : 'Rejection logged as immutable audit record'}
          </div>
          <div className={styles.bId}>
            <span className={styles.bLabel}>Submission ID</span>
            <span className="mono">{data.submission_id}</span>
          </div>
          {data.blockchain_ref && (
            <div className={styles.bId}>
              <span className={styles.bLabel}>Tx hash</span>
              <span className="mono">{data.blockchain_ref}</span>
            </div>
          )}
        </div>
        <div className={`${styles.blockchainStatus} ${approved ? styles.bApproved : styles.bRejected}`}>
          <div className={styles.bStatusIcon}>{approved ? '⬡' : '✗'}</div>
          <div className={styles.bStatusText}>{approved ? 'Mint pending' : 'Not eligible'}</div>
        </div>
      </div>
    </div>
  )
}

function Row({ label, value, mono, highlight, small }) {
  return (
    <div className={styles.row}>
      <span className={styles.rowLabel}>{label}</span>
      <span className={`${styles.rowVal} ${mono ? 'mono' : ''} ${highlight ? styles.highlight : ''} ${small ? styles.small : ''}`}>
        {value}
      </span>
    </div>
  )
}
