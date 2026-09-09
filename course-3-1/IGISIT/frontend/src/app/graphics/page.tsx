"use client"

import styles from "./page.module.css"
import { useEffect, useState } from "react"
import Header from "@/companents/Header/Header"
import selectRegionStats from "@/sorse/selectRegionStats"

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid
} from "recharts"

import dynamic from "next/dynamic"
const Map = dynamic(() => import("@/companents/Map/Map"), { ssr: false })

type RegionRow = {
  year: number
  [indicator: string]: number | null
}

type RegionAnalytics = {
  years: number[]
  merged: RegionRow[]
  indicators: string[]
}

export default function AnalyticsPage() {
  const [region, setRegion] = useState<string>("Республика Беларусь")
  const [regionData, setRegionData] = useState<RegionAnalytics | null>(null)

  useEffect(() => {
    async function getRegionStats() {
      const response = await selectRegionStats(region)
      const list = Array.isArray(response) ? response : response?.data ?? []

      if (!Array.isArray(list) || list.length === 0) {
        setRegionData(null)
        return
      }

      const allIndicators = Array.from(
        new Set(list.map((item) => item.indicator))
      )

      const allYears = Array.from(
        new Set(list.map((item) => item.year))
      ).sort((a, b) => a - b)

      const merged = allYears.map((year) => {
        const row: RegionRow = { year }

        allIndicators.forEach((indicator) => {
          const record = list.find(
            (i) => i.year === year && i.indicator === indicator
          )
          row[indicator] = record ? record.value : null
        })

        return row
      })

      setRegionData({
        years: merged.map((r) => r.year),
        merged,
        indicators: allIndicators
      })
    }

    getRegionStats()
  }, [region])

  const indicators =
    regionData?.merged && regionData.merged.length > 0
      ? Object.keys(regionData.merged[0]).filter((k) => k !== "year")
      : []

  function trimIndicator(series: RegionRow[], indicator: string) {
    const idx = series.findIndex((row) => row[indicator] !== null)
    if (idx === -1) return []
    return series.slice(idx)
  }

  return (
    <>
      <Header setRegion={setRegion} />
      <main className={styles.main}>

        {/* КАРТА */}
        <div className={styles.mapContainer}>
          <Map setRegion={setRegion} />
        </div>

        {/* ГРАФИКИ */}
        <div className={styles.graphPanel}>
          <h1 className={styles.regionTitle}>
            Аналитика: {region || "Регион не выбран"}
          </h1>

          {!region && (
            <p className={styles.note}>Выберите регион на карте</p>
          )}

          {regionData && (
            <div className={styles.grid}>
              {indicators.map((indicator) => {
                const trimmed = trimIndicator(regionData.merged, indicator)
                const hasData = trimmed.length > 0

                return (
                  <div key={indicator} className={styles.chartCard}>
                    <h3 className={styles.chartTitle}>{indicator}</h3>

                    {!hasData && (
                      <div style={{ padding: 14, color: "#fff9", fontSize: 14 }}>
                        Нет данных для данного показателя
                      </div>
                    )}

                    {hasData && (
                      <ResponsiveContainer width="100%" height={260}>
                        <LineChart data={trimmed}>
                          <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                          <XAxis dataKey="year" />
                          <YAxis />
                          <Tooltip />
                          <Legend />
                          <Line
                            type="monotone"
                            dataKey={indicator}
                            stroke="#2e2a2a"
                            strokeWidth={2}
                            dot={false}
                            connectNulls={true}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    )}
                  </div>
                )
              })}
            </div>
          )}
        </div>

      </main>
    </>
  )
}
