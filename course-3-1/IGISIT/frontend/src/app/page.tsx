'use client'

import styles from "./page.module.css"
import dynamic from "next/dynamic"
const Map = dynamic(() => import("@/companents/Map/Map"), { ssr: false })
import YearSlider from "@/companents/YearSlider/YearSlider"
import { useEffect, useState } from "react"
import Header from "@/companents/Header/Header"
import selectRegionStats from "@/sorse/selectRegionStats"


type RegionStats = {
  years: number[]
  data: Record<number, Record<string, number>>
}


export default function Page() {
  const [year, setYear] = useState<number | null>(null)
  const [region, setRegion] = useState<string>("")
  const [regionData, setRegionData] = useState<RegionStats | null>(null)

useEffect(() => {
  async function getRegionStats() {
    const response = await selectRegionStats(region)

    // Универсальная защита — приводим что угодно к массиву
    const list = Array.isArray(response) ? response : response?.data ?? []

    if (!Array.isArray(list) || list.length === 0) {
      setRegionData(null)
      return
    }

    // 1) Собираем список лет
    const years = Array.from(new Set(list.map(item => item.year))).sort(
      (a, b) => a - b
    )

    // 2) Группируем данные по году
  const dataByYear: Record<number, Record<string, number>> = {}

    years.forEach(year => {
      dataByYear[year] = {}

      list
        .filter(item => item.year === year)
        .forEach(item => {
          dataByYear[year][item.indicator] = item.value
        })
    })

    setRegionData({ years, data: dataByYear })
    setYear(years[0])
  }

  getRegionStats()
}, [region])



  const startYear = regionData?.years?.[0]
  const lastYear = regionData?.years?.[regionData.years.length - 1]

  const metricsForYear =
    year && regionData?.data ? regionData.data[year] || {} : {}

  return (
    <>
      <Header setRegion={setRegion} />
      <main>
        <ul className={styles.ul}>
          <li className={styles.mapLi}>
            <div>
              <ul className={styles.div}>
                <Map setRegion={setRegion} />
                
                <li
                  className={`${styles.rightLi} ${
                    Object.keys(metricsForYear).length > 6 ? styles.wideMetrics : ""
                  }`}
                >
                  <div className={styles.infoBox}>
                    <h2 className={styles.regionName}>{region}</h2>
                    <h2 className={styles.regionName}>{year}</h2>

                    <div
                      className={`${styles.metrics} ${
                        Object.keys(metricsForYear).length > 6 ? styles.metricsGrid : ""
                      }`}
                    >
                      {Object.entries(metricsForYear).map(([key, value]) => (
                        <div key={key} className={styles.metricRow}>
                          <span className={styles.metricName}>{key}</span>
                          <span className={styles.metricValue}>{value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </li>
              </ul>
            </div>
          </li>

          <li>
            {startYear && lastYear && (
              <YearSlider
                onChange={setYear}
                startYear={startYear}
                lastYear={lastYear}
                value={startYear}
              />
            )}
          </li>
        </ul>
      </main>
    </>
  )
}
