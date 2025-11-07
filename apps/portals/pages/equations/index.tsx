import { useEffect, useState } from 'react';
import Head from 'next/head';

interface Am2Response {
  t: number[];
  a: number[];
  theta: number[];
  amp: number[];
  units: Record<string, string>;
  thermo?: Record<string, unknown>;
}

interface TransportResponse {
  x: number[];
  A: number[];
  flux: number[];
  mass: number;
  mass_initial: number;
  mass_error: number;
  mass_relative_error: number;
  units: Record<string, string>;
  invariants: Record<string, { tolerance: number; relative_error: number; pass: boolean }>;
  thermo?: Record<string, unknown>;
}

interface TruthTableResponse {
  expression: string;
  variables: string[];
  rows: Record<string, boolean>[];
}

interface PrimesResponse {
  limit: number;
  count: number;
  primes: number[];
}

const fetchJson = async <T,>(url: string, init?: RequestInit): Promise<T> => {
  const res = await fetch(url, init);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return (await res.json()) as T;
};

const fetchText = async (url: string, init?: RequestInit): Promise<string> => {
  const res = await fetch(url, init);
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return await res.text();
};

const pretty = (value: unknown): string => JSON.stringify(value, null, 2);

const buildTransportPayload = () => {
  const points = 64;
  const xs = Array.from({ length: points }, (_, i) => -1 + (2 * i) / (points - 1));
  const A = xs.map((x) => Math.exp(-x * x));
  const rho = xs.map((x) => 1 - 0.2 * x * x);
  return {
    x: xs,
    A,
    rho,
    dt: 1e-3,
    steps: 50,
    bits: 8,
    temperature: 300,
  };
};

export default function EquationsPage() {
  const [am2, setAm2] = useState<Am2Response | null>(null);
  const [am2Svg, setAm2Svg] = useState<string>('');
  const [transport, setTransport] = useState<TransportResponse | null>(null);
  const [transportPgm, setTransportPgm] = useState<string>('');
  const [mandelbrot, setMandelbrot] = useState<string>('');
  const [waveSvg, setWaveSvg] = useState<string>('');
  const [primes, setPrimes] = useState<PrimesResponse | null>(null);
  const [truthTable, setTruthTable] = useState<TruthTableResponse | null>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const load = async () => {
      try {
        const am2Data = await fetchJson<Am2Response>('/api/ambr/sim/am2?bits=8&temperature=300');
        setAm2(am2Data);
        const am2Plot = await fetchText('/api/ambr/plot/am2.svg?bits=8&temperature=300');
        setAm2Svg(am2Plot);

        const transportPayload = buildTransportPayload();
        const transportData = await fetchJson<TransportResponse>('/api/ambr/sim/transport', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(transportPayload),
        });
        setTransport(transportData);
        const pgm = await fetchText('/api/ambr/field/a.pgm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ values: transportData.A }),
        });
        setTransportPgm(pgm);

        const mandelbrotText = await fetchText('/api/math/fractals/mandelbrot.pgm?width=64&height=64&iter=64');
        setMandelbrot(mandelbrotText);

        const wave = await fetchText('/api/math/waves/sine.svg?samples=128&freq=1.5');
        setWaveSvg(wave);

        const primesData = await fetchJson<PrimesResponse>('/api/math/primes.json?limit=200');
        setPrimes(primesData);

        const tt = await fetchJson<TruthTableResponse>('/api/math/logic/truth-table', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ expression: 'a and (b or not c)', variables: ['a', 'b', 'c'] }),
        });
        setTruthTable(tt);
      } catch (err) {
        setError((err as Error).message);
      }
    };

    void load();
  }, []);

  const renderSvg = (svg: string) => (
    <div
      className="overflow-auto rounded border border-neutral-300 bg-white p-4 shadow-sm"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  );

  return (
    <>
      <Head>
        <title>Equations Lab — Text-Only Rendering</title>
        <meta name="description" content="Amundson–BlackRoad + Infinity Math rendered with text artefacts only." />
      </Head>
      <main className="mx-auto flex max-w-5xl flex-col gap-8 p-6">
        <header>
          <h1 className="text-3xl font-semibold">Equations Lab</h1>
          <p className="mt-2 text-sm text-neutral-600">
            All artefacts on this page are delivered as JSON, SVG, or ASCII PGM to honour the text-only policy.
          </p>
          {error ? <p className="mt-2 rounded bg-red-100 p-2 text-sm text-red-700">{error}</p> : null}
        </header>

        <section>
          <h2 className="text-2xl font-semibold">AM-2 Spiral</h2>
          {am2 ? (
            <>
              <pre className="mt-2 max-h-64 overflow-auto rounded bg-neutral-900 p-3 text-xs text-lime-100">
                {pretty({ units: am2.units, thermo: am2.thermo })}
              </pre>
              {am2Svg ? <div className="mt-4">{renderSvg(am2Svg)}</div> : null}
            </>
          ) : (
            <p className="text-sm text-neutral-500">Loading AM-2 data…</p>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-semibold">Transport Invariants</h2>
          {transport ? (
            <>
              <pre className="mt-2 max-h-64 overflow-auto rounded bg-neutral-900 p-3 text-xs text-sky-100">
                {pretty({
                  invariants: transport.invariants,
                  mass: transport.mass,
                  mass_initial: transport.mass_initial,
                  mass_error: transport.mass_error,
                  thermo: transport.thermo,
                })}
              </pre>
              {transportPgm ? (
                <pre className="mt-4 max-h-64 overflow-auto rounded bg-neutral-100 p-3 text-[10px] leading-tight text-neutral-700">
                  {transportPgm}
                </pre>
              ) : null}
            </>
          ) : (
            <p className="text-sm text-neutral-500">Loading transport simulation…</p>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-semibold">Mandelbrot (PGM)</h2>
          {mandelbrot ? (
            <pre className="mt-2 max-h-64 overflow-auto rounded bg-neutral-100 p-3 text-[10px] leading-tight text-neutral-700">
              {mandelbrot}
            </pre>
          ) : (
            <p className="text-sm text-neutral-500">Loading fractal…</p>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-semibold">Waveform (SVG)</h2>
          {waveSvg ? <div>{renderSvg(waveSvg)}</div> : <p className="text-sm text-neutral-500">Loading wave…</p>}
        </section>

        <section>
          <h2 className="text-2xl font-semibold">Prime Constellations</h2>
          {primes ? (
            <pre className="mt-2 max-h-64 overflow-auto rounded bg-neutral-900 p-3 text-xs text-amber-100">
              {pretty({ limit: primes.limit, count: primes.count, sample: primes.primes.slice(0, 32) })}
            </pre>
          ) : (
            <p className="text-sm text-neutral-500">Loading primes…</p>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-semibold">Logic Truth Table</h2>
          {truthTable ? (
            <pre className="mt-2 max-h-64 overflow-auto rounded bg-neutral-900 p-3 text-xs text-fuchsia-100">
              {pretty(truthTable.rows.slice(0, 8))}
            </pre>
          ) : (
            <p className="text-sm text-neutral-500">Loading truth table…</p>
          )}
        </section>
      </main>
    </>
  );
}
