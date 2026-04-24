import React, { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import styles from './Layout.module.css'

const NAV = [
  { to: '/dashboard',    label: 'Dashboard',    icon: '▦' },
  { to: '/submit',       label: 'Submit Report', icon: '⊕' },
  { to: '/submissions',  label: 'Submissions',  icon: '≡' },
  { to: '/marketplace',  label: 'Marketplace',  icon: '◈' },
]

export default function Layout() {
  const location = useLocation()

  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.logo}>
          <span className={styles.logoMark}>CCT</span>
          <div>
            <div className={styles.logoName}>Carbon Credit</div>
            <div className={styles.logoSub}>Tracer</div>
          </div>
        </div>

        <nav className={styles.nav}>
          {NAV.map(n => (
            <NavLink
              key={n.to}
              to={n.to}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.active : ''}`
              }
            >
              <span className={styles.navIcon}>{n.icon}</span>
              <span>{n.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.networkBadge}>
            <span className={styles.dot} />
            Polygon Testnet
          </div>
          <div className={styles.version}>v1.0.0 MVP</div>
        </div>
      </aside>

      <main className={styles.main}>
        <Outlet />
      </main>
    </div>
  )
}
