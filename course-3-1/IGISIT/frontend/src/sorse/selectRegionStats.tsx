'use state'

export default async function selectRegionStats(region: string) {
  try {
    const encodedRegion = encodeURIComponent(region);
    const baseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"; // <- fallback

    const response = await fetch(`${baseUrl}/data/region/${encodedRegion}`);

    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}