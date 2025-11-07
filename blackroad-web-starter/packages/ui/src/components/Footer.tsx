import Link from "next/link";
import type { Route } from "next";

type FooterLink = {
  href: Route<string>;
  label: string;
};

type FooterProps = {
  links: FooterLink[];
};

export function Footer({ links }: FooterProps) {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-sm text-slate-600 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs text-slate-400">© {year} BlackRoad. All rights reserved.</p>
        <nav aria-label="Footer navigation">
          <ul className="flex flex-wrap gap-4">
            {links.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="transition hover:text-slate-900"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </footer>
  );
}
