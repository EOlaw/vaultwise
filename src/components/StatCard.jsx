export function StatCard({ label, value, accent = "text-ink" }) {
  return (
    <div className="panel p-3 sm:p-4">
      <div className="mb-3 h-1 w-10 rounded-full bg-mint/70" />
      <p className="text-[11px] font-black uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-1 text-lg font-black sm:text-xl ${accent}`}>{value}</p>
    </div>
  )
}
