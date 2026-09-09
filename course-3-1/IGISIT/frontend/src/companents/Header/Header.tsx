'use client'
import styles from "./Header.module.css"
import { usePathname, useRouter } from "next/navigation"

interface Props {
  setRegion: (region: string) => void
}

export default function Header({ setRegion }: Props) {
  const router = useRouter()
  const pathname = usePathname()

  function togglePage() {
    if (pathname === "/graphics") {
      router.push("/")
    } else {
      router.push("/graphics")
    }
  }

  return (
    <header className={styles.header}>
      <li className={styles.li}>
        <button
          className={styles.link}
          onClick={() => setRegion("Республика Беларусь")}
        >
          Вся Республика
        </button>

        <button
          className={styles.link}
          onClick={togglePage}
        >
          {pathname === "/graphics" ? "По годам" : "Статистика"}
        </button>
      </li>
    </header>
  )
}
