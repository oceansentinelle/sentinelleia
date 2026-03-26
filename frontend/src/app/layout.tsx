import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Ocean Sentinel - Dashboard BARAG",
  description: "Surveillance océanographique temps réel - Bassin d'Arcachon",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="fr"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <Providers>
          <div className="flex-1">{children}</div>
          <footer className="text-xs opacity-70 text-center py-4 border-t mt-8">
            Ce travail a bénéficié du soutien de l&apos;Infrastructure de Recherche Littorale et Côtière : IR ILICO.
          </footer>
        </Providers>
      </body>
    </html>
  );
}
