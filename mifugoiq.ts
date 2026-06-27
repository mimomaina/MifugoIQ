/**
 * MifugoIQ API Service
 * Paste this file into your Lovable project at: src/services/mifugoiq.ts
 *
 * In Lovable: Add the BACKEND URL as an environment variable named VITE_API_URL
 * (Project Settings → Environment Variables)
 */

const API_URL = import.meta.env.VITE_API_URL || "https://your-backend.railway.app";

// ── Types ──────────────────────────────────────────────────────

export interface ChatResponse {
  answer: string;
  intent: string;
  entities: Record<string, unknown>;
  graph_data: Record<string, unknown>[];
  model: string;
  query_description: string;
}

export interface PriceRecord {
  breed: string;
  ageClass: string;
  county: string;
  market: string;
  priceKES: number;
  date: string;
  source: string;
}

export interface Slaughterhouse {
  name: string;
  county: string;
  location: string;
  capacityPerDay: number;
  halal: boolean;
  feeKES?: number;
}

export interface NRVRecord {
  market: string;
  destCounty: string;
  grossPrice: number;
  transportCost: number;
  netPrice: number;
  date: string;
  source: string;
  transporter: string;
}

export interface CollateralReport {
  breed: string;
  ageClass: string;
  county: string;
  perHeadPriceKes: number;
  headCount: number;
  totalGrossKes: number;
  transportCostPerHeadKes: number;
  netRealizableValueKes: number;
  underwritingRecommendation: string;
  suggestedLtvPct: number;
  priceDate: string;
  source: string;
  referenceMarket: string;
  disclaimer: string;
}

export interface MasumiDemoResult {
  flow: string;
  step_1_payment_request: Record<string, unknown>;
  step_2_payment_ref: string;
  step_3_payment_verified: boolean;
  step_4_collateral_report: CollateralReport;
  step_5_lender_decision: {
    net_realizable_value_kes: number;
    ltv_pct: number;
    recommended_loan_limit_kes: number;
    decision: "APPROVE" | "DECLINE";
    decision_note: string;
  };
}

// ── API calls ──────────────────────────────────────────────────

/** Send a natural-language query to the MifugoIQ agent */
export async function askMifugoIQ(query: string): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

/** Fetch all recent price observations (for Price Explorer map/chart) */
export async function getPrices(county?: string, breed?: string): Promise<PriceRecord[]> {
  const params = new URLSearchParams();
  if (county) params.set("county", county);
  if (breed) params.set("breed", breed);
  const res = await fetch(`${API_URL}/api/prices?${params}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = await res.json();
  return data.prices;
}

/** Fetch slaughterhouse directory */
export async function getSlaughterhouses(halalOnly = false): Promise<Slaughterhouse[]> {
  const res = await fetch(`${API_URL}/api/slaughterhouses?halal_only=${halalOnly}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = await res.json();
  return data.slaughterhouses;
}

/** Fetch Net Realizable Value ranking */
export async function getNRV(
  breed: string,
  ageClass: string,
  originCounty: string
): Promise<NRVRecord[]> {
  const params = new URLSearchParams({
    breed,
    age_class: ageClass,
    origin_county: originCounty,
  });
  const res = await fetch(`${API_URL}/api/nrv?${params}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  const data = await res.json();
  return data.nrv_ranking;
}

/** Run the Masumi agent-to-agent demo flow */
export async function runMasumiDemo(
  breed = "Boran",
  ageClass = "Store(2-3yr)",
  head = 15,
  county = "Kajiado"
): Promise<MasumiDemoResult> {
  const params = new URLSearchParams({
    breed,
    age_class: ageClass,
    head: String(head),
    county,
  });
  const res = await fetch(`${API_URL}/api/masumi/demo?${params}`);
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json();
}

/** Health check */
export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}
