import React from 'react'
import styles from './StatCard.module.css'

export default function StatCard({ label, value, sub, accent = 'green', loading }) {
  return (
    <div className={`${styles.card} ${styles[accent]}`}>
      <div className={styles.label}>{label}</div>
      {loading ? (
        <div className={styles.skeleton} />
      ) : (
        <div className={styles.value}>{value}</div>
      )}
      {sub && <div className={styles.sub}>{sub}</div>}
    </div>
  )
}
