/**
 * MifugoIQ Masumi Demo Component
 * Paste as: src/components/MasumiDemo.tsx
 *
 * Shows the live agent-to-agent payment flow for the demo:
 * AgriFin Lender Agent → pays MifugoIQ via Masumi → receives Collateral Valuation Report
 */
import { useState } from "react";
import { runMasumiDemo, MasumiDemoResult } from "../services/mifugoiq";

export default function MasumiDemo() {
  const [breed, setBreed] = useState("Boran");
  const [ageClass, setAgeClass] = useState("Store(2-3yr)");
  const [head, setHead] = useState(15);
  const [county, setCounty] = useState("Kajiado");
  const [result, setResult] = useState<MasumiDemoResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const run = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const r = await runMasumiDemo(breed, ageClass, head, county);
      setResult(r);
    } catch (e) {
      setError("Demo failed — check backend connection");
    } finally {
      setLoading(false);
    }
  };

  const fmt = (n: number) => `KES ${n.toLocaleString()}`;

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
        <h2 className="font-bold text-amber-900 text-sm mb-1">🔗 Masumi Agent-to-Agent Demo</h2>
        <p className="text-xs text-amber-700">
          Simulates an AgriFin Lender Agent paying MifugoIQ for a collateral valuation report via Masumi.
        </p>
      </div>

      {/* Inputs */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Breed</label>
          <select
            value={breed}
            onChange={(e) => setBreed(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option>Boran</option>
            <option>Zebu</option>
            <option>Sahiwal-cross</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Age Class</label>
          <select
            value={ageClass}
            onChange={(e) => setAgeClass(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option value="Store(2-3yr)">Store 2–3yr</option>
            <option value="Mature(3+yr)">Mature 3+yr</option>
            <option value="Weaner(1-2yr)">Weaner 1–2yr</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">Head Count</label>
          <input
            type="number"
            value={head}
            min={1}
            max={500}
            onChange={(e) => setHead(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="text-xs text-gray-500 mb-1 block">County</label>
          <select
            value={county}
            onChange={(e) => setCounty(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          >
            <option>Kajiado</option>
            <option>Machakos</option>
            <option>Nairobi</option>
          </select>
        </div>
      </div>

      <button
        onClick={run}
        disabled={loading}
        className="w-full bg-amber-600 text-white rounded-xl py-3 font-medium text-sm hover:bg-amber-700 disabled:opacity-50 transition-colors"
      >
        {loading ? "Running demo…" : "▶ Run Agent-to-Agent Demo"}
      </button>

      {error && <p className="text-red-600 text-sm text-center">{error}</p>}

      {result && (
        <div className="space-y-3">
          {/* Step 1 */}
          <Step n={1} label="Lender Agent requests payment invoice from MifugoIQ">
            <Row label="Service" value="Collateral Valuation Report" />
            <Row label="Price" value={`${result.step_1_payment_request.amount_usdm} USDM`} />
            <Row label="Payment Ref" value={result.step_2_payment_ref} mono />
          </Step>

          {/* Step 2 */}
          <Step n={2} label="Payment Verified" ok={result.step_3_payment_verified}>
            <Row label="Status" value={result.step_3_payment_verified ? "✅ Confirmed" : "❌ Failed"} />
          </Step>

          {/* Step 3 — Collateral Report */}
          <Step n={3} label="MifugoIQ Collateral Valuation Report">
            {(() => {
              const r = result.step_4_collateral_report as any;
              return (
                <>
                  <Row label="Breed / Age" value={`${r.breed} · ${r.age_class}`} />
                  <Row label="Reference Market" value={r.reference_market} />
                  <Row label="Per Head Price" value={fmt(r.per_head_price_kes)} highlight />
                  <Row label={`× ${r.head_count} head`} value={fmt(r.total_gross_kes)} />
                  <Row label="Transport deduction" value={`−${fmt(r.transport_cost_per_head_kes * r.head_count)}`} />
                  <Row label="Net Realizable Value" value={fmt(r.net_realizable_value_kes)} highlight />
                  <Row label="Risk Flag" value={r.underwriting_recommendation} />
                  <Row label="Source / Date" value={`${r.data_source} · ${r.price_date}`} />
                </>
              );
            })()}
          </Step>

          {/* Step 4 — Lending Decision */}
          <Step n={4} label="Lender Agent Decision">
            {(() => {
              const d = result.step_5_lender_decision;
              return (
                <>
                  <Row label="LTV Applied" value={`${d.ltv_pct}%`} />
                  <Row label="Loan Limit" value={fmt(d.recommended_loan_limit_kes)} highlight />
                  <div className={`mt-2 rounded-lg px-3 py-2 text-sm font-bold text-center ${d.decision === "APPROVE" ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                    {d.decision} — {d.decision_note}
                  </div>
                </>
              );
            })()}
          </Step>
        </div>
      )}
    </div>
  );
}

function Step({ n, label, ok, children }: { n: number; label: string; ok?: boolean; children: React.ReactNode }) {
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <div className="bg-gray-50 px-4 py-2 flex items-center gap-2">
        <span className="bg-gray-800 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">{n}</span>
        <span className="text-sm font-medium text-gray-700">{label}</span>
        {ok !== undefined && <span className="ml-auto">{ok ? "✅" : "❌"}</span>}
      </div>
      <div className="px-4 py-3 space-y-1">{children}</div>
    </div>
  );
}

function Row({ label, value, mono, highlight }: { label: string; value: string | number; mono?: boolean; highlight?: boolean }) {
  return (
    <div className="flex justify-between items-start gap-2 text-sm">
      <span className="text-gray-500 shrink-0">{label}</span>
      <span className={`text-right ${mono ? "font-mono text-xs" : ""} ${highlight ? "font-bold text-gray-900" : "text-gray-700"}`}>
        {String(value)}
      </span>
    </div>
  );
}
