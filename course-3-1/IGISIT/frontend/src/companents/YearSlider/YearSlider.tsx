"use client";

import * as Slider from "@radix-ui/react-slider"
import { useEffect, useState } from "react"
import styles from "./YearSlider.module.css"

interface YearSliderProps {
  startYear: number
  lastYear: number
  value: number
  onChange?: (year: number) => void
}

export default function YearSlider({
  startYear,
  lastYear,
  value,
  onChange,
}: YearSliderProps) {
  const [year, setYear] = useState(value)
  useEffect(() => {
    setYear(value)
  }, [value])
  const handleChange = (val: number[]) => {
    setYear(val[0])
    onChange?.(val[0])
  };

  return (
    <div className={styles.container}>
      <Slider.Root
        className={styles.sliderRoot}
        min={startYear}
        max={lastYear}
        step={1}
        defaultValue={[value]}
        onValueChange={handleChange}
      >
        <Slider.Track className={styles.sliderTrack}>
          <Slider.Range className={styles.sliderRange} />
        </Slider.Track>
        <Slider.Thumb className={styles.sliderThumb} />
      </Slider.Root>

      <span className={styles.yearLabel}>{year}</span>
    </div>
  );
}
