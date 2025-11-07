import Link from "next/link";
import { Button, Card } from "@br/ui";
import { features, hero } from "./site-config";

export default function HomePage() {
  return (
    <div className="flex flex-col gap-16">
      <section className="rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-10 text-white shadow-xl">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-300">{hero.eyebrow}</p>
        <h2 className="mt-4 text-4xl font-semibold leading-tight sm:text-5xl">{hero.title}</h2>
        <p className="mt-6 max-w-2xl text-lg text-slate-200">{hero.description}</p>
        <div className="mt-8 flex flex-wrap gap-4">
          <Button asChild>
            <Link href={hero.primary.href}>{hero.primary.label}</Link>
          </Button>
          <Button asChild variant="secondary">
            <Link href={hero.secondary.href}>{hero.secondary.label}</Link>
          </Button>
        </div>
      </section>

      <section>
        <h3 className="text-2xl font-semibold text-slate-900">Operational highlights</h3>
        <div className="mt-6 grid gap-6 md:grid-cols-3">
          {features.map((feature) => (
            <Card key={feature.title} title={feature.title} description={feature.description} />
          ))}
        </div>
      </section>
    </div>
  );
}
