import React, { useEffect, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getSubmissions } from '../utils/api'
import StatusBadge from '../components/StatusBadge'
import styles from './SubmissionsPage.module.css'

const fmt = (n) => new Intl.NumberFormat('en', { maximumFractionDigits: 2 }).format(n)
const fmtDate = (d) => new Date(d).toLocaleDateString('en', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })

export default function SubmissionsPage() {
  const navigate = useNavigate()
  const [rows, setRows]         = useState([])
  const [loading, setLoading]   = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [materialFilter, setMaterialFilter] = useState('')

  const load = useCallback(() => {
    setLoading(true)
    const params = {}
    if (statusFilter)   params.status   = statusFilter
    if (materialFilter) params.material = materialFilter
    getSubmissions(params)
      .then(setRows)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [statusFilter, materialFilter])

  useEffect(() => { load() }, [load])

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>All Submissions</h1>
          <p className={styles.sub}>Full audit trail of every emission report</p>
        </div>
        <button className={styles.ctaBtn} onClick={() => navigate('/submit')}>+ New Report</button>
      </div>

      {/* Filters */}
      <div className={styles.filters}>
        <select className={styles.filterSelect} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="APPROVED">Approved</option>
          <option value="REJECTED">Rejected</option>
        </select>
        <select className={styles.filterSelect} value={materialFilter} onChange={e => setMaterialFilter(e.target.value)}>
          <option value="">All materials</option>
          <option value="cement">Cement</option>
          <option value="steel">Steel</option>
          <option value="aluminum">Aluminum</option>
        </select>
        <span className={styles.count}>{rows.length} records</span>
      </div>

      {/* Table */}
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Company</th>
              <th>Period</th>
              <th>Material</th>
              <th>Qty (t)</th>
              <th>Reported CO₂</th>
              <th>Baseline CO₂</th>
              <th>CO₂ Saved</th>
              <th>Credits (CCT)</th>
              <th>AI</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={11} className={styles.loading}>Loading...</td></tr>
            )}
            {!loading && rows.length === 0 && (
              <tr><td colSpan={11} className={styles.empty}>No submissions found</td></tr>
            )}
            {!loading && rows.map(r => {
              const saved = r.baseline_co2_tonnes - r.reported_co2_tonnes
              return (
                <tr key={r.submission_id} onClick={() => navigate(`/submissions/${r.submission_id}`)} className={styles.row}>
                  <td className={styles.company}>{r.company_name}</td>
                  <td className={`mono ${styles.period}`}>{r.period || '—'}</td>
                  <td><span className={styles.mat}>{r.material}</span></td>
                  <td className="mono">{fmt(r.quantity_tonnes)}</td>
                  <td className="mono">{fmt(r.reported_co2_tonnes)}t</td>
                  <td className="mono">{fmt(r.baseline_co2_tonnes)}t</td>
                  <td className={`mono ${saved > 0 ? styles.savedPos : styles.savedNeg}`}>
                    {saved > 0 ? `−${fmt(saved)}t` : `+${fmt(Math.abs(saved))}t`}
                  </td>
                  <td className={`mono ${styles.credits}`}>
                    {r.credits_earned > 0 ? `+${fmt(r.credits_earned)}` : '0'}
                  </td>
                  <td><StatusBadge status={r.ai_verdict || 'NORMAL'} /></td>
                  <td><StatusBadge status={r.final_status} /></td>
                  <td className={styles.date}>{fmtDate(r.created_at)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
