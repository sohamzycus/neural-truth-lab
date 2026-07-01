import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Source_Serif_4 } from "next/font/google";
import { ThemeProvider } from "@/components/theme-provider";
import { AppProviders } from "@/components/providers/app-providers";
import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { SITE } from "@/lib/constants";
import "./globals.css";

const fontBody = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-ibm-sans",
  display: "swap",
});

const fontDisplay = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-source-serif",
  display: "swap",
});

const fontMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-ibm-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: SITE.name,
    template: `%s · ${SITE.name}`,
  },
  description: SITE.tagline,
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "https://neural-truth-lab.netlify.app"
  ),
  openGraph: {
    title: SITE.name,
    description: SITE.tagline,
    siteName: SITE.name,
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: SITE.name,
    description: SITE.tagline,
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>): React.ReactElement {
  return (
    <html
      lang="en"
      className={`${fontBody.variable} ${fontDisplay.variable} ${fontMono.variable}`}
      suppressHydrationWarning
    >
      <body className="min-h-screen font-sans antialiased" suppressHydrationWarning>
        <ThemeProvider>
          <AppProviders>
            <a
              href="#main"
              className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-[var(--accent-primary)] focus:px-4 focus:py-2 focus:text-white"
            >
              Skip to content
            </a>
            <Header />
            <main id="main">{children}</main>
            <Footer />
          </AppProviders>
        </ThemeProvider>
      </body>
    </html>
  );
}
