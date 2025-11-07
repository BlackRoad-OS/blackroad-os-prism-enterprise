import type { Metadata } from "next";
import "./globals.css";
import { Header, Footer } from "@br/ui";
import { Analytics } from "./components/Analytics";
import { hero, siteConfig } from "./site-config";

export const metadata: Metadata = {
  title: siteConfig.name,
  description: hero.description,
  metadataBase: new URL(`https://${siteConfig.domain}`),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col">
        <Header title={siteConfig.name} navigation={siteConfig.navigation} />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-12">{children}</main>
        <Footer
          links={[
            { label: "Docs", href: "/docs" },
            { label: "Status", href: "/status" },
            { label: "Privacy", href: "/privacy" }
          ]}
        />
        <Analytics />
      </body>
    </html>
  );
}
