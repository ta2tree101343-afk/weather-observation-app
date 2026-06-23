import { useEffect, useRef, useState } from "react";
import type { Ward } from "../api";

export function WardSelect({
  wards,
  selected,
  onChange,
}: {
  wards: Ward[];
  selected: string;
  onChange: (code: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handle(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handle);
    return () => document.removeEventListener("mousedown", handle);
  }, []);

  const selectedName = wards.find((w) => w.code === selected)?.name ?? "選択";

  return (
    <div className="relative inline-block" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="border border-slate-300 rounded px-3 py-1.5 bg-white min-w-24 text-left text-sm"
      >
        {selectedName} ▾
      </button>
      {open && (
        <ul className="absolute z-10 mt-1 max-h-64 w-40 overflow-y-auto rounded border border-slate-300 bg-white shadow-lg">
          {wards.map((w) => (
            <li key={w.code}>
              <button
                type="button"
                onClick={() => {
                  onChange(w.code);
                  setOpen(false);
                }}
                className={`block w-full px-3 py-1.5 text-left text-sm hover:bg-slate-100 ${
                  w.code === selected ? "bg-blue-50 font-medium" : ""
                }`}
              >
                {w.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
