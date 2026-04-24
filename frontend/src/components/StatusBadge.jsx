import React from 'react'
import styles from './StatusBadge.module.css'

export default function StatusBadge({ status }) {
  const map = {
    APPROVED:   styles.approved,
    REJECTED:   styles.rejected,
    NORMAL:     styles.normal,
    SUSPICIOUS: styles.suspicious,
    FLAGGED:    styles.flagged,
  }
  return (
    <span className={`${styles.badge} ${map[status] || styles.default}`}>
      {status}
    </span>
  )
}
