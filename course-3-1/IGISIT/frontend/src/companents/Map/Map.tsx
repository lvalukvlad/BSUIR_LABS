'use client';

import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import belarusDistricts from '@/data/belarus-districts.json'
import { useEffect, useState } from 'react'
import { useMedia } from 'react-use'
import styles from './Map.module.css'
import { Feature, Geometry } from "geojson"
import { FeatureCollection } from "geojson"
import { Layer } from "leaflet"
import { Path } from "leaflet"

const useThemeDetector = () => {
  const isLight = useMedia('(prefers-color-scheme: light)')
  return isLight
}

type DistrictProps = {
  shapeName: string
  [key: string]: string | number | boolean | null
}



interface Props{
  setRegion: (region: string) => void
}

export default function Map({setRegion}: Props) {
const [selected, setSelected] = useState<DistrictProps | null>(null)
  useEffect(() => {
    if (selected !== null){
      setRegion(selected.shapeName)
    }
    else {
      setRegion("Республика Беларусь")
    }
  }, [selected])
  const isLight = useThemeDetector()
  const primary = isLight ? '#D32F2F' : '#A53939'
  const foreground = isLight ? '#F7DEF8' : '#2E2A2A'

  const districtStyle = {
    fillColor: primary,
    color: '#fff',
    weight: 1,
    fillOpacity: 0.7,
  };

const onEachDistrict = (
  feature: Feature<Geometry, DistrictProps>,
  layer: Layer
) => {
  if (layer instanceof Path) {
    layer.on({
      click: () => setSelected(feature.properties),
      mouseover: () => layer.setStyle({ fillOpacity: 1 }),
      mouseout: () => layer.setStyle({ fillOpacity: 0.7 }),
    })
  }
}

  return (
      <li>
      <MapContainer
        center={[53.9, 27.5667]}
        zoom={7}
        style={{ height: '500px', width: '100%', backgroundColor: '#2E2A2A' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        <GeoJSON
          data={belarusDistricts as unknown as FeatureCollection<Geometry, DistrictProps>}
          style={districtStyle}
          onEachFeature={onEachDistrict}
        />
      </MapContainer>
      </li>
  )
}
